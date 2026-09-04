import re
def validate(text:str,allowed:str,min_length:int=12,max_length:int=240):
    text=text.strip();errors=[]
    if text.startswith('```') and text.endswith('```'):text=re.sub(r'^```(?:text)?\s*','',text);text=re.sub(r'\s*```$','',text).strip()
    if len(text)<min_length:errors.append('too_short')
    if len(text)>max_length:errors.append('too_long')
    if any(char not in set(allowed) for char in text):errors.append('forbidden_character')
    if re.search(r'(.{2,})\1\1\1',text):errors.append('repetitive')
    return {'valid':not errors,'errors':errors,'text':text}
