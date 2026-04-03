"""
Translation using Claude API (claude-haiku-4-5).
Requires ANTHROPIC_API_KEY in environment / .env.
"""
import anthropic

from app.config import settings

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


_LANG_NAMES = {
    "en": "English",
    "zh": "Traditional Chinese (Taiwan)",
}

_SYSTEM = (
    "You are a professional interpreter. Translate the user's text accurately. "
    "Output only the translation — no explanations, no alternatives, no punctuation changes."
)


def translate(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text. src_lang/tgt_lang: 'en' or 'zh'."""
    if not text:
        return ""
    src = _LANG_NAMES[src_lang]
    tgt = _LANG_NAMES[tgt_lang]
    response = _get_client().messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=_SYSTEM,
        messages=[
            {"role": "user", "content": f"Translate from {src} to {tgt}:\n{text}"},
        ],
    )
    return response.content[0].text.strip()
