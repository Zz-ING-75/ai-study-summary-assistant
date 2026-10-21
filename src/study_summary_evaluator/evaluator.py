from __future__ import annotations

import time
from dataclasses import dataclass

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams


@dataclass
class MetricResult:
    score: float | None
    reason: str
    passed: bool | None


def build_metrics(model: str) -> list[GEval]:
    return [
        GEval(
            name="知识点覆盖率",
            criteria=(
                "依据expected output中的人工复核知识点，逐条判断actual output是否正确表达。"
                "遗漏核心知识点应明显扣分；只出现相关词但没有表达完整含义不算覆盖。"
            ),
            evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
            threshold=0.7,
            model=model,
        ),
        GEval(
            name="事实忠实度",
            criteria=(
                "判断actual output是否严格忠于input原文。原文没有的信息、事实错误、因果倒置或过度推断均应扣分。"
            ),
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            threshold=0.8,
            model=model,
        ),
        GEval(
            name="简洁度",
            criteria="判断actual output是否精炼、无明显重复和无关展开，同时不能以严重遗漏核心内容换取简短。",
            evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
            threshold=0.7,
            model=model,
        ),
        GEval(
            name="结构清晰度",
            criteria="判断actual output是否层次清楚、逻辑连贯、适合作为学生复习摘要。",
            evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
            threshold=0.7,
            model=model,
        ),
    ]


def evaluate_summary(
    source_text: str,
    summary: str,
    confirmed_key_points: str,
    judge_model: str,
) -> dict[str, MetricResult]:
    test_case = LLMTestCase(
        input=source_text,
        actual_output=summary,
        expected_output=confirmed_key_points,
    )
    results: dict[str, MetricResult] = {}
    for metric in build_metrics(judge_model):
        for attempt in range(1, 4):
            try:
                metric.measure(test_case)
                break
            except Exception as exc:
                if attempt == 3:
                    raise
                wait_seconds = attempt * 5
                print(
                    f"  {metric.name}评测暂时失败（{type(exc).__name__}），"
                    f"{wait_seconds}秒后进行第{attempt + 1}次尝试……"
                )
                time.sleep(wait_seconds)
        score = float(metric.score) if metric.score is not None else None
        results[metric.name] = MetricResult(
            score=score,
            reason=str(metric.reason or ""),
            passed=(score >= metric.threshold) if score is not None and metric.threshold is not None else None,
        )
    return results
