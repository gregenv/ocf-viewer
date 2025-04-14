# Password protection
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt
import os
import base64
import tempfile
from datetime import datetime
from PIL import Image

def check_password():
    def password_entered():
        if st.session_state["password"] == "env96":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        st.stop()

check_password()

st.set_page_config(page_title="OCF Sample 2024", layout="wide")

# 🔗 Λογότυπο + Σύνδεσμος εταιρείας με εντυπωσιακή εμφάνιση
col1, col2 = st.columns([2, 6])
with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=260)
    except Exception:
        st.warning("Το λογότυπο δεν φορτώθηκε σωστά.")
    
        st.warning("Το λογότυπο δεν φορτώθηκε σωστά.")
with col2:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 100%; font-size: 1.5em;'>
            <a href="https://envirometrics.evolution-isa.gr/" target="_blank" style="text-decoration: none; color: #000;">
                <strong>Envirometrics</strong><br>
                <span style="font-size: 0.8em; font-style: italic; color: white; animation: fadeIn 2s ease-in-out infinite alternate;">Data-driven Sustainability Excellence</span>
<style>
@keyframes fadeIn {
  from { opacity: 0.4; }
  to { opacity: 1; }
}
</style>
            </a>
        </div>
    """, unsafe_allow_html=True)

st.title("📊 OCF Sample 2024")

# Διαβάζουμε όλα τα φύλλα
excel_file = "OCF_SAMPLE_2024.xlsx"
sheets = pd.read_excel(excel_file, sheet_name=None)

# Επιλογή φύλλου
sheet_names = list(sheets.keys())
selected_sheet = st.selectbox("Select sheet:", sheet_names)

df = sheets[selected_sheet]
df.columns = df.columns.map(str)

# Μορφοποίηση αριθμών
pd.options.display.float_format = '{:,.2f}'.format

# Επιλογή εμφάνισης Top 10 ή όλων
show_top_10 = st.checkbox("Show only Top 10 (by value)", value=False)

# Επιλογή στήλης για φιλτράρισμα Top 10
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
text_columns = df.select_dtypes(include=['object']).columns.tolist()

if show_top_10 and numeric_columns:
    top_col = st.selectbox("Select numeric column for Top 10:", numeric_columns)
    df = df.nlargest(10, top_col)

# AgGrid με auto column sizing και scrollable ύψος
st.subheader("📋 Data table (with filters and scroll)")

gb = GridOptionsBuilder.from_dataframe(df)
for col in numeric_columns:
    gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2, valueFormatter='value.toLocaleString("de-DE")')

grid_options = gb.build()


grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width='100%',
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=False,
    enable_enterprise_modules=False,
    editable=False,
    enable_quicksearch=True,
    update_mode='MODEL_CHANGED',
    reload_data=True
)

filtered_df = grid_response['data']

# Συνάρτηση μορφοποίησης ευρωπαϊκού τύπου

def format_eu_number(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Υπολογισμός Total
if numeric_columns:
    st.markdown("### 📌 Total of selected (filtered) data:")
    for col in numeric_columns:
        if col in filtered_df.columns:
            total = filtered_df[col].sum()
            formatted_total = format_eu_number(total)
            st.markdown(f"**{col}:** {formatted_total}")

# Διάγραμμα πίτας
st.subheader("🥧 Pie Chart from filtered data")

if numeric_columns and text_columns:
    value_col = st.selectbox("Select numeric column (value):", numeric_columns)
    category_col = st.selectbox("Select category (label):", text_columns)

    pie_data = filtered_df[[category_col, value_col]].dropna()
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

    with st.expander("📥 Export Chart to PDF"):
        st.info("⚠️ ⚠️ Exporting chart to PDF is not fully supported on Streamlit Cloud. To save it, right-click on the chart and choose 'Save as image'.. Αν θέλετε να το αποθηκεύσετε, μπορείτε να κάνετε δεξί κλικ στο διάγραμμα και να επιλέξετε 'Save as image'.")
else:
    st.info("At least one numeric and one text column are required for pie chart.")
