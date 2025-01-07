def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    
    text = text.strip().replace("\n", "").replace("\\n", "")
    text = ' '.join(text.split())
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    text = text.rstrip(';')
    text = text.replace('\\"', '').replace("\\'", "")
    text = text.replace('"', '').replace("'", "")
    
    return text