from __future__ import annotations

import time
from pathlib import Path

def load_prompt(path: Path) -> str:
    template = path.read_text(encoding="utf-8")
    if "{source_text}" not in template:
        raise ValueError(f"Prompt文件缺少 {{source_text}} 占位符：{path}")
    return template


class OpenAICompatibleSummarizer:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=180.0, max_retries=2)

    def generate(self, source_text: str, prompt_template: str) -> dict[str, object]:
        started = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是严谨的生物学习资料整理助手。只能依据用户提供的资料生成摘要。",
                },
                {"role": "user", "content": prompt_template.format(source_text=source_text)},
            ],
            stream=False,
        )
        elapsed = time.perf_counter() - started
        summary = (response.choices[0].message.content or "").strip()
        if not summary:
            raise RuntimeError("模型返回了空摘要。")

        usage = response.usage
        return {
            "summary": summary,
            "latency_seconds": round(elapsed, 3),
            "input_tokens": getattr(usage, "prompt_tokens", None),
            "output_tokens": getattr(usage, "completion_tokens", None),
        }


class DoubaoSummarizer:
    """使用火山方舟Responses API，并关闭摘要任务不需要的深度思考。"""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=120.0, max_retries=2)

    def generate(self, source_text: str, prompt_template: str) -> dict[str, object]:
        prompt = (
            "你是严谨的生物学习资料整理助手。只能依据用户提供的资料生成摘要。\n\n"
            + prompt_template.format(source_text=source_text)
        )
        started = time.perf_counter()
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            extra_body={"thinking": {"type": "disabled"}},
        )
        elapsed = time.perf_counter() - started
        summary = (response.output_text or "").strip()
        if not summary:
            raise RuntimeError("豆包返回了空摘要。")

        usage = response.usage
        return {
            "summary": summary,
            "latency_seconds": round(elapsed, 3),
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }
