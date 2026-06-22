import os
import gradio as gr
from fastapi import FastAPI
from app.main import app as fastapi_app

# Create a clean dashboard UI for Hugging Face Spaces
with gr.Blocks(title="SignDecoder API Dashboard") as demo:
    gr.Markdown("# 🚀 SignDecoder API Backend")
    gr.Markdown("This Hugging Face Space hosts the FastAPI backend for the **SignDecoder** application.")
    
    gr.Markdown("### 🔍 Live API Status")
    with gr.Row():
        status_box = gr.Textbox(value="🟢 Running", label="API Status", interactive=False)
        model_box = gr.Textbox(value="FLAN-T5-small + LoRA adapter", label="Model Architecture", interactive=False)
        device_box = gr.Textbox(value="CPU", label="Hardware Accelerator", interactive=False)

    gr.Markdown("### 📡 Available Endpoints:")
    gr.Markdown(
        """
        - **POST `/api/v1/translate`**
          - Translate English text to Indian Sign Language (ISL) glosses and emoji card sequences.
        - **POST `/api/v1/translate/reverse`**
          - Decode a sequence of sign language emojis back into grammatically correct English.
        - **GET `/health`**
          - Check API health status.
        """
    )
    
    gr.Markdown("---")
    gr.Markdown("*Note: The frontend client communicates directly with this Space via the public API URL.*")

# Mount the Gradio UI onto the FastAPI app
# This makes the app run on Hugging Face Spaces Gradio SDK without Docker
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
