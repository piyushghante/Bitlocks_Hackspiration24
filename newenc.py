from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image
import streamlit as st
import os
import requests
from io import BytesIO

st.set_page_config(
    page_title="BitLocks-Decryption",
    page_icon="🥶",
    layout="centered",
)
st.title("Decrypt File")

key = b'\xbf\x1b\xb3O\x8fB\x88e\x04\xea\xfb\xcd{.\xa9\xdc<\xef\xeb\xb9\x08\x10\xd3\x18\x92\x0f\xb6\x80\xe1 <V'

def retrieve_file_from_ipfs(ipfs_link):
    response = requests.get(ipfs_link)
    if response.status_code == 200:
        return response.content
    else:
        return None

def image_to_data(image_path):
    img = Image.open(image_path).convert("L")
    width, height = img.size
    binary_str = ""
    for i in range(height):
        for j in range(width):
            pixel_value = img.getpixel((j, i))
            binary_str += "1" if pixel_value < 128 else "0"
    binary_data = bytes(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    return binary_data

def decrypt_image(encrypted_image_path, key, iv, output_file_path):
    encrypted_message = image_to_data(encrypted_image_path)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    decrypted_message = cipher.decrypt(encrypted_message)
    unpadded_message = pad(decrypted_message, AES.block_size)
    with open(output_file_path, 'wb') as f:
        f.write(unpadded_message)

key2 = st.text_input("Enter Key")
iv = b'P\x05\x95\xac\xf5\x88\x9c\x1a\x89\x94 ^\x92i\xc8\xbc'
ipfs_link = st.text_input("Enter IPFS link")

if st.button("Fetch File from IPFS"):
    if ipfs_link:
        file_content = retrieve_file_from_ipfs(ipfs_link)
        if file_content:
            img = Image.open(BytesIO(file_content))
            img.save("retrieved_file.png", "PNG")
            st.download_button(
                label="Download IPFS File (PNG)",
                data=open("retrieved_file.png", "rb").read(),
                file_name="retrieved_file.png",
                mime="image/png"
            )
        else:
            st.write("Failed to retrieve file from IPFS. Please check the IPFS link.")
    else:
        st.write("Please enter the IPFS link.")

output_file_path = 'Cell6.txt'

uploaded_file = st.file_uploader("Drag and drop an image here", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    decrypt_image(uploaded_file, key, iv, output_file_path)
else:
    st.write("Drag and drop an image file to decrypt.")

with open("Cell6.txt", "rb") as input_file, open("process.txt", "w") as output_file:
    input_bytes = input_file.read()
    input_str = input_bytes.decode("utf-8", errors="ignore")
    filtered_str = ''.join(c for c in input_str if c in {'0', '1'})
    output_file.write(filtered_str)

binary_file_path = "process.txt"

with open(binary_file_path, "r") as f:
    binary_string = f.read()

binary_data = bytearray(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))

header_size = 4
extension_size = int.from_bytes(binary_data[:header_size], byteorder='big')
try:
    original_file_ext = binary_data[header_size:header_size+extension_size].decode("utf-8")
except UnicodeDecodeError:
    st.write("Error decoding file extension. Make sure the data is valid.")
    original_file_ext = ".bin"

if '\0' in original_file_ext:
    original_file_ext = ".bin"

original_data = binary_data[header_size+extension_size:]

with open("example3" + original_file_ext, "wb") as f:
    f.write(original_data)

def app():
    st.download_button(
        label="Download",
        data=bytes(original_data),
        file_name="example3" + original_file_ext,
        mime="application/octet-stream"
    )

with open("Cell6.txt", "w") as f:
    f.truncate(0)

with open("process.txt", "w") as f:
    f.truncate(0)

if __name__ == "__main__":
    app()
