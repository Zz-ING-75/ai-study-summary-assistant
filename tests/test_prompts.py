from pathlib import Path

from study_summary_evaluator.generator import load_prompt


def test_prompts_contain_placeholder() -> None:
    prompt_dir = Path(__file__).parents[1] / "prompts"
    for name in ("prompt_v1.txt", "prompt_v2.txt"):
        template = load_prompt(prompt_dir / name)
        rendered = template.format(source_text="测试正文")
        assert "测试正文" in rendered

