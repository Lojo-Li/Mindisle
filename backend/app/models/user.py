"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Boolean, Enum, Date
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, comment="用户ID")
    email = Column(String(255), unique=True, index=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), comment="昵称")
    avatar = Column(String(500), comment="头像URL")
    gender = Column(Enum('male', 'female', 'secret'), default='secret', comment="性别")
    birth_date = Column(Date, comment="出生日期")
    phone = Column(String(20), comment="手机号")
    bio = Column(String(200), comment="个人简介")
    status = Column(Enum('active', 'inactive', 'banned'), default='active', comment="状态")
    is_verified = Column(Boolean, default=False, comment="邮箱是否验证")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    # 角色字段
    role = Column(Enum('user', 'admin', 'counselor'), default='user', comment="用户角色")

    # 隐私设置字段
    save_chat_history = Column(Boolean, default=True, comment="保存对话历史")
    allow_ai_analysis = Column(Boolean, default=False, comment="允许AI分析对话")
    chat_only_visible = Column(Boolean, default=False, comment="对话仅自己可见")
    save_test_records = Column(Boolean, default=True, comment="保存测试记录")
    test_only_visible = Column(Boolean, default=False, comment="测试结果仅自己可见")
    allow_trend_analysis = Column(Boolean, default=True, comment="允许查看趋势分析")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    deleted_at = Column(DateTime, comment="删除时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, comment="最后登录时间")

    @property
    def password(self):
        """为了兼容代码，提供password属性"""
        return self.password_hash

    @password.setter
    def password(self, value):
        """为了兼容代码，提供password设置"""
        self.password_hash = value

    @property
    def role_value(self):
        """获取角色值"""
        return self.role or "user"

    @property
    def gender_value(self):
        """获取性别值"""
        return self.gender or "secret"

    @property
    def is_active(self):
        """兼容前端需要的is_active字段"""
        return self.status == "active"

    @property
    def is_banned(self):
        """兼容前端需要的is_banned字段"""
        return self.status == "banned"

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"

