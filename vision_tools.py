# vision_tools.py
import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
import openai

# os.environ["OPENAI_API_KEY"] = "SET_YOUR_OPENAI_API_KEY"
# client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = openai.OpenAI(api_key=api_key)

def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def describe_image(image, style="default"):
    style_prompts = {
        "default": "Describe this image in one sentence.",
        "analyze": "Analyze the objects and composition in this image in detail.",
        "creative": "Describe this image as if you're writing a scene in a novel."
    }
    prompt = style_prompts.get(style, style_prompts["default"])
    base64_image = image_to_base64(image)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]}
        ]
    )
    return response.choices[0].message.content.strip()

def ask_about_image(image, question):
    base64_image = image_to_base64(image)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]}
        ]
    )
    return response.choices[0].message.content.strip()

def reason_from_description(description, question):
    prompt = (
        "Given the image description:\n"
        f"{description}\n"
        "Answer the following question using step-by-step reasoning:\n"
        f"{question}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def multi_image_compare(images, task="Compare the following images."):
    contents = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_to_base64(img)}"}}
        for img in images
    ]
    contents.insert(0, {"type": "text", "text": task})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": contents}]
    )
    return response.choices[0].message.content.strip()

def conversational_vision_agent(image: Image.Image, messages: list[dict]):
    image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_to_base64(image)}"}}
    if not any("image_url" in msg["content"][0] for msg in messages):
        messages[0]["content"].append(image_content)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def describe_and_draw(image: Image.Image):
    description = describe_image(image)
    dalle_response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1024x1024",
        n=1
    )
    return {
        "description": description,
        "image_url": dalle_response.data[0].url
    }
