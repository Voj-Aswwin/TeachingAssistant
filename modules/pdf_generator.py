import os
import streamlit as st
from fpdf import FPDF
def generate_pdf_of_youtube_summaries():
    """Generates a PDF containing the summary and Q&A."""
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)
    pdf_path = os.path.join(data_folder, "summary.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('Noto', '', 'fonts/NotoSans-Regular.ttf', uni=True)
    pdf.set_font('Noto', '', 5)

    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(190, 10, st.session_state['summary']
)

    pdf.ln(10)
    pdf.cell(200, 10, "Questions & Answers", ln=True, align='C')
    pdf.ln(10)

    if st.session_state['conversation_history']:
        page_width = pdf.w - 2 * pdf.l_margin
        for i, (q, a) in enumerate(st.session_state['conversation_history']):
            pdf.multi_cell(page_width, 10, f"Q{i+1}: {q}")
            pdf.multi_cell(page_width, 10, f"A{i+1}: {a}")
            pdf.ln(5)

    pdf.output(pdf_path)
    return pdf_path

def generate_pdf_of_rough_notes(notes):
    """Generates a PDF containing the summary and Q&A."""
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)
    pdf_path = os.path.join(data_folder, "summary.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('Noto', '', 'fonts/NotoSans-Regular.ttf', uni=True)
    pdf.set_font('Noto', '', 5)

    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(190, 10, notes)
    pdf.output(pdf_path)
    return pdf_path