# main.py
# This is the main file that runs the whole pipeline step by step.
# Run this with: python main.py

import os
from dotenv import load_dotenv

from extract import get_pdf_text
from masking import mask_pii, unmask_text, save_mapping
from summarizer import summarize_document

load_dotenv()


def run():
    # ---------- Settings ----------
    pdf_path = os.getenv("PDF_PATH", "data\HealthCare_Reports 1.pdf")
    output_file = "output_summary.txt"
    mapping_file = "mappings/pii_mapping.json"
    # ------------------------------

    print("\n" + "=" * 50)
    print("Privacy-Preserving PDF Summarization System")
    print("=" * 50 + "\n")

    # STEP 1: Read the PDF
    print("STEP 1: Reading PDF...")
    raw_text = get_pdf_text(pdf_path)
    print(f"Extracted {len(raw_text)} characters.\n")

    # STEP 2: Find and hide all PII
    print("STEP 2: Detecting and masking PII...")
    masked_text, reverse_map = mask_pii(raw_text)
    print(f"{len(reverse_map)} PII values masked.\n")

    # STEP 3: Save the mapping
    print("STEP 3: Saving PII mapping to file...")
    save_mapping(reverse_map, mapping_file)
    print()

    # STEP 4: Security check
    print("STEP 4: Security check - making sure no real PII goes to Gemini...")

    leaks_found = 0

    for placeholder, original_value in reverse_map.items():
        if original_value in masked_text:
            print(f"WARNING: '{original_value}' still found in masked text!")
            leaks_found += 1

    if leaks_found == 0:
        print("All clear! No real PII found in masked text.\n")
    else:
        print(f"{leaks_found} potential leaks found. Proceeding anyway.\n")

    # STEP 5: Summarization
    print("STEP 5: Sending masked text to Gemini for summarization...")
    print("(Gemini only sees placeholders like PERSON_001, not real names)\n")

    placeholder_summary = summarize_document(masked_text)
    print()

    # STEP 6: Restore PII
    print("STEP 6: Restoring original PII values into the summary...")
    final_summary = unmask_text(placeholder_summary, reverse_map)
    print()

    # STEP 7: Save output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_summary)

    print("=" * 50)
    print("FINAL SUMMARY (with original PII restored):")
    print("=" * 50)
    print(final_summary)
    print("=" * 50)

    print(f"\nSummary also saved to: {output_file}")


if __name__ == "__main__":
    run()