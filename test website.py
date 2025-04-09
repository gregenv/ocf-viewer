import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt
import os
import base64
import tempfile
from datetime import datetime

st.set_page_config(page_title="OCF ΕΛΛΑΚΤΩΡ 2024", layout="wide")
st.title("📊 Προβολή Excel: OCF ΕΛΛΑΚΤΩΡ 2024")

# Διαβάζουμε όλα τα φύλλα
excel_file = "OCF_ELLAKTOR_2024_DRAFT_V3.xlsx"
sheets = pd.read_excel(excel_file, sheet_name=None)

# Επιλογή φύλλου
sheet_names = list(sheets.keys())
selected_sheet = st.selectbox("Επέλεξε φύλλο:", sheet_names)

df = sheets[selected_sheet]
df.columns = df.columns.map(str)

# Μορφοποίηση αριθμών
pd.options.display.float_format = '{:,.2f}'.format

# Επιλογή εμφάνισης Top 10 ή όλων
show_top_10 = st.checkbox("Προβολή μόνο Top 10 (βάσει τιμής)", value=False)

# Επιλογή στήλης για φιλτράρισμα Top 10
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
text_columns = df.select_dtypes(include=['object']).columns.tolist()

if show_top_10 and numeric_columns:
    top_col = st.selectbox("Επέλεξε αριθμητική στήλη για Top 10:", numeric_columns)
    df = df.nlargest(10, top_col)

# AgGrid με auto column sizing και scrollable ύψος
st.subheader("📋 Πίνακας δεδομένων (με φίλτρα και scroll)")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True, wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_grid_options(domLayout='normal', suppressHorizontalScroll=True)
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

# Υπολογισμός Total
if numeric_columns:
    st.markdown("### 📌 Σύνολο επιλεγμένων (φιλτραρισμένων) δεδομένων:")
    for col in numeric_columns:
        if col in filtered_df.columns:
            total = filtered_df[col].sum()
            st.markdown(f"**{col}:** {total:,.2f}")

# Διάγραμμα πίτας
st.subheader("🥧 Διάγραμμα Πίτας από τα φιλτραρισμένα δεδομένα")

if numeric_columns and text_columns:
    value_col = st.selectbox("Επέλεξε αριθμητική στήλη (τιμή):", numeric_columns)
    category_col = st.selectbox("Επέλεξε κατηγορία (ετικέτα):", text_columns)

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

    with st.expander("📥 Εξαγωγή Διαγράμματος σε PDF"):
        try:
            svg = chart.save(None, format='svg')

            tmp_svg_path = os.path.join(tempfile.gettempdir(), "chart.svg")
            with open(tmp_svg_path, "w", encoding="utf-8") as f:
                f.write(svg)

            import svglib.svglib
            import reportlab.graphics
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF

            drawing = svg2rlg(tmp_svg_path)
            tmp_pdf_path = os.path.join(tempfile.gettempdir(), "chart.pdf")
            renderPDF.drawToFile(drawing, tmp_pdf_path)

            with open(tmp_pdf_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="chart.pdf">📄 Κατέβασε PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
        except:
            st.warning("Δεν υποστηρίζεται πλήρως η μετατροπή SVG σε PDF σε αυτό το περιβάλλον.")
else:
    st.info("Χρειάζονται τουλάχιστον μία αριθμητική και μία κειμενική στήλη για γράφημα πίτας.")