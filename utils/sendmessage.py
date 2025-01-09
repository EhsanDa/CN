import socket
from common import *
from keyReader import *
import time

def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect(("127.0.0.1", 8001))
        key1 = return_key(1)
        key2 = return_key(2)
        key3 = return_key(3)
        
        if isinstance(message, str):
            message = message.encode() 
        print(message)
        # Encrypt Router2's key with Router1's key
        encrypted_payload1 = encrypt_aes(key3, message)
        encrypted_payload2 = encrypt_aes(key2, encrypted_payload1)
        encrypted_payload3 = encrypt_aes(key1, encrypted_payload2)
        message = create_message("1", "Client", "Server", "request", encrypted_payload3.hex())
        s2.sendall(message)
        print("Sent Server Message")
        
        response = s2.recv(4096)
        response_message = parse_message(response)
        # print(response_message)
        
        # print(response_message['payload'])
        # print(bytes.fromhex(response_message['payload']))
        # Decrypt with Router1's key
        encrypted_with_router2_key = decrypt_aes(key1, bytes.fromhex(response_message['payload']))
        # Decrypt the result with Router2's key
        final_response = decrypt_aes(key2, encrypted_with_router2_key)
        final_response = decrypt_aes(key3, final_response)
        print("Final Response:", final_response.decode('utf-8'))
        return final_response.decode('utf-8')
        


