import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="OCF ΕΛΛΑΚΤΩΡ 2024", layout="wide")
st.title("📊 Προβολή Excel: OCF ΕΛΛΑΚΤΩΡ 2024")

# Διαβάζουμε όλα τα φύλλα
excel_file = "OCF_ELLAKTOR_2024_DRAFT_V3.xlsx"
sheets = pd.read_excel(excel_file, sheet_name=None)

# Επιλογή φύλλου
sheet_names = list(sheets.keys())
selected_sheet = st.selectbox("Επέλεξε φύλλο:", sheet_names)

df = sheets[selected_sheet]

# Δημιουργία ρυθμίσεων AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=False)
gb.configure_grid_options(domLayout='autoHeight')
grid_options = gb.build()

# Προβολή πίνακα με AgGrid (μόνο για ανάγνωση)
AgGrid(
    df,
    gridOptions=grid_options,
    height=600,
    width='100%',
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=False,
    enable_enterprise_modules=False,
    editable=False
)