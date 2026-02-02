"""UI 事件处理函数模块"""

from typing import List, Tuple
import gradio as gr

from generator import get_generator, switch_provider, get_current_provider
from utils import process_input_images, extract_image_paths


def generate_images(
    prompt: str,
    num_images: int,
    aspect_ratio: str,
    resolution: str,
    use_individual_prompts: bool,
    prompt_1: str,
    prompt_2: str,
    prompt_3: str,
    prompt_4: str,
    prompt_5: str,
    prompt_6: str,
    prompt_7: str,
    prompt_8: str,
    input_images=None,
    progress=gr.Progress()
) -> Tuple[List[str], str, List[str]]:
    """Gradio 接口函数：生成图片"""
    num_images = int(num_images)

    # 构建prompts列表
    if use_individual_prompts:
        individual_prompts = [
            prompt_1, prompt_2, prompt_3, prompt_4,
            prompt_5, prompt_6, prompt_7, prompt_8
        ]
        prompts = []
        for i in range(num_images):
            p = individual_prompts[i].strip() if i < len(individual_prompts) else ""
            if p:
                prompts.append(p)
            else:
                if prompts:
                    prompts.append(prompts[-1])
                elif prompt.strip():
                    prompts.append(prompt.strip())
                else:
                    return [], "请至少输入一个提示词", []

        if not prompts:
            return [], "请至少输入一个提示词", []
    else:
        if not prompt.strip():
            return [], "请输入提示词", []
        prompts = [prompt.strip()]

    try:
        gen = get_generator()
        processed_images = process_input_images(input_images)

        images, paths, messages = gen.generate_multiple_images(
            prompts=prompts,
            num_images=num_images,
            input_images=processed_images,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            progress_callback=lambda p, msg: progress(p, desc=msg)
        )

        # 构建状态消息
        status = f"成功生成 {len(images)}/{num_images} 张图片\n"
        if use_individual_prompts:
            status += "\n使用的提示词:\n"
            for i, p in enumerate(prompts[:num_images]):
                status += f"  图片 {i+1}: {p[:50]}{'...' if len(p) > 50 else ''}\n"
        if paths:
            status += "\n保存路径:\n" + "\n".join(paths)
        if messages:
            status += "\n\n" + "\n".join(messages)

        return paths if paths else [], status, paths if paths else []

    except Exception as e:
        return [], f"错误: {str(e)}", []


def update_prompt_visibility(num: int, use_individual: bool) -> List[gr.update]:
    """更新独立提示词输入框的可见性"""
    num = int(num)
    updates = []

    # 更新独立提示词组的可见性
    group_visible = use_individual and num > 1
    updates.append(gr.update(visible=group_visible))

    # 更新每个提示词输入框的可见性
    for i in range(8):
        visible = use_individual and i < num
        updates.append(gr.update(visible=visible))

    return updates


def handle_upload(files, existing_images) -> Tuple[List[str], None]:
    """处理上传的图片（追加到现有图片）"""
    if files is None:
        return existing_images if existing_images else [], None

    current_paths = extract_image_paths(existing_images)

    for file in files:
        if hasattr(file, 'name'):
            current_paths.append(file.name)
        elif isinstance(file, str):
            current_paths.append(file)

    return current_paths, None


def clear_images() -> Tuple[List, None]:
    """清除所有图片"""
    return [], None


def on_select_image(evt: gr.SelectData) -> int:
    """选择图片时记录索引"""
    return evt.index


def delete_selected_image(images, index) -> Tuple[List[str], None]:
    """删除选中的图片"""
    if images is None or len(images) == 0:
        return [], None
    if index is None:
        return images, None

    current_paths = extract_image_paths(images)

    if 0 <= index < len(current_paths):
        current_paths.pop(index)

    return current_paths, None


def add_output_to_input(
    output_files,
    output_index,
    existing_input_images
) -> Tuple[List[str], None]:
    """将选中的生成图片添加到参考图片"""
    if output_files is None or len(output_files) == 0:
        return existing_input_images if existing_input_images else [], None
    if output_index is None:
        return existing_input_images if existing_input_images else [], None

    current_paths = extract_image_paths(existing_input_images)

    if 0 <= output_index < len(output_files):
        selected_file = output_files[output_index]
        if isinstance(selected_file, str):
            current_paths.append(selected_file)
        elif hasattr(selected_file, 'name'):
            current_paths.append(selected_file.name)

    return current_paths, None


def on_provider_change(provider_name: str) -> str:
    """处理供应商切换事件"""
    # 检查是否是未配置状态
    if provider_name == "未配置供应商":
        return "❌ 请在 .env 文件中配置供应商后重启应用"

    # 尝试切换供应商
    success = switch_provider(provider_name)
    if success:
        current = get_current_provider()
        return f"✅ 已切换到供应商: {current}"
    else:
        return f"❌ 切换供应商失败: {provider_name}"
