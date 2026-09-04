import base64, hashlib, hmac, os
DEFAULT_ITERATIONS=600_000
def derive(pin:str,pepper:str,salt:bytes,iterations:int=DEFAULT_ITERATIONS)->bytes:return hashlib.pbkdf2_hmac('sha256',(pin.strip()+pepper).encode(),salt,iterations,dklen=32)
def create_verifier(pin:str,pepper:str,iterations:int=DEFAULT_ITERATIONS):
    salt=os.urandom(16);return base64.b64encode(salt).decode(),base64.b64encode(derive(pin,pepper,salt,iterations)).decode(),iterations
def verify(pin:str,pepper:str,salt_b64:str,verifier_b64:str,iterations:int)->bool:return hmac.compare_digest(derive(pin,pepper,base64.b64decode(salt_b64),iterations),base64.b64decode(verifier_b64))
def valid_pin(pin:str,kind:str)->bool:return pin.isdigit() and ({'profile':(4,6),'site':(6,12),'admin':(8,12)}[kind][0]<=len(pin)<={'profile':(4,6),'site':(6,12),'admin':(8,12)}[kind][1])
