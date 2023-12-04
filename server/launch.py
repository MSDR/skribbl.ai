from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/prompt_to_sketch', methods=['GET'])
def prompt_to_sketch():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    
    # Generate and return image here
    
    return jsonify({"success": ""}), 200

@app.route('/sketch_to_prompt', methods=['POST'])
def sketch_to_prompt():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.png'):
        filename = secure_filename(file.filename)
        
        # Generate prompt and return

        return jsonify({"prompt": "Something"}), 200
    else:
        return jsonify({"error": "Only PNG files are allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
