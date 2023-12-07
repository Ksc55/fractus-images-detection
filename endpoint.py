from flask import Flask, request, jsonify
import os
import subprocess
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

def get_similarity_score(image_path1, image_path2):
    try:
        result = subprocess.check_output(["python", "similarity_script.py", image_path1, image_path2], text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return str(e)

def download_and_convert_image_from_ipfs(cid, output_path):
    ipfs_gateway_url = f"https://ipfs.io/ipfs/{cid}"
    print(f"Downloading and converting image from IPFS: {ipfs_gateway_url}")
    
    try:
        response = requests.get(ipfs_gateway_url)
        img = Image.open(BytesIO(response.content))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the image as JPG
        img.convert("RGB").save(output_path, "JPEG")
        
        print(f"Image downloaded and converted successfully to: {output_path}")
    except Exception as e:
        print(f"Error downloading/convert image from IPFS: {e}")

@app.route('/run-similarity', methods=['POST'])
def run_similarity():
    data = request.get_json()
    python_script_path = "similarity_script.py"

    for key, cid in data.items():
        image_path = f'./content/{key}.jpg'
        download_and_convert_image_from_ipfs(cid, image_path)

    try:
        result = get_similarity_score('./content/1.jpg', './content/2.jpg')
        return jsonify(result), 200
    except Exception as e:
        print(f"Error running similarity script: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    port = 3000
    app.run(host='0.0.0.0', port=port)
