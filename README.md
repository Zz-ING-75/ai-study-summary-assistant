# 生物学习资料摘要自动评测

这是一个适合AI产品经理作品集的学生项目：Python从Excel读取生物学习资料，调用DeepSeek、通义千问或豆包生成摘要，再使用DeepEval的G-Eval指标和OpenAI评审模型，从知识点覆盖率、事实忠实度、简洁度与结构清晰度四个维度自动评分。

## 项目流程

```text
biology_first5.xlsx
        ↓
DeepSeek API生成V1/V2摘要
        ↓
generated_summaries.xlsx
        ↓
DeepEval + OpenAI评审模型
        ↓
evaluation_results.xlsx
```

## 生成V1/V2分析报告

完成评测后运行：

```bash
python analyze_results.py
```

程序会生成 `data/output/analysis_report.xlsx`，其中包含：

- `V1_V2汇总`：不同Prompt版本的平均得分、响应时间和Token；
- `评分明细`：适合查看的精简逐条结果；
- `自动结论`：V2相较V1的变化；
- V1/V2质量得分对比柱状图。

## 1. 在VS Code中打开项目

打开文件夹 `study-summary-evaluator`，然后打开VS Code内置终端。

## 2. 创建虚拟环境

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

## 3. 安装依赖

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## 4. 配置API Key

复制 `.env.example`，并把副本命名为 `.env`：

```text
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
OPENAI_API_KEY=你的OpenAI_API_Key
QWEN_API_KEY=你的千问API_Key
DOUBAO_API_KEY=你的豆包API_Key
DEEPSEEK_MODEL=deepseek-v4-flash
OPENAI_JUDGE_MODEL=gpt-5.4
QWEN_MODEL=qwen3.8-flash
DOUBAO_MODEL=doubao-seed-2-1-turbo-260628
MAX_MATERIALS=5
```

不要把 `.env` 上传到GitHub。.gitignore已经忽略该文件。OpenAI官方SDK会通过环境变量使用API Key；DeepSeek接口使用OpenAI兼容格式。

## 5. 先做不调用API的本地检查

```bash
python generate_summaries.py --dry-run
pytest -q
```

预期结果：显示读取到5份资料、将生成10份摘要，测试全部通过。

## 6. 先生成1份资料的两版摘要

```bash
python generate_summaries.py --limit 1
```

输出文件：`data/output/generated_summaries.xlsx`

确认两份摘要正常后，再运行全部5份：

```bash
python generate_summaries.py --limit 5
```

## 7. 先评测一份摘要

```bash
python evaluate_summaries.py --limit 1
```

输出文件：`data/output/evaluation_results.xlsx`

确认评分与理由正常后，再评测全部摘要：

```bash
python evaluate_summaries.py
```

## 8. 使用同一Prompt比较三个模型

固定使用V2，各生成1份资料进行低成本测试：

```bash
python generate_summaries.py --model deepseek --prompt-version V2 --limit 1
python generate_summaries.py --model qwen --prompt-version V2 --limit 1
python generate_summaries.py --model doubao --prompt-version V2 --limit 1
```

确认成功后，把 `--limit 1` 改为 `--limit 5`。生成结果会合并到同一个
`generated_summaries.xlsx`，不会删除另一个模型的结果。

只评测千问或豆包新生成的摘要：

```bash
python evaluate_summaries.py --model qwen --limit 1
python evaluate_summaries.py --model doubao --limit 1
```

完成所有模型评测后运行 `python analyze_results.py`，在报告的
`模型对比_V2` 工作表查看统一Prompt下的模型横向结果。

## 数据字段如何进入DeepEval

- `input`：学习资料正文
- `actual_output`：DeepSeek生成的摘要
- `expected_output`：人工复核知识点

DeepEval负责建立测试用例、运行G-Eval指标并保存分数；OpenAI模型承担语义判断。自动评分不是绝对标准，项目完成后仍应抽查5～10份结果。

## 常见问题

### 提示缺少API Key

确认项目根目录存在 `.env`，变量名完全一致，并重新打开终端。

### OpenAI模型不可用

把 `.env` 中的 `OPENAI_JUDGE_MODEL` 改成你的API账号可调用的模型。不要把ChatGPT网页会员误认为API额度。

### DeepSeek模型不可用

模型名称可能随平台更新。到DeepSeek API官方文档确认当前模型名，再修改 `DEEPSEEK_MODEL`。

### 控制成本

始终先使用 `--limit 1`。确认单条流程正确后，再扩展到5份或30份。

## 后续扩展

1. 加入千问、豆包和Gemini作为被测模型。
2. 比较不同模型、Prompt、成本与响应时间。
3. 人工抽样评分并计算与自动评分的差异。
4. 使用Streamlit制作上传、运行和查看报告的网页。

## 参考文档

- DeepEval G-Eval：https://deepeval.com/docs/metrics-llm-evals
- DeepEval测试用例：https://deepeval.com/docs/evaluation-test-cases
- OpenAI API快速入门：https://platform.openai.com/docs/quickstart/make-your-first-api-request
- DeepSeek API快速入门：https://api-docs.deepseek.com/
