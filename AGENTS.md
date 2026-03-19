# AGENTS.md

此文件包含为在此代码库中工作的智能代理开发人员提供的指南。

## 🚀 快速开始

### 运行应用
```bash
# 使用 uv 运行主应用
uv run python main.py

# Windows 快捷方式
双击 run.bat 文件

# 应用将在 http://localhost:7860 启动
```

### 依赖管理
```bash
# 安装依赖
uv sync

# 添加新依赖
uv add package_name
```

## 🧪 测试指南

### 当前测试状态
项目使用 pytest 进行测试，但目前测试覆盖率有限。

### 运行测试
```bash
# 运行所有测试
uv run pytest

# 运行单个测试文件
uv run pytest test/test_generator.py

# 运行特定测试函数
uv run pytest test/test_generator.py::test_generate_images

# 运行测试并显示覆盖率
uv run pytest --cov=. --cov-report=html
```

### 测试结构
```
test/
├── test_generator.py      # 图片生成器测试
├── test_config.py         # 配置管理测试
├── test_utils.py          # 工具函数测试
└── conftest.py            # pytest 配置和 fixtures
```

## 🔧 开发工具

### 代码格式化
```bash
# 使用 Black 格式化代码
uv run black .

# 检查格式
uv run black --check .
```

### 代码检查
```bash
# 使用 Ruff 进行 linting
uv run ruff check .

# 修复 Ruff 发现的问题
uv run ruff check --fix .
```

### 类型检查
```bash
# 使用 mypy 进行类型检查
uv run mypy .
```

## 📝 代码风格指南

### 导入约定
```python
# 导入顺序：标准库 → 第三方库 → 本地模块
import os
import re
from typing import Dict, List, Optional, Tuple

import gradio as gr
from dotenv import load_dotenv

from config import Config
from generator import GeminiImageGenerator
```

### 命名约定
```python
# 类名：PascalCase
class GeminiImageGenerator:
class ProviderConfig:

# 函数名和变量：snake_case
def generate_images():
provider_name = "AIHUBMIX"
image_counter = 0

# 常量：UPPER_SNAKE_CASE
MODEL = "gemini-3-pro-image-preview"
DEFAULT_ASPECT_RATIO = "2:3"
RESULTS_DIR = "results"

# 私有方法：下划线前缀
def _ensure_results_dir():
```

### 类型注解
项目强制使用类型注解：
```python
from typing import Dict, List, Optional, Tuple, Union

def generate_image(
    prompt: str,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    reference_image: Optional[str] = None
) -> Tuple[str, str]:
    """生成图片并返回路径和描述"""
    pass

class Config:
    providers: Dict[str, str] = {}
    current_provider: Optional[str] = None
```

### 错误处理
```python
# 标准异常处理模式
try:
    response = await loop.run_in_executor(None, func, *args)
    return response
except Exception as e:
    return None, f"操作失败: {str(e)}"

# 特定异常处理
try:
    config.load()
except FileNotFoundError as e:
    logger.error(f"配置文件未找到: {e}")
except ValueError as e:
    logger.error(f"配置格式错误: {e}")
```

### 字符串格式化
```python
# 使用 f-strings
message = f"生成失败: {error_message}"
filename = f"image_{counter:04d}.png"

# 避免使用 % 格式化
# 错误示例：message = "生成失败: %s" % error_message
```

### 异步编程
```python
# 使用 asyncio 进行异步操作
async def batch_generate(prompts: List[str]) -> List[Tuple[int, Optional[str], str]]:
    tasks = []
    for i, prompt in enumerate(prompts):
        task = generate_single_image(i, prompt)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# 在同步环境中运行异步代码
loop = asyncio.get_event_loop()
results = await loop.run_in_executor(None, async_func, *args)
```

## 📁 项目结构

