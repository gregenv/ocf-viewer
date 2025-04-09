import streamlit as st
import pandas as pd

# Τίτλος σελίδας
st.set_page_config(page_title="OCF ΕΛΛΑΚΤΩΡ 2024", layout="wide")
st.title("📊 Προβολή Excel: OCF ΕΛΛΑΚΤΩΡ 2024")

# Ανάγνωση του αρχείου
df = pd.read_excel("OCF_ELLAKTOR_2024_DRAFT_V3.xlsx", sheet_name=None)

# Εμφάνιση κάθε φύλλου
for sheet_name, data in df.items():
    st.subheader(f"Φύλλο: {sheet_name}")
    st.dataframe(data, use_container_width=True)
