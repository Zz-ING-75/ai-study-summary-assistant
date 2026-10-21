from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from study_summary_evaluator.config import get_settings
from study_summary_evaluator.data_io import load_materials, save_excel
from study_summary_evaluator.generator import DoubaoSummarizer, OpenAICompatibleSummarizer, load_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="调用不同大模型批量生成学习资料摘要。")
    parser.add_argument(
        "--model",
        choices=["deepseek", "qwen", "doubao"],
        default="deepseek",
        help="选择生成摘要的模型提供商。",
    )
    parser.add_argument(
        "--prompt-version",
        choices=["V1", "V2", "all"],
        default="all",
        help="选择Prompt版本；模型横向比较时使用V2。",
    )
    parser.add_argument("--limit", type=int, default=None, help="最多处理多少份资料。")
    parser.add_argument("--dry-run", action="store_true", help="只检查Excel和Prompt，不调用API。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    limit = args.limit if args.limit is not None else settings.max_materials
    materials = load_materials(settings.input_file, limit=limit)
    all_prompts = {
        "V1": load_prompt(settings.prompt_dir / "prompt_v1.txt"),
        "V2": load_prompt(settings.prompt_dir / "prompt_v2.txt"),
    }
    prompts = all_prompts if args.prompt_version == "all" else {args.prompt_version: all_prompts[args.prompt_version]}

    print(f"已读取 {len(materials)} 份资料，将生成 {len(materials) * len(prompts)} 份摘要。")
    if args.dry_run:
        for _, row in materials.iterrows():
            print(f"- {row['资料ID']}｜{row['标题']}｜正文{len(row['学习资料正文'])}字")
        print("本地检查通过，未调用API。")
        return

    settings.require_model_key(args.model)
    settings.ensure_output_dir()
    provider_config = {
        "deepseek": (settings.deepseek_api_key, settings.deepseek_base_url, settings.deepseek_model, "DS"),
        "qwen": (settings.qwen_api_key, settings.qwen_base_url, settings.qwen_model, "QW"),
        "doubao": (settings.doubao_api_key, settings.doubao_base_url, settings.doubao_model, "DB"),
    }
    api_key, base_url, model_name, id_prefix = provider_config[args.model]
    summarizer_class = DoubaoSummarizer if args.model == "doubao" else OpenAICompatibleSummarizer
    summarizer = summarizer_class(api_key=api_key, base_url=base_url, model=model_name)

    # 提前读取已有结果。后续每成功一条就立刻保存，并在再次运行时跳过已完成项。
    output_path = settings.output_dir / "generated_summaries.xlsx"
    if output_path.exists():
        saved_frame = pd.read_excel(output_path, sheet_name="模型摘要")
    else:
        saved_frame = pd.DataFrame()
    saved_ids = set(saved_frame["摘要ID"].astype(str)) if "摘要ID" in saved_frame.columns else set()
    failed_ids: list[str] = []

    from openai import APIConnectionError, APITimeoutError, RateLimitError

    for _, row in materials.iterrows():
        for prompt_version, template in prompts.items():
            summary_id = f"{id_prefix}-{row['资料ID']}-{prompt_version}"
            if summary_id in saved_ids:
                print(f"已存在，跳过：{row['资料ID']} {prompt_version}")
                continue

            print(f"正在生成：{row['资料ID']} {prompt_version}")
            result = None
            for attempt in range(1, 4):
                try:
                    result = summarizer.generate(row["学习资料正文"], template)
                    break
                except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
                    if attempt == 3:
                        print(f"失败，已重试3次：{summary_id}｜{type(exc).__name__}")
                        failed_ids.append(summary_id)
                    else:
                        wait_seconds = attempt * 5
                        print(f"请求暂时失败，{wait_seconds}秒后进行第{attempt + 1}次尝试……")
                        time.sleep(wait_seconds)

            if result is None:
                continue

            record = {
                "摘要ID": summary_id,
                "资料ID": row["资料ID"],
                "模块": row["模块"],
                "标题": row["标题"],
                "模型": model_name,
                "Prompt版本": prompt_version,
                "模型摘要": result["summary"],
                "响应时间秒": result["latency_seconds"],
                "输入Token": result["input_tokens"],
                "输出Token": result["output_tokens"],
                "学习资料正文": row["学习资料正文"],
                "人工复核知识点": row["人工复核知识点"],
            }
            saved_frame = pd.concat([saved_frame, pd.DataFrame([record])], ignore_index=True)
            saved_frame = saved_frame.drop_duplicates(subset=["摘要ID"], keep="last")
            save_excel(saved_frame, output_path, "模型摘要")
            saved_ids.add(summary_id)
            print(f"已保存：{summary_id}")

    if failed_ids:
        print(f"本轮完成，但有 {len(failed_ids)} 条失败：{', '.join(failed_ids)}")
        print("再次运行相同命令即可只补充失败项。")
    else:
        print(f"完成：{output_path}")


if __name__ == "__main__":
    main()
