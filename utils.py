"""工具函数模块"""

from typing import List, Optional
from PIL import Image


def process_input_images(input_images) -> Optional[List[Image.Image]]:
    """处理输入图片，统一格式转换为 PIL Image 列表"""
    if not input_images or len(input_images) == 0:
        return None

    processed_images = []
    for item in input_images:
        if item is None:
            continue

        # 处理不同的输入格式
        img = None
        if isinstance(item, tuple):
            # Gallery 返回的是 (image, caption) 元组
            img = item[0]
        else:
            img = item

        if img is None:
            continue

        # 如果是文件路径字符串
        if isinstance(img, str):
            img = Image.open(img)
        elif hasattr(img, 'name'):
            # 如果是文件对象
            img = Image.open(img.name)
        elif not isinstance(img, Image.Image):
            # 尝试从 numpy 数组转换
            try:
                img = Image.fromarray(img)
            except Exception:
                continue

        if img is not None:
            processed_images.append(img)

    return processed_images if processed_images else None


def extract_image_paths(images) -> List[str]:
    """从 Gallery 数据中提取图片路径列表"""
    if not images:
        return []

    paths = []
    for item in images:
        if item is None:
            continue
        if isinstance(item, tuple):
            path = item[0]
        else:
            path = item
        if path:
            paths.append(path)
    return paths
