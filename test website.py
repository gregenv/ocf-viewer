import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import base64
import io

st.set_page_config(page_title="OCF Viewer", layout="wide")

# === Logo and Title ===
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("""
        <a href="https://envirometrics.evolution-isa.gr/" target="_blank">
            <img src="logo.png" width="110">
        </a>
    """, unsafe_allow_html=True)
with col2:
    st.title("OCF Viewer – ΕΛΛΑΚΤΩΡ 2024")

# === File Upload ===
uploaded_file = st.file_uploader("Επιλέξτε ένα αρχείο Excel", type=["xlsx"])

if uploaded_file:
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    sheet = st.selectbox("Επιλέξτε φύλλο εργασίας", sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet)

    st.subheader("Πίνακας Δεδομένων")
    df.columns = df.columns.astype(str)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter="agTextColumnFilter", resizable=True, sortable=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_side_bar()
    gb.configure_selection("multiple", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400,
        width='100%',
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True
    )

    selected = grid_response["selected_rows"]
    filtered_df = pd.DataFrame(selected) if selected else df

    # === Total Row ===
    if not filtered_df.empty:
        total_row = filtered_df.select_dtypes(include=['number']).sum(numeric_only=True).to_frame().T
        total_row.index = ["Σύνολο"]
        styled_total = total_row.style.format("{:.2f}", thousands=",")
        st.subheader("Σύνολα επιλεγμένων:")
        st.dataframe(styled_total)

    # === Pie Chart ===
    st.subheader("Διάγραμμα Πίτας")
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        col = st.selectbox("Επιλέξτε αριθμητική στήλη", numeric_cols)
        pie_data = filtered_df[col].groupby(filtered_df.index).sum()
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

    # === Export to PDF ===
    st.subheader("Εξαγωγή σε PDF")
    if st.button("Export PDF"):
        try:
            import pdfkit
            html = filtered_df.to_html(index=False)
            pdf_bytes = pdfkit.from_string(html, False)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="filtered_data.pdf">Λήψη PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error("Αποτυχία δημιουργίας PDF. Σφάλμα: " + str(e))

