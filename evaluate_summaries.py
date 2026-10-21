from __future__ import annotations

import argparse

import pandas as pd

from study_summary_evaluator.config import get_settings
from study_summary_evaluator.data_io import save_excel
from study_summary_evaluator.evaluator import evaluate_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用DeepEval和OpenAI评审模型评价摘要。")
    parser.add_argument("--limit", type=int, default=None, help="最多评测多少份摘要。")
    parser.add_argument(
        "--model",
        choices=["deepseek", "qwen", "doubao"],
        default=None,
        help="只评测指定模型生成的摘要。",
    )
    parser.add_argument(
        "--prompt-version",
        choices=["V1", "V2"],
        default=None,
        help="只评测指定Prompt版本；模型横向比较时使用V2。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    settings.require_judge_key()
    settings.ensure_output_dir()

    input_path = settings.output_dir / "generated_summaries.xlsx"
    if not input_path.exists():
        raise FileNotFoundError("尚未找到 generated_summaries.xlsx，请先运行 generate_summaries.py。")
    frame = pd.read_excel(input_path, sheet_name="模型摘要")
    if args.model is not None:
        frame = frame[frame["模型"].astype(str).str.lower().str.contains(args.model)].copy()
    if args.prompt_version is not None:
        frame = frame[
            frame["Prompt版本"].astype(str).str.upper() == args.prompt_version.upper()
        ].copy()
    # 旧版摘要ID与新版摘要ID可能不同，但同一模型、版本和资料只应评测最新一条。
    frame = frame.drop_duplicates(
        subset=["模型", "Prompt版本", "资料ID"], keep="last"
    ).sort_values("资料ID")
    if args.limit is not None:
        frame = frame.head(args.limit).copy()
    if frame.empty:
        raise ValueError("没有找到符合条件的摘要，请先运行对应模型的生成命令。")

    # 提前读取已有评测。每完成一份就立即保存，再次运行时自动跳过。
    output_path = settings.output_dir / "evaluation_results.xlsx"
    if output_path.exists():
        saved_frame = pd.read_excel(output_path, sheet_name="评测结果")
    else:
        saved_frame = pd.DataFrame()
    saved_ids = set(saved_frame["摘要ID"].astype(str)) if "摘要ID" in saved_frame.columns else set()
    failed_ids: list[str] = []

    for _, row in frame.iterrows():
        summary_id = str(row["摘要ID"])
        if summary_id in saved_ids:
            previous = saved_frame[saved_frame["摘要ID"].astype(str) == summary_id].iloc[-1]
            if str(previous.get("模型摘要", "")) == str(row["模型摘要"]):
                print(f"已有评测，跳过：{summary_id}")
                continue
            print(f"摘要内容已更新，将重新评测：{summary_id}")

        print(f"正在评测：{row['摘要ID']}｜{row['资料ID']}｜{row['Prompt版本']}")
        try:
            metrics = evaluate_summary(
                source_text=str(row["学习资料正文"]),
                summary=str(row["模型摘要"]),
                confirmed_key_points=str(row["人工复核知识点"]),
                judge_model=settings.judge_model,
            )
        except Exception as exc:
            print(f"评测失败，已保留此前结果：{summary_id}｜{type(exc).__name__}: {exc}")
            failed_ids.append(summary_id)
            continue

        result: dict[str, object] = row.to_dict()
        scores = []
        for name, metric_result in metrics.items():
            result[f"{name}得分"] = metric_result.score
            result[f"{name}理由"] = metric_result.reason
            result[f"{name}通过"] = metric_result.passed
            if metric_result.score is not None:
                scores.append(metric_result.score)
        result["综合平均分"] = round(sum(scores) / len(scores), 4) if scores else None
        saved_frame = pd.concat([saved_frame, pd.DataFrame([result])], ignore_index=True)
        saved_frame = saved_frame.drop_duplicates(subset=["摘要ID"], keep="last")
        save_excel(saved_frame, output_path, "评测结果")
        saved_ids.add(summary_id)
        print(f"已保存评测：{summary_id}")

    if failed_ids:
        print(f"本轮完成，但有 {len(failed_ids)} 条失败：{', '.join(failed_ids)}")
        print("再次运行相同命令即可只补充失败项。")
    else:
        print(f"完成：{output_path}")


if __name__ == "__main__":
    main()
