import base64
from io import BytesIO
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import os
# from stg import SketchToGuess
# from pts import PromptToSketch
import sys
import random

load_dotenv()

TEST_MODE = 'test_mode' in sys.argv
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
print(OPEN_AI_KEY)

app = Flask(__name__)

if not TEST_MODE:
    print('Preparing SketchToGuess Model')
    stg = SketchToGuess()

    print('Preparing PromptToSketch Model')
    pts = PromptToSketch()
    
@app.route('/choose_prompt', methods=['GET'])
def choose_prompt():
    prompts = request.args.getlist('prompts')

    if not prompts or len(prompts) != 3:
        return jsonify({"error": "3 prompts required"}), 400

    if OPEN_AI_KEY and not TEST_MODE:
        client = OpenAI(api_key=OPEN_AI_KEY)
        msg = f'From a list of 3 items, return in a JSON key "selection", the simplist item to draw out of the 3 choices. List: {str(prompts)}'
        choice = ""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format = { "type": "json_object" },
                messages=[
                    {"role": "system", "content": "You can only generate and output JSON for all messages."},
                    {"role": "user", "content": msg}
                ]
            )

            choice = json.loads(response.choices[0].message.content).get('selection')
        except Exception as error:
            print(f'Choosing randomly: {error}')
            choice = random.choice(prompts)
    else:
        print('No OpenAI key or in Test Mode. Reverting to random selection.')
        choice = random.choice(prompts)
    
    return jsonify({"success": "Prompt selected", "prompt": choice}), 200

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
