# VisionGPT: Visual Intelligence Toolkit

This is a project that demonstrates a multi-functional visual intelligence tool powered by OpenAI's GPT-4o.  
It allows users to describe, analyze, reason about, and compare images through a simple web interface.

![Demo](demo_img.png)

---

## Features

- **Image Description** – One-sentence, analytical, or creative caption generation
- **Ask About Image** – Ask natural-language questions about image content (VQA-style)
- **Reason From Description** – Logical inference from visual scene
- **Compare Images** – Side-by-side image comparison with explanation
- **Describe and Draw** – Describe uploaded image and generate a new one with DALL·E 3
- **Conversational Agent** – Multimodal chatbot with image understanding
- **Referring Expression** – Identify regions from phrases (e.g., "the red box on the left")
- **Visual Entailment** – Judge if a textual hypothesis matches the image content
- **Sketch to Image** – Draw in browser (canvas) and generate a full image using ControlNet

---

## Input Modes

- **Image Upload** – Standard `.png` / `.jpg` image inputs
- **Canvas Sketching** – Draw directly in-browser using `<canvas>` for selected tasks

---

## Project Structure
```
VisionGPT/
├── app.py # Flask backend app
├── vision_tools.py # Core logic for image processing with GPT
├── templates/
│ └── index.html # Frontend interface
├── static/ # Optional assets (CSS/JS)
├── demo.png # Screenshot for README
```

## Built With

- Python + Flask – Backend server
- OpenAI GPT-4o – Multimodal image & text model
- DALL·E 3 – Image generation
- HTML / JS – Simple frontend interface

---

## Setup & Run

1. Install dependencies (via `pip`)
   ```bash
   pip install flask openai pillow python-dotenv```
   
2. Set your OpenAI API key

3. Run the Flask app
   ```
   python app.py
   ```

4. Open your browser and visit: `http://localhost:5000`
