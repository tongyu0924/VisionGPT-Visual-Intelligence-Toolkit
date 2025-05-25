from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
import base64
from vision_tools import (
    describe_image,
    ask_about_image,
    reason_from_description,
    multi_image_compare,
    conversational_vision_agent,
    describe_and_draw,
    referring_expression_localization,
    visual_entailment,
    sketch_to_image
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
                result = describe_and_draw(image)
                return jsonify(result)
            elif mode == 'conversational':
                question = question or "What can you tell me about this image?"
                result = conversational_vision_agent(image, messages=[
                    {"role": "user", "content": [{"type": "text", "text": question}]}
                ])
            elif mode == 'referring_expression':
                result = referring_expression_localization(image, question)
            elif mode == 'entailment':
                result = visual_entailment(image, question)
            elif mode == 'sketch_to_image':
                try:
                    prompt = question or "A sketch-based drawing"
                    result_image = sketch_to_image(image, prompt)
                    buffered = io.BytesIO()
                    result_image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    return jsonify({
                        "description": prompt,
                        "image_url": f"data:image/png;base64,{img_base64}"
                    })
                except Exception as e:
                    print("sketch_to_image error:", e)
                    return jsonify({"error": str(e)})

            else:
                result = "Unknown mode."

        return jsonify({'result': result})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

