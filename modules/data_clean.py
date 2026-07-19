import pandas as pd
import numpy as np
from io import BytesIO


def load_data(file_path):
    """依副檔名載入 CSV 或 Excel，回傳 (DataFrame, 錯誤訊息)"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        return df, None
    except Exception as e:
        return None, str(e)


def handle_missing_values(df, strategy='mean'):
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if strategy == 'drop':
        return df.dropna()

    for col in numeric_cols:
        if strategy == 'mean':
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == 'median':
            df[col] = df[col].fillna(df[col].median())
        elif strategy == 'most_frequent':
            mode = df[col].mode()
            if not mode.empty:
                df[col] = df[col].fillna(mode[0])
    return df


def remove_duplicates(df):
    return df.drop_duplicates()


def convert_data_types(df, column_type_map):
    df = df.copy()
    for col, dtype in column_type_map.items():
        df[col] = df[col].astype(dtype)
    return df


def detect_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    return df[(df[column] < lower) | (df[column] > upper)]


def detect_outliers_multi(df, columns, method='iqr', z_thresh=3):
    """
    多欄批次異常值檢測
    method: 'iqr' 或 'zscore'
    回傳：(各欄異常值數量的 dict, 標記異常行的完整 DataFrame)
    """
    report = {}
    outlier_mask = pd.Series(False, index=df.index)

    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        if method == 'iqr':
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            col_mask = (df[col] < lower) | (df[col] > upper)
        else:  # zscore
            mean, std = df[col].mean(), df[col].std()
            z_scores = (df[col] - mean) / std
            col_mask = z_scores.abs() > z_thresh

        report[col] = int(col_mask.sum())
        outlier_mask = outlier_mask | col_mask

    return report, df[outlier_mask]


def clean_comparison_report(df_before, df_after):
    """清洗前後對比報告"""
    return {
        "清洗前列數": len(df_before),
        "清洗後列數": len(df_after),
        "刪除列數": len(df_before) - len(df_after),
        "清洗前缺失值總數": int(df_before.isnull().sum().sum()),
        "清洗後缺失值總數": int(df_after.isnull().sum().sum()),
        "清洗前重複列數": int(df_before.duplicated().sum()),
        "清洗後重複列數": int(df_after.duplicated().sum()),
    }


def export_dataframe(df, file_format='csv'):
    """匯出成 bytes，供 st.download_button 使用"""
    if file_format == 'csv':
        return df.to_csv(index=False).encode('utf-8-sig')
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    return buffer.getvalue()
