import streamlit as st
import os
import pandas as pd
import tempfile

from modules.pdf import (
    extract_text_from_pdf, get_pdf_page_count, get_pdf_metadata,
    extract_tables_from_pdf, extract_text_ocr
)
from modules.word import extract_text_from_docx, get_docx_metadata, extract_tables_from_docx
from modules.text_utils import keyword_search, simple_summary
from modules.translate import translate_text, translate_long_text, translate_bilingual
from modules.data_clean import (
    load_data, handle_missing_values, remove_duplicates, convert_data_types,
    detect_outliers_iqr, detect_outliers_multi, clean_comparison_report, export_dataframe
)
from modules.analysis import (
    get_descriptive_statistics, get_correlation_matrix,
    plot_correlation_heatmap, plot_histogram, plot_scatterplot,
    plot_box, plot_line, plot_pie, auto_insight
)

st.set_page_config(layout="wide", page_title="AI 資料處理中心")

st.title("🤖 AI 資料處理中心（進階版）")
st.markdown("--- 您的智能文件與數據助手 ---")

if "df_global" not in st.session_state:
    st.session_state.df_global = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# ================= 文件處理 =================
st.header("📄 文件處理 (PDF/DOCX)")

with st.expander("上傳文件並提取文字", expanded=True):
    doc_file_input = st.file_uploader("上傳文件 (PDF 或 DOCX)", type=["pdf", "docx"])
    doc_file_type_radio = st.radio("選擇文件類型", ["PDF", "DOCX"], index=0, horizontal=True)
    use_ocr_checkbox = st.checkbox("啟用 OCR（適用於掃描版 PDF）", value=False)

    if doc_file_input is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{doc_file_input.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(doc_file_input.getvalue())
            file_path = tmp_file.name

        output_text = ""
        metadata_output = ""
        extracted_tables = []

        try:
            if doc_file_type_radio == "PDF":
                if use_ocr_checkbox:
                    output_text = extract_text_ocr(file_path)
                else:
                    output_text = extract_text_from_pdf(file_path)
                page_count = get_pdf_page_count(file_path)
                metadata = get_pdf_metadata(file_path)
                metadata_output = f"頁數: {page_count}\n\nMetadata:\n" + "\n".join(
                    f"  {k}: {v}" for k, v in metadata.items()
                )
                extracted_tables = extract_tables_from_pdf(file_path)

            elif doc_file_type_radio == "DOCX":
                output_text = extract_text_from_docx(file_path)
                metadata = get_docx_metadata(file_path)
                metadata_output = "Metadata:\n" + "\n".join(
                    f"  {k}: {v}" for k, v in metadata.items()
                )
                extracted_tables = extract_tables_from_docx(file_path)

            st.session_state.extracted_text = output_text

            st.subheader("提取文字預覽")
            st.text_area("內容預覽", output_text, height=300)

            st.subheader("文件元數據")
            st.text_area("元數據資訊", metadata_output, height=150)

            if extracted_tables:
                st.subheader(f"📊 偵測到 {len(extracted_tables)} 個表格")
                for i, tdf in enumerate(extracted_tables):
                    st.markdown(f"**表格 {i+1}**")
                    st.dataframe(tdf)

            st.download_button(
                label="下載提取的文字檔案",
                data=output_text.encode("utf-8"),
                file_name=f"{doc_file_input.name}.txt",
                mime="text/plain"
            )

            st.markdown("---")
            st.subheader("🔍 關鍵字搜尋")
            keyword_input = st.text_input("輸入關鍵字", key="keyword_search_input")
            if keyword_input:
                matches = keyword_search(output_text, keyword_input)
                if matches:
                    st.write(f"找到 {len(matches)} 筆結果：")
                    for m in matches:
                        st.markdown(f"- {m}")
                else:
                    st.info("未找到符合的關鍵字。")

            st.subheader("📝 自動摘要")
            if st.button("生成摘要"):
                summary = simple_summary(output_text)
                st.success(summary)

        except Exception as e:
            st.error(f"處理文件時發生錯誤: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

# ================= 翻譯 =================
st.header("🌐 文本翻譯")
with st.expander("翻譯文字內容", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        src_lang_dropdown = st.selectbox("來源語言", ["auto", "en", "zh-TW", "ja", "ko", "fr", "de"], index=0)
    with col2:
        dest_lang_dropdown = st.selectbox("目標語言", ["en", "zh-TW", "ja", "ko", "fr", "de"], index=1)

    bilingual_mode = st.checkbox("雙語對照顯示", value=False)

    translate_source = st.radio("翻譯來源", ["手動輸入文字", "使用上方文件提取的內容"], horizontal=True)

    if translate_source == "手動輸入文字":
        translate_input = st.text_area("要翻譯的文字", height=150, key="translate_input_area")
    else:
        translate_input = st.session_state.extracted_text
        st.text_area("將翻譯以下文件提取內容", translate_input, height=150, disabled=True)

    if st.button("翻譯", key="translate_btn"):
        if translate_input:
            if bilingual_mode:
                pairs = translate_bilingual(translate_input, dest_lang_dropdown, src_lang_dropdown)
                for original, translated in pairs:
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**原文：** {original}")
                    c2.markdown(f"**譯文：** {translated}")
            else:
                translated_output = translate_long_text(translate_input, dest_lang_dropdown, src_lang_dropdown)
                st.text_area("翻譯結果", translated_output, height=150, key="translated_output_area")
        else:
            st.warning("請輸入或提取要翻譯的文字。")

# ================= 數據清洗與分析 =================
st.header("📊 數據清洗與分析 (CSV/Excel)")

with st.expander("上傳數據檔案並預覽", expanded=True):
    data_file_input = st.file_uploader("上傳數據檔案 (CSV 或 Excel)", type=["csv", "xlsx", "xls"], key="data_uploader")

    if data_file_input is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{data_file_input.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(data_file_input.getvalue())
            data_file_path = tmp_file.name

        df, error_msg = load_data(data_file_path)
        if error_msg:
            st.error(f"載入檔案時發生錯誤: {error_msg}")
            st.session_state.df_global = None
        else:
            st.success("資料載入成功。")
            st.session_state.df_global = df
            st.subheader("數據預覽 (前5行)")
            st.dataframe(df.head())

        if os.path.exists(data_file_path):
            os.remove(data_file_path)


if st.session_state.df_global is not None:
    df_current = st.session_state.df_global

    st.subheader("🧹 數據清洗")
    with st.expander("執行數據清洗操作", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            missing_strategy_dropdown = st.selectbox(
                "缺失值處理策略", ["無", "mean", "median", "most_frequent", "drop"], index=0
            )
        with col2:
            remove_duplicates_checkbox = st.checkbox("移除重複行", value=False)

        st.markdown("--- 轉換資料類型 ---")
        col3, col4 = st.columns(2)
        with col3:
            convert_column_input = st.selectbox("轉換資料類型欄位 (選填)", ["無"] + list(df_current.columns))
        with col4:
            convert_type_input = st.selectbox("目標資料類型 (選填)", ["無", "int", "float", "str", "datetime64[ns]"])

        st.markdown("--- 異常值檢測（可多選欄位） ---")
        numeric_columns = df_current.select_dtypes(include='number').columns.tolist()
        outlier_columns_multiselect = st.multiselect("選擇要檢測的數值欄位", numeric_columns)
        outlier_method_radio = st.radio("檢測方法", ["iqr", "zscore"], horizontal=True)

        if st.button("執行數據清洗", key="clean_btn"):
            df_before = df_current.copy()
            df_cleaned = df_current.copy()
            status_messages = []

            if missing_strategy_dropdown != "無":
                df_cleaned = handle_missing_values(df_cleaned, strategy=missing_strategy_dropdown)
                status_messages.append(f"已使用 '{missing_strategy_dropdown}' 策略處理缺失值。")

            if remove_duplicates_checkbox:
                initial_rows = len(df_cleaned)
                df_cleaned = remove_duplicates(df_cleaned)
                status_messages.append(f"已移除 {initial_rows - len(df_cleaned)} 條重複記錄。")

            if convert_column_input != "無" and convert_type_input != "無":
                try:
                    df_cleaned = convert_data_types(df_cleaned, {convert_column_input: convert_type_input})
                    status_messages.append(f"欄位 '{convert_column_input}' 已轉換為 '{convert_type_input}' 類型。")
                except Exception as e:
                    status_messages.append(f"轉換欄位 '{convert_column_input}' 類型失敗: {e}")

            if outlier_columns_multiselect:
                outlier_report, outlier_rows = detect_outliers_multi(
                    df_cleaned, outlier_columns_multiselect, method=outlier_method_radio
                )
                st.markdown("**異常值檢測報告：**")
                st.json(outlier_report)
                if not outlier_rows.empty:
                    st.dataframe(outlier_rows)

            st.session_state.df_global = df_cleaned
            st.success("\n".join(status_messages) if status_messages else "未執行任何清洗操作。")

            st.markdown("**📋 清洗前後對比報告：**")
            st.json(clean_comparison_report(df_before, df_cleaned))

            st.subheader("清洗後數據預覽 (前5行)")
            st.dataframe(df_cleaned.head())

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("下載為 CSV", export_dataframe(df_cleaned, 'csv'),
                                    "cleaned_data.csv", "text/csv")
            with col_dl2:
                st.download_button("下載為 Excel", export_dataframe(df_cleaned, 'excel'),
                                    "cleaned_data.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("📈 數據分析與視覺化")
    with st.expander("執行數據分析與繪圖", expanded=True):
        df_analysis = st.session_state.df_global
        all_columns = df_analysis.columns.tolist()
        numeric_columns = df_analysis.select_dtypes(include='number').columns.tolist()

        analysis_type_dropdown = st.selectbox(
            "分析類型",
            ["描述性統計", "相關係數熱力圖", "直方圖", "散佈圖", "箱型圖", "折線圖", "圓餅圖", "自動洞察摘要"],
            index=0
        )

        col5, col6 = st.columns(2)
        with col5:
            col1_select = st.selectbox("欄位 1 (X軸 / 主欄位)", ["無"] + all_columns)
        with col6:
            col2_select = st.selectbox("欄位 2 (Y軸 / 分組，選填)", ["無"] + all_columns)

        if st.button("執行分析", key="analyze_btn"):
            if analysis_type_dropdown == "描述性統計":
                st.dataframe(get_descriptive_statistics(df_analysis))

            elif analysis_type_dropdown == "相關係數熱力圖":
                st.plotly_chart(plot_correlation_heatmap(df_analysis), use_container_width=True)

            elif analysis_type_dropdown == "直方圖" and col1_select != "無":
                st.plotly_chart(plot_histogram(df_analysis, col1_select), use_container_width=True)

            elif analysis_type_dropdown == "散佈圖" and col1_select != "無" and col2_select != "無":
                st.plotly_chart(plot_scatterplot(df_analysis, col1_select, col2_select), use_container_width=True)

            elif analysis_type_dropdown == "箱型圖" and col1_select != "無":
                group = col2_select if col2_select != "無" else None
                st.plotly_chart(plot_box(df_analysis, col1_select, group), use_container_width=True)

            elif analysis_type_dropdown == "折線圖" and col1_select != "無" and col2_select != "無":
                st.plotly_chart(plot_line(df_analysis, col1_select, col2_select), use_container_width=True)

            elif analysis_type_dropdown == "圓餅圖" and col1_select != "無":
                st.plotly_chart(plot_pie(df_analysis, col1_select), use_container_width=True)

            elif analysis_type_dropdown == "自動洞察摘要":
                for insight in auto_insight(df_analysis):
                    st.markdown(insight)

            else:
                st.warning("請選擇正確的欄位組合以執行此分析類型。")

else:
    st.info("請先上傳數據檔案以啟用數據清洗與分析功能。")
