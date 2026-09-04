import hashlib,hmac,secrets
COOKIE='__Host-cadence_session'
def new_token()->str:return secrets.token_urlsafe(32)
def token_hash(token:str,pepper:str)->str:return hmac.new(pepper.encode(),token.encode(),hashlib.sha256).hexdigest()
def cookie_header(token:str)->str:return f'{COOKIE}={token}; Secure; HttpOnly; SameSite=Strict; Path=/'
