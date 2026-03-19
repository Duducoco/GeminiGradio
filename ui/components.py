"""UI 组件定义模块"""

import gradio as gr
from config import Config
from generator import get_current_provider


def create_provider_selector():
    """创建供应商选择组件"""
    available_providers = Config.get_available_providers()

    if not available_providers:
        # 没有配置任何供应商
        provider_dropdown = gr.Dropdown(
            choices=["未配置供应商"],
            value="未配置供应商",
            label="🔌 API 供应商",
            info="请在 .env 文件中配置供应商",
            interactive=False
        )
    else:
        # 获取当前供应商或默认供应商
        current = get_current_provider()
        if current not in available_providers:
            current = Config.get_default_provider()

        provider_dropdown = gr.Dropdown(
            choices=available_providers,
            value=current,
            label="🔌 API 供应商",
            info="选择要使用的 API 供应商（在 .env 中配置）",
            interactive=True
        )

    return provider_dropdown


def create_prompt_inputs():
    """创建提示词输入组件"""
    prompt_input = gr.Textbox(
        label="统一提示词",
        placeholder="描述你想要生成的图片...",
        lines=3,
        max_lines=10
    )

    with gr.Row():
        num_images = gr.Radio(
            choices=[1, 2, 4, 8],
            value=1,
            label="生成数量",
            info="选择要生成的图片数量"
        )

    with gr.Row():
        aspect_ratio = gr.Dropdown(
            choices=Config.ASPECT_RATIOS,
            value=Config.DEFAULT_ASPECT_RATIO,
            label="宽高比"
        )
        resolution = gr.Dropdown(
            choices=Config.RESOLUTIONS,
            value=Config.DEFAULT_RESOLUTION,
            label="分辨率"
        )

    with gr.Row():
        image_max_size = gr.Slider(
            minimum=100,
            maximum=20480,
            value=Config.IMAGE_MAX_SIZE_KB,
            step=100,
            label="参考图片最大尺寸 (KB)",
            info="上传的参考图片将被压缩到此大小以下"
        )

    use_individual_prompts = gr.Checkbox(
        label="🎯 为每张图片使用独立提示词",
        value=False,
        info="启用后可以为每张图片指定不同的提示词"
    )

    return prompt_input, num_images, aspect_ratio, resolution, image_max_size, use_individual_prompts


def create_individual_prompts():
    """创建独立提示词输入组件"""
    with gr.Group(visible=False) as individual_prompts_group:
        gr.Markdown("### 📝 独立提示词")
        gr.Markdown("*留空的提示词将使用上方的统一提示词或前一个有效提示词*")

        prompts = []
        for i in range(1, 9):
            prompt = gr.Textbox(
                label=f"图片 {i} 提示词",
                placeholder=f"第 {i} 张图片的提示词...",
                lines=2,
                visible=False
            )
            prompts.append(prompt)

    return individual_prompts_group, prompts


def create_input_gallery():
    """创建输入图片 Gallery 组件"""
    input_images = gr.Gallery(
        label="参考图片（可选，可上传多张）- 点击图片选中后可删除",
        show_label=True,
        columns=4,
        rows=2,
        height="auto",
        object_fit="contain",
        interactive=True,
        type="filepath"
    )

    selected_index = gr.State(value=None)

    with gr.Row():
        upload_btn = gr.UploadButton(
            "📁 上传参考图片",
            file_types=["image"],
            file_count="multiple"
        )
        delete_selected_btn = gr.Button(
            "❌ 删除选中",
            variant="secondary"
        )
        clear_btn = gr.Button(
            "🗑️ 清除全部",
            variant="secondary"
        )

    generate_btn = gr.Button(
        "🚀 生成图片",
        variant="primary",
        size="lg"
    )

    return (
        input_images, selected_index,
        upload_btn, delete_selected_btn, clear_btn, generate_btn
    )


def create_output_gallery():
    """创建输出图片 Gallery 组件"""
    output_gallery = gr.Gallery(
        label="生成结果 - 点击图片选中后可添加到参考图片",
        show_label=True,
        columns=2,
        rows=2,
        height="auto",
        object_fit="contain",
        preview=True
    )

    output_selected_index = gr.State(value=None)

    with gr.Row():
        add_to_input_btn = gr.Button(
            "➕ 添加选中到参考图片",
            variant="secondary"
        )

    download_files = gr.Files(
        label="📥 下载原图",
        file_count="multiple",
        interactive=False
    )

    status_output = gr.Textbox(
        label="状态",
        lines=5,
        interactive=False
    )

    return (
        output_gallery, output_selected_index,
        add_to_input_btn, download_files, status_output
    )


def create_examples(prompt_input, num_images, aspect_ratio, resolution):
    """创建示例组件"""
    gr.Examples(
        examples=[
            ["一只可爱的橘猫坐在窗台上，阳光洒在它身上，温暖的氛围", 1, "2:3", "4K"],
            ["未来城市的天际线，霓虹灯闪烁，赛博朋克风格", 2, "16:9", "4K"],
            ["水彩风格的山水画，云雾缭绕，意境悠远", 4, "3:2", "4K"],
            ["一杯热咖啡，蒸汽袅袅，旁边放着一本打开的书", 1, "1:1", "2K"],
        ],
        inputs=[prompt_input, num_images, aspect_ratio, resolution],
        label="示例提示词"
    )


def create_instructions():
    """创建使用说明"""
    gr.Markdown(
        """
        ---
        ### 使用说明
        1. 在提示词框中输入你想要生成的图片描述
        2. 选择要生成的图片数量（1、2、4 或 8 张）
        3. **新功能**：勾选"为每张图片使用独立提示词"可以为每张图片指定不同的描述
        4. 可选：调整宽高比和分辨率
        5. 可选：上传参考图片进行图片编辑
        6. 点击"生成图片"按钮开始生成

        ### 提示
        - 提示词越详细，生成的图片越符合预期
        - 可以指定风格、颜色、光线、构图等细节
        - 上传参考图片后，可以要求 AI 对图片进行修改或融合
        - 使用独立提示词时，留空的输入框会自动使用统一提示词或前一个有效提示词
        - **删除单张参考图片**：点击图片选中，然后点击"❌ 删除选中"按钮
        - **添加生成图片到参考**：点击生成的图片选中，然后点击"➕ 添加选中到参考图片"按钮
        """
    )
