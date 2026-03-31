"""
Translation using Helsinki-NLP opus-mt models via transformers.
Models are downloaded on first use and cached in translation_models_dir.
  EN→ZH: Helsinki-NLP/opus-mt-en-zh
  ZH→EN: Helsinki-NLP/opus-mt-zh-en
"""
from transformers import MarianMTModel, MarianTokenizer

from app.config import settings

_pipelines: dict[str, tuple[MarianTokenizer, MarianMTModel]] = {}

MODEL_IDS = {
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
}


def _get_pipeline(src: str, tgt: str) -> tuple[MarianTokenizer, MarianMTModel]:
    key = (src, tgt)
    if key not in _pipelines:
        model_id = MODEL_IDS[key]
        tokenizer = MarianTokenizer.from_pretrained(
            model_id, cache_dir=settings.translation_models_dir
        )
        model = MarianMTModel.from_pretrained(
            model_id, cache_dir=settings.translation_models_dir
        )
        _pipelines[key] = (tokenizer, model)
    return _pipelines[key]


def translate(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text. src_lang/tgt_lang: 'en' or 'zh'."""
    if not text:
        return ""
    tokenizer, model = _get_pipeline(src_lang, tgt_lang)
    inputs = tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
