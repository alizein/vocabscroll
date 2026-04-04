"""
Convert B1_Wortliste_DTZ_Goethe .apkg to VocabScroll vocab.json format
and merge with existing A1 entries.

Usage:
    python scripts/convert_anki_b1.py
"""

import sqlite3
import json
import re
import os

APKG_DB = r"C:\Temp\apkg_extract\extracted\collection.anki2"
VOCAB_JSON = os.path.join(os.path.dirname(__file__), "..", "vocab.json")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "..", "vocab.json")

# Known German prepositions (common list)
PREPOSITIONS = {
    "ab", "an", "auf", "aus", "außer", "bei", "bis", "durch", "für", "gegen",
    "hinter", "in", "mit", "nach", "neben", "ohne", "seit", "statt", "trotz",
    "über", "um", "unter", "von", "vor", "während", "wegen", "zu", "zwischen",
    "anstatt", "aufgrund", "mithilfe", "gegenüber", "entlang", "innerhalb",
    "außerhalb", "oberhalb", "unterhalb", "anhand", "bezüglich", "gemäß",
    "laut", "mangels", "seitens", "zwecks",
}

# Adjective suffixes
ADJ_SUFFIXES = (
    "lich", "ig", "isch", "ell", "al", "iv", "är", "ös", "haft",
    "sam", "bar", "los", "reich", "arm", "voll", "würdig", "fähig",
    "mäßig", "fertig", "frei", "fremd",
)


def infer_type(full_d: str, artikel_d: str) -> str:
    """Infer word type from available fields."""
    if artikel_d.strip():
        return "noun"
    full = full_d.strip().lower()
    # Verb: comma-separated conjugation forms (e.g. "gehen, geht, ging, ist gegangen")
    if "," in full_d and not artikel_d.strip():
        return "verb"
    # Preposition: exact match against known list
    if full in PREPOSITIONS:
        return "prep"
    # Adjective: suffix heuristics
    for suffix in ADJ_SUFFIXES:
        if full.endswith(suffix) and len(full) > len(suffix) + 1:
            return "adj"
    return "phrase"


def extract_audio_filename(sound_field: str) -> str:
    """Extract bare filename from Anki [sound:file.mp3] syntax."""
    m = re.search(r"\[sound:([^\]]+)\]", sound_field)
    return m.group(1) if m else ""


def build_example_str(de: str, en: str) -> str:
    """Build example string in A1 format: 'DE — EN'"""
    de = de.strip()
    en = en.strip()
    if de and en:
        return f"{de} — {en}"
    return de or en


def convert_notes(db_path: str) -> list:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get field names from model definition
    cur.execute("SELECT models FROM col")
    models_raw = cur.fetchone()[0]
    model = list(json.loads(models_raw).values())[0]
    fields = [f["name"] for f in model["flds"]]

    cur.execute("SELECT flds FROM notes ORDER BY CAST(flds AS TEXT)")
    rows = cur.fetchall()

    entries = []
    for (flds_raw,) in rows:
        flds = flds_raw.split("\x1f")
        note = dict(zip(fields, flds))

        full_d = note.get("full_d", "").strip()
        base_e = note.get("base_e", "").strip()
        base_d = note.get("base_d", "").strip()
        artikel_d = note.get("artikel_d", "").strip()
        plural_d = note.get("plural_d", "").strip()
        base_a = note.get("base_a", "").strip()

        if not full_d or not base_e:
            continue

        word_type = infer_type(full_d, artikel_d)

        # Collect all example pairs
        examples = []
        for i in range(1, 10):
            s_de = note.get(f"s{i}", "").strip()
            s_en = note.get(f"s{i}e", "").strip()
            if s_de:
                examples.append({"de": s_de, "en": s_en})

        entry = {
            "de": full_d,
            "en": base_e,
            "lv": "B1",
            "type": word_type,
        }

        if artikel_d:
            entry["article"] = artikel_d
        if base_d:
            entry["base"] = base_d
        if plural_d:
            entry["plural"] = plural_d

        # Keep first example in A1-compatible `example` field
        if examples:
            entry["example"] = build_example_str(examples[0]["de"], examples[0]["en"])

        # Store full list in `examples` array (only if more than 1)
        if len(examples) > 1:
            entry["examples"] = [
                build_example_str(ex["de"], ex["en"]) for ex in examples
            ]

        # For verbs, store conjugation info from full_d
        if word_type == "verb" and "," in full_d:
            parts = [p.strip() for p in full_d.split(",")]
            if len(parts) > 1:
                entry["conjugation"] = full_d  # keep original full form

        audio = extract_audio_filename(base_a)
        if audio:
            entry["audio"] = audio

        entries.append(entry)

    conn.close()
    return entries


def main():
    print(f"Reading existing vocab from {VOCAB_JSON}...")
    with open(VOCAB_JSON, encoding="utf-8") as f:
        existing = json.load(f)
    print(f"  {len(existing)} existing entries (A1)")

    print(f"\nConverting Anki deck from {APKG_DB}...")
    b1_entries = convert_notes(APKG_DB)
    print(f"  {len(b1_entries)} B1 entries converted")

    # Type distribution
    from collections import Counter
    types = Counter(e["type"] for e in b1_entries)
    print(f"  Type distribution: {dict(types)}")

    merged = existing + b1_entries
    print(f"\nTotal after merge: {len(merged)}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Written to {OUTPUT_JSON}")

    # Print a few samples of each type
    print("\n--- Sample B1 entries ---")
    shown = set()
    for e in b1_entries:
        t = e["type"]
        if t not in shown:
            shown.add(t)
            print(f"\n[{t}]")
            print(json.dumps(e, ensure_ascii=False, indent=2))
        if len(shown) >= 5:
            break


if __name__ == "__main__":
    main()
