import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def get_descriptive_statistics(df):
    """
    獲取 DataFrame 的描述性統計。
    """
    if df is None:
        return "無資料可分析。"
    return df.describe().to_markdown()


def plot_histogram(df, column, title="Histogram", xlabel="Value", ylabel="Frequency"):
    """
    繪製指定欄位的直方圖並返回 Base64 編碼的圖片。
    """
    if df is None or column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None, "無法繪製直方圖：欄位不存在或非數值類型。"

    plt.figure(figsize=(8, 6))
    sns.histplot(df[column].dropna(), kde=True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

    # 將圖表保存到 BytesIO 對象中，然後進行 Base64 編碼
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}", "直方圖已生成。"


def plot_scatterplot(df, x_column, y_column, title="Scatter Plot", xlabel="X-axis", ylabel="Y-axis"):
    """
    繪製指定兩個欄位的散佈圖並返回 Base64 編碼的圖片。
    """
    if (df is None or x_column not in df.columns or y_column not in df.columns or
            not pd.api.types.is_numeric_dtype(df[x_column]) or
            not pd.api.types.is_numeric_dtype(df[y_column])):
        return None, "無法繪製散佈圖：欄位不存在或非數值類型。"

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=df[x_column], y=df[y_column])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}", "散佈圖已生成。"


def get_correlation_matrix(df):
    """
    計算數值欄位的相關係數矩陣。
    """
    if df is None:
        return "無資料可分析。"
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return "DataFrame 中沒有數值欄位可計算相關係數。"
    return numeric_df.corr().to_markdown()


if __name__ == "__main__":
    # 創建一個模擬的 DataFrame
    data = {
        "A": np.random.rand(100),
        "B": np.random.randn(100),
        "C": np.random.randint(0, 100, 100),
        "D": np.random.choice(["X", "Y", "Z"], 100)
    }
    test_df = pd.DataFrame(data)

    print("\nDescriptive Statistics:")
    print(get_descriptive_statistics(test_df))

    print("\nCorrelation Matrix:")
    print(get_correlation_matrix(test_df))

    # 測試直方圖
    hist_img, hist_msg = plot_histogram(test_df, "A")
    if hist_img:
        print("Histogram for column A generated (Base64 string).")
    else:
        print(hist_msg)

    # 測試散佈圖
    scatter_img, scatter_msg = plot_scatterplot(test_df, "A", "B")
    if scatter_img:
        print("Scatter plot for A vs B generated (Base64 string).")
    else:
        print(scatter_msg)
