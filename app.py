from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
from vision_tools import (
    describe_image,
    ask_about_image,
    reason_from_description,
    multi_image_compare,
    conversational_vision_agent,
    describe_and_draw
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'mode' not in request.form:
            return jsonify({'error': 'Mode is required'}), 400

        mode = request.form['mode']
        question = request.form.get('question', '')

        if mode == 'compare':
            # 從單一 input name="file" 拿多張圖
            files = request.files.getlist("file")
            if len(files) < 2:
                return jsonify({'error': 'Please upload both Image A and Image B.'}), 400

            images = [
                Image.open(io.BytesIO(files[0].read())).convert("RGB"),
                Image.open(io.BytesIO(files[1].read())).convert("RGB")
            ]
            result = multi_image_compare(images, task=question or "Compare these images.")

        else:
            if 'file' not in request.files:
                return jsonify({'error': 'Image is required'}), 400

            file = request.files['file']
            image = Image.open(io.BytesIO(file.read())).convert("RGB")

            if mode == 'describe':
                result = describe_image(image, style='default')
            elif mode == 'analyze':
                result = describe_image(image, style='analyze')
            elif mode == 'creative':
                result = describe_image(image, style='creative')
            elif mode == 'ask':
                result = ask_about_image(image, question)
            elif mode == 'reason':
                desc = describe_image(image)
                result = reason_from_description(desc, question)
            elif mode == 'describe_and_draw':
                result = describe_and_draw(image)  # returns dict
                return jsonify(result)
            elif mode == 'conversational':
                question = question or "What can you tell me about this image?"
                result = conversational_vision_agent(image, messages=[
                    {"role": "user", "content": [{"type": "text", "text": question}]}
                ])
            else:
                result = "Unknown mode."

        return jsonify({'result': result})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
