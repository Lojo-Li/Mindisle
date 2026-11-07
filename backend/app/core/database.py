"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# 配置 SQLAlchemy 日志级别，减少不必要的输出
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.APP_DEBUG,
    # 隐式开启只读模式的事务（可以避免不必要的 ROLLBACK 日志）
    connect_args={
        "charset": "utf8mb4",
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
        # 如果有未提交的修改（写入操作），自动提交
        if db.dirty or db.new or db.deleted:
            db.commit()
    except Exception:
        # 发生异常时回滚
        db.rollback()
        raise
    finally:
        db.close()
