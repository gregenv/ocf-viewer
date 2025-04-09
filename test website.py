import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
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
df.columns = df.columns.map(str)

# Μορφοποίηση αριθμών (χιλιάδες και δύο δεκαδικά)
pd.options.display.float_format = '{:,.2f}'.format

# Επιλογή εμφάνισης Top 10 ή όλων
show_top_10 = st.checkbox("Προβολή μόνο Top 10 (βάσει τιμής)", value=False)

# Επιλογή στήλης για φιλτράρισμα Top 10
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
text_columns = df.select_dtypes(include=['object']).columns.tolist()

if show_top_10 and numeric_columns:
    top_col = st.selectbox("Επέλεξε αριθμητική στήλη για Top 10:", numeric_columns)
    df = df.nlargest(10, top_col)

# AgGrid με φίλτρα
st.subheader("📋 Πίνακας δεδομένων (με φίλτρα)")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=False, filter=True, sortable=True)
gb.configure_grid_options(domLayout='autoHeight')
grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=500,
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

# Υπολογισμός Total αν υπάρχει αριθμητική στήλη
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
else:
    st.info("Χρειάζονται τουλάχιστον μία αριθμητική και μία κειμενική στήλη για γράφημα πίτας.")