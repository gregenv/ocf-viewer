import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt

st.set_page_config(page_title="OCF ΕΛΛΑΚΤΩΡ 2024", layout="wide")
st.title("📊 Προβολή Excel: OCF ΕΛΛΑΚΤΩΡ 2024")

# Διαβάζουμε όλα τα φύλλα
excel_file = "OCF_ELLAKTOR_2024_DRAFT_V3.xlsx"
sheets = pd.read_excel(excel_file, sheet_name=None)

# Επιλογή φύλλου
sheet_names = list(sheets.keys())
selected_sheet = st.selectbox("Επέλεξε φύλλο:", sheet_names)

df = sheets[selected_sheet]
df.columns = df.columns.map(str)  # Αποφυγή σφαλμάτων AgGrid

# Μορφοποίηση αριθμών (χιλιάδες και δύο δεκαδικά)
pd.options.display.float_format = '{:,.2f}'.format

# Εμφάνιση πίνακα AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=False)
gb.configure_grid_options(domLayout='autoHeight')
grid_options = gb.build()

st.subheader("📋 Πίνακας δεδομένων")
AgGrid(
    df,
    gridOptions=grid_options,
    height=500,
    width='100%',
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=False,
    enable_enterprise_modules=False,
    editable=False
)

# Διάγραμμα πίτας
st.subheader("🥧 Διάγραμμα Πίτας")

numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
text_columns = df.select_dtypes(include=['object']).columns.tolist()

if numeric_columns and text_columns:
    value_col = st.selectbox("Επέλεξε αριθμητική στήλη (τιμή):", numeric_columns)
    category_col = st.selectbox("Επέλεξε κατηγορία (ετικέτα):", text_columns)

    pie_data = df[[category_col, value_col]].dropna()
    chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field=value_col, type="quantitative"),
        color=alt.Color(field=category_col, type="nominal"),
        tooltip=[category_col, alt.Tooltip(value_col, format=',.2f')]
    ).properties(
        width=600,
        height=500,
        title=f"{value_col} κατά {category_col}"
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Χρειάζονται τουλάχιστον μία αριθμητική και μία κειμενική στήλη για γράφημα πίτας.")