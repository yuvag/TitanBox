import pyDes

def decrypt(cipher,key):
    """This function will decrypt cipher using 3des from key"""
    decrypter = pyDes.triple_des(key, pad=None, padmode=pyDes.PAD_PKCS5)
    buf = decrypter.decrypt(cipher, pad=None, padmode=pyDes.PAD_PKCS5)
    return buf

def encrypt(buf,key):
    """This function will encrypt buffer using key using 3DES"""
    encrypter = pyDes.triple_des(key,pad = None,padmode = pyDes.PAD_PKCS5)
    buf = encrypter.encrypt(buf,pad=None,padmode=pyDes.PAD_PKCS5)
    return buf