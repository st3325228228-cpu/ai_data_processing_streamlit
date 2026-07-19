import pandas as pd
import numpy as np


def detect_outliers(df, columns, method='iqr', z_thresh=3):
    """
    多欄異常值檢測
    method: 'iqr' 或 'zscore'
    回傳：包含各欄異常值統計的 dict，以及標記異常行的 DataFrame
    """
    report = {}
    outlier_mask = pd.Series(False, index=df.index)

    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            col_mask = (df[col] < lower) | (df[col] > upper)
        else:  # zscore
            mean = df[col].mean()
            std = df[col].std()
            z_scores = (df[col] - mean) / std
            col_mask = z_scores.abs() > z_thresh

        report[col] = int(col_mask.sum())
        outlier_mask = outlier_mask | col_mask

    return report, df[outlier_mask]


def clean_comparison_report(df_before, df_after):
    """產生清洗前後的對比摘要"""
    report = {
        "清洗前列數": len(df_before),
        "清洗後列數": len(df_after),
        "刪除列數": len(df_before) - len(df_after),
        "清洗前缺失值總數": int(df_before.isnull().sum().sum()),
        "清洗後缺失值總數": int(df_after.isnull().sum().sum()),
        "清洗前重複列數": int(df_before.duplicated().sum()),
        "清洗後重複列數": int(df_after.duplicated().sum()),
    }
    return report


def export_dataframe(df, file_format='csv'):
    """
    匯出 DataFrame，回傳 bytes 供 st.download_button 使用
    file_format: 'csv' 或 'excel'
    """
    if file_format == 'csv':
        return df.to_csv(index=False).encode('utf-8-sig')
    else:
        from io import BytesIO
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        return buffer.getvalue()
