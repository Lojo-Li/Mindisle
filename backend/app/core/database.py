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

# 根据数据库类型设置不同的连接参数
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_is_mysql = settings.DATABASE_URL.startswith("mysql")

_engine_args = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": settings.APP_DEBUG,
}

if _is_mysql:
    # 隐式开启只读模式的事务（可以避免不必要的 ROLLBACK 日志）
    _engine_args["connect_args"] = {"charset": "utf8mb4"}
elif _is_sqlite:
    # SQLite 需要允许跨线程访问（FastAPI 多线程处理请求）
    _engine_args["connect_args"] = {"check_same_thread": False}
    _engine_args.pop("pool_recycle", None)

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **_engine_args)

if _is_sqlite:
    # SQLite 只有 INTEGER PRIMARY KEY 才会自增，而模型使用 BigInteger。
    # 在 SQLite 编译阶段把 BIGINT 主键改写为 INTEGER，便于本地无 MySQL 时调试。
    from sqlalchemy import BigInteger
    from sqlalchemy.ext.compiler import compiles

    @compiles(BigInteger, "sqlite")
    def _compile_bigint_sqlite(type_, compiler, **kw):
        return "INTEGER"


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
