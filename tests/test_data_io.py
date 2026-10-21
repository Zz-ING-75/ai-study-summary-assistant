from pathlib import Path

from study_summary_evaluator.data_io import load_materials


def test_load_first_five_materials() -> None:
    path = Path(__file__).parents[1] / "data" / "input" / "biology_first5.xlsx"
    frame = load_materials(path, limit=5)
    assert len(frame) == 5
    assert frame.iloc[0]["资料ID"] == "BIO-001"
    assert frame["学习资料正文"].str.len().min() > 100
    assert frame["人工复核知识点"].str.contains("1.").all()

