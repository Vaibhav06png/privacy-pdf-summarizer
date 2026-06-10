# masking.py
# Simple and reliable PII masking using Presidio

import json
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider


# PII types we care about (keep it simple)
PII_TYPES = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "DATE_TIME",
    "US_SSN",
    "LOCATION",
]

MIN_CONFIDENCE = 0.6


# ✅ Setup Presidio once
def setup_presidio():
    config = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_sm"}
        ],
    }

    provider = NlpEngineProvider(nlp_configuration=config)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"]
    )

    return analyzer


# ✅ Initialize globally (avoid reloading every time)
analyzer = setup_presidio()


def mask_pii(text):
    """
    Replace PII with placeholders.

    Returns:
        masked_text
        reverse_map (placeholder → original)
    """

    print("Scanning text for PII...")

    detections = analyzer.analyze(
        text=text,
        entities=PII_TYPES,
        language="en"
    )

    # ✅ Filter low-confidence detections
    detections = [d for d in detections if d.score >= MIN_CONFIDENCE]

    # ✅ Sort from end → start (important)
    detections.sort(key=lambda d: d.start, reverse=True)

    value_to_placeholder = {}
    reverse_map = {}
    counters = {}

    text_modified = text

    for d in detections:
        original_value = text[d.start:d.end].strip()

        # ✅ Skip very short / noisy values
        if len(original_value) < 3:
            continue

        # ✅ Reuse placeholder if already seen
        if original_value in value_to_placeholder:
            placeholder = value_to_placeholder[original_value]
        else:
            entity_type = d.entity_type

            counters[entity_type] = counters.get(entity_type, 0) + 1

            placeholder = f"{entity_type}_{counters[entity_type]:03d}"

            value_to_placeholder[original_value] = placeholder
            reverse_map[placeholder] = original_value

        # ✅ Replace in text
        text_modified = (
            text_modified[:d.start]
            + placeholder
            + text_modified[d.end:]
        )

    # ✅ Final safety pass (important but simple)
    for original, placeholder in value_to_placeholder.items():
        text_modified = text_modified.replace(original, placeholder)

    print(f"Masking done. {len(reverse_map)} PII values replaced.")

    return text_modified, reverse_map


def unmask_text(text, reverse_map):
    """
    Replace placeholders back with original values.
    """

    result = text

    for placeholder, original_value in reverse_map.items():
        result = result.replace(placeholder, original_value)

    return result


def save_mapping(reverse_map, path="mappings/pii_mapping.json"):
    """
    Save mapping to JSON file.
    """

    import os

    os.makedirs("mappings", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(reverse_map, f, indent=2)

    print(f"Mapping saved to {path}")