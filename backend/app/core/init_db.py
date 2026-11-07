"""
数据库初始化脚本（简化版，用于向后兼容）
"""
from sqlalchemy import text
from app.core.database import engine, Base


def _safe_migrate():
    """执行数据库迁移（幂等，容错已存在的结构）"""
    migrations = [
        # 1. 清理 likes 重复数据
        """
        DELETE t1 FROM knowledge_likes t1
        INNER JOIN knowledge_likes t2
        WHERE t1.id > t2.id AND t1.article_id = t2.article_id AND t1.user_id = t2.user_id
        """,
        # 2. likes 唯一索引
        """
        ALTER TABLE knowledge_likes ADD UNIQUE INDEX uq_knowledge_likes_article_user (article_id, user_id)
        """,
        # 3. 清理 favorites 重复数据
        """
        DELETE t1 FROM knowledge_favorites t1
        INNER JOIN knowledge_favorites t2
        WHERE t1.id > t2.id AND t1.article_id = t2.article_id AND t1.user_id = t2.user_id
        """,
        # 4. favorites 唯一索引
        """
        ALTER TABLE knowledge_favorites ADD UNIQUE INDEX uq_knowledge_favorites_article_user (article_id, user_id)
        """,
        # 5. comment_likes 唯一索引
        """
        ALTER TABLE knowledge_comment_likes ADD UNIQUE INDEX uq_comment_likes_comment_user (comment_id, user_id)
        """,
        # 6. 修正可能不一致的 comment_count
        """
        UPDATE knowledge_articles a
        SET a.comment_count = (
            SELECT COUNT(*) FROM knowledge_comments c
            WHERE c.article_id = a.id AND c.is_deleted = 0 AND c.is_visible = 1
        )
        WHERE a.comment_count != (
            SELECT COUNT(*) FROM knowledge_comments c
            WHERE c.article_id = a.id AND c.is_deleted = 0 AND c.is_visible = 1
        )
        """,
    ]
    for sql in migrations:
        try:
            with engine.begin() as conn:
                conn.execute(text(sql))
        except Exception:
            pass  # 索引已存在、表不存在等情况均忽略


def init_db():
    """初始化数据库表"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("执行数据库迁移...")
    _safe_migrate()
    print("数据库迁移完成！")


if __name__ == "__main__":
    init_db()
