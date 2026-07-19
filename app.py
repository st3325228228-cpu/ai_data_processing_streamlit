import streamlit as st
import os
import pandas as pd
import tempfile

from modules.pdf import extract_text_from_pdf, get_pdf_page_count, get_pdf_metadata
from modules.word import extract_text_from_docx, get_docx_metadata
from modules.translate import translate_text
from modules.data_clean import load_data, handle_missing_values, remove_duplicates, convert_data_types, detect_outliers_iqr
from modules.analysis import get_descriptive_statistics, plot_histogram, plot_scatterplot, get_correlation_matrix

# 確保 modules 目錄存在
if not os.path.exists("modules"):
    os.makedirs("modules")

# Streamlit 頁面配置
st.set_page_config(layout="wide", page_title="AI 資料處理中心")

st.title("🤖 AI 資料處理中心")
st.markdown("--- 您的智能文件與數據助手 ---")

# 全局變數用於儲存 DataFrame
if "df_global" not in st.session_state:
    st.session_state.df_global = None

# --- 文件處理 (PDF/DOCX) --- 
st.header("文件處理 (PDF/DOCX)")

with st.expander("上傳文件並提取文字", expanded=True):
    doc_file_input = st.file_uploader("上傳文件 (PDF 或 DOCX)", type=["pdf", "docx"])
    doc_file_type_radio = st.radio("選擇文件類型", ["PDF", "DOCX"], index=0, horizontal=True)

    if doc_file_input is not None:
        # 將上傳的檔案寫入臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{doc_file_input.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(doc_file_input.getvalue())
            file_path = tmp_file.name

        output_text = ""
        metadata_output = ""
        download_file_path = None

        try:
            if doc_file_type_radio == "PDF":
                if not file_path.lower().endswith(".pdf"):
                    st.error("請上傳 PDF 檔案。")
                else:
                    output_text = extract_text_from_pdf(file_path)
                    page_count = get_pdf_page_count(file_path)
                    metadata = get_pdf_metadata(file_path)
                    metadata_output = f"頁數: {page_count}\n\nMetadata:\n"
                    if isinstance(metadata, dict):
                        for k, v in metadata.items():
                            metadata_output += f"  {k}: {v}\n"
                    else:
                        metadata_output += str(metadata)
                    
                    download_file_path = file_path + ".txt"
                    with open(download_file_path, "w", encoding="utf-8") as f:
                        f.write(output_text)

            elif doc_file_type_radio == "DOCX":
                if not file_path.lower().endswith(".docx"):
                    st.error("請上傳 DOCX 檔案。")
                else:
                    output_text = extract_text_from_docx(file_path)
                    metadata = get_docx_metadata(file_path)
                    metadata_output = "Metadata:\n"
                    if isinstance(metadata, dict):
                        for k, v in metadata.items():
                            metadata_output += f"  {k}: {v}\n"
                    else:
                        metadata_output += str(metadata)

                    download_file_path = file_path + ".txt"
                    with open(download_file_path, "w", encoding="utf-8") as f:
                        f.write(output_text)

            st.subheader("提取文字預覽")
            st.text_area("內容預覽", output_text, height=300)

            st.subheader("文件元數據")
            st.text_area("元數據資訊", metadata_output, height=200)

            if download_file_path and os.path.exists(download_file_path):
                with open(download_file_path, "rb") as f:
                    st.download_button(
                        label="下載提取的文字檔案",
                        data=f.read(),
                        file_name=f"{doc_file_input.name}.txt",
                        mime="text/plain"
                    )
            
        except Exception as e:
            st.error(f"處理文件時發生錯誤: {e}")
        finally:
            # 清理臨時文件
            if "file_path" in locals() and os.path.exists(file_path):
                os.remove(file_path)
            if "download_file_path" in locals() and download_file_path and os.path.exists(download_file_path):
                os.remove(download_file_path)


st.subheader("文本翻譯")
with st.expander("翻譯文字內容", expanded=False):
    translate_input = st.text_area("要翻譯的文字", height=150, key="translate_input_area")
    col1, col2 = st.columns(2)
    with col1:
        src_lang_dropdown = st.selectbox("來源語言", ["auto", "en", "zh-tw", "ja", "ko", "fr", "de"], index=0)
    with col2:
        dest_lang_dropdown = st.selectbox("目標語言", ["en", "zh-tw", "ja", "ko", "fr", "de"], index=1)
    
    if st.button("翻譯", key="translate_btn"):
        if translate_input:
            translated_output = translate_text(translate_input, dest_lang_dropdown, src_lang_dropdown)
            st.text_area("翻譯結果", translated_output, height=150, key="translated_output_area")
        else:
            st.warning("請輸入要翻譯的文字。")


