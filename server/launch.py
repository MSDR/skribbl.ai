from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from stg import SketchToGuess
import os

app = Flask(__name__)
print('Preparing SketchToGuess Model')
stg = SketchToGuess()

@app.route('/prompt_to_sketch', methods=['GET'])
def prompt_to_sketch():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    
    # Generate and return image here
    
    return jsonify({"success": ""}), 200

@app.route('/sketch_to_guess', methods=['POST'])
def sketch_to_guess():
    print('Recieved Request..')
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
        
        guess = stg.guess(image)

        return jsonify({"guess": guess}), 200
    else:
        return jsonify({"error": "Only PNG files are allowed"}), 400

if __name__ == '__main__':
    app.run(debug=False)
