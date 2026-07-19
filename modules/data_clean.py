import pandas as pd
import numpy as np

def load_data(file_path):
    """
    根據檔案類型載入資料 (CSV 或 Excel)。
    :return: (df, error_msg) tuple，成功時 error_msg 為 None。
    """
    try:
        if file_path.lower().endswith(".csv"):
            return pd.read_csv(file_path), None
        elif file_path.lower().endswith((".xls", ".xlsx")):
            return pd.read_excel(file_path), None
        else:
            return None, "不支援的檔案格式。請上傳 CSV 或 Excel 檔案。"
    except Exception as e:
        return None, f"載入檔案時發生錯誤: {e}"


def handle_missing_values(df, strategy="mean", columns=None):
    """
    處理缺失值。
    :param df: DataFrame。
    :param strategy: 填充策略 ("mean", "median", "most_frequent", "drop")。
    :param columns: 要處理的欄位列表，None 表示處理所有適用欄位。
    :return: 處理後的 DataFrame。
    """
    if df is None:
        return None

    df_cleaned = df.copy()
    if columns is None:
        columns = df_cleaned.columns

    for col in columns:
        if col not in df_cleaned.columns:
            continue

        if df_cleaned[col].isnull().any():
            if strategy == "drop":
                df_cleaned = df_cleaned.dropna(subset=[col])
            elif strategy == "mean" and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
            elif strategy == "median" and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
            elif strategy == "most_frequent":
                mode_vals = df_cleaned[col].mode()
                if not mode_vals.empty:
                    df_cleaned[col] = df_cleaned[col].fillna(mode_vals[0])
    return df_cleaned


def remove_duplicates(df):
    """
    移除重複行。
    """
    if df is None:
        return None
    return df.drop_duplicates()


def convert_data_types(df, conversions=None):
    """
    轉換資料類型。
    :param df: DataFrame。
    :param conversions: 字典，鍵為欄位名，值為目標類型 (例如: {"Age": int, "Date": "datetime64[ns]"})。
    :return: 轉換後的 DataFrame。
    """
    if df is None:
        return None

    df_converted = df.copy()
    if conversions:
        for col, dtype in conversions.items():
            if col in df_converted.columns:
                try:
                    df_converted[col] = df_converted[col].astype(dtype)
                except Exception as e:
                    print(f"Warning: Could not convert column {col} to {dtype}. Error: {e}")
    return df_converted


def detect_outliers_iqr(df, column):
    """
    使用 IQR 方法檢測單一數值欄位的異常值。
    :param df: DataFrame。
    :param column: 要檢測的數值欄位名。
    :return: 包含異常值的 DataFrame，若欄位不存在或非數值型則回傳 None。
    """
    if df is None or column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers
