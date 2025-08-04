# 智能小说多人配音工具

一个基于AI的智能小说配音工具，能够自动识别小说中的角色，为不同角色匹配合适的音色，并生成高质量的多人配音音频文件。

## 项目特色

- 🤖 **智能角色识别**：自动识别小说中的所有角色
- 🎭 **智能说话人识别**：准确识别每个文本片段的说话人
- 🎵 **自动音色匹配**：根据角色特征自动匹配最合适的音色
- 🔄 **多TTS服务支持**：支持Minimax和豆包(Doubao)两种TTS服务
- 🧠 **多LLM模型支持**：支持Qwen、Hunyuan、Gemini等多种大语言模型
- ⚡ **并发处理**：使用多线程提高处理效率
- 🎯 **面向对象设计**：采用抽象类和工厂模式，易于扩展

## 安装说明

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/multi_tts.git
cd multi_tts
```

### 2. 安装uv包管理器
请参考 [uv官方文档](https://github.com/astral-sh/uv) 安装uv包管理器。

### 3. 安装依赖
```bash
uv sync
```

### 4. 运行项目
```bash
uv run src/multi_tts_workflow.py
```

## 环境配置

在项目根目录创建 `.env` 文件，配置以下内容：

```env
# Qwen API配置（用于角色识别）
QWEN_TOKEN=your_qwen_token_here
QWEN_CHAT_URL=your_qwen_chat_url_here

# New API配置（用于说话人识别和音色匹配，支持Gemini等模型）
NEW_API_TOKEN=your_new_api_token_here
NEW_API_CHAT_URL=your_new_api_chat_url_here

# Hunyuan API配置（可选）
HUNYUAN_TOKEN=your_hunyuan_token_here
HUNYUAN_URL=your_hunyuan_url_here

# Minimax TTS配置
MINIMAXI_API_URL=your_minimax_api_url_here
MINIMAXI_GROUP_ID=your_minimax_group_id_here
MINIMAXI_API_KEY=your_minimax_api_key_here

# 豆包TTS配置
DOUBAO_API_URL=your_doubao_api_url_here
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_APPID=your_doubao_appid_here

# 文本分割标点符号配置
SEGMENTATION_PUNCTUATION=。！？
```
