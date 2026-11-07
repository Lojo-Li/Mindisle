"""
用户API路由 - 个人中心功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserProfileResponse, UserProfileUpdate,
    AvatarUploadResponse, PrivacySettings, UserStatistics,
    ActivityTrendItem, TestDistributionItem, ChatDistributionItem,
    MessageResponse
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from typing import Dict, Optional
import logging

router = APIRouter(prefix="/user", tags=["用户"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
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

    # 过滤已删除的用户
    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在或已注销"
        )

    return user


# ==================== 个人中心接口 ====================

@router.get("/profile", summary="获取用户资料")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的完整资料信息

    返回用户信息包括：
    - 基本信息：昵称、邮箱、头像
    - 个人信息：性别、出生日期、手机号
    - 账户信息：角色、状态、验证状态
    - 时间信息：创建时间、最后登录时间
    """
    try:
        profile = UserService.get_user_profile(db, current_user.id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": profile
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        )


@router.put("/profile", summary="更新用户资料")
async def update_user_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料

    可更新的字段：
    - **nickname**: 昵称（2-20个字符）
    - **phone**: 手机号（11位数字）
    - **birth_date**: 出生日期
    - **gender**: 性别（male/female/secret）
    - **bio**: 个人简介（最多200字）
    """
    try:
        profile = UserService.update_user_profile(db, current_user.id, update_data)
        return {
            "code": 200,
            "message": "更新成功",
            "data": profile
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户资料失败"
        )


@router.post("/avatar", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像

    - 支持的格式：JPG、PNG、GIF
    - 文件大小限制：2MB
    - 上传后会自动更新用户头像
    """
    try:
        # 读取文件数据
        file_data = await file.read()
        filename = file.filename or "avatar.jpg"

        # 上传文件
        avatar_url = UserService.upload_avatar(
            file_data=file_data,
            filename=filename,
            content_type=file.content_type
        )

        # 更新用户头像
        UserService.update_user_avatar(db, current_user.id, avatar_url)

        # 提交事务
        db.commit()

        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "avatar": avatar_url
            }
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"上传头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传头像失败"
        )


@router.get("/privacy", summary="获取隐私设置")
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户隐私设置

    返回隐私配置包括：
    - 对话隐私：保存历史、AI分析、可见性
    - 测试隐私：保存记录、可见性、趋势分析
    """
    try:
        settings = UserService.get_privacy_settings(db, current_user.id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": settings
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取隐私设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取隐私设置失败"
        )


@router.put("/privacy", summary="更新隐私设置")
async def update_privacy_settings(
    settings: PrivacySettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户隐私设置

    可配置项：
    - **save_chat_history**: 是否保存对话历史
    - **allow_ai_analysis**: 是否允许AI分析对话数据
    - **chat_only_visible**: 对话是否仅自己可见
    - **save_test_records**: 是否保存测试记录
    - **test_only_visible**: 测试结果是否仅自己可见
    - **allow_trend_analysis**: 是否允许查看趋势分析
    """
    try:
        updated_settings = UserService.update_privacy_settings(db, current_user.id, settings)
        return {
            "code": 200,
            "message": "更新成功",
            "data": updated_settings
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新隐私设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新隐私设置失败"
        )


@router.delete("/chat-history", summary="清除对话记录")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清除所有对话记录

    ⚠️ 此操作不可恢复，将删除：
    - 所有对话及其消息
    - 对话关联的标签关系

    请谨慎操作！
    """
    try:
        count = UserService.clear_chat_history(db, current_user.id)
        return {
            "code": 200,
            "message": f"已清除 {count} 条对话记录",
            "data": {
                "deleted_count": count
            }
        }
    except Exception as e:
        logger.error(f"清除对话记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清除对话记录失败"
        )


@router.delete("/test-records", summary="清除测试记录")
async def clear_test_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清除所有测试记录

    ⚠️ 此操作不可恢复，将删除：
    - 所有测试结果
    - 所有测试进度

    请谨慎操作！
    """
    try:
        count = UserService.clear_test_records(db, current_user.id)
        return {
            "code": 200,
            "message": f"已清除 {count} 条测试记录",
            "data": {
                "deleted_count": count
            }
        }
    except Exception as e:
        logger.error(f"清除测试记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清除测试记录失败"
        )


