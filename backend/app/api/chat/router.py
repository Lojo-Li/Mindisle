"""
聊天路由 - 智能心理问答
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List
import asyncio
import json
from app.core.database import get_db, SessionLocal
from app.models.chat import ChatDialogue, ChatMessage
from app.schemas.chat import (
    DialogueCreate, DialogueUpdate, DialogueListResponse,
    DialogueDetailResponse, TagCreate, TagResponse,
    MessageCreate, ChatResponse
)
from app.services.chat_service import chat_service
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service
from app.services.auth_service import AuthService
from app.services.crisis_service import detect_risk, build_crisis_system_instruction
from app.services.risk_service import risk_service

router = APIRouter(prefix="/chat", tags=["智能问答"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """从 token 中获取当前用户 ID"""
    from app.core.security import decode_access_token
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
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
    return int(user_id)


# ========== 对话管理 ==========

@router.get("/list", summary="获取对话列表")
async def get_dialogue_list(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取当前用户的所有对话

    返回对话列表，包含：
    - 对话基本信息
    - 消息数量
    - 最后一条消息预览
    - 关联的标签
    """
    dialogues = chat_service.get_dialogue_list(db, user_id)
    return {
        "code": 200,
        "message": "获取成功",
        "data": dialogues
    }


@router.post("/create", summary="创建新对话")
async def create_dialogue(
    dialogue_data: DialogueCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    创建新的对话

    - **title**: 对话标题（默认"新对话"）
    - **tag_ids**: 关联的标签ID列表（可选）
    """
    dialogue = chat_service.create_dialogue(db, user_id, dialogue_data)
    return {
        "code": 200,
        "message": "创建成功",
        "data": {
            "id": dialogue.id,
            "title": dialogue.title,
            "created_at": dialogue.created_at
        }
    }


# ========== 标签管理（必须在动态路由之前）==========

@router.get("/tags", summary="获取所有标签")
async def get_all_tags(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取当前用户创建的所有标签
    """
    tags = chat_service.get_all_tags(db, user_id)
    return {
        "code": 200,
        "message": "获取成功",
        "data": tags
    }


@router.post("/tag", summary="创建标签")
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    创建新的标签

    - **name**: 标签名称（1-50字符）
    - **color**: 标签颜色（默认 #1890ff）
    """
    try:
        tag = chat_service.create_tag(db, user_id, tag_data)
        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/tag/{tag_id}", summary="删除标签")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    删除指定标签

    删除标签不会删除对话，只是移除关联关系
    """
    success = chat_service.delete_tag(db, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "删除成功"
    }


# ========== 语音转文字（必须在动态路由之前）==========

@router.post("/voice-to-text", summary="语音转文字")
async def voice_to_text(
    audio_file: UploadFile = File(...),
    language: str = "zh-CN",
    user_id: int = Depends(get_current_user_id)
):
    """
    将语音转换为文字（使用豆包大模型录音文件识别）

    - **audio_file**: 音频文件（支持 mp3, wav, m4a, ogg, webm）
    - **language**: 语言代码（默认 zh-CN）

    支持的语言：
    - zh-CN: 中文普通话
    - en-US: 英语
    - ja-JP: 日语
    - yue-CN: 粤语
    - 等等...
    """
    from app.services.speech_service import speech_service

    try:
        text = await speech_service.transcribe_audio(audio_file, language)
        return {
            "code": 200,
            "message": "识别成功",
            "data": {
                "text": text
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )


# ========== 动态路由（必须放在最后）==========

@router.get("/{dialogue_id}", summary="获取对话详情")
async def get_dialogue_detail(
    dialogue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取指定对话的详细信息

    包含完整的消息历史和关联的标签
    """
    detail = chat_service.get_dialogue_detail(db, dialogue_id, user_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "获取成功",
        "data": detail
    }


@router.put("/{dialogue_id}/title", summary="更新对话标题")
async def update_dialogue_title(
    dialogue_id: int,
    title: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    更新对话标题

    - **dialogue_id**: 对话ID
    - **title**: 新标题
    """
    dialogue = chat_service.update_dialogue_title(db, dialogue_id, user_id, title)
    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": dialogue.id,
            "title": dialogue.title
        }
    }


@router.delete("/{dialogue_id}", summary="删除对话")
async def delete_dialogue(
    dialogue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    删除指定对话（软删除）

    实际上不会真正删除数据，只是标记为已删除
    """
    success = chat_service.delete_dialogue(db, dialogue_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )
    return {
        "code": 200,
        "message": "删除成功"
    }

@router.delete("/{dialogue_id}/tag/{tag_id}", summary="移除对话标签")
async def remove_tag_from_dialogue(
    dialogue_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    为指定对话移除标签

    - **dialogue_id**: 对话ID
    - **tag_id**: 标签ID
    """
    success = chat_service.remove_tag_from_dialogue(db, dialogue_id, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="对话或标签不存在，或无权访问"
        )
    return {
        "code": 200,
        "message": "移除成功"
    }

@router.post("/{dialogue_id}/message", summary="发送消息")
async def send_message(
    dialogue_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    发送消息并获取 AI 回复

    - **dialogue_id**: 对话ID
    - **message**: 用户消息内容

    返回 AI 的回复和消息ID
    """
    try:
        result = chat_service.send_message(db, dialogue_id, user_id, message_data)
        return {
            "code": 200,
            "message": "发送成功",
            "data": {
                "id": result["ai_message"]["id"],
                "content": result["ai_message"]["content"],
                "created_at": result["ai_message"]["created_at"],
                "dialogue_title": result.get("dialogue_title")
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"消息发送失败: {str(e)}"
        )


@router.post("/{dialogue_id}/message/stream", summary="发送消息（流式输出）")
async def send_message_stream(
    dialogue_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    发送消息并获取 AI 回复（流式输出）

    事件序列（SSE，每条均为 data: {...}\\n\\n）：
      1. {"type": "risk", ...}              风险提示，先于正文下发
      2. {"type": "sources", ...}           引用来源，供前端展示"参考 N 条"
      3. {"content": "...", "done": false}  正文增量（可能多条）
      4. {"content": "", "done": true, ...} 结束，携带 message_id 与风险字段
      5. {"type": "title_update", ...}      首轮对话的主题

    为什么 risk 要单独成事件：旧实现把它塞在 done 里，
    前端收到 done 往往只处理"结束"，风险提示就被丢掉了。
    """

    # 用请求级会话做一次校验，随后不再在流式过程中持有它
    dialogue = db.query(ChatDialogue).filter(
        and_(
            ChatDialogue.id == dialogue_id,
            ChatDialogue.user_id == user_id,
            ChatDialogue.is_deleted == False
        )
    ).first()

    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权访问"
        )

    dialogue_title_current = (dialogue.title or "").strip()

    async def generate():
        stream_db = SessionLocal()
        try:
            from app.models.user import User as UserModel

            user = stream_db.query(UserModel).filter(UserModel.id == user_id).first()
            should_save = bool(user.save_chat_history) if user else True

            # 先取历史，此时还没写入本条，避免当前消息被重复拼进上下文
            history_messages = stream_db.query(ChatMessage).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).limit(10).all()

            # 写入用户消息，拿到 id 供风险事件关联
            user_message_id = None
            if should_save:
                user_message = ChatMessage(
                    dialogue_id=dialogue_id,
                    role="user",
                    content=message_data.content
                )
                stream_db.add(user_message)
                stream_db.flush()
                user_message_id = user_message.id
                stream_db.commit()

            # ── 风险判定：先落库、再下发 ────────────────────────────
            verdict = detect_risk(message_data.content)
            if verdict.is_risk:
                try:
                    risk_service.record_risk(
                        stream_db, user_id, dialogue_id, user_message_id, verdict
                    )
                    stream_db.commit()
                except Exception as risk_error:
                    stream_db.rollback()
                    print(f"[风险事件落库失败] {risk_error}")

                yield f"data: {json.dumps({'type': 'risk', 'risk': verdict.to_payload()}, ensure_ascii=False)}\n\n"

            # ── RAG 检索，并保留结构化来源 ──────────────────────────
            sources = rag_service.search_with_sources(message_data.content)
            kb_context = ""
            if sources:
                parts = [
                    f"相似问题：{s['input']}\n参考回答：{s['output']}" for s in sources
                ]
                kb_context = (
                    "以下是从心理咨询知识库中检索到的相似案例，供你参考。"
                    "请你**千万不要照搬参考回答中的生硬语气**，而是用温暖、共情、自然的口吻，"
                    "把这些知识转化为对用户的贴心回应：\n\n"
                    + "\n\n---\n\n".join(parts)
                )

            source_payload = [
                {
                    "vector_id": s.get("vector_id"),
                    "title": s.get("title"),
                    "snippet": s.get("snippet"),
                    "score": s.get("score"),
                }
                for s in sources
            ]
            yield f"data: {json.dumps({'type': 'sources', 'sources': source_payload}, ensure_ascii=False)}\n\n"

            # ── 组装 prompt ──────────────────────────────────────
            base_system_prompt = ai_service.generate_system_prompt(kb_context)
            if not sources:
                base_system_prompt += (
                    "\n\n【重要】知识库里没有检索到直接相关的条目。"
                    "请明确说明这一点，把内容定位为一般性建议，不要编造依据。"
                )
            if verdict.is_risk:
                base_system_prompt += build_crisis_system_instruction(True, verdict.level)

            messages_list = [{"role": "system", "content": base_system_prompt}]
            for msg in reversed(history_messages):
                messages_list.append({"role": msg.role, "content": msg.content})
            messages_list.append({"role": "user", "content": message_data.content})

            # ── 流式生成 ────────────────────────────────────────
            full_response = ""
            try:
                for content_chunk in ai_service.chat_stream(messages=messages_list):
                    full_response += content_chunk
                    yield f"data: {json.dumps({'content': content_chunk, 'done': False}, ensure_ascii=False)}\n\n"
            except Exception as ai_error:
                # 原始报错只进日志，不写进对话内容
                from app.services.ai_error import friendly_message
                print(f"AI调用失败: {ai_error}")
                full_response = friendly_message(ai_error)
                yield f"data: {json.dumps({'content': full_response, 'done': False}, ensure_ascii=False)}\n\n"

            # ── 保存回复与引用溯源 ────────────────────────────────
            ai_message_id = None
            needs_title = False
            if should_save:
                ai_message = ChatMessage(
                    dialogue_id=dialogue_id,
                    role="assistant",
                    content=full_response
                )
                stream_db.add(ai_message)
                stream_db.flush()
                ai_message_id = ai_message.id

                if source_payload:
                    try:
                        risk_service.save_sources(stream_db, ai_message_id, source_payload)
                    except Exception as source_error:
                        print(f"[引用溯源落库失败] {source_error}")

                message_count = stream_db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.dialogue_id == dialogue_id,
                        ChatMessage.is_deleted == False
                    )
                ).count()
                needs_title = (
                    message_count == 2
                    and dialogue_title_current in {"", "新对话", "未命名对话", "新聊天"}
                )

            stream_db.commit()

            yield f"data: {json.dumps({'content': '', 'done': True, 'message_id': ai_message_id, 'crisis_detected': verdict.is_risk, 'crisis_level': verdict.level, 'crisis_keywords': verdict.keywords, 'source_count': len(source_payload)}, ensure_ascii=False)}\n\n"

            # 后台异步生成标题，结束后推送 title_update
            if needs_title:
                _user_content = message_data.content
                _ai_content = full_response
                _dial_id = dialogue_id

                def _bg_gen_title():
                    from app.core.database import SessionLocal as _SessionLocal
                    _db = _SessionLocal()
                    try:
                        title = chat_service._generate_dialogue_topic(_user_content, _ai_content)
                        d = _db.query(ChatDialogue).filter(ChatDialogue.id == _dial_id).first()
                        if d:
                            d.title = title
                            _db.commit()
                        return title
                    except Exception:
                        _db.rollback()
                        return chat_service._fallback_topic(_user_content)
                    finally:
                        _db.close()

                try:
                    final_title = await asyncio.get_running_loop().run_in_executor(None, _bg_gen_title)
                    yield f"data: {json.dumps({'type': 'title_update', 'dialogue_title': final_title}, ensure_ascii=False)}\n\n"
                except Exception:
                    pass

        except Exception as e:
            stream_db.rollback()
            print(f"流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
        finally:
            stream_db.close()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/{dialogue_id}/tag", summary="为对话添加标签")
async def add_tag_to_dialogue(
    dialogue_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    为指定对话添加标签

    - **dialogue_id**: 对话ID
    - **tag_id**: 标签ID
    """
    success = chat_service.add_tag_to_dialogue(db, dialogue_id, tag_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="对话或标签不存在，或无权访问"
        )
    return {
        "code": 200,
        "message": "添加成功"
    }
