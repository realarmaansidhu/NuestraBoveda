
import os
from cryptography.fernet import Fernet
import glob

# 1. Generate or Load Key
KEY_FILE = "secret.key"

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"Generated new key: {key.decode()}")
        print("IMPORTANT: Add this key to your .env file as VAULT_KEY='...'")
        return key

key = load_key()
cipher = Fernet(key)

# 2. Files to Encrypt
files_to_encrypt = []

# Chat History
if os.path.exists("whatsapp_chat.txt"):
    files_to_encrypt.append("whatsapp_chat.txt")

# Asset Files (Images, Videos, JSON)
# Recursive search in assets folder
for root, dirs, files in os.walk("assets"):
    for file in files:
        if file.endswith((".jpg", ".jpeg", ".png", ".mp4", ".mov", ".json", ".txt")):
            # Skip already encrypted files and example files
            if not file.endswith(".enc") and "example" not in file:
                 files_to_encrypt.append(os.path.join(root, file))

# 3. Encrypt Loop
print(f"Found {len(files_to_encrypt)} files to encrypt.")

for file_path in files_to_encrypt:
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        encrypted_data = cipher.encrypt(data)
        
        enc_file_path = file_path + ".enc"
        with open(enc_file_path, "wb") as f:
            f.write(encrypted_data)
            
        print(f"Encrypted: {file_path} -> {enc_file_path}")
        
    except Exception as e:
        print(f"Error encrypting {file_path}: {e}")

print("\nDONE. You can now commit the .enc files.")
print("Run: git add assets/*.enc *.enc")
