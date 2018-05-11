import hashlib
import pyDes

BLOCKSIZE = 800


def decrypt(cipher,key):
    """This function will decrypt cipher using 3des from key"""
    decrypter = pyDes.triple_des(key, pad=None, padmode=pyDes.PAD_PKCS5)
    buf = decrypter.decrypt(cipher, pad=None, padmode=pyDes.PAD_PKCS5)
    return buf

def generate_file_tag(filename):
    """This function will generate tag for whole file"""
    hasher = hashlib.md5()
    with open(filename,'rb') as file_handle:
        buf = file_handle.read(BLOCKSIZE)
        while(len(buf) > 0):
            hasher.update(buf)
            buf = file_handle.read(BLOCKSIZE)
    return hasher.hexdigest()

def generate_block_tag(buf):
    """This function will generate tag for a block"""
    hasher = hashlib.md5()
    hasher.update(buf)
    return hasher.hexdigest()

def generate_key(buf):
    """This function will derive key from block (sha256)"""
    hasher = hashlib.sha256()
    hasher.update(buf)
    key = hasher.digest()
    key = key[0:16]
    if(len(key) < 16):
        required_length = 16 - len(key)
        key = key + "0"*required_length
    return key


def encrypt(buf,key):
    """This function will encrypt buffer using key using 3DES"""
    encrypter = pyDes.triple_des(key,pad = None,padmode = pyDes.PAD_PKCS5)
    buf = encrypter.encrypt(buf,pad=None,padmode=pyDes.PAD_PKCS5)
    return buf

if __name__ == "__main__":
    print(generate_file_tag("Encryption.py"))
    print(generate_key('551996'))
