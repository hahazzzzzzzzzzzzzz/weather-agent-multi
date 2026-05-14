"""LLM 客户端配置，使用 OpenAI 兼容接口"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_llm() -> OpenAI:
    """获取 LLM 客户端（单例模式）"""
    global _client
    if _client is None:
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("BASE_URL", "https://api.openai.com/v1")
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def get_model_name() -> str:
    """获取模型名称"""
    return os.getenv("MODEL_NAME", "gpt-4o-mini")
