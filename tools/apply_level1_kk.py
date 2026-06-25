import csv
import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "tmp" / "pdfs" / "level1.pdf"
CSV_PATH = ROOT / "tmp" / "vocab6000.csv"
KK_JSON_PATH = ROOT / "eng6000" / "level1_kk.json"


def normalize_key(text):
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def add_mapping(mapping, raw_word, kk):
    word = raw_word.strip(" \n\t\r,.;:()")
    kk = kk.strip()
    if not word or not kk:
        return

    # 避免把英文句尾或頁首標題誤判成單字。
    if len(word) > 40 or any(ch.isdigit() for ch in word):
        return
    if not re.search(r"[A-Za-z]", word):
        return

    variants = [word]
    variants += [part for part in re.split(r"/", word) if part]

    # agree(ment) 這類寫法同時補 agree 與 agreement。
    expanded = []
    for item in variants:
        expanded.append(item)
        match = re.fullmatch(r"([A-Za-z]+)\(([A-Za-z]+)\)", item)
        if match:
            expanded.append(match.group(1))
            expanded.append(match.group(1) + match.group(2))

    for item in expanded:
        key = normalize_key(item)
        if key and key not in mapping:
            mapping[key] = kk


def extract_pdf_kk():
    mapping = {}
    bracket_pattern = re.compile(r"\[([^\]\[]+)\]")
    word_pattern = re.compile(r"([A-Za-z][A-Za-z.()'/-]*(?:\s+[A-Za-z][A-Za-z.()'/-]*){0,3})\s*$")

    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            for match in bracket_pattern.finditer(text):
                kk = match.group(1)
                # 回看最近一小段文字，取最靠近音標前方的英文詞組。
                prefix = text[max(0, match.start() - 80):match.start()]
                prefix = prefix.replace("\n", " ")
                word_match = word_pattern.search(prefix)
                if word_match:
                    add_mapping(mapping, word_match.group(1), kk)

    return mapping


def load_level1_words():
    words = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 6 and row[1].strip() == "1":
                words.append(row[2].strip())
    return words


SUPPLEMENT_KK = {
    "agree": "əˋgri",
    "am/a.m.": "æm / ˋe ˋɛm",
    "area": "ˋɛrɪə",
    "bored": "bɔrd",
    "boring": "ˋbɔrɪŋ",
    "bow": "baʊ / bo",
    "card": "kɑrd",
    "cellphone": "ˋsɛl͵fon",
    "earth": "ɝθ",
    "everyone/everybody": "ˋɛvrɪ͵wʌn / ˋɛvrɪ͵bɑdɪ",
    "everything": "ˋɛvrɪ͵θɪŋ",
    "excited": "ɪkˋsaɪtɪd",
    "exciting": "ɪkˋsaɪtɪŋ",
    "finally": "ˋfaɪn!ɪ",
    "flower": "ˋflaʊɚ",
    "glove(s)": "glʌv",
    "goodbye": "͵gʊdˋbaɪ",
    "he (him, his, himself)": "hi / hɪm / hɪz / hɪmˋsɛlf",
    "headache": "ˋhɛd͵ek",
    "I (me, my, mine, myself)": "aɪ / mi / maɪ / maɪn / maɪˋsɛlf",
    "interested": "ˋɪntərɪstɪd",
    "interesting": "ˋɪntərɪstɪŋ",
    "it (its, itself)": "ɪt / ɪts / ɪtˋsɛlf",
    "knowledge n. lake": "ˋnɑlɪdʒ / lek",
    "later": "ˋletɚ",
    "live": "laɪv / lɪv",
    "married": "ˋmærɪd",
    "mathematics/math": "͵mæθəˋmætɪks / mæθ",
    "move(ment)": "muv / ˋmuvmənt",
    "movie/film": "ˋmuvɪ / fɪlm",
    "much": "mʌtʃ",
    "oˇclock": "əˋklɑk",
    "o’clock": "əˋklɑk",
    "once": "wʌns",
    "online": "ˋɑnˋlaɪn",
    "pants": "pænts",
    "parent(s)": "ˋpɛrənt",
    "pay(ment)": "pe / ˋpemənt",
    "pm/p.m.": "ˋpi ˋɛm",
    "probably": "ˋprɑbəblɪ",
    "race": "res",
    "really": "ˋrɪəlɪ",
    "relative": "ˋrɛlətɪv",
    "she (her, hers, herself)": "ʃi / hɚ / hɝz / hɚˋsɛlf",
    "shoe(s)": "ʃu",
    "someone/somebody": "ˋsʌm͵wʌn / ˋsʌm͵bɑdɪ",
    "soup": "sup",
    "surprised": "sɚˋpraɪzd",
    "taxicab/taxi/cab": "ˋtæksɪ͵kæb / ˋtæksɪ / kæb",
    "they (them, their, theirs, themselves)": "ðe / ðɛm / ðɛr / ðɛrz / ðɛmˋsɛlvz",
    "tired": "taɪrd",
    "usually": "ˋjuʒʊəlɪ",
    "voice": "vɔɪs",
    "we (us, our, ours, ourselves)": "wi / ʌs / aʊr / aʊrz / aʊrˋsɛlvz",
    "you (your, yours, yourself, yourselves)": "ju / jʊr / jʊrz / jʊrˋsɛlf / jʊrˋsɛlvz",
    "zero": "ˋzɪro",
    "zoo": "zu",
}


def main():
    pdf_mapping = extract_pdf_kk()
    level1_words = load_level1_words()
    selected = {}
    missing = []

    for word in level1_words:
        key = normalize_key(word)
        kk = pdf_mapping.get(key)
        if kk:
            selected[word] = kk
        elif word in SUPPLEMENT_KK:
            selected[word] = SUPPLEMENT_KK[word]
        else:
            missing.append(word)

    KK_JSON_PATH.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pdf kk entries: {len(pdf_mapping)}")
    print(f"level1 words: {len(level1_words)}")
    print(f"matched: {len(selected)}")
    print(f"missing: {len(missing)}")
    print("missing sample:", ", ".join(missing[:50]))


if __name__ == "__main__":
    main()
