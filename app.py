import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="PLFS Scrutiny", layout="wide")
st.title("🛡️ Financial Scrutiny & CSV Streamliner")

def extract_data(file):
    with pdfplumber.open(file) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    
    # Matching variables anywhere on the page
    mapping = {
        "Revenue": [r"Revenue", r"Turnover", r"Total Income"],
        "Net Profit": [r"Net Profit", r"PAT", r"Profit for the year"],
        "Total Assets": [r"Total Assets"],
        "Total Liabilities": [r"Total Liabilities"]
    }

    found_row = {}
    lines = text.split('\n')
    for header, keywords in mapping.items():
        found_row[header] = 0.0
        for line in lines:
            if any(re.search(k, line, re.IGNORECASE) for k in keywords):
                nums = re.findall(r'\(?\d[\d,.]*\)?', line)
                if nums:
                    val = nums[0].replace(',', '')
                    if '(' in val: val = '-' + val.replace('(', '').replace(')', '')
                    found_row[header] = float(val)
                    break
    return pd.DataFrame([found_row])

uploaded_file = st.file_uploader("Upload Balance Sheet PDF", type="pdf")

if uploaded_file:
    df = extract_data(uploaded_file)
    st.write("### 🔍 Extracted Data Preview")
    st.table(df) # Streamlined: Headers on top, content below
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Streamlined CSV", data=csv, file_name="scrutiny.csv")
