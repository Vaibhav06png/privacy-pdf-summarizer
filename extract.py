# extract.py
# This file reads a PDF and gives back all the text from it as a string.

import fitz  # PyMuPDF - used to read PDF files


def get_pdf_text(pdf_path):
    # Open the PDF file
    pdf = fitz.open(pdf_path)

    all_text = ""  # We will keep adding page text to this

    # Loop through every page
    for page_number in range(len(pdf)):
        page = pdf[page_number]

        # Extract text from this page
        page_text = page.get_text("text")

        # Add a label so we know which page this is from
        all_text += f"\n[PAGE {page_number + 1}]\n"
        all_text += page_text

    pdf.close()

    print(f"Done reading PDF. Total characters extracted: {len(all_text)}")

    return all_text