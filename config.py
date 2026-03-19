"""应用配置模块

供应商配置说明：
在 .env 文件中，使用以下格式配置供应商：
  <供应商名称>_API_KEY=your_api_key
  <供应商名称>_BASE_URL=https://api.example.com  (可选)

例如：
  AIHUBMIX_API_KEY=sk-xxx
  AIHUBMIX_BASE_URL=https://aihubmix.com/gemini

  OPENAI_API_KEY=sk-xxx
  OPENAI_BASE_URL=https://api.openai.com/v1

系统会自动扫描所有以 _API_KEY 结尾的环境变量，提取供应商名称。
"""

import os
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ProviderConfig:
    """供应商配置"""

    def __init__(self, name: str, api_key: str, base_url: str):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url


class Config:
    """应用配置"""

    MODEL = "gemini-3.1-flash-image-preview"
    DEFAULT_ASPECT_RATIO = "2:3"
    DEFAULT_RESOLUTION = "4K"
    RESULTS_DIR = "results"
    IMAGE_MAX_SIZE_KB = 1024*10

    # 可选的宽高比
    ASPECT_RATIOS = [
        "1:1", "2:3", "3:2", "3:4", "4:3",
        "4:5", "5:4", "9:16", "16:9", "21:9"
    ]
    # 可选的分辨率
    RESOLUTIONS = ["1K", "2K", "4K"]

    # 默认 Base URL（当供应商没有配置 BASE_URL 时使用）
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    # 缓存的供应商列表
    _providers_cache: Optional[Dict[str, Dict[str, str]]] = None

    @classmethod
    def _scan_providers(cls) -> Dict[str, Dict[str, str]]:
        """扫描环境变量，动态发现所有供应商配置"""
        if cls._providers_cache is not None:
            return cls._providers_cache

        providers = {}
        api_key_pattern = re.compile(r'^(.+)_API_KEY$')

        for key, value in os.environ.items():
            match = api_key_pattern.match(key)
            if match and value:  # 确保 API_KEY 有值
                provider_name = match.group(1)
                # 获取对应的 BASE_URL（如果有）
                base_url_key = f"{provider_name}_BASE_URL"
                base_url = os.getenv(base_url_key, cls.DEFAULT_BASE_URL)

                providers[provider_name] = {
                    "api_key": value,
                    "base_url": base_url
                }

        cls._providers_cache = providers
        return providers

    @classmethod
    def reload_providers(cls):
        """重新加载供应商配置（清除缓存）"""
        cls._providers_cache = None
        load_dotenv(override=True)
        return cls._scan_providers()

    @classmethod
    def get_provider_list(cls) -> List[str]:
        """获取所有已配置的供应商列表"""
        providers = cls._scan_providers()
        return list(providers.keys())

    @classmethod
    def get_provider_config(cls, provider_name: str) -> Optional[ProviderConfig]:
        """获取指定供应商的配置"""
        providers = cls._scan_providers()

        if provider_name not in providers:
            return None

        provider_info = providers[provider_name]
        return ProviderConfig(
            name=provider_name,
            api_key=provider_info["api_key"],
            base_url=provider_info["base_url"]
        )

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """获取已配置API Key的可用供应商列表"""
        # 由于我们只扫描有 API_KEY 的供应商，所以所有扫描到的都是可用的
        return cls.get_provider_list()

    @classmethod
    def get_default_provider(cls) -> str:
        """获取默认供应商（返回第一个可用的供应商）"""
        available = cls.get_available_providers()
        return available[0] if available else ""
