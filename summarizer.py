# summarizer.py
# This file sends the masked text to Gemini and gets a summary back.
# The text sent to Gemini has NO real PII - only placeholders.

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def setup_gemini():
    """Connect to Gemini using the API key from .env file."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception("GEMINI_API_KEY not found. Please add it to your .env file.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.1-flash-lite")

    return model

from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 12000,
        chunk_overlap = 500,
    )
    chunks = splitter.split_text(text)
    print(f"Split into {len(chunks)}chunks.")
    return chunks


def ask_gemini(model, prompt):
    """Send a prompt to Gemini and return response text."""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Gemini error: {e}")
        time.sleep(5)

        # Retry once
        response = model.generate_content(prompt)
        return response.text


def summarize_one_chunk(model, chunk, chunk_number):
    """Summarize one chunk of masked text."""

    prompt = f"""You are analyzing a medical document.

IMPORTANT:
- The text contains placeholders like PERSON_001, US_SSN_001, DATE_TIME_001.
- DO NOT change or remove any placeholders.
- Identify EACH patient separately.

For each patient, extract and summarize:

1. Patient Details:
   - Name (PERSON_XXX)
   - SSN (US_SSN_XXX if available)
   - DOB (DATE_TIME_XXX if available)
   - Doctor (PERSON_XXX if mentioned)

2. Medical History:
   - Diagnoses
   - Tests (e.g. X-Ray, HbA1c)
   - Medications
   - Key observations

FORMAT:
Patient 1:
[details + history]

Patient 2:
[details + history]

Be detailed. Do NOT overly shorten.

--- TEXT SECTION {chunk_number} ---
{chunk}
--- END ---

Write the summary below:
"""

    print(f"Summarizing chunk {chunk_number}...")
    summary = ask_gemini(model, prompt)

    time.sleep(1.5)

    return summary


def combine_all_summaries(model, chunk_summaries):
    """
    Combine chunk summaries into a final summary.
    """

    all_summaries_text = ""

    for i, summary in enumerate(chunk_summaries):
        all_summaries_text += f"\n[SECTION {i + 1} SUMMARY]\n{summary}\n"

    prompt = f"""You are combining multiple summaries of a medical document.

IMPORTANT:
- Keep ALL placeholders exactly as they are.
- Do NOT lose any patient information.
- Merge duplicate patient entries if the same person appears multiple times.

For EACH patient provide:

1. Patient Details:
   - Name (PERSON_XXX)
   - SSN
   - DOB
   - Doctor

2. Complete Medical History:
   - Diagnoses
   - Tests
   - Medications
   - Observations

Make the summary:
- Structured
- Detailed
- Easy to read
- Complete (no missing info)

--- SECTION SUMMARIES ---
{all_summaries_text}
--- END ---

Final summary:

Write the final combined summary below:
"""

    print("Combining all chunk summaries into final summary...")
    final_summary = ask_gemini(model, prompt)

    return final_summary


def summarize_document(masked_text):
    """
    Main function:
    Splits text, summarizes chunks, combines results.
    """

    model = setup_gemini()

    chunks = split_into_chunks(masked_text)

    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        summary = summarize_one_chunk(model, chunk, i + 1)
        chunk_summaries.append(summary)

    if len(chunk_summaries) == 1:
        return chunk_summaries[0]

    final_summary = combine_all_summaries(model, chunk_summaries)

    return final_summary