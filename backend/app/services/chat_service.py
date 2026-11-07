"""
聊天服务 - 业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime

from app.models.chat import ChatDialogue, ChatMessage, ChatTag, ChatDialogueTag
from app.models.user import User
from app.schemas.chat import (
    DialogueCreate, DialogueUpdate, TagCreate, MessageCreate
)
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service
from app.services.crisis_service import (
    detect_crisis,
    build_crisis_system_instruction,
    get_crisis_level_label,
)


class ChatService:
    """聊天服务类"""

    @staticmethod
    def _should_generate_dialogue_title(dialogue: ChatDialogue, message_count: int) -> bool:
        """仅在首轮对话后为默认标题的会话生成主题。"""
        default_titles = {"", "新对话", "未命名对话", "新聊天"}
        current_title = (dialogue.title or "").strip()
        return message_count == 2 and current_title in default_titles

    @staticmethod
    def _fallback_topic(user_content: str) -> str:
        """生成失败时，基于用户首条消息给一个简短主题。"""
        cleaned = " ".join((user_content or "").split())
        if not cleaned:
            return "新的心理咨询"
        return cleaned[:14] + ("..." if len(cleaned) > 14 else "")

    @staticmethod
    def _generate_dialogue_topic(user_content: str, ai_content: str) -> str:
        """根据首轮问答生成简短主题。"""
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "你是对话主题提炼助手。"
                    "请基于以下首轮对话内容生成一个中文短主题。"
                    "要求：8-16字、不要标点、不要引号、不要解释、不要出现\"用户\"\"AI\"\"助手\"等词汇，只输出主题本身。"
                )
            },
            {
                "role": "user",
                "content": f"提问：{user_content}\n回应：{ai_content}"
            }
        ]
        topic = ai_service.chat(messages=prompt_messages, stream=False, temperature=0.2, max_tokens=32)
        topic = (topic or "").strip().replace("\n", "")
        if not topic:
            return ChatService._fallback_topic(user_content)
        return topic[:24]

    @staticmethod
    def apply_auto_dialogue_title(
        db: Session,
        dialogue: ChatDialogue,
        user_content: str,
        ai_content: str
    ) -> str:
        """首轮对话后自动设置主题，返回最终标题。"""
        message_count = db.query(func.count(ChatMessage.id)).filter(
            and_(
                ChatMessage.dialogue_id == dialogue.id,
                ChatMessage.is_deleted == False
            )
        ).scalar() or 0

        if not ChatService._should_generate_dialogue_title(dialogue, message_count):
            return dialogue.title

        try:
            dialogue.title = ChatService._generate_dialogue_topic(user_content=user_content, ai_content=ai_content)
        except Exception:
            dialogue.title = ChatService._fallback_topic(user_content)

        return dialogue.title

    # ========== 对话管理 ==========
    @staticmethod
    def get_dialogue_list(db: Session, user_id: int) -> List[dict]:
        """
        获取用户的对话列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[dict]: 对话列表
        """
        dialogues = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).order_by(desc(ChatDialogue.updated_at)).all()

        result = []
        for dialogue in dialogues:
            # 获取消息数量
            message_count = db.query(func.count(ChatMessage.id)).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).scalar() or 0

            # 获取最后一条消息
            last_message = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).first()

            # 获取标签
            tags = db.query(ChatTag).join(
                ChatDialogueTag,
                ChatDialogueTag.tag_id == ChatTag.id
            ).filter(
                ChatDialogueTag.dialogue_id == dialogue.id
            ).all()

            result.append({
                "id": dialogue.id,
                "title": dialogue.title,
                "created_at": dialogue.created_at,
                "updated_at": dialogue.updated_at,
                "message_count": message_count,
                "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags],
                "last_message": last_message.content[:50] + "..." if last_message and len(last_message.content) > 50 else (last_message.content if last_message else None)
            })

        return result

    @staticmethod
    def get_dialogue_detail(db: Session, dialogue_id: int, user_id: int) -> Optional[dict]:
        """
        获取对话详情

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID

        Returns:
            Optional[dict]: 对话详情
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return None

        # 获取消息列表
        messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.dialogue_id == dialogue_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(ChatMessage.created_at).all()

        # 获取标签
        tags = db.query(ChatTag).join(
            ChatDialogueTag,
            ChatDialogueTag.tag_id == ChatTag.id
        ).filter(
            ChatDialogueTag.dialogue_id == dialogue_id
        ).all()

        return {
            "id": dialogue.id,
            "user_id": dialogue.user_id,
            "title": dialogue.title,
            "created_at": dialogue.created_at,
            "updated_at": dialogue.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags]
        }

    @staticmethod
    def create_dialogue(db: Session, user_id: int, dialogue_data: DialogueCreate) -> ChatDialogue:
        """
        创建新对话

        Args:
            db: 数据库会话
            user_id: 用户ID
            dialogue_data: 对话数据

        Returns:
            ChatDialogue: 创建的对话对象
        """
        # 创建对话
        dialogue = ChatDialogue(
            user_id=user_id,
            title=dialogue_data.title
        )
        db.add(dialogue)
        db.flush()  # 获取 dialogue.id

        # 关联标签
        if dialogue_data.tag_ids:
            for tag_id in dialogue_data.tag_ids:
                # 检查标签是否存在且属于该用户
                tag = db.query(ChatTag).filter(
                    and_(
                        ChatTag.id == tag_id,
                        ChatTag.user_id == user_id,
                        ChatTag.is_deleted == False
                    )
                ).first()
                if tag:
                    dialogue_tag = ChatDialogueTag(
                        dialogue_id=dialogue.id,
                        tag_id=tag_id
                    )
                    db.add(dialogue_tag)

        db.commit()
        db.refresh(dialogue)
        return dialogue

    @staticmethod
    def update_dialogue_title(db: Session, dialogue_id: int, user_id: int, title: str) -> Optional[ChatDialogue]:
        """
        更新对话标题

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID
            title: 新标题

        Returns:
            Optional[ChatDialogue]: 更新后的对话对象
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return None

        dialogue.title = title
        db.commit()
        db.refresh(dialogue)
        return dialogue

    @staticmethod
    def delete_dialogue(db: Session, dialogue_id: int, user_id: int) -> bool:
        """
        删除对话（软删除）

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return False

        dialogue.is_deleted = True
        db.commit()
        return True

    # ========== 消息管理 ==========
    @staticmethod
    def send_message(db: Session, dialogue_id: int, user_id: int, message_data: MessageCreate) -> dict:
        """
        发送消息并获取 AI 回复

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            user_id: 用户ID
            message_data: 消息数据

        Returns:
            dict: 包含用户消息和 AI 回复的字典
        """
        # 验证对话是否属于该用户
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            raise ValueError("对话不存在或无权访问")

        # 保存用户消息
        user_message = ChatMessage(
            dialogue_id=dialogue_id,
            role="user",
            content=message_data.content
        )
        db.add(user_message)
        db.flush()

        # 获取历史消息（最近10条）
        history_messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.dialogue_id == dialogue_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(desc(ChatMessage.created_at)).limit(10).all()

        # RAG：从心理知识库检索相似案例
        similar_cases = rag_service.search_similar(message_data.content)
        kb_context = ""
        if similar_cases:
            parts = []
            for case in similar_cases:
                parts.append(
                    f"相似问题：{case['input']}\n参考回答：{case['output']}"
                )
            kb_context = (
                "以下是从心理咨询知识库中检索到的相似案例，供你参考。"
                "请你**千万不要照搬参考回答中的生硬语气**，而是用温暖、共情、自然的口吻，"
                "把这些知识转化为对用户的贴心回应，让用户感受到你真心在乎ta的感受：\n\n"
                + "\n\n---\n\n".join(parts)
            )

        # ── 危机检测 ────────────────────────────────────────────────────
        crisis_level, crisis_keywords = detect_crisis(message_data.content)
        is_crisis = crisis_level > 0

        # 构建消息列表（按时间正序）
        base_system_prompt = ai_service.generate_system_prompt(kb_context)
        if is_crisis:
            crisis_instruction = build_crisis_system_instruction(is_crisis)
            base_system_prompt += crisis_instruction

        messages_list = [
            {"role": "system", "content": base_system_prompt}
        ]
        for msg in reversed(history_messages):
            messages_list.append({
                "role": msg.role,
                "content": msg.content
            })

        # 调用 AI 服务获取回复
        try:
            ai_reply = ai_service.chat(messages=messages_list, stream=False)
        except Exception as e:
            ai_reply = f"抱歉，我遇到了一些问题：{str(e)}。请稍后再试。"

        # 保存 AI 回复
        ai_message = ChatMessage(
            dialogue_id=dialogue_id,
            role="assistant",
            content=ai_reply
        )
        db.add(ai_message)
        db.flush()  # flush 后计数包含 ai_message，_should_generate_dialogue_title 判断才准确

        # 首轮问答结束后，自动生成主题标题
        final_dialogue_title = ChatService.apply_auto_dialogue_title(
            db=db,
            dialogue=dialogue,
            user_content=message_data.content,
            ai_content=ai_reply
        )

        db.commit()

        return {
            "user_message": {
                "id": user_message.id,
                "role": "user",
                "content": user_message.content,
                "created_at": user_message.created_at
            },
            "ai_message": {
                "id": ai_message.id,
                "role": "assistant",
                "content": ai_message.content,
                "created_at": ai_message.created_at
            },
            "dialogue_title": final_dialogue_title,
            "crisis_detected": is_crisis,
            "crisis_level": crisis_level,
            "crisis_keywords": crisis_keywords if is_crisis else []
        }

    # ========== 标签管理 ==========
    @staticmethod
    def get_all_tags(db: Session, user_id: int) -> List[ChatTag]:
        """
        获取用户的所有标签

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[ChatTag]: 标签列表
        """
        return db.query(ChatTag).filter(
            and_(
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).order_by(ChatTag.created_at).all()

    @staticmethod
    def create_tag(db: Session, user_id: int, tag_data: TagCreate) -> ChatTag:
        """
        创建标签

        Args:
            db: 数据库会话
            user_id: 用户ID
            tag_data: 标签数据

        Returns:
            ChatTag: 创建的标签对象
        """
        # 检查标签名是否已存在
        existing_tag = db.query(ChatTag).filter(
            and_(
                ChatTag.user_id == user_id,
                ChatTag.name == tag_data.name,
                ChatTag.is_deleted == False
            )
        ).first()

        if existing_tag:
            raise ValueError("标签名已存在")

        tag = ChatTag(
            user_id=user_id,
            name=tag_data.name,
            color=tag_data.color
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def delete_tag(db: Session, tag_id: int, user_id: int) -> bool:
        """
        删除标签

        Args:
            db: 数据库会话
            tag_id: 标签ID
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        tag = db.query(ChatTag).filter(
            and_(
                ChatTag.id == tag_id,
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).first()

        if not tag:
            return False

        tag.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def add_tag_to_dialogue(db: Session, dialogue_id: int, tag_id: int, user_id: int) -> bool:
        """
        为对话添加标签

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            tag_id: 标签ID
            user_id: 用户ID

        Returns:
            bool: 是否添加成功
        """
        # 验证对话和标签是否都属于该用户
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        tag = db.query(ChatTag).filter(
            and_(
                ChatTag.id == tag_id,
                ChatTag.user_id == user_id,
                ChatTag.is_deleted == False
            )
        ).first()

        if not dialogue or not tag:
            return False

        # 检查是否已经关联
        existing = db.query(ChatDialogueTag).filter(
            and_(
                ChatDialogueTag.dialogue_id == dialogue_id,
                ChatDialogueTag.tag_id == tag_id
            )
        ).first()

        if existing:
            return True  # 已关联，直接返回成功

        # 创建关联
        dialogue_tag = ChatDialogueTag(
            dialogue_id=dialogue_id,
            tag_id=tag_id
        )
        db.add(dialogue_tag)
        db.commit()
        return True

    @staticmethod
    def remove_tag_from_dialogue(db: Session, dialogue_id: int, tag_id: int, user_id: int) -> bool:
        """
        从对话中移除标签

        Args:
            db: 数据库会话
            dialogue_id: 对话ID
            tag_id: 标签ID
            user_id: 用户ID

        Returns:
            bool: 是否移除成功
        """
        # 验证对话是否属于该用户
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return False

        # 查找关联并删除
        existing = db.query(ChatDialogueTag).filter(
            and_(
                ChatDialogueTag.dialogue_id == dialogue_id,
                ChatDialogueTag.tag_id == tag_id
            )
        ).first()

        if not existing:
            return False

        db.delete(existing)
        db.commit()
        return True


# 创建全局聊天服务实例
chat_service = ChatService()
