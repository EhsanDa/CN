import socket
import threading
import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
import os
from utils import common

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

        message = common.parse_message(data)
        print(
            f"Router {port}: Received {message['type']} from {message['sender']} targeting {message['receiver']}"
        )

        if message['receiver'] == "Router1":
            global router_key
            router_key = bytes.fromhex(message["payload"])

            # Encode the response payload as bytes
            response_payload = encrypt_aes(
                router_key, b"AES Key set successfully")
            response = common.create_message(
                "1", f"Router{port % 5000}", message['sender'], "set_key_response", response_payload.hex(
                )
            )
            conn.sendall(response)

        else:
            if next_host and next_port:
                # Decrypt the received payload with Router1's key
                decrypted_payload = decrypt_aes(
                    router_key, bytes.fromhex(message["payload"]))

                # Create a forwarded message with the original sender and receiver
                forwarded_message = common.create_message(
                    message["version"],  # Keep the original version
                    message["sender"],  # Preserve the original sender
                    message["receiver"],  # Preserve the original receiver
                    message["type"],  # Keep the original message type
                    decrypted_payload.hex()  # Use the decrypted payload
                )

                # Forward the message to the next router
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_s:
                    next_s.connect((next_host, next_port))
                    next_s.sendall(forwarded_message)
                    next_response = next_s.recv(4096)
                    next_response = common.parse_message(next_response)
                    re_encrypted_payload = encrypt_aes(
                        router_key, bytes.fromhex(next_response["payload"]))

                    # Create a new message with the original sender and receiver
                    response_message = common.create_message(
                        "1",  # Version
                        next_response["sender"],  # Original sender (Router2)
                        next_response["receiver"],  # Original receiver (Client)
                        "server_response",  # Message type
                        re_encrypted_payload.hex()  # Re-encrypted payload
                    )
                    # Send the re-encrypted response to the client
                    conn.sendall(response_message)
        conn.close()

    # Start server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Router listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


def start_router1():
    router_node("127.0.0.1", 8001, "127.0.0.1", 8002)


if __name__ == "__main__":
    start_router1()