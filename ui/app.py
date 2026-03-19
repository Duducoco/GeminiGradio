"""Gradio 应用主模块"""

import gradio as gr

from .components import (
    create_provider_selector,
    create_prompt_inputs,
    create_individual_prompts,
    create_input_gallery,
    create_output_gallery,
    create_examples,
    create_instructions,
)
from .handlers import (
    generate_images,
    update_prompt_visibility,
    handle_upload,
    clear_images,
    on_select_image,
    delete_selected_image,
    add_output_to_input,
    on_provider_change,
)


def create_ui() -> gr.Blocks:
    """创建 Gradio 界面"""
    with gr.Blocks(title="Gemini 图片生成器") as demo:
        gr.Markdown(
            """
            # 🎨 Gemini 图片生成器
            使用 Google Gemini AI 生成精美图片
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                # 供应商选择
                provider_selector = create_provider_selector()

                # 提示词输入区域
                (
                    prompt_input, num_images, aspect_ratio,
                    resolution, image_max_size, use_individual_prompts
                ) = create_prompt_inputs()

                # 独立提示词区域
                individual_prompts_group, prompts = create_individual_prompts()
                (
                    prompt_1, prompt_2, prompt_3, prompt_4,
                    prompt_5, prompt_6, prompt_7, prompt_8
                ) = prompts

                # 输入图片区域
                (
                    input_images, selected_index,
                    upload_btn, delete_selected_btn, clear_btn, generate_btn
                ) = create_input_gallery()

            with gr.Column(scale=2):
                # 输出区域
                (
                    output_gallery, output_selected_index,
                    add_to_input_btn, download_files, status_output
                ) = create_output_gallery()

        # 所有独立提示词输入框列表
        all_prompt_inputs = [
            prompt_1, prompt_2, prompt_3, prompt_4,
            prompt_5, prompt_6, prompt_7, prompt_8
        ]

        # === 事件绑定 ===

        # 供应商切换事件
        provider_selector.change(
            fn=on_provider_change,
            inputs=[provider_selector],
            outputs=[status_output]
        )

        # 监听生成数量和独立提示词开关的变化
        num_images.change(
            fn=update_prompt_visibility,
            inputs=[num_images, use_individual_prompts],
            outputs=[individual_prompts_group] + all_prompt_inputs
        )

        use_individual_prompts.change(
            fn=update_prompt_visibility,
            inputs=[num_images, use_individual_prompts],
            outputs=[individual_prompts_group] + all_prompt_inputs
        )

        # 输入图片选择事件
        input_images.select(
            fn=on_select_image,
            inputs=[],
            outputs=[selected_index]
        )

        # 上传图片
        upload_btn.upload(
            fn=handle_upload,
            inputs=[upload_btn, input_images],
            outputs=[input_images, selected_index]
        )

        # 删除选中图片
        delete_selected_btn.click(
            fn=delete_selected_image,
            inputs=[input_images, selected_index],
            outputs=[input_images, selected_index]
        )

        # 清除所有图片
        clear_btn.click(
            fn=clear_images,
            inputs=[],
            outputs=[input_images, selected_index]
        )

        # 生成图片
        generate_btn.click(
            fn=generate_images,
            inputs=[
                prompt_input, num_images, aspect_ratio, resolution,
                image_max_size, use_individual_prompts,
                prompt_1, prompt_2, prompt_3, prompt_4,
                prompt_5, prompt_6, prompt_7, prompt_8,
                input_images
            ],
            outputs=[output_gallery, status_output, download_files]
        )

        # 输出图片选择事件
        output_gallery.select(
            fn=on_select_image,
            inputs=[],
            outputs=[output_selected_index]
        )

        # 添加生成图片到参考图片
        add_to_input_btn.click(
            fn=add_output_to_input,
            inputs=[download_files, output_selected_index, input_images],
            outputs=[input_images, selected_index]
        )

        # 示例和说明
        create_examples(prompt_input, num_images, aspect_ratio, resolution)
        create_instructions()

    return demo


def main():
    """应用入口"""
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .gallery-item { border-radius: 8px; }
        """
    )


if __name__ == "__main__":
    main()
