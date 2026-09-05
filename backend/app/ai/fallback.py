def choose_fallback(drills:list[str],constraint_hash:str)->str:
    if not drills:raise ValueError('fallback drills must not be empty')
    return drills[int(constraint_hash[:8],16)%len(drills)]

def constrained_pattern(allowed, focus_keys=(), module_id='', recent=(), target=60, seed=''):
    """Deterministic, key-safe patterns; never requires prose or a provider."""
    import hashlib
    from .validator import validate
    keys = sorted(set(allowed) - {' ', '\n', '\r', '\t'})
    if not keys: raise ValueError('Curriculum has no printable keys')
    focus = [key for key in focus_keys if key in keys]
    pool = keys + focus
    target = max(20, min(int(target), 1200))
    for variant in range(100):
        words = []
        counter = 0
        while len(' '.join(words)) < target:
            digest = hashlib.sha256(f'{module_id}|{seed}|{variant}|{counter}'.encode()).digest()
            word = ''.join(pool[digest[i+1] % len(pool)] for i in range(1 + digest[0] % 4))
            words.append(word); counter += 1
        text = (' ' if ' ' in allowed else '').join(words)[:target].rstrip()
        if text not in recent and validate(text, allowed, 12, 1200)['valid']:
            return text
    raise ValueError('Curriculum cannot produce a varied valid pattern')
