"""Gemini 图片生成器核心模块"""

import os
import io
import asyncio
from datetime import datetime
from typing import List, Optional, Tuple, Dict

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

from config import Config, ProviderConfig

# 加载环境变量
load_dotenv()


class GeminiImageGenerator:
    """Gemini 图片生成器"""

    def __init__(self, provider_name: Optional[str] = None):
        self.client: Optional[genai.Client] = None
        self.image_counter = 0
        self.current_provider: Optional[str] = None
        self._init_client(provider_name)
        self._ensure_results_dir()

    def _init_client(self, provider_name: Optional[str] = None):
        """初始化 Gemini API 客户端"""
        if provider_name is None:
            provider_name = Config.get_default_provider()

        provider_config = Config.get_provider_config(provider_name)
        if not provider_config:
            available = Config.get_available_providers()
            if available:
                provider_config = Config.get_provider_config(available[0])
            if not provider_config:
                raise ValueError(
                    f"未找到可用的供应商配置。请在 .env 文件中设置 API Key。\n"
                    f"支持的供应商: {', '.join(Config.get_provider_list())}"
                )

        self.current_provider = provider_config.name
        self.client = genai.Client(
            api_key=provider_config.api_key,
            http_options={'base_url': provider_config.base_url}
        )

    def switch_provider(self, provider_name: str) -> bool:
        """切换供应商"""
        if provider_name == self.current_provider:
            return True

        provider_config = Config.get_provider_config(provider_name)
        if not provider_config:
            return False

        self.current_provider = provider_config.name
        self.client = genai.Client(
            api_key=provider_config.api_key,
            http_options={'base_url': provider_config.base_url}
        )
        return True

    def get_current_provider(self) -> str:
        """获取当前供应商名称"""
        return self.current_provider or ""

    def _ensure_results_dir(self):
        """确保结果目录存在"""
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)

    def compress_image(
        self,
        image: Image.Image,
        target_size_kb: Optional[int] = None
    ) -> Image.Image:
        """压缩图片到指定大小（KB）"""
        if target_size_kb is None:
            target_size_kb = Config.IMAGE_MAX_SIZE_KB

        target_size_bytes = target_size_kb * 1024

        # 如果图片有 alpha 通道，转换为 RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(
                image,
                mask=image.split()[-1] if image.mode == 'RGBA' else None
            )
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # 先检查原始大小
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        original_size = buffer.tell()

        if original_size <= target_size_bytes:
            buffer.seek(0)
            return Image.open(buffer).copy()

        # 二分法查找合适的质量值
        min_quality = 10
        max_quality = 95
        best_buffer = None

        while min_quality <= max_quality:
            mid_quality = (min_quality + max_quality) // 2
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=mid_quality)
            size = buffer.tell()

            if size <= target_size_bytes:
                best_buffer = buffer
                min_quality = mid_quality + 1
            else:
                max_quality = mid_quality - 1

        if best_buffer is None:
            scale = (target_size_bytes / original_size) ** 0.5
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            size = buffer.tell()

            if size > target_size_bytes:
                for quality in range(80, 9, -5):
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=quality)
                    if buffer.tell() <= target_size_bytes:
                        break

            best_buffer = buffer

        best_buffer.seek(0)
        return Image.open(best_buffer).copy()

    def save_generated_image(
        self,
        image: Image.Image,
        prefix: str = "generated"
    ) -> str:
        """保存生成的图片"""
        self.image_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}_{self.image_counter}.png"
        filepath = os.path.join(Config.RESULTS_DIR, filename)

        try:
            # 先保存到内存缓冲区
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()

            # 写入文件并确保完全同步到磁盘
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
                f.flush()
                os.fsync(f.fileno())

            return filepath
        except Exception as e:
            print(f"保存图片失败: {e}")
            return ""

    async def generate_single_image_async(
        self,
        prompt: str,
        index: int = 0,
        input_images: Optional[List[Image.Image]] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Tuple[int, Optional[Image.Image], str]:
        """异步生成单张图片"""
        if aspect_ratio is None:
            aspect_ratio = Config.DEFAULT_ASPECT_RATIO
        if resolution is None:
            resolution = Config.DEFAULT_RESOLUTION

        try:
            contents = []

            # 添加输入图片
            if input_images:
                for img in input_images:
                    compressed = self.compress_image(img)
                    contents.append(compressed)

            # 添加文本提示
            contents.append(prompt)

            # 使用线程池执行同步 API 调用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=Config.MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=resolution,
                        ),
                    ),
                )
            )

            # 处理响应
            text_response = ""
            generated_image = None

            for part in response.parts:
                if part.text is not None:
                    text_response = part.text
                elif part.inline_data is not None:
                    image_data = part.inline_data.data
                    generated_image = Image.open(io.BytesIO(image_data))

            return index, generated_image, text_response

        except Exception as e:
            return index, None, f"生成失败: {str(e)}"

    async def generate_multiple_images_async(
        self,
        prompts: List[str],
        num_images: int,
        input_images: Optional[List[Image.Image]] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        progress_callback=None
    ) -> Tuple[List[Image.Image], List[str], List[str]]:
        """并行生成多张图片，支持每张图片使用不同的prompt"""
        if progress_callback:
            progress_callback(0, f"正在使用 {self.current_provider} 并行生成 {num_images} 张图片...")

        # 确保prompts列表长度与num_images匹配
        if len(prompts) == 1:
            prompts = prompts * num_images
        elif len(prompts) < num_images:
            prompts = prompts + [prompts[-1]] * (num_images - len(prompts))

        # 创建所有生成任务
        tasks = [
            self.generate_single_image_async(
                prompt=prompts[i],
                index=i,
                input_images=input_images,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            for i in range(num_images)
        ]

        # 并行执行所有任务
        results = await asyncio.gather(*tasks)

        # 按索引排序结果
        results = sorted(results, key=lambda x: x[0])

        # 处理结果
        generated_images = []
        saved_paths = []
        messages = []

        for index, image, text in results:
            if image:
                generated_images.append(image)
                filepath = self.save_generated_image(image)
                if filepath:
                    saved_paths.append(filepath)
            else:
                messages.append(f"图片 {index + 1} 生成失败: {text}")

        if progress_callback:
            progress_callback(1.0, "生成完成!")

        return generated_images, saved_paths, messages

    def generate_multiple_images(
        self,
        prompts: List[str],
        num_images: int,
        input_images: Optional[List[Image.Image]] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        progress_callback=None
    ) -> Tuple[List[Image.Image], List[str], List[str]]:
        """生成多张图片（同步包装器，内部使用异步并行）"""
        import concurrent.futures

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.generate_multiple_images_async(
                            prompts=prompts,
                            num_images=num_images,
                            input_images=input_images,
                            aspect_ratio=aspect_ratio,
                            resolution=resolution,
                            progress_callback=progress_callback
                        )
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.generate_multiple_images_async(
                        prompts=prompts,
                        num_images=num_images,
                        input_images=input_images,
                        aspect_ratio=aspect_ratio,
                        resolution=resolution,
                        progress_callback=progress_callback
                    )
                )
        except RuntimeError:
            return asyncio.run(
                self.generate_multiple_images_async(
                    prompts=prompts,
                    num_images=num_images,
                    input_images=input_images,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    progress_callback=progress_callback
                )
            )


# 全局生成器实例
_generator: Optional[GeminiImageGenerator] = None


def get_generator(provider_name: Optional[str] = None) -> GeminiImageGenerator:
    """获取全局生成器实例（单例模式）"""
    global _generator
    if _generator is None:
        _generator = GeminiImageGenerator(provider_name)
    elif provider_name and provider_name != _generator.get_current_provider():
        _generator.switch_provider(provider_name)
    return _generator


def switch_provider(provider_name: str) -> bool:
    """切换供应商"""
    global _generator
    if _generator is None:
        _generator = GeminiImageGenerator(provider_name)
        return True
    return _generator.switch_provider(provider_name)


def get_current_provider() -> str:
    """获取当前供应商名称"""
    global _generator
    if _generator is None:
        return Config.get_default_provider()
    return _generator.get_current_provider()
