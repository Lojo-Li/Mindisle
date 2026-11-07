"""
认证相关的 Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr
    purpose: Optional[str] = None  # "register" 注册 / "reset" 找回密码


class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6, max_length=20)


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class VerifyEmailForResetRequest(BaseModel):
    """验证邮箱（重置密码）请求"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr
    newPassword: str = Field(..., min_length=6, max_length=20)


class ApiResponse(BaseModel):
    """通用API响应"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