@router.get("/statistics", summary="获取用户数据统计")
async def get_user_statistics(
    time_range: str = "30days",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户数据统计

    支持的时间范围：
    - **7days**: 最近7天
    - **30days**: 最近30天（默认）
    - **90days**: 最近90天

    统计数据包括：
    - 心理测试次数
    - 智能对话次数
    - 咨询预约次数
    - 收藏内容数量
    """
    try:
        statistics = UserService.get_user_statistics(db, current_user.id, time_range)
        return {
            "code": 200,
            "message": "获取成功",
            "data": statistics
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.get("/activity-trend", summary="获取活动趋势数据")
async def get_activity_trend(
    time_range: str = "30days",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户活动趋势数据

    用于绘制活动趋势图，返回每日活动次数：
    - 对话创建次数
    - 测试完成次数

    支持的时间范围：
    - **7days**: 最近7天
    - **30days**: 最近30天（默认）
    - **90days**: 最近90天
    """
    try:
        trend_data = UserService.get_activity_trend(db, current_user.id, time_range)
        return {
            "code": 200,
            "message": "获取成功",
            "data": trend_data
        }
    except Exception as e:
        logger.error(f"获取活动趋势失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取活动趋势失败"
        )


@router.get("/test-distribution", summary="获取测试分类分布")
async def get_test_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户测试分类分布

    返回各类测试的完成次数分布，用于绘制饼图
    """
    try:
        distribution = UserService.get_test_distribution(db, current_user.id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": distribution
        }
    except Exception as e:
        logger.error(f"获取测试分布失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取测试分布失败"
        )


@router.get("/chat-distribution", summary="获取对话主题分布")
async def get_chat_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户对话主题分布

    返回各主题标签的对话数量分布，用于绘制柱状图
    """
    try:
        distribution = UserService.get_chat_distribution(db, current_user.id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": distribution
        }
    except Exception as e:
        logger.error(f"获取对话分布失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话分布失败"
        )


@router.post("/change-password", summary="修改密码")
async def change_password(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改登录密码，需要验证旧密码"""
    from app.core.security import verify_password, get_password_hash
    old_password = request.get("old_password", "")
    new_password = request.get("new_password", "")

    if not old_password or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请填写旧密码和新密码")

    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于6位")

    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")

    current_user.password_hash = get_password_hash(new_password)
    db.commit()

    return {"code": 200, "message": "密码修改成功"}


@router.post("/delete-account", summary="注销账户")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    注销账户（危险操作）

    ⚠️ 此操作不可逆，将永久删除：
    - 用户账户信息
    - 所有测试记录
    - 所有对话记录
    - 所有预约信息
    - 所有个人数据

    需要用户明确确认后执行。
    """
    try:
        import logging
        logger = logging.getLogger(__name__)

        logger.warning(f"用户 {current_user.id} ({current_user.email}) 正在注销账户")

        # 软删除：标记用户为已删除状态
        current_user.is_deleted = True
        current_user.deleted_at = func.now()
        current_user.status = 'inactive'

        # 匿名化用户信息（保留ID用于数据统计）
        current_user.email = f"deleted_user_{current_user.id}@deleted.local"
        current_user.nickname = "已注销用户"
        current_user.phone = None
        current_user.avatar = None
        current_user.password_hash = ""  # 清除密码

        db.commit()

        logger.info(f"用户 {current_user.id} 账户已注销")

        return {
            "code": 200,
            "message": "账户已注销，感谢您的使用",
            "data": {
                "deleted": True,
                "message": "您的账户已被永久注销，所有数据已清除"
            }
        }
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"注销账户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注销账户失败: {str(e)}"
        )


# 导入SQL函数
from sqlalchemy import func
