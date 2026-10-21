from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "资料ID",
    "模块",
    "标题",
    "学习资料正文",
    "人工复核知识点",
}


def load_materials(path: Path, limit: int | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到输入文件：{path}")

    workbook = pd.ExcelFile(path)
    if "学习资料" in workbook.sheet_names:
        sheet_name = "学习资料"
    elif "前5份资料" in workbook.sheet_names:
        sheet_name = "前5份资料"
    else:
        raise ValueError("Excel中未找到“学习资料”或“前5份资料”工作表。")
    frame = pd.read_excel(workbook, sheet_name=sheet_name)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Excel缺少必要列：{', '.join(sorted(missing))}")

    frame = frame.dropna(subset=["资料ID", "学习资料正文"]).copy()
    frame["资料ID"] = frame["资料ID"].astype(str).str.strip()
    frame["学习资料正文"] = frame["学习资料正文"].astype(str).str.strip()
    frame["人工复核知识点"] = frame["人工复核知识点"].fillna("").astype(str).str.strip()
    if limit is not None:
        frame = frame.head(limit)
    return frame.reset_index(drop=True)


def save_excel(frame: pd.DataFrame, path: Path, sheet_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name)
        sheet = writer.book[sheet_name]
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        widths = {
            "A": 14,
            "B": 14,
            "C": 26,
            "D": 16,
            "E": 16,
            "F": 85,
            "G": 14,
            "H": 75,
            "I": 75,
        }
        for column, width in widths.items():
            sheet.column_dimensions[column].width = width
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = cell.alignment.copy(vertical="top", wrap_text=True)
