import secrets

key = secrets.token_bytes(16)  # Gera uma chave de 16 bytes (128 bits) para seu sistema de criptografia
print(f"Chave AES gerada: {key.hex()}")
