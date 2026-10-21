import streamlit as st

from study_summary_evaluator.config import get_settings
from study_summary_evaluator.generator import (
    DoubaoSummarizer,
    OpenAICompatibleSummarizer,
    load_prompt,
)


# ----------------------------
# 网页基础设置
# ----------------------------

st.set_page_config(
    page_title="AI学习资料助手",
    page_icon="📚",
    layout="centered",
)


# ----------------------------
# 页面标题
# ----------------------------

st.title("📚 AI学习资料助手")

st.caption(
    "将长篇学习资料转化为结构清晰、便于复习的知识摘要"
)


# ----------------------------
# 用户输入
# ----------------------------

source_text = st.text_area(
    "请粘贴学习资料",
    placeholder="在这里粘贴教材、讲义或课程资料……",
    height=260,
    max_chars=5000,
)

text_length = len(source_text)

st.caption(
    f"当前已输入 {text_length} 个字符，最多支持 5000 个字符。"
)


# ----------------------------
# 学习模式选择
# ----------------------------

mode = st.radio(
    "选择学习模式",
    options=["快速总结", "详细总结"],
    horizontal=True,
)

if mode == "快速总结":
    st.info(
        "适合日常预习和快速复习，提取3～5个核心知识点，"
        "优先保证生成速度。"
    )

else:
    st.info(
        "适合考试复习和系统整理，提供更完整的知识结构和总结。"
    )


# ----------------------------
# 生成按钮
# ----------------------------

generate_button = st.button(
    "生成学习摘要",
    type="primary",
    use_container_width=True,
)


# ----------------------------
# 生成逻辑
# ----------------------------

if generate_button:

    # 检查用户输入
    if not source_text.strip():
        st.warning("请先输入需要总结的学习资料。")

    elif len(source_text.strip()) < 20:
        st.warning("输入内容过短，请至少输入20个字符。")

    else:
        try:
            settings = get_settings()

            # ----------------------------
            # 快速总结：豆包 + 快速Prompt
            # ----------------------------

            if mode == "快速总结":

                settings.require_model_key("doubao")

                prompt_template = load_prompt(
                    settings.prompt_dir / "prompt_fast.txt"
                )

                summarizer = DoubaoSummarizer(
                    api_key=settings.doubao_api_key,
                    base_url=settings.doubao_base_url,
                    model=settings.doubao_model,
                )

                strategy_label = "快速总结方案"
                model_label = "豆包"

            # ----------------------------
            # 详细总结：DeepSeek + 详细Prompt
            # ----------------------------

            else:

                settings.require_model_key("deepseek")

                prompt_template = load_prompt(
                    settings.prompt_dir / "prompt_detailed.txt"
                )

                summarizer = OpenAICompatibleSummarizer(
                    api_key=settings.deepseek_api_key,
                    base_url=settings.deepseek_base_url,
                    model=settings.deepseek_model,
                )

                strategy_label = "详细总结方案"
                model_label = "DeepSeek"

            # ----------------------------
            # 调用大模型
            # ----------------------------

            with st.spinner(
                "AI正在阅读和整理学习资料，请稍候……"
            ):
                result = summarizer.generate(
                    source_text=source_text.strip(),
                    prompt_template=prompt_template,
                )

            # ----------------------------
            # 展示生成结果
            # ----------------------------

            st.success("学习摘要生成完成！")

            st.subheader("生成结果")

            st.markdown(result["summary"])

            input_tokens = result.get("input_tokens")
            output_tokens = result.get("output_tokens")
            latency_seconds = result.get("latency_seconds")

            # ----------------------------
            # 展示生成指标
            # ----------------------------

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "学习模式",
                mode,
            )

            col2.metric(
                "响应时间",
                (
                    f"{latency_seconds} 秒"
                    if latency_seconds is not None
                    else "暂无"
                ),
            )

            col3.metric(
                "模型返回 Token",
                (
                    output_tokens
                    if output_tokens is not None
                    else "暂无"
                ),
            )

            # ----------------------------
            # 查看详细调用信息
            # ----------------------------

            with st.expander("查看本次生成信息"):

                st.write(f"调用策略：{strategy_label}")

                st.write(f"调用模型：{model_label}")

                st.write(
                    "输入 Token："
                    f"{input_tokens if input_tokens is not None else '暂无'}"
                )

                st.write(
                    "模型返回 Token："
                    f"{output_tokens if output_tokens is not None else '暂无'}"
                )

                st.write(
                    f"输入字符数：{len(source_text.strip())}"
                )

                st.write(
                    "使用Prompt："
                    + (
                        "prompt_fast.txt"
                        if mode == "快速总结"
                        else "prompt_detailed.txt"
                    )
                )

            st.caption(
                "AI生成内容可能存在遗漏或错误，"
                "重要知识点请结合原始资料核对。"
            )

        # ----------------------------
        # 错误处理
        # ----------------------------

        except FileNotFoundError as exc:

            st.error("找不到Prompt文件，请检查prompts文件夹。")

            with st.expander("查看错误信息"):
                st.code(f"{type(exc).__name__}: {exc}")

        except RuntimeError as exc:

            st.error("模型配置或生成过程出现问题。")

            with st.expander("查看错误信息"):
                st.code(f"{type(exc).__name__}: {exc}")

        except Exception as exc:

            st.error(
                "生成失败，可能是网络、接口超时或模型服务繁忙，"
                "请稍后重试。"
            )

            with st.expander("查看错误信息"):
                st.code(f"{type(exc).__name__}: {exc}")


# ----------------------------
# 页面说明
# ----------------------------

st.divider()

st.caption(
    "产品说明：快速总结使用豆包，详细总结使用DeepSeek。"
    "模型方案来源于30份生物学习资料、90份模型摘要的离线评测。"
)