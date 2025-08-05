import pandas as pd
import streamlit as st
import os

# === Excelファイルの読み込み ===
# .pyファイルと同じディレクトリにある.xlsxファイルを探す
excel_file = next((f for f in os.listdir('.') if f.endswith('.xlsx')), None)

if excel_file is None:
    st.error("同じフォルダに .xlsx ファイルが見つかりません。")
    st.stop()

# Excelファイルの全シートを読み込み
sheets_dict = pd.read_excel(excel_file, sheet_name=None)

# FinvizとSeekingAlfaシートを探す
df1 = sheets_dict.get("Finviz", pd.DataFrame())
df2 = sheets_dict.get("SeekingAlfa", pd.DataFrame())

# === Ticker Symbolの統一 ===
def standardize_ticker_column(df, source):
    if "Ticker" in df.columns:
        df = df.rename(columns={"Ticker": "Ticker Symbol"})
    else:
        # "Symbol" で始まる列を探す（完全一致以外も含む）
        symbol_cols = [col for col in df.columns if col.startswith("Symbol")]
        if symbol_cols:
            df = df.rename(columns={symbol_cols[0]: "Ticker Symbol"})
        else:
            st.warning(f"{source} に 'Ticker' も 'Symbol' で始まる列も見つかりませんでした。")
            df["Ticker Symbol"] = None
    return df


df1 = standardize_ticker_column(df1, "Finviz")
df2 = standardize_ticker_column(df2, "SeekigAlfa")

# === データベース作成（Ticker Symbol をキーに外部結合） ===
db = pd.merge(df1, df2, on="Ticker Symbol", how="outer", suffixes=('_Finviz', '_SeekingAlfa'))

# === Streamlit UI表示 ===
st.title("Ticker Symbol 統合データビューア")
st.markdown("🧭 **複数列のソートをする場合は、Shiftを押しながらソート列を選択してください。**")

# 複数列のソートが可能なStreamlit標準のデータテーブル表示
st.dataframe(db, use_container_width=True)

