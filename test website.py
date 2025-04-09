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

# Επιλογή τύπου διαγράμματος
st.subheader("📈 Διάγραμμα από τα δεδομένα")

chart_types = ["Bar Chart", "Line Chart", "Area Chart", "Pie Chart"]
chart_type = st.selectbox("Επέλεξε τύπο διαγράμματος:", chart_types)

# Επιλογή στήλης (μόνο αριθμητικές)
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
text_columns = df.select_dtypes(include=['object']).columns.tolist()

if chart_type == "Pie Chart":
    if numeric_columns and text_columns:
        value_col = st.selectbox("Επέλεξε αριθμητική στήλη (τιμή):", numeric_columns)
        category_col = st.selectbox("Επέλεξε κατηγορία (ετικέτα):", text_columns)

        pie_data = df[[category_col, value_col]].dropna()
        chart = alt.Chart(pie_data).mark_arc().encode(
            theta=alt.Theta(field=value_col, type="quantitative"),
            color=alt.Color(field=category_col, type="nominal"),
            tooltip=[category_col, value_col]
        ).properties(
            width=600,
            height=500,
            title=f"Pie Chart: {value_col} κατά {category_col}"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Χρειάζονται τουλάχιστον μία αριθμητική και μία κειμενική στήλη για γράφημα πίτας.")
else:
    if numeric_columns:
        chart_col = st.selectbox("Επέλεξε στήλη:", numeric_columns)

        chart_base = alt.Chart(df.reset_index()).encode(
            x=alt.X('index:O', title="Γραμμές"),
            y=alt.Y(chart_col, title=chart_col)
        )

        if chart_type == "Bar Chart":
            chart = chart_base.mark_bar()
        elif chart_type == "Line Chart":
            chart = chart_base.mark_line(point=True)
        elif chart_type == "Area Chart":
            chart = chart_base.mark_area()

        st.altair_chart(chart.properties(width=800, height=400), use_container_width=True)
    else:
        st.info("Δεν βρέθηκαν αριθμητικές στήλες για διάγραμμα.")