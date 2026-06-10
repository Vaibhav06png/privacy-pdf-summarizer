# app.py
# Simple Streamlit UI (no upload, clean view)

import streamlit as st
import os

from extract import get_pdf_text
from masking import mask_pii, unmask_text
from summarizer import summarize_document

st.set_page_config(page_title="PDF Summarizer", layout="wide")

st.title("📄 Medical PDF Summarizer")

st.write("Click the button to generate summary from the configured PDF.")

# ✅ Use fixed path (same as main.py)
pdf_path = os.getenv("PDF_PATH", "data\HealthCare_Reports 1.pdf")

if st.button("Run Summarization"):

    with st.spinner("Processing... ⏳"):

        # STEP 1: Extract
        raw_text = get_pdf_text(pdf_path)

        # STEP 2: Mask
        masked_text, reverse_map = mask_pii(raw_text)

        # STEP 3: Summarize
        placeholder_summary = summarize_document(masked_text)

        # STEP 4: Unmask
        final_summary = unmask_text(placeholder_summary, reverse_map)

    st.success("✅ Summary Generated!")

    # ✅ Show result
    st.subheader("📄 Final Summary")
    st.write(final_summary)

    # ✅ Download option
    st.download_button(
        label="📥 Download Summary",
        data=final_summary,
        file_name="summary.txt",
        mime="text/plain"
    )
