import plotly.express as px
import pandas as pd
import numpy as np


def get_descriptive_statistics(df):
    return df.describe(include='all').transpose()


def get_correlation_matrix(df):
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr()


def plot_correlation_heatmap(df):
    corr = get_correlation_matrix(df)
    return px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                      title="相關係數熱力圖", aspect="auto")


def plot_histogram(df, column):
    return px.histogram(df, x=column, title=f"{column} 分布直方圖")


def plot_scatterplot(df, x_col, y_col):
    return px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col} 散佈圖")


def plot_box(df, column, group_by=None):
    if group_by:
        return px.box(df, x=group_by, y=column, title=f"{column} 依 {group_by} 分組箱型圖")
    return px.box(df, y=column, title=f"{column} 箱型圖")


def plot_line(df, x_col, y_col):
    return px.line(df, x=x_col, y=y_col, title=f"{y_col} 隨 {x_col} 變化的折線圖")


def plot_pie(df, column):
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    return px.pie(value_counts, names=column, values='count', title=f"{column} 佔比圓餅圖")


def auto_insight(df):
    """規則式自動洞察摘要，不需外部 LLM API"""
    insights = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        skew = df[col].skew()
        mean, std = df[col].mean(), df[col].std()
        missing_pct = df[col].isnull().mean() * 100

        if abs(skew) > 1:
            direction = "右偏（存在較多高值極端值）" if skew > 0 else "左偏（存在較多低值極端值）"
            insights.append(f"📌 **{col}**：分布明顯 {direction}，平均值 {mean:.2f}，標準差 {std:.2f}。")

        if missing_pct > 10:
            insights.append(f"⚠️ **{col}**：缺失值比例達 {missing_pct:.1f}%，建議留意資料完整性。")

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                r = corr.loc[col1, col2]
                if abs(r) > 0.7:
                    relation = "正相關" if r > 0 else "負相關"
                    insights.append(f"🔗 **{col1}** 與 **{col2}** 呈現強{relation}（r = {r:.2f}）。")

    if not insights:
        insights.append("目前數據未偵測到明顯的異常分布或強相關性。")

    return insights
