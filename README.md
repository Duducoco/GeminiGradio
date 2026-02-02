# 🎨 Gemini 图片生成器

使用 Google Gemini AI 生成精美图片的 Web 应用。

## 功能特点

- 🖼️ 支持文本到图片生成
- 📷 支持参考图片编辑和融合
- 🔢 批量生成（1、2、4、8 张）
- 🎯 为每张图片设置独立提示词
- 📐 多种宽高比选择
- 🔌 支持多个 API 供应商

## 项目结构

```
gemini/
├── config.py          # 配置模块
├── generator.py       # 图片生成核心模块
├── utils.py           # 工具函数
├── main.py            # 主入口
├── ui/                # UI 模块
│   ├── __init__.py
│   ├── app.py         # Gradio 应用
│   ├── components.py  # UI 组件
│   └── handlers.py    # 事件处理
├── .env.example       # 环境变量示例
├── pyproject.toml     # 项目配置
└── run.bat            # Windows 启动脚本
```

## 安装

1. 确保已安装 Python 3.11+
2. 安装 [uv](https://github.com/astral-sh/uv) 包管理器
3. 克隆项目并安装依赖：

```bash
git clone https://github.com/Duducoco/GeminiGradio.git
cd GeminiGradio
uv sync
```

## 配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中配置供应商：

```env
# 配置格式：
# <供应商名称>_API_KEY=your_api_key
# <供应商名称>_BASE_URL=https://api.example.com  (可选)

# Aihubmix 供应商
AIHUBMIX_API_KEY=your_api_key_here
AIHUBMIX_BASE_URL=https://aihubmix.com/gemini

# DMX 供应商
DMX_API_KEY=your_api_key_here
DMX_BASE_URL=https://www.dmxapi.cn

# 添加更多供应商只需按照上述格式添加即可
# MYAPI_API_KEY=your_api_key_here
# MYAPI_BASE_URL=https://my-api.example.com
```

系统会自动扫描所有以 `_API_KEY` 结尾的环境变量，无需修改代码即可增删供应商。

## 运行

### Windows

双击 `run.bat` 或在命令行运行：

```bash
uv run python main.py
```

### Linux/macOS

```bash
uv run python main.py
```

启动后访问 http://localhost:7860

## 使用说明

1. 在提示词框中输入图片描述
2. 选择生成数量（1、2、4 或 8 张）
3. 可选：勾选"为每张图片使用独立提示词"
4. 可选：调整宽高比和分辨率
5. 可选：上传参考图片
6. 点击"生成图片"按钮
