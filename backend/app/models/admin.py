"""
管理员相关数据库模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Boolean, Enum, func
from app.core.database import Base


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True, index=True, comment="管理员ID")

    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(100), comment="真实姓名")
    email = Column(String(100), comment="邮箱")

    # 权限
    role = Column(Enum('super_admin', 'admin', 'moderator'), default='admin', comment="角色")
    permissions = Column(Text, comment="权限列表（JSON格式）")

    # 状态
    status = Column(Enum('active', 'inactive'), default='active', comment="状态")
    last_login_at = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime, comment="删除时间")

    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username}, role={self.role})>"

    @property
    def is_super_admin(self):
        """是否是超级管理员"""
        return self.role == 'super_admin'

    @property
    def is_active(self):
        """是否激活（兼容代码）"""
        return self.status == 'active'
