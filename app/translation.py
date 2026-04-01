"""
Translation using Meta's NLLB-200 (No Language Left Behind) model.
Model is downloaded on first use and cached in translation_models_dir.
  EN→ZH: eng_Latn → zho_Hant (Traditional Chinese, direct — no conversion needed)
  ZH→EN: zho_Hant → eng_Latn
"""
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.config import settings

NLLB_MODEL = "facebook/nllb-200-distilled-600M"

# Map our internal lang codes to NLLB language codes
LANG_CODES = {
    "en": "eng_Latn",
    "zh": "zho_Hant",  # Traditional Chinese
}

_model = None
_tokenizer = None


def _get_model():
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(
            NLLB_MODEL, cache_dir=settings.translation_models_dir
        )
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            NLLB_MODEL, cache_dir=settings.translation_models_dir
        )
    return _tokenizer, _model


def translate(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text. src_lang/tgt_lang: 'en' or 'zh'."""
    if not text:
        return ""
    tokenizer, model = _get_model()
    src_code = LANG_CODES[src_lang]
    tgt_code = LANG_CODES[tgt_lang]
    tokenizer.src_lang = src_code
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
        max_length=400,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
