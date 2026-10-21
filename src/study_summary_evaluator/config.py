from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_local_env(path: Path) -> None:
    """加载项目根目录的简单 KEY=VALUE 配置，不覆盖系统已有环境变量。"""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    input_file: Path = PROJECT_ROOT / "data" / "input" / "biology_30.xlsx"
    output_dir: Path = PROJECT_ROOT / "data" / "output"
    prompt_dir: Path = PROJECT_ROOT / "prompts"
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    doubao_api_key: str = os.getenv("DOUBAO_API_KEY", "")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    judge_model: str = os.getenv("OPENAI_JUDGE_MODEL", "gpt-5.4")
    qwen_model: str = os.getenv("QWEN_MODEL", "qwen3.8-flash")
    qwen_base_url: str = os.getenv(
        "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    doubao_model: str = os.getenv("DOUBAO_MODEL", "doubao-seed-2-1-turbo-260628")
    doubao_base_url: str = os.getenv(
        "DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
    )
    max_materials: int = int(os.getenv("MAX_MATERIALS", "5"))

    def ensure_output_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def require_generation_key(self) -> None:
        if not self.deepseek_api_key:
            raise RuntimeError("缺少 DEEPSEEK_API_KEY。请先复制 .env.example 为 .env 并填写密钥。")

    def require_judge_key(self) -> None:
        if not self.openai_api_key:
            raise RuntimeError("缺少 OPENAI_API_KEY。请在 .env 中填写评审模型的API密钥。")

    def require_model_key(self, provider: str) -> None:
        if provider == "deepseek":
            self.require_generation_key()
        elif provider == "qwen" and not self.qwen_api_key:
            raise RuntimeError("缺少 QWEN_API_KEY。请在 .env 中填写千问的API密钥。")
        elif provider == "doubao" and not self.doubao_api_key:
            raise RuntimeError("缺少 DOUBAO_API_KEY。请在 .env 中填写豆包的API密钥。")


def get_settings() -> Settings:
    return Settings()
