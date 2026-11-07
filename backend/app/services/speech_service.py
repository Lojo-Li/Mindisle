"""
语音转文字服务 - 使用豆包大模型录音文件识别
"""
import os
import uuid
import base64
import time
import asyncio
from typing import Optional
from fastapi import UploadFile, HTTPException
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DoubaoSpeechService:
    """豆包语音识别服务"""

    def __init__(self):
        """初始化服务"""
        # 优先使用旧版控制台配置
        self.app_id = getattr(settings, 'DOUBAO_APP_ID', '')
        self.access_token = getattr(settings, 'DOUBAO_ACCESS_TOKEN', '')
        # 新版控制台的 API Key 作为备选
        self.api_key = getattr(settings, 'DOUBAO_API_KEY', '')

        self.submit_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
        self.query_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"
        self.resource_id = "volc.seedasr.auc"  # 豆包录音文件识别模型2.0

        # 判断使用哪种认证方式
        self.use_legacy_auth = bool(self.app_id and self.access_token)

        if not self.use_legacy_auth and not self.api_key:
            logger.warning("豆包 API 未配置，语音识别功能将不可用")
        else:
            auth_type = "旧版控制台" if self.use_legacy_auth else "新版控制台"
            logger.info(f"语音识别服务已初始化（{auth_type}）")

    async def transcribe_audio(
        self,
        audio_file: UploadFile,
        language: str = "zh-CN"
    ) -> str:
        """
        转录音频文件为文字

        Args:
            audio_file: 上传的音频文件
            language: 语言代码，默认 zh-CN（中文）

        Returns:
            转录后的文本

        Raises:
            HTTPException: 当转录失败时
        """
        # 检查认证配置
        if not self.use_legacy_auth and not self.api_key:
            raise HTTPException(
                status_code=503,
                detail="语音识别服务未配置，请设置 DOUBAO_APP_ID/DOUBAO_ACCESS_TOKEN 或 DOUBAO_API_KEY"
            )

        # 验证文件格式
        allowed_formats = ["mp3", "wav", "m4a", "ogg", "webm"]
        file_ext = audio_file.filename.split('.')[-1].lower() if audio_file.filename else ""

        if file_ext not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的音频格式: {file_ext}，支持的格式: {', '.join(allowed_formats)}"
            )

        try:
            # 1. 读取音频内容
            audio_content = await audio_file.read()

            # 2. 提交识别任务（base64直传，无需公网URL）
            task_id = await self._submit_task(audio_content, file_ext, language)

            # 3. 轮询查询结果（最长等待30秒）
            result = await self._poll_result(task_id, max_wait=30)

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"音频转录失败: {str(e)}"
            )

    async def _submit_task(
        self,
        audio_content: bytes,
        format: str,
        language: str = "zh-CN"
    ) -> str:
        """
        提交识别任务（base64直传音频，无需公网URL）

        Returns:
            task_id: 任务ID
        """
        # 检查文件大小（限制25MB）
        if len(audio_content) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="音频文件过大，请上传小于 25MB 的文件"
            )

        task_id = str(uuid.uuid4())

        # 根据认证方式构建 headers
        if self.use_legacy_auth:
            # 旧版控制台认证
            headers = {
                "X-Api-App-Key": self.app_id,
                "X-Api-Access-Key": self.access_token,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": task_id,
                "X-Api-Sequence": "-1"
            }
        else:
            # 新版控制台认证
            headers = {
                "X-Api-Key": self.api_key,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": task_id,
                "X-Api-Sequence": "-1"
            }

        # 将音频编码为base64，直接传入请求体，无需公网URL
        audio_b64 = base64.b64encode(audio_content).decode("utf-8")

        payload = {
            "audio": {
                "format": format,
                "data": audio_b64
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,  # 启用文本规范化
                "enable_punc": True  # 启用标点
            }
        }

        # 如果指定了语言，添加语言参数
        if language:
            payload["audio"]["language"] = language

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.submit_url,
                    headers=headers,
                    json=payload
                )

                # 检查状态码
                status_code = response.headers.get("X-Api-Status-Code")
                message = response.headers.get("X-Api-Message", "")

                if status_code != "20000000":
                    logger.error(f"提交任务失败: {status_code} - {message}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"提交识别任务失败: {message}"
                    )

                logger.info(f"识别任务已提交: {task_id}")
                return task_id

        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"提交任务失败: 网络错误"
            )

    async def _poll_result(self, task_id: str, max_wait: int = 30) -> str:
        """
        轮询查询识别结果

        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）

        Returns:
            识别结果文本
        """
        # 根据认证方式构建 headers
        if self.use_legacy_auth:
            # 旧版控制台认证
            headers = {
                "X-Api-App-Key": self.app_id,
                "X-Api-Access-Key": self.access_token,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": task_id
            }
        else:
            # 新版控制台认证
            headers = {
                "X-Api-Key": self.api_key,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": task_id
            }

        start_time = time.time()
        poll_interval = 1  # 初始轮询间隔1秒

        while (time.time() - start_time) < max_wait:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.query_url,
                        headers=headers,
                        json={}
                    )

                    status_code = response.headers.get("X-Api-Status-Code")

                    # 任务完成
                    if status_code == "20000000":
                        data = response.json()
                        result_text = data.get("result", {}).get("text", "")

                        if not result_text:
                            raise HTTPException(
                                status_code=500,
                                detail="识别结果为空"
                            )

                        logger.info(f"识别成功: {result_text[:50]}...")
                        return result_text

                    # 任务处理中
                    elif status_code in ["20000001", "20000002"]:
                        logger.info(f"任务处理中... ({status_code})")
                        await asyncio.sleep(poll_interval)
                        poll_interval = min(poll_interval * 1.5, 5)  # 最多5秒间隔
                        continue

                    # 错误
                    else:
                        message = response.headers.get("X-Api-Message", "未知错误")
                        raise HTTPException(
                            status_code=500,
                            detail=f"识别失败: {message} (错误码: {status_code})"
                        )

            except httpx.RequestError as e:
                logger.error(f"查询结果失败: {e}")
                await asyncio.sleep(poll_interval)
                continue

        # 超时
        raise HTTPException(
            status_code=504,
            detail=f"识别超时（超过{max_wait}秒），请稍后重试"
        )


# 创建全局实例
speech_service = DoubaoSpeechService()
