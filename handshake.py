import socket
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from common import *

# Define the directory to save keys
KEYS_DIR = 'keys'

def generate_aes_key(key_size=256):
    if key_size not in [128, 192, 256]:
        raise ValueError("Key size must be 128, 192, or 256 bits")
    return os.urandom(key_size // 8)

def encrypt_aes(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext

def decrypt_aes(key, ciphertext):
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext

def create_keys_directory():
    """ Create the keys directory if it doesn't exist. """
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

def save_key_to_file(key, filename):
    filepath = os.path.join(KEYS_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(key)
    print(f"Saved key to {filepath}")

def handshake():
    # Create the keys directory
    create_keys_directory()

    key1 = generate_aes_key()
    key2 = generate_aes_key()
    key3 = generate_aes_key()
    print(f"Router key 1 {key1}")
    print(f"Router key 2 {key2}")
    print(f"Router key 3 {key3}")

    # Save keys to files in the 'keys' directory
    save_key_to_file(key1, "key1.bin")
    save_key_to_file(key2, "key2.bin")
    save_key_to_file(key3, "key3.bin")

    # Connection 1: Send key1 to Router1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
        s1.connect(("127.0.0.1", 8001))
        print(key1.hex())
        message = create_message("1", "Client", "Router1", "set_key", key1.hex())
        s1.sendall(message)
        print("Sent client private key to Router1.")
        response = s1.recv(4096)
        response_message = parse_message(response)
        encrypted_payload = bytes.fromhex(response_message['payload'])
        decrypted_payload = decrypt_aes(key1, encrypted_payload)
        print(decrypted_payload)
        print(f"Response from Router1: {response_message}")

    # Connection 2: Send key2 to Router2
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect(("127.0.0.1", 8001))
        print(f"Router2 Key: {key2.hex()}")
        
        # Encrypt Router2's key with Router1's key
        encrypted_payload = encrypt_aes(key1, key2)
        message = create_message("1", "Client", "Router2", "set_key", encrypted_payload.hex())
        s2.sendall(message)
        print("Sent Router2 key encrypted with Router1 key.")
        
        response = s2.recv(4096)
        response_message = parse_message(response)
        print(response_message)
        
        print(response_message['payload'])
        print(bytes.fromhex(response_message['payload']))
        # Decrypt with Router1's key
        encrypted_with_router2_key = decrypt_aes(key1, bytes.fromhex(response_message['payload']))
        print("Decrypted with Router1's key.")

        # Decrypt the result with Router2's key
        final_response = decrypt_aes(key2, encrypted_with_router2_key)
        print("Final Response:", final_response.decode('utf-8'))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s3:
        s3.connect(("127.0.0.1", 8001))
        print(f"Router3 Key: {key3.hex()}")
        
        # Encrypt Router3's key with Router1's key
        encrypted_payload = encrypt_aes(key2, key3)
        encrypted_payload2 = encrypt_aes(key1, encrypted_payload)
        message = create_message("1", "Client", "Router3", "set_key", encrypted_payload2.hex())
        s3.sendall(message)
        print("Sent Router3 key")
        
        response = s3.recv(4096)
        response_message = parse_message(response)
        print(response_message)
        
        print(response_message['payload'])
        print(bytes.fromhex(response_message['payload']))
        # Decrypt with Router1's key
        encrypted_with_router2_key = decrypt_aes(key1, bytes.fromhex(response_message['payload']))
        print("Decrypted with Router1's key.")

        # Decrypt the result with Router2's key
        final_response = decrypt_aes(key2, encrypted_with_router2_key)
        final_response = decrypt_aes(key3, final_response)
        print("Final Response:", final_response.decode('utf-8'))