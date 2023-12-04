import base64
from io import BytesIO
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from stg import SketchToGuess
from pts import PromptToSketch
import os
import sys

TEST_MODE = 'test_mode' in sys.argv

app = Flask(__name__)

if not TEST_MODE:
    print('Preparing SketchToGuess Model')
    stg = SketchToGuess()

    print('Preparing PromptToSketch Model')
    pts = PromptToSketch()

@app.route('/prompt_to_sketch', methods=['GET'])
def prompt_to_sketch():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    
    img = pts.sketch(prompt) if not TEST_MODE else Image.open('test_imgs/pizza.png')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({"success": "Image generated", "image": img_str}), 200

@app.route('/sketch_to_guess', methods=['POST'])
def sketch_to_guess():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.png'):
        filename = secure_filename(file.filename)
        try:
            image = Image.open(file)
        except Exception as e:
            return jsonify({"error": f"Error opening the image: {str(e)}"}), 400
        
        guess = stg.guess(image) if not TEST_MODE else 'pizza'

        return jsonify({"guess": guess}), 200
    else:
        return jsonify({"error": "Only PNG files are allowed"}), 400

if __name__ == '__main__':
    app.run(debug=False)