# --- 數據清洗與分析 (CSV/Excel) --- 
st.header("數據清洗與分析 (CSV/Excel)")

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
            os.remove(data_file_path) # 清理臨時文件


if st.session_state.df_global is not None:
    st.subheader("數據清洗")
    with st.expander("執行數據清洗操作", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            missing_strategy_dropdown = st.selectbox(
                "缺失值處理策略",
                ["無", "mean", "median", "most_frequent", "drop"],
                index=0,
                key="missing_strategy"
            )
        with col2:
            remove_duplicates_checkbox = st.checkbox("移除重複行", value=False, key="remove_dup")
        
        st.markdown("--- 轉換資料類型 ---")
        col3, col4 = st.columns(2)
        with col3:
            convert_column_input = st.text_input("轉換資料類型欄位 (選填)", placeholder="例如: Age", key="convert_col")
        with col4:
            convert_type_input = st.text_input("目標資料類型 (選填)", placeholder="例如: int, float, datetime64[ns]", key="convert_type")
        
        st.markdown("--- 異常值檢測 ---")
        outlier_column_input = st.text_input("異常值檢測欄位 (選填)", placeholder="例如: Salary", key="outlier_col")

        if st.button("執行數據清洗", key="clean_btn"):
            df_cleaned = st.session_state.df_global.copy()
            status_messages = []

            # 處理缺失值
            if missing_strategy_dropdown != "無":
                df_cleaned = handle_missing_values(df_cleaned, strategy=missing_strategy_dropdown)
                status_messages.append(f"已使用 '{missing_strategy_dropdown}' 策略處理缺失值。")

            # 移除重複值
            if remove_duplicates_checkbox:
                initial_rows = len(df_cleaned)
                df_cleaned = remove_duplicates(df_cleaned)
                if len(df_cleaned) < initial_rows:
                    status_messages.append(f"已移除 {initial_rows - len(df_cleaned)} 條重複記錄。")
                else:
                    status_messages.append("未發現重複記錄。")

            # 轉換資料類型
            if convert_column_input and convert_type_input and convert_column_input in df_cleaned.columns:
                try:
                    df_cleaned = convert_data_types(df_cleaned, {convert_column_input: convert_type_input})
                    status_messages.append(f"欄位 '{convert_column_input}' 已轉換為 '{convert_type_input}' 類型。")
                except Exception as e:
                    status_messages.append(f"轉換欄位 '{convert_column_input}' 類型失敗: {e}")

            # 檢測異常值
            outlier_info = ""
            if outlier_column_input and outlier_column_input in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[outlier_column_input]):
                outliers = detect_outliers_iqr(df_cleaned, outlier_column_input)
                if not outliers.empty:
                    outlier_info = f"\n\n在 '{outlier_column_input}' 欄位中檢測到異常值 (前5行):\n" + outliers.head().to_markdown()
                else:
                    outlier_info = f"\n\n在 '{outlier_column_input}' 欄位中未檢測到異常值。"
            elif outlier_column_input and outlier_column_input not in df_cleaned.columns:
                outlier_info = f"\n\n異常值檢測失敗：欄位 '{outlier_column_input}' 不存在。"
            elif outlier_column_input and not pd.api.types.is_numeric_dtype(df_cleaned[outlier_column_input]):
                outlier_info = f"\n\n異常值檢測失敗：欄位 '{outlier_column_input}' 不是數值類型。"

            st.session_state.df_global = df_cleaned # 更新全局 DataFrame
            st.success("\n".join(status_messages) + outlier_info)
            st.subheader("清洗後數據預覽 (前5行)")
            st.dataframe(df_cleaned.head())

    st.subheader("數據分析與視覺化")
    with st.expander("執行數據分析與繪圖", expanded=True):
        analysis_type_dropdown = st.selectbox(
            "分析類型",
            ["描述性統計", "相關係數矩陣", "直方圖", "散佈圖"],
            index=0,
            key="analysis_type"
        )
        
        col5, col6 = st.columns(2)
        with col5:
            analysis_column1_input = st.text_input("欄位 1 (直方圖/散佈圖 X軸)", placeholder="例如: Age", key="analysis_col1")
        with col6:
            analysis_column2_input = st.text_input("欄位 2 (散佈圖 Y軸)", placeholder="例如: Salary", key="analysis_col2")
        
        if st.button("執行分析", key="analyze_btn"):
            result_text, plot_image = perform_analysis(analysis_type_dropdown, analysis_column1_input, analysis_column2_input)
            
            if result_text:
                st.text_area("分析結果", result_text, height=200, key="analysis_result_area")
            if plot_image:
                st.image(plot_image, caption=f"{analysis_type_dropdown} for {analysis_column1_input}")
            else:
                st.warning("無法生成圖表，請檢查欄位名稱和數據類型。")

else:
    st.info("請先上傳數據檔案以啟用數據清洗與分析功能。")