```
gemini/
├── main.py                    # 应用入口点
├── config.py                  # 配置管理
├── generator.py               # 图片生成核心逻辑
├── utils.py                   # 通用工具函数
├── test/                      # 测试目录
│   ├── conftest.py            # pytest 配置
│   ├── test_generator.py      # 生成器测试
│   ├── test_config.py         # 配置测试
│   └── test_utils.py          # 工具函数测试
├── ui/                        # UI 模块
│   ├── __init__.py
│   ├── app.py                 # Gradio 应用配置
│   ├── components.py          # UI 组件定义
│   └── handlers.py            # 事件处理逻辑
├── results/                   # 生成图片存储目录
├── .env.example               # 环境变量示例
├── pyproject.toml             # 项目配置
├── uv.lock                    # 依赖锁定文件
└── run.bat                    # Windows 启动脚本
```

## 🔑 配置管理

### 环境变量
项目使用 `.env` 文件管理环境变量：
```bash
# API 密钥格式：*_API_KEY
GOOGLE_API_KEY=your_google_api_key
AIHUBMIX_API_KEY=your_aihubmix_api_key

# 其他配置
MODEL=gemini-3-pro-image-preview
RESULTS_DIR=results
```

### 配置类使用
```python
from config import Config

# 加载配置
config = Config()
config.load()

# 获取供应商列表
providers = config.get_providers()

# 设置当前供应商
success = config.set_provider("GOOGLE")

# 检查供应商状态
is_available = config.is_provider_available("GOOGLE")
```

## 🎨 UI 开发指南

### Gradio 组件约定
```python
# 组件命名使用描述性名称
prompt_input = gr.Textbox(
    label="图片描述",
    placeholder="请输入您想要生成的图片描述...",
    lines=3
)

generate_btn = gr.Button(
    value="生成图片",
    variant="primary",
    size="lg"
)
```

### 事件处理
```python
# 处理函数命名：handle_<action>
def handle_generate_images(prompts, aspect_ratio, reference_image):
    """处理图片生成事件"""
    pass

def handle_upload_image(file):
    """处理图片上传事件"""
    pass

# 事件绑定
generate_btn.click(
    fn=handle_generate_images,
    inputs=[prompt_input, aspect_ratio, reference_upload],
    outputs=[gallery, status]
)
```

## 🏗️ 架构原则

### 模块分离
- **config.py**: 仅处理配置逻辑
- **generator.py**: 仅处理图片生成逻辑
- **utils.py**: 通用工具函数
- **ui/**: 所有 UI 相关代码

### 依赖注入
避免硬编码依赖，使用配置和环境变量：
```python
# 好的做法
model = os.getenv("MODEL", "gemini-3-pro-image-preview")

# 避免硬编码
# model = "gemini-3-pro-image-preview"  # 错误
```

### 错误消息
用户友好的中文错误消息：
```python
return None, "网络连接失败，请检查网络后重试"
return None, f"API 密钥无效: {provider_name}"
```

## 📋 代码审查检查清单

- [ ] 所有函数都有类型注解
- [ ] 导入按正确顺序排列
- [ ] 使用 f-strings 进行字符串格式化
- [ ] 异常处理提供有意义的错误消息
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 私有方法使用下划线前缀
- [ ] 代码已通过 Black 格式化
- [ ] 代码已通过 Ruff 检查
- [ ] 添加了适当的测试
- [ ] 文档字符串使用中文

## 🚀 部署注意事项

### 环境变量
生产环境必须设置：
- `*_API_KEY`：至少一个供应商的 API 密钥
- `RESULTS_DIR`：图片存储目录（确保可写权限）

### 性能优化
- 图片会自动压缩到 300KB 以下
- 使用 asyncio 并行处理多个图片生成请求
- 缓存配置信息避免重复加载

### 安全考虑
- API 密钥通过环境变量管理，不在代码中硬编码
- 用户上传的文件存储在临时目录，定期清理
- 对用户输入进行适当验证和清理