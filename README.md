# 🤖 AI 資料處理中心

一個以 Streamlit 打造的多功能資料處理工具，整合**文件處理**、**智能翻譯**、**數據清洗**與**數據分析視覺化**四大模組，讓文件與數據處理不再需要在多個工具間來回切換。

---

## ✨ 功能總覽

| 模組 | 核心功能 |
|---|---|
| 📄 文件處理 | PDF/DOCX 文字提取、表格提取、OCR 掃描版辨識、關鍵字搜尋、自動摘要 |
| 🌐 智能翻譯 | 多語言翻譯、長文件自動分段翻譯、雙語對照顯示 |
| 🧹 數據清洗 | 缺失值處理、去重、資料類型轉換、多欄異常值檢測（IQR / Z-score）、清洗前後對比報告 |
| 📊 數據分析 | 描述性統計、相關係數熱力圖、直方圖、散佈圖、箱型圖、折線圖、圓餅圖、自動洞察摘要 |

---

## 🗂️ 專案結構

```
├── app.py                     # 主程式，負責 UI 與流程串接
├── requirements.txt            # Python 套件依賴
├── packages.txt                 # 系統層依賴（Streamlit Cloud 用，支援 OCR）
├── runtime.txt                   # 指定 Python 版本
└── modules/
    ├── pdf.py                    # PDF 文字/表格提取、OCR
    ├── word.py                   # DOCX 文字/表格提取
    ├── text_utils.py              # 關鍵字搜尋、自動摘要
    ├── translate.py                # 翻譯功能（單句 / 長文 / 雙語對照）
    ├── data_clean.py                # 數據清洗與異常值檢測
    └── analysis.py                    # 數據分析與 Plotly 視覺化
```

---

## 🚀 快速開始

### 本機執行

```bash
git clone <您的專案網址>
cd <專案資料夾>
pip install -r requirements.txt
streamlit run app.py
```

### OCR 功能額外需求

若要使用「掃描版 PDF 辨識」功能，本機需額外安裝：

- **Tesseract OCR**（含繁體中文語言包 `chi_tra`）
- **Poppler**（供 `pdf2image` 轉換頁面用）

macOS 範例：
```bash
brew install tesseract tesseract-lang poppler
```

Ubuntu / Debian 範例：
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-tra poppler-utils
```

### 部署到 Streamlit Cloud

1. 將專案推送到 GitHub。
2. 在 [Streamlit Cloud](https://streamlit.io/cloud) 建立新 App，指向 `app.py`。
3. 確認專案根目錄包含 `packages.txt`（Streamlit Cloud 會自動讀取並安裝系統層依賴，用於 OCR 功能）。

---

## 📖 使用說明

### 📄 文件處理

1. 上傳 PDF 或 DOCX 檔案。
2. 若是掃描版 PDF（純文字提取結果空白），勾選「啟用 OCR」重新提取。
3. 若文件內含表格，系統會自動偵測並以表格形式顯示。
4. 可輸入關鍵字搜尋文中出現位置，或一鍵生成自動摘要。

### 🌐 智能翻譯

- 可手動輸入文字，或直接選擇「使用上方文件提取的內容」進行翻譯，省去複製貼上。
- 長文件會自動依段落切塊翻譯後拼接，避免超出單次請求字數限制。
- 勾選「雙語對照顯示」可逐段並排比對原文與譯文。

> ⚠️ 繁體中文語言代碼請使用 `zh-TW`（大寫 TW）。

### 🧹 數據清洗

1. 上傳 CSV 或 Excel 檔案。
2. 選擇缺失值處理策略（平均值 / 中位數 / 最常見值 / 直接刪除）。
3. 可勾選移除重複行、指定欄位轉換資料類型。
4. 多選欄位進行異常值檢測，可選擇 **IQR** 或 **Z-score** 方法。
5. 清洗完成後會顯示「清洗前後對比報告」，並可下載 CSV 或 Excel 格式的清洗結果。

### 📊 數據分析

- 支援 8 種分析類型：描述性統計、相關係數熱力圖、直方圖、散佈圖、箱型圖、折線圖、圓餅圖、自動洞察摘要。
- 所有圖表使用 **Plotly** 繪製，可互動縮放、hover 查看數值。
- 「自動洞察摘要」會依據偏度、缺失值比例、強相關性等規則，自動生成文字分析結論。

---

## 🛠️ 技術棧

- **前端框架**：Streamlit
- **文件處理**：PyMuPDF、pdfplumber、python-docx、pytesseract、pdf2image
- **翻譯引擎**：deep-translator（Google Translate）
- **數據處理**：pandas、numpy
- **視覺化**：Plotly

---

## ❓ 常見問題

**Q: 翻譯功能報錯 `ModuleNotFoundError: No module named 'cgi'`？**
A: 這是舊版 `googletrans` 依賴的 `httpx` 呼叫已被 Python 3.13+ 移除的 `cgi` 模組所致。本專案已改用 `deep-translator`，不再有此問題。

**Q: OCR 功能沒反應或報錯？**
A: 請確認 `packages.txt` 已包含 `tesseract-ocr`、`tesseract-ocr-chi-tra`、`poppler-utils`，並重新 Reboot App 讓系統依賴生效。

**Q: 異常值檢測欄位選單是空的？**
A: 異常值檢測僅支援數值型欄位，請確認上傳的資料中該欄位已正確轉換為數字類型。

---

## 📝 授權

本專案僅供學習與內部使用，翻譯功能依賴第三方 Google Translate 服務，請留意其使用條款。
```

---

## 📌 使用建議

把這份內容存成專案根目錄下的 `README.md`，GitHub 和 Streamlit Cloud 都會自動在專案首頁顯示這份說明，未來如果又新增功能（比如串接真正的 LLM API 做摘要），直接更新「功能總覽」表格和「使用說明」段落就好，保持文件跟程式碼同步。
