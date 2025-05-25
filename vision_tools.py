# vision_tools.py
import os
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import openai

_pipe = None
_controlnet = None

# OpenAI API 
api_key = os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY_HERE"
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# === Basic GPT-Vision Tasks ===
def describe_image(image, style="default"):
    prompt_map = {
        "default": "Describe this image in one sentence.",
        "analyze": "Analyze the objects and composition in this image in detail.",
        "creative": "Describe this image as if you're writing a scene in a novel."
    }
    prompt = prompt_map.get(style, prompt_map["default"])
    base64_img = image_to_base64(image)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()

def ask_about_image(image, question):
    base64_img = image_to_base64(image)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()

def reason_from_description(description, question):
    prompt = f"Given the image description:\n{description}\nAnswer step by step:\n{question}"
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def multi_image_compare(images, task="Compare the following images."):
    contents = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_to_base64(img)}"}} for img in images]
    contents.insert(0, {"type": "text", "text": task})
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": contents}]
    )
    return response.choices[0].message.content.strip()

def conversational_vision_agent(image: Image.Image, messages: list[dict]):
    image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_to_base64(image)}"}}
    if not any("image_url" in msg["content"][0] for msg in messages):
        messages[0]["content"].append(image_content)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content.strip()

def describe_and_draw(image: Image.Image):
    description = describe_image(image)
    dalle_response = client.images.generate(
        model="dall-e-3", prompt=description, size="1024x1024", n=1
    )
    return {"description": description, "image_url": dalle_response.data[0].url}

def referring_expression_localization(image: Image.Image, expression: str):
    base64_img = image_to_base64(image)
    prompt = f"In the image, identify the object described as: '{expression}'"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()

def visual_entailment(image: Image.Image, hypothesis: str):
    base64_img = image_to_base64(image)
    prompt = f"Does the statement match the image? Statement: '{hypothesis}' Answer True or False."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()

# === Sketch-to-Image ===
def sketch_to_image(sketch_image: Image.Image, prompt: str) -> Image.Image:
    global _pipe, _controlnet
    if _pipe is None:
        print("Loading ControlNet + SD pipeline on CPU...")
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
        import torch

        _controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-scribble", torch_dtype=torch.float32
        )
        _pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", controlnet=_controlnet, torch_dtype=torch.float32
        ).to("cpu")
        print("Pipeline loaded.")

    # 草圖預處理
    sketch_image = sketch_image.convert("L").resize((512, 512))
    sketch_array = np.array(sketch_image)
    sketch_array = cv2.Canny(sketch_array, 100, 200)
    sketch_array = cv2.cvtColor(sketch_array, cv2.COLOR_GRAY2RGB)
    processed = Image.fromarray(sketch_array)

    result = _pipe(prompt=prompt, image=processed, num_inference_steps=30).images[0]
    return result

