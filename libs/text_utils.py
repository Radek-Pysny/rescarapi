from unicodedata import normalize, combining


def remove_diacritics(text: str) -> str:
    nfkd = normalize('NFKD', text)
    return ''.join([c for c in nfkd if not combining(c)])


def safe_casefold(text: str) -> str:
    return remove_diacritics(text.strip()).lower()


def preprocess_for_comparison(text: str):
    return safe_casefold(text.strip())
