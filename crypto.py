# pip install pycryptodome

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# Generate RSA key pair
key = RSA.generate(2048)

# Get public and private keys
private_key = key.export_key()
public_key = key.publickey().export_key()

# Encrypt string using public key
cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
message = "Hello, world!"
encrypted_message = cipher.encrypt(message.encode())

# Decrypt string using private key
cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
decrypted_message = cipher.decrypt(encrypted_message)

# Print results
print("Public key:", public_key.decode(), sep="\n")
print("Private key:", private_key.decode(), sep="\n")
print("Original message:", message)
print("Encrypted message:", encrypted_message.hex())
print("Decrypted message:", decrypted_message.decode())

# base64str = "P9S9Hrd1GzCeQ8aolX39cDu2K/rdJLISVNeEki3yYDthZLFcR/SxLQ/7C743aOWtNblxAk4Hhv7yGFdePIheUZt0vQQxJGvAOfXnE6aSdBYl9IJaJKsVHQQTIeYbNxX/lBNtXxjU8nK0pkumrkPk3h9vYHOgTeeLNvCrFY+oP8CtXeVs/kqFDMz1s2+cjFmwvWnS9WnHZDMZ58BJ8nj1jeSQWCeNALJknWleJBwRbaSXxaHzVvjXzmPFjwm/3PElwHI77Zj3mijbclZbC3NEs5xTYXJpt/Z8ALjEOt3V3d+ZjXLB/FHAWoUZUpf1oB4eYukiI7XWRwKkx5Wyl2/dDQ=="
# encrypted_bytes = base64.b64decode(base64str)
# bytes = cipher.decrypt(encrypted_bytes)
# decrypted_message = bytes.decode()
# # bytes to string
# print(decrypted_message)
