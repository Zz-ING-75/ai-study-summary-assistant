# 📚 AI 学习资料助手

一个面向学生预习与复习场景的双模式 AI 学习资料总结 Demo。

用户可以粘贴教材、讲义或课程资料，根据学习需求选择“快速总结”或“详细总结”。系统会自动调用对应的大模型，生成结构化学习摘要，并展示响应时间与 Token 使用情况。

本项目基于 30 份生物学习资料、90 份模型摘要的离线评测结果完成模型选型，并将评测结论转化为可交互的产品 Demo。

## 一、项目背景

长篇学习资料通常存在阅读成本高、重点不突出和复习效率低等问题。

本项目希望解决以下需求：

- 快速提取学习资料中的核心知识点；
- 根据预习和考试复习场景提供不同详细程度的摘要；
- 通过质量、速度和输出长度评测，为不同模式选择合适的模型；
- 将模型评测结果转化为用户可以直接使用的网页产品。

## 二、核心功能

- 支持粘贴最长 5000 字符的学习资料；
- 提供“快速总结”和“详细总结”两种学习模式；
- 自动校验空内容和过短内容；
- 展示生成结果、响应时间和模型返回 Token；
- 显示本次调用的模型、Prompt 和输入信息；
- 模型调用失败时提供错误提示；
- API Key 通过 `.env` 管理，不写入代码。

## 三、双模式产品方案

### 快速总结

- 调用模型：豆包
- 使用 Prompt：`prompt_fast.txt`
- 适用场景：日常预习、快速浏览和考前回顾
- 输出特点：提取 3～5 个核心知识点，内容更精简

### 详细总结

- 调用模型：DeepSeek
- 使用 Prompt：`prompt_detailed.txt`
- 适用场景：考试复习、系统整理和深度学习
- 输出特点：提供核心概念、重要知识点、易混淆点和总结

模型分层方案来自离线评测结果。模型实际响应时间会受到网络状态、服务负载和生成长度影响，单次调用速度不代表长期平均表现。

## 四、产品流程

```text
用户粘贴学习资料
        ↓
系统校验输入内容
        ↓
用户选择学习模式
        ↓
快速总结：豆包 + prompt_fast.txt
详细总结：DeepSeek + prompt_detailed.txt
        ↓
生成结构化学习摘要
        ↓
展示响应时间、Token 和调用信息
```

## 五、模型评测实验

### 实验设计

- 数据集：30 份生物学习资料
- 被测模型：DeepSeek、通义千问、豆包
- 摘要数量：90 份
- Prompt 实验：V1/V2 对比
- 评测维度：
  - 知识点覆盖率
  - 事实忠实度
  - 简洁度
  - 结构清晰度
- 效率指标：
  - 响应时间
  - 输出 Token

### 评测方法

项目使用 Python 和 Pandas 完成数据处理，通过大模型 API 批量生成摘要，并使用 DeepEval 与评审模型完成自动评分。

针对批量调用中的超时、重复数据和任务中断问题，流程加入：

- 自动重试
- 逐条保存
- 结果去重
- 断点续跑

### 实验结论

在本次测试数据和配置下：

- 三个模型综合得分均超过 0.95；
- V2 Prompt 在结构化表达和知识覆盖方面表现更稳定；
- 豆包平均响应时间约为 5.38 秒，表现出较好的响应效率与稳定性；
- 综合质量、速度和输出长度，最终形成“豆包快速总结 + DeepSeek详细总结”的分层产品方案。

自动评分并非绝对标准，重要结论仍需结合人工抽查判断。

## 六、技术架构

```text
Streamlit
    ↓
输入校验与模式选择
    ↓
Python 业务逻辑
    ↓
豆包 API / DeepSeek API
    ↓
结构化摘要与调用指标展示
```

主要技术：

- Python
- Streamlit
- Pandas
- OpenAI SDK
- DeepEval
- OpenPyXL
- Pytest
- 大模型 API

## 七、项目结构

```text
study-summary-evaluator/
├── app.py                         # Streamlit 网页入口
├── generate_summaries.py          # 批量生成摘要
├── evaluate_summaries.py          # 自动评测
├── analyze_results.py             # 生成分析报告
├── prompts/
│   ├── prompt_fast.txt            # 快速总结 Prompt
│   ├── prompt_detailed.txt        # 详细总结 Prompt
│   ├── prompt_v1.txt
│   └── prompt_v2.txt
├── src/study_summary_evaluator/   # 核心业务模块
├── data/input/                    # 测试数据集
├── data/output/                   # 本地结果文件
├── tests/                         # 自动化测试
├── docs/
│   ├── demo-acceptance-test-report.pdf
│   └── demo-acceptance-test-report.docx
├── .env.example                   # 环境变量示例
└── requirements.txt               # Python 依赖
```

## 八、本地运行

### 1. 下载项目

```bash
git clone https://github.com/Zz-ING-75/ai-study-summary-assistant.git
cd ai-study-summary-assistant
```

### 2. 创建虚拟环境

macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 4. 配置 API Key

复制 `.env.example` 并将副本命名为 `.env`，然后填写自己账号可用的 API Key：

```text
DEEPSEEK_API_KEY=
DOUBAO_API_KEY=
OPENAI_API_KEY=
QWEN_API_KEY=
```

请勿将 `.env` 或任何真实 API Key 上传到 GitHub。

### 5. 启动网页 Demo

```bash
python -m streamlit run app.py
```

浏览器访问：

```text
http://localhost:8501
```

## 九、运行离线评测

生成摘要：

```bash
python generate_summaries.py --model doubao --prompt-version V2 --limit 1
```

执行评测：

```bash
python evaluate_summaries.py --model doubao --limit 1
```

生成分析报告：

```bash
python analyze_results.py
```

建议先使用 `--limit 1` 验证流程，再逐步扩大测试数量，以控制 API 成本。

## 十、Demo 验收结果

本轮共执行 6 个核心测试用例，已执行用例全部通过，包括：

- 空内容校验；
- 过短内容校验；
- 正常短资料的快速总结；
- 正常短资料的详细总结；
- 较长资料的快速总结；
- 较长资料的详细总结。

模型服务异常和接口超时场景仍需进一步补充测试，因此当前 Demo 的验收结果为“有条件通过”。

详细报告：

- [Demo 验收测试报告（PDF）](docs/demo-acceptance-test-report.pdf)
- [Demo 验收测试报告（Word）](docs/demo-acceptance-test-report.docx)

## 十一、项目价值

本项目不仅完成了大模型 API 调用，还覆盖了 AI 产品从评测到落地的完整过程：

1. 定义真实学习场景与用户需求；
2. 构建测试数据集和评测指标；
3. 完成多模型与 Prompt 对比实验；
4. 根据质量和效率结果制定模型选型方案；
5. 将实验结论转化为双模式网页 Demo；
6. 通过验收测试验证核心产品链路。

## 十二、后续规划

- 增加 PDF、Word 和 TXT 文件上传；
- 增加摘要复制与下载功能；
- 补充超时、限流和接口失败测试；
- 保存用户历史生成记录；
- 增加模型成本估算；
- 部署为可公开访问的在线 Demo。

## 安全说明

- `.env` 已加入 `.gitignore`；
- 仓库仅保留 `.env.example`；
- 请勿在代码、截图、报告或提交记录中公开真实 API Key；
- AI 生成内容可能存在遗漏或错误，重要知识点应结合原始资料核对。