#encryption ------------

# -- password section --
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw,Type
from argon2.exceptions import VerifyMismatchError
from json import loads,load,dumps,dump
from base64 import b64encode,b64decode
from os import urandom,replace,remove
ph = PasswordHasher( # <-- this causes high cpu usage
    time_cost=3,
    memory_cost=64 * 1024,
    parallelism=2,
    hash_len=32
)
def hashedPasswordGen(password: str) -> str:
    hash_value = ph.hash(password)
    return hash_value
def correctPassword(password: str) -> bool:
    with open("lopAuth Data/data.json",'r')as f:
        hash_value = load(f)
        if "password" in hash_value:
            hash_value = hash_value["password"]
        else:
            return False
    try:
        return ph.verify(hash_value,password)
    except VerifyMismatchError:
        return False
# ----------------------
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
def deriveKey(password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=2,
        hash_len=32,
        type=Type.ID,
    )
def encrypt(two_factor: entry2fa,password:str):
        data = {"title": two_factor.title,"secret": two_factor.secret,"issuer": two_factor.issuer,"digits": two_factor.digits,"interval": two_factor.interval,"type": two_factor.type}
        # ^ json data from entry2fa
        textData = dumps(data).encode("utf-8")
        
        keySalt = urandom(16)     # store
        nonce = urandom(12)       # store
        key = deriveKey(password, keySalt)
        cipher = ChaCha20Poly1305(key)

        ciphertext = cipher.encrypt(nonce, textData, None)

        return [keySalt,nonce,ciphertext]





def decrypt(encrypted_entry: dict, password: str) -> entry2fa:
    ciphertext = b64decode(encrypted_entry["ciphertext"])
    keySalt = b64decode(encrypted_entry["keySalt"])
    nonce = b64decode(encrypted_entry["nonce"])
    key = deriveKey(password, keySalt)
    cipher = ChaCha20Poly1305(key)
    plaintext = cipher.decrypt(nonce, ciphertext, None)
    data = loads(plaintext.decode("utf-8"))
    return entry2fa(title=data["title"],secret=data["secret"],issuer=data["issuer"],digits=data["digits"],interval=data["interval"],type=data["type"])






#utils ------------------------



class entry2fa():
    def __init__(self,secret="sample",issuer="sample",title="sample",digits=6,interval=30,type="TOTP"):
        self.title = title
        self.secret = secret
        self.issuer = issuer
        self.digits = digits
        self.interval = interval
        self.type = type



from pyzbar.pyzbar import decode
from PIL import ImageGrab
from urllib.parse import urlparse, parse_qs, unquote
def scanClipboard():
    img = ImageGrab.grabclipboard()
    if img == None:
        return None
    decoded = decode(img)
    for obj in decoded:
        if obj.type == "QRCODE":
            url = obj.data.decode("utf-8")
            parsed = urlparse(url)
            path = unquote(parsed.path[1:]) #remove ' / '
            params = parse_qs(parsed.query)
            entry = entry2fa(
                type=parsed.netloc,
                title=path,
                issuer=unquote(params.get("issuer",[path.split(":"),1])[0]),
                digits=int(unquote(params.get("digits",["6"])[0])),
                interval=int(unquote(params.get("period",["30"])[0])),
                secret=unquote(params.get("secret")[0])
            ) #use strings for integers else unquote error
            return entry

def dataWrite(entry:entry2fa,password:str):
    data = {}
    parts = encrypt(entry,password)
    keySalt = parts[0]
    nonce = parts[1]
    encryptedValue = parts[2]
    data["ciphertext"] = b64encode(encryptedValue).decode("utf-8")
    data["keySalt"] = b64encode(keySalt).decode("utf-8")
    data["nonce"] = b64encode(nonce).decode("utf-8")
    with open("lopAuth Data/data.json",'r') as f:
        curData = load(f)
    curData["data"].append(data)
    with open("lopAuth Data/tempdata.json",'w') as f:
        dump(curData,f,indent=4)
    replace("lopAuth Data/tempdata.json","lopAuth Data/data.json")
    


from pyotp import TOTP
from pyotp.contrib.steam import Steam
def getOTP(entry: entry2fa) -> str:
    secret = entry.secret.replace(" ", "")  # allow spaced secrets e.g. cz9s f9ea etc
    if entry.type.upper() == "TOTP":
        return TOTP(secret,digits=entry.digits,interval=entry.interval,issuer=entry.issuer,name=entry.title).now()
    elif entry.type.upper() == "STEAM":
        return Steam(secret,name=entry.title,issuer=entry.issuer,interval=entry.interval).now()
    else:
        print("error of " + entry.type)

from os.path import join,abspath
import sys
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # running as PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = abspath(".")
    return join(base_path, relative_path)