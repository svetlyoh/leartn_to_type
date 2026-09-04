def choose_fallback(drills:list[str],constraint_hash:str)->str:
    if not drills:raise ValueError('fallback drills must not be empty')
    return drills[int(constraint_hash[:8],16)%len(drills)]
