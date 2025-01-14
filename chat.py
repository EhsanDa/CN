import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

class P2PChat:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Chat")

        # Chat window
        self.chat_display = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Input field
        self.input_field = tk.Entry(self.root)
        self.input_field.pack(fill=tk.X, padx=10, pady=10)

        # Send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.socket = None
        self.running = True

    def setup_chat(self, username, mode, host=None, port=None):
        # Store user details
        self.username = username
        self.mode = mode.lower()

        if self.mode == 'host':
            self.start_host(host,port)
        elif self.mode == 'join' and host and port:
            self.start_client(host, port)
        else:
            self.append_message("Invalid mode or missing host/port. Please restart the program.")

    def start_host(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.socket.listen(1)
        self.append_message("Hosting on port 9086... Waiting for a connection.")
        
        threading.Thread(target=self.accept_connection).start()

    def accept_connection(self):
        conn, addr = self.socket.accept()
        self.append_message(f"Connected by {addr}")
        self.conn = conn
        threading.Thread(target=self.receive_messages, args=(conn,)).start()

    def start_client(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
            self.append_message("Connected to the host.")
            threading.Thread(target=self.receive_messages, args=(self.socket,)).start()
        except Exception as e:
            self.append_message(f"Connection failed: {e}")

    def receive_messages(self, conn):
        while self.running:
            try:
                message = conn.recv(1024).decode('utf-8')
                if message:
                    self.append_message(message)
            except Exception as e:
                self.append_message(f"Connection error: {e}")
                break

    def send_message(self):
        message = self.input_field.get()
        if message:
            self.append_message(f"{self.username}: {message}")
            if self.mode == 'host':
                self.conn.sendall(f"{self.username}: {message}".encode('utf-8'))
            elif self.mode == 'join':
                self.socket.sendall(f"{self.username}: {message}".encode('utf-8'))
            self.input_field.delete(0, tk.END)

    def append_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def on_close(self):
        self.running = False
        if self.socket:
            self.socket.close()
        self.root.destroy()

def start_chat(username, mode, host=None, port=None):
    root = tk.Tk()
    app = P2PChat(root)
    app.setup_chat(username, mode, host, port)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

