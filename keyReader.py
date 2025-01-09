import os

# Define the directory to save keys
KEYS_DIR = 'keys'

def read_key_from_file(filename):
    """Read a key from a specified file and return it as bytes."""
    filepath = os.path.join(KEYS_DIR, filename)
    with open(filepath, 'rb') as f:  # Open the file in binary mode
        return f.read()  # Read the bytes directly

def read_keys():
    """Read all keys from the files in the 'keys' directory."""
    key1 = read_key_from_file("key1.bin")
    key2 = read_key_from_file("key2.bin")
    key3 = read_key_from_file("key3.bin")
    return key1, key2, key3

# Example usage
def return_key(number):
    key1, key2, key3 = read_keys()
    if number == 1:
        return key1
    if number == 2:
        return key2
    if number == 3:
        return key3