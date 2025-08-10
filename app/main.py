from fastapi import FastAPI
from pydantic import BaseModel
import re
from app.lexicon import POS_WORDS, NEG_WORDS, PROFILES  # add PROFILES
from typing import Optional

# Word weights (can be expanded as needed)
WORD_WEIGHTS_POS = {
    "excellent": 2.0,
    "fantastic": 2.0,
    "amazing": 1.5,
    "perfect": 1.5,
}
WORD_WEIGHTS_NEG = {
    "worst": 2.0,
    "terrible": 1.8,
    "awful": 1.5,
    "broken": 1.2,
}

# Intensifiers that scale the sentiment strength of the next word
INTENSIFIERS = {
    "very": 1.3,
    "too": 1.2,
    "extremely": 1.5,
    "so": 1.2,
    "really": 1.15,
    "slightly": 0.8,   # weakening example
}

app = FastAPI(title="Sentiment API", version="0.3.0")


class PredictIn(BaseModel):
    text: str
    # default language: "en" (use "tr" for Turkish)
    lang: Optional[str] = "en"  # If on Python 3.9, use: Optional[str] = "en"

class PredictOut(BaseModel):
    label: str
    score: float

# Preprocessing: Unicode-aware lowercasing and cleaning
def preprocess(text: str) -> str:
    text = text.casefold()  # better for Unicode than lower()
    # keep word chars, spaces, apostrophes (Unicode-aware)
    text = re.sub(r"[^\w\s']", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Handle negations: merge "not" with the next word (e.g., "not good" → "not_good")
def handle_negations(tokens: list[str]) -> list[str]:
    out = []
    skip = False
    for i in range(len(tokens)):
        if skip:
            skip = False
            continue
        if tokens[i] == "not" and i + 1 < len(tokens):
            out.append(f"not_{tokens[i+1]}")
            skip = True
        else:
            out.append(tokens[i])
    return out

def normalize_token(tok: str, lang: str) -> str:
    """Naive stemming for Turkish to match lexicon entries."""
    if lang == "tr":
        # past/personal copula: kötüydü → kötü
        tok = re.sub(r"y[dt][iuü]$", "", tok)
        # simple plural: kullanıcılar → kullanıcı
        tok = re.sub(r"(ler|lar)$", "", tok)
    return tok

@app.get("/")
def root():
    return {"message": "fastapi-sentiment is up. See /docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictOut)
def predict(inp: PredictIn):
    # 1) pick lexicon by language (fallback to English)
    lang = (inp.lang or "en").lower()
    pos_words, neg_words = PROFILES.get(lang, (POS_WORDS, NEG_WORDS))

    # 2) preprocess + negations
    text = preprocess(inp.text)
    tokens = handle_negations(text.split())

    # 2.1) normalize tokens per language (e.g., TR: "kötüydü" -> "kötü")
    tokens = [normalize_token(t, lang) for t in tokens]

    # 3) weighted, token-based sentiment scoring
    pos_score = 0.0
    neg_score = 0.0

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        # scale next token if we see an intensifier
        scale = 1.0
        if tok in INTENSIFIERS and i + 1 < len(tokens):
            scale = INTENSIFIERS[tok]
            i += 1
            tok = tokens[i]

        if tok.startswith("not_"):
            base = tok[4:]
            if base in pos_words:
                w = WORD_WEIGHTS_POS.get(base, 1.0)
                neg_score += w * scale     # not_good → negative
            elif base in neg_words:
                w = WORD_WEIGHTS_NEG.get(base, 1.0)
                pos_score += w * scale     # not_bad → positive
        else:
            if tok in pos_words:
                w = WORD_WEIGHTS_POS.get(tok, 1.0)
                pos_score += w * scale
            elif tok in neg_words:
                w = WORD_WEIGHTS_NEG.get(tok, 1.0)
                neg_score += w * scale

        i += 1

    total = pos_score + neg_score

    # low-signal guard: if too weak, stay neutral
    if total < 0.6:
        label = "neutral"
        score = 0.0
    else:
        score = (pos_score - neg_score) / max(1e-9, total)  # normalize to [-1, 1]
        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"
        else:
            label = "neutral"

    return {"label": label, "score": float(score)}
