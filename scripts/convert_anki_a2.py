"""
Convert A2_Wortliste_Goethe .apkg to VocabScroll vocab.json format
and merge with existing entries.

Usage:
    python scripts/convert_anki_a2.py
"""

import sqlite3
import json
import re
import os

APKG_DB = r"C:\Temp\a2_apkg_extract\extracted\collection.anki2"
VOCAB_JSON = os.path.join(os.path.dirname(__file__), "..", "vocab.json")
OUTPUT_JSON = VOCAB_JSON

PREPOSITIONS = {
    "ab", "an", "auf", "aus", "außer", "bei", "bis", "durch", "für", "gegen",
    "hinter", "in", "mit", "nach", "neben", "ohne", "seit", "statt", "trotz",
    "über", "um", "unter", "von", "vor", "während", "wegen", "zu", "zwischen",
    "anstatt", "aufgrund", "gegenüber", "entlang", "innerhalb", "außerhalb",
    "laut", "gemäß",
}

ADJ_SUFFIXES = (
    "lich", "ig", "isch", "ell", "al", "iv", "är", "ös", "haft",
    "sam", "bar", "los", "reich", "arm", "voll", "würdig", "fähig",
    "mäßig", "fertig", "frei", "fremd",
)


def infer_type(wort_de: str, artikel: str, verbformen: str) -> str:
    if artikel.strip():
        return "noun"
    if verbformen.strip():
        return "verb"
    w = wort_de.strip().lower()
    if w in PREPOSITIONS:
        return "prep"
    for suffix in ADJ_SUFFIXES:
        if w.endswith(suffix) and len(w) > len(suffix) + 1:
            return "adj"
    return "phrase"


def extract_audio_filename(sound_field: str) -> str:
    m = re.search(r"\[sound:([^\]]+)\]", sound_field)
    return m.group(1) if m else ""


def build_example_str(de: str, en: str) -> str:
    de, en = de.strip(), en.strip()
    if de and en:
        return f"{de} — {en}"
    return de or en


def convert_notes(db_path: str) -> list:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT models FROM col")
    model = list(json.loads(cur.fetchone()[0]).values())[0]
    fields = [f["name"] for f in model["flds"]]

    cur.execute("SELECT flds FROM notes ORDER BY CAST(flds AS TEXT)")
    rows = cur.fetchall()

    entries = []
    for (flds_raw,) in rows:
        note = dict(zip(fields, flds_raw.split("\x1f")))

        wort_de   = note.get("Wort_DE", "").strip()
        wort_en   = note.get("Wort_EN", "").strip()
        artikel   = note.get("Artikel", "").strip()
        plural    = note.get("Plural", "").strip()
        hinweis   = note.get("Hinweis", "").strip()
        verbformen = note.get("Verbformen", "").strip()
        audio_wort = note.get("Audio_Wort", "").strip()

        if not wort_de or not wort_en:
            continue

        word_type = infer_type(wort_de, artikel, verbformen)

        # Build de field: nouns get "artikel base, plural" to match A1/B1 style
        if word_type == "noun" and artikel:
            de = f"{artikel} {wort_de}, {plural}" if plural else f"{artikel} {wort_de}"
        else:
            de = wort_de

        # Collect examples (up to 4)
        examples = []
        for i in range(1, 5):
            s_de = note.get(f"Satz{i}_DE", "").strip()
            s_en = note.get(f"Satz{i}_EN", "").strip()
            if s_de:
                examples.append(build_example_str(s_de, s_en))

        entry = {
            "de":   de,
            "en":   wort_en,
            "lv":   "A2",
            "type": word_type,
        }

        if artikel:
            entry["article"] = artikel
        entry["base"] = wort_de
        if plural:
            entry["plural"] = plural
        if verbformen:
            entry["conjugation"] = verbformen
        if hinweis:
            entry["note"] = hinweis
        if examples:
            entry["example"] = examples[0]
        if len(examples) > 1:
            entry["examples"] = examples

        audio = extract_audio_filename(audio_wort)
        if audio:
            entry["audio"] = audio

        entries.append(entry)

    conn.close()
    return entries


def main():
    print(f"Reading existing vocab from {VOCAB_JSON}...")
    with open(VOCAB_JSON, encoding="utf-8") as f:
        existing = json.load(f)
    by_level = {}
    for e in existing:
        by_level[e["lv"]] = by_level.get(e["lv"], 0) + 1
    print(f"  Existing: {dict(by_level)}")

    print(f"\nConverting A2 deck from {APKG_DB}...")
    a2_entries = convert_notes(APKG_DB)
    print(f"  {len(a2_entries)} A2 entries converted")

    from collections import Counter
    types = Counter(e["type"] for e in a2_entries)
    print(f"  Type distribution: {dict(types)}")

    # Insert A2 after A1, before B1
    a1 = [e for e in existing if e["lv"] == "A1"]
    rest = [e for e in existing if e["lv"] != "A1"]
    merged = a1 + a2_entries + rest
    print(f"\nTotal after merge: {len(merged)}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Written to {OUTPUT_JSON}")

    # Samples
    print("\n--- Sample A2 entries ---")
    shown = set()
    for e in a2_entries:
        t = e["type"]
        if t not in shown:
            shown.add(t)
            print(f"\n[{t}]")
            print(json.dumps(e, ensure_ascii=False, indent=2))
        if len(shown) >= 5:
            break


if __name__ == "__main__":
    main()
