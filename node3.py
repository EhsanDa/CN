import socket
import threading
import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
import os
from utils.common import *

router_key = ""


def encrypt_aes(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext


def decrypt_aes(key, ciphertext):
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(
        actual_ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext


def router_node(host, port, next_host=None, next_port=None, is_exit_node=False):
    def handle_client(conn, addr):
        data = conn.recv(4096)
        if not data:
            conn.close()
            return

        message = parse_message(data)
        print(
            f"Router {port}: Received {message['type']} from {message['sender']} targeting {message['receiver']}"
        )

        if message['receiver'] == "Router3":
            global router_key
            router_key = bytes.fromhex(message["payload"])

            response_payload = encrypt_aes(router_key, b"AES Key set successfully")
            response = create_message(
                "1", f"Router3", message['sender'], "set_key_response", response_payload.hex()
            )
            conn.sendall(response)

        else:
            print("Handling message forwarding")
            
            decrypted_payload = decrypt_aes(router_key, bytes.fromhex(message["payload"]))
            
            updated_payload = json.loads(decrypted_payload.decode())

            forwarded_message = create_message(
                message["version"],
                message["sender"],
                message["receiver"],
                message["type"],
                json.dumps(updated_payload)
            )
        
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_s:
                next_s.connect((next_host, next_port))
                next_s.sendall(forwarded_message)
                next_response = next_s.recv(4096)
                # Check if next response is valid
                if not next_response:
                    print("No response received from next node.")
                    return
                
                print("Response from server")
                # Ensure that the response data is in a valid format (e.g., str or byte-like)
                response_message = create_message(
                    "1",
                    "Server",
                    message["sender"],
                    "set_key_response",
                    encrypt_aes(router_key, next_response).hex()  # Convert to hex
                )

                conn.sendall(response_message)
                
                    
        conn.close()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Router listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


def start_router1():
    router_node("127.0.0.1", 8003, "127.0.0.1", 65432)


if __name__ == "__main__":
    start_router1()
