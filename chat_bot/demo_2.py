from llama_cpp import Llama
import llama_cpp
import gradio as gr
import subprocess

# Define the model path
model_path = r"D:\FOKUS\Projects\AKKA\most_recent\akka_usc_integrations\models\Meta-Llama-3-8B-Instruct.Q8_0.gguf"
"""
https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/blob/main/Meta-Llama-3-8B-Instruct-Q8_0.gguf
april 2024
"""

def load_llama_model():
    """Loads the Llama model and checks if GPU is available."""
    try:
        subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        gpu_available = True
        print("GPU is available. Using GPU acceleration.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        gpu_available = False
        print("No GPU detected. Using CPU.")
    #explicitely chek if llama cpp is using GPU
    print(llama_cpp.LLAMA_CUBLAS)

    # Load the model
    llm = Llama(
        model_path=model_path,
        chat_format="chatml",
        temperature=0.1,
        n_ctx=2000,
        max_tokens=2500,
        seed=42,
        verbose=False,
        n_batch=100,
        n_gpu_layers=-1 if gpu_available else 0,  # Enable GPU if available
    )

    print("Model loaded successfully.")
    return llm

# Load the model
model = load_llama_model()

def generate_response(prompt):
    """Generates a response using the loaded Llama model."""
    if not prompt.strip():
        return "Please enter a valid prompt."
    
    response = model.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )
    
    return response["choices"][0]["message"]["content"].strip()

# Gradio Interface
interface = gr.Interface(
    fn=generate_response,
    inputs=gr.Textbox(lines=5, placeholder="Enter your prompt here..."),
    outputs=gr.Textbox(lines=10, placeholder="The model's response will appear here..."),
    title="LESS Requirement",
    description="Model: Meta-Llama-3-8B-Instruct."
)

# Launch the Gradio app
interface.launch()
