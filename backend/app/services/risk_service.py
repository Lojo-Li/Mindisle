"""
风险事件与引用溯源服务

把"判定出来的风险"变成"可查询、可处置、可统计的记录"。
所有写库操作都容忍失败：记录不到也不能影响对话本身。
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.risk import RiskEvent, AiMessageSource, AiFeedback
from app.models.user import User
from app.services.crisis_service import LEVEL_LABELS, RiskVerdict

logger = logging.getLogger(__name__)


class RiskService:

    # ========== 写入 ==========

    @staticmethod
    def record_risk(
        db: Session,
        user_id: int,
        dialogue_id: Optional[int],
        message_id: Optional[int],
        verdict: RiskVerdict,
        detected_by: str = "keyword",
    ) -> Optional[RiskEvent]:
        """落一条风险事件。level=0 不落库。"""
        if verdict is None or verdict.level <= 0:
            return None

        event = RiskEvent(
            user_id=user_id,
            dialogue_id=dialogue_id,
            message_id=message_id,
            level=verdict.level,
            keywords=",".join(verdict.keywords)[:300],
            detected_by=detected_by,
            action_taken=",".join(verdict.actions)[:200],
            handled_status="pending",
        )
        db.add(event)
        db.flush()
        return event

    @staticmethod
    def save_sources(db: Session, message_id: int, sources: List[dict]) -> int:
        """保存一条回答的引用来源，返回写入条数。"""
        if not message_id or not sources:
            return 0
        count = 0
        for rank, item in enumerate(sources, start=1):
            db.add(AiMessageSource(
                message_id=message_id,
                vector_id=(item.get("vector_id") or "")[:64] or None,
                doc_title=(item.get("title") or item.get("input") or "")[:200],
                snippet=item.get("snippet") or item.get("output"),
                score=item.get("score"),
                rank=rank,
            ))
            count += 1
        db.flush()
        return count

    @staticmethod
    def save_feedback(
        db: Session, user_id: int, message_id: int, rating: int, reason: Optional[str] = None
    ) -> AiFeedback:
        """记录答案反馈，同一用户对同一消息只保留最新一条。"""
        existing = db.query(AiFeedback).filter(
            and_(AiFeedback.message_id == message_id, AiFeedback.user_id == user_id)
        ).first()
        if existing:
            existing.rating = rating
            existing.reason = reason
            db.commit()
            db.refresh(existing)
            return existing

        feedback = AiFeedback(
            message_id=message_id, user_id=user_id, rating=rating, reason=reason
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    # ========== 查询 ==========

    @staticmethod
    def get_message_sources(db: Session, message_id: int) -> List[dict]:
        rows = db.query(AiMessageSource).filter(
            AiMessageSource.message_id == message_id
        ).order_by(AiMessageSource.rank).all()
        return [
            {
                "vector_id": r.vector_id,
                "title": r.doc_title,
                "snippet": r.snippet,
                "score": r.score,
                "rank": r.rank,
            }
            for r in rows
        ]

    @staticmethod
    def list_events(
        db: Session,
        level: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        q = db.query(RiskEvent)
        if level:
            q = q.filter(RiskEvent.level == level)
        if status:
            q = q.filter(RiskEvent.handled_status == status)

        total = q.count()
        rows = (
            q.order_by(desc(RiskEvent.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        user_ids = {r.user_id for r in rows}
        users = {}
        if user_ids:
            users = {
                u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()
            }

        items = []
        for r in rows:
            user = users.get(r.user_id)
            items.append({
                "id": r.id,
                "user_id": r.user_id,
                "user_name": (user.nickname or user.email) if user else None,
                "dialogue_id": r.dialogue_id,
                "message_id": r.message_id,
                "level": r.level,
                "level_label": LEVEL_LABELS.get(r.level, "未知"),
                "keywords": r.keywords,
                "detected_by": r.detected_by,
                "handled_status": r.handled_status,
                "handled_by": r.handled_by,
                "note": r.note,
                "created_at": r.created_at,
                "handled_at": r.handled_at,
            })

        pending = db.query(func.count(RiskEvent.id)).filter(
            RiskEvent.handled_status == "pending"
        ).scalar() or 0

        return {"total": total, "items": items, "pending_count": pending}

    @staticmethod
    def handle_event(
        db: Session,
        event_id: int,
        status: str,
        note: Optional[str],
        admin_id: Optional[int] = None,
    ) -> RiskEvent:
        event = db.query(RiskEvent).filter(RiskEvent.id == event_id).first()
        if not event:
            raise ValueError("风险事件不存在")

        event.handled_status = status
        event.note = note
        event.handled_by = admin_id
        event.handled_at = datetime.now()
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def stats(db: Session) -> Dict[str, Any]:
        total = db.query(func.count(RiskEvent.id)).scalar() or 0
        pending = db.query(func.count(RiskEvent.id)).filter(
            RiskEvent.handled_status == "pending"
        ).scalar() or 0

        by_level = {}
        for level, count in db.query(
            RiskEvent.level, func.count(RiskEvent.id)
        ).group_by(RiskEvent.level).all():
            by_level[str(level)] = count

        since = datetime.now() - timedelta(days=6)
        rows = db.query(
            func.date(RiskEvent.created_at), func.count(RiskEvent.id)
        ).filter(RiskEvent.created_at >= since).group_by(
            func.date(RiskEvent.created_at)
        ).all()
        day_map = {str(d): c for d, c in rows}

        last_7_days = []
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            last_7_days.append({"date": day, "count": day_map.get(day, 0)})

        return {
            "total": total,
            "pending": pending,
            "by_level": by_level,
            "last_7_days": last_7_days,
        }


risk_service = RiskService()
