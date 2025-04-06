import os
import streamlit as st
from fpdf import FPDF
def generate_pdf():
    """Generates a PDF containing the summary and Q&A."""
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)
    pdf_path = os.path.join(data_folder, "summary.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(190, 10, st.session_state['summary']
)

    pdf.ln(10)
    pdf.cell(200, 10, "Questions & Answers", ln=True, align='C')
    pdf.ln(10)

    if st.session_state['conversation_history']:
        for i, (q, a) in enumerate(st.session_state['conversation_history']):
            pdf.multi_cell(0, 10, f"Q{i+1}: {q}")
            pdf.multi_cell(0, 10, f"A{i+1}: {a}")
            pdf.ln(5)

    pdf.output(pdf_path)
    return pdf_path
