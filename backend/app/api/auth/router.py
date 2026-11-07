"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    SendCodeRequest,
    VerifyEmailForResetRequest,
    ResetPasswordRequest,
    ApiResponse
)
from app.schemas.user import Token, UserResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post("/login", summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码
    """
    result = AuthService.login(db, login_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 返回符合前端期望的格式
    # result["user"] 可能是 Pydantic 模型（users 表）或 dict（admins 表），均处理
    user_data = result["user"]
    user_info = user_data.model_dump() if hasattr(user_data, 'model_dump') else user_data
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": result["access_token"],
            "userInfo": user_info,
            "redirect": result.get("redirect", "/")
        }
    }


@router.post("/register", summary="用户注册")
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **email**: 邮箱地址
    - **code**: 邮箱验证码
    - **password**: 密码
    """
    # 先检查邮箱是否已注册
    existing_user = AuthService.get_user_by_email(db, register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册，请直接登录"
        )

    # 验证验证码
    if not AuthService.verify_code(register_data.email, register_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期，请重新获取"
        )

    # 创建用户
    try:
        user = AuthService.create_user(db, register_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

    # 注册成功后自动登录，创建访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # 返回符合前端期望的格式，包含token和用户信息
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": access_token,
            "userInfo": UserResponse.model_validate(user).model_dump()
        }
    }


@router.post("/send-code", summary="发送验证码")
async def send_code(
    request: SendCodeRequest,
    db: Session = Depends(get_db)
):
    """
    发送邮箱验证码

    - **email**: 邮箱地址
    - **purpose**: 验证码用途，"register" 注册 / "reset" 找回密码

    验证码有效期为5分钟，每个邮箱间隔60秒才能重新发送。
    """
    success, message, remaining = AuthService.send_verification_code(db, request.email, request.purpose)

    if success:
        return {
            "code": 200,
            "message": message,
            "data": {"expire_seconds": 300}  # 5分钟有效期
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


@router.get("/user-info", summary="获取当前用户信息")
async def get_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前登录用户的信息"""
    token = credentials.credentials
    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 返回符合前端期望的格式
    return {
        "code": 200,
        "message": "获取成功",
        "data": UserResponse.model_validate(user).model_dump()
    }


@router.post("/logout", response_model=ApiResponse, summary="退出登录")
async def logout():
    """
    退出登录
    (前端需要清除存储的token)
    """
    return ApiResponse(code=200, message="退出成功")


@router.post("/verify-email-reset", summary="验证邮箱（重置密码）")
async def verify_email_for_reset(request: VerifyEmailForResetRequest):
    """
    验证邮箱和验证码（重置密码前）

    - **email**: 邮箱地址
    - **code**: 验证码

    验证成功后允许继续重置密码。
    """
    # 验证验证码（不删除，用于后续重置密码）
    if not AuthService.verify_code_for_reset(request.email, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # 检查用户是否存在
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        user = AuthService.get_user_by_email(db, request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该邮箱未注册"
            )

        return {
            "code": 200,
            "message": "验证成功",
            "data": {"email": request.email}
        }
    finally:
        db.close()


@router.post("/reset-password", summary="重置密码")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    重置密码

    - **email**: 邮箱地址
    - **newPassword**: 新密码
    """
    # 重置密码
    if not AuthService.reset_password(db, request.email, request.newPassword):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置密码失败，请重新验证邮箱"
        )

    return {
        "code": 200,
        "message": "密码重置成功，请使用新密码登录"
    }


# 导入User模型用于user-info端点
from app.models.user import User
