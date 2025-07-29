# Project Name
智能小说多人配音工具

# Installation
1. 克隆项目到本地：
```
git clone https://github.com/yourusername/multi_tts.git
```
2. 确保已安装uv
需要先安装uv，详细可见https://github.com/astral-sh/uv
3. 安装完成后，在项目根目录下执行以下命令安装依赖：
```
uv run src\multi_tts_workflow.py
```
# Usage

## 环境配置

### 1. 配置环境变量
在项目根目录创建 `.env` 文件，配置以下内容：

```env
# 大模型API配置
QWEN_API_KEY=your_qwen_api_key_here
NEW_API_BASE_URL=your_new_api_base_url_here
NEW_API_KEY=your_new_api_key_here

# Minimax TTS配置
MINIMAX_API_KEY=your_minimax_api_key_here

# 文本分割标点符号配置
SEGMENTATION_PUNCTUATION=。！？“”
```

### 2. API密钥获取说明
- **Qwen API**: 用于角色识别，需要到阿里云通义千问官网申请
- **New API**: 用于说话人识别和音色匹配，支持Gemini等模型
- **Minimax API**: 用于TTS语音合成，需要到Minimax官网申请

## 基本使用方法

### 方法一：使用完整工作流程（推荐）

```python
from src.multi_tts_workflow import multi_tts_workflow

# 读取小说文本
with open("your_novel.txt", "r", encoding="utf-8") as f:
    novel_text = f.read()

# 一键生成多人配音
multi_tts_workflow(novel_text, folder_name="my_novel_audio")
```

### 方法二：分步骤使用

```python
from src.multi_tts_workflow import (
    identify_role,
    novel_segmentation, 
    identify_speaker,
    auto_voice_match_minimax,
    combine_data,
    integrate_same_speaker,
    tts_generation
)

# 1. 读取小说文本
with open("your_novel.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 2. 识别角色
role_list = identify_role(text)
print("识别到的角色：", role_list)

# 3. 文本分割
segments = novel_segmentation(text)
print("文本片段数量：", len(segments))

# 4. 识别说话人
speaker_list = identify_speaker(segments, role_list)

# 5. 自动匹配音色
voice_match_list = auto_voice_match_minimax(role_list)

# 6. 合并数据
combined_data = combine_data(segments, speaker_list, voice_match_list)

# 7. 整合相同说话人的连续片段
integrated_data = integrate_same_speaker(combined_data)

# 8. 生成TTS音频
tts_generation(integrated_data, folder_name="output")
```

## 功能详解

### 1. 角色识别 (identify_role)
- **功能**：自动识别小说中的所有角色
- **支持**：第一人称、第二人称、第三人称小说
- **输出**：包含角色ID、姓名、描述的JSON列表

### 2. 文本分割 (novel_segmentation)  
- **功能**：根据标点符号将小说分割成适合配音的片段
- **配置**：可在.env文件中自定义分割标点符号
- **输出**：包含片段ID和内容的JSON列表

### 3. 说话人识别 (identify_speaker)
- **功能**：为每个文本片段分配合适的说话人
- **智能**：基于上下文理解，准确识别对话和旁白
- **输出**：片段ID与说话人的对应关系

### 4. 音色匹配 (auto_voice_match_minimax)
- **功能**：根据角色描述自动匹配最合适的音色
- **音色库**：使用Minimax提供的多种音色
- **智能**：考虑角色的性别、年龄、性格等特征

### 5. 数据整合 (integrate_same_speaker)
- **功能**：合并相同说话人的连续片段
- **优化**：减少音频文件数量，提高播放连贯性

### 6. TTS生成 (tts_generation)
- **功能**：生成高质量的语音文件
- **格式**：输出MP3格式音频
- **组织**：按片段ID命名，便于后续处理

## 输入文件要求

### 支持的小说类型
- ✅ 第一人称小说（自动添加"我"角色）
- ✅ 第二人称小说（自动添加"你"角色）  
- ✅ 第三人称小说（自动添加"旁白"角色）

### 文件格式要求
- **编码**：UTF-8
- **格式**：纯文本文件(.txt)
- **内容**：中文小说文本

## 输出结果

### 文件结构
```
tests/output_tts/your_folder_name/
├── 0.mp3    # 第一个音频片段
├── 1.mp3    # 第二个音频片段
├── 2.mp3    # 第三个音频片段
└── ...      # 更多音频片段
```

### 音频特点
- **格式**：MP3
- **质量**：高质量语音合成
- **多样性**：不同角色使用不同音色
- **连贯性**：相同角色的连续对话已合并

## 示例演示

项目提供了丰富的测试示例：

```bash
# 运行完整示例
uv run src/multi_tts_workflow.py

# 测试文件位置
tests/test_novel/第一人称/    # 第一人称小说示例
tests/test_novel/第三人称/    # 第三人称小说示例
```

## 高级配置

### 自定义分割规则
在`.env`文件中修改`SEGMENTATION_PUNCTUATION`来自定义文本分割的标点符号：

```env
# 默认配置
SEGMENTATION_PUNCTUATION=。！？；

# 更细粒度分割
SEGMENTATION_PUNCTUATION=。！？；，：

# 更粗粒度分割  
SEGMENTATION_PUNCTUATION=。！？
```

### 模型选择
项目支持多种AI模型：
- **角色识别**：Qwen模型
- **说话人识别**：Gemini-2.5-pro（通过New API）
- **音色匹配**：Gemini-2.5-pro（通过New API）
- **TTS合成**：Minimax语音合成

## 注意事项

1. **API配额**：请注意各API服务的使用配额和费用
2. **文件大小**：建议单次处理的小说文本不超过10万字
3. **网络连接**：需要稳定的网络连接访问AI服务
4. **处理时间**：根据文本长度，完整处理可能需要几分钟到几十分钟
5. **音频质量**：生成的音频质量取决于Minimax TTS服务的质量

## 故障排除

### 常见问题
1. **API密钥错误**：检查`.env`文件中的API密钥是否正确
2. **网络超时**：检查网络连接，必要时重试
3. **JSON解析错误**：通常是AI模型返回格式异常，重试即可
4. **音频生成失败**：检查Minimax API密钥和配额

### 调试模式
运行主文件时会输出详细的中间结果，便于调试：

```bash
uv run src/multi_tts_workflow.py
```
