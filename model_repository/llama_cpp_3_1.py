import os
import subprocess
from llama_cpp import Llama

model_filename = "Meta-Llama-3.1-8B-Instruct-Q6_K.gguf"
_model_directory = r"D:\FOKUS\LESS_2\_LESS_OLD\src\LESS_Req_Generation\less_testgeneration\model_repository\llama3_1"

def load_llama_cpp_model(_local_model_path=""):
    # Define model repository and filename
    # repo_id = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"
    # Define the local directory where the model will be saved
    if _local_model_path is None or _local_model_path == "":
        model_directory = _model_directory
    else:
        model_directory = _local_model_path
        
    #os.makedirs(model_directory, exist_ok=True)

    # Check if the file already exists
    model_path = os.path.join(model_directory, model_filename)
    if not os.path.exists(model_path):
         raise Exception("Cannot find model")
    else:
        print(f"Model found at: {model_path}")

    # Check GPU availability
    try:
        # Attempt to run nvidia-smi
        subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        gpu_available = True
        print("GPU is available. Using GPU acceleration (if Nvidia driver is installed correctly).")
    except (FileNotFoundError, subprocess.CalledProcessError):
        gpu_available = False
        print("No GPU detected. Using CPU.")

    # Load model
    llm = Llama(
        model_path=model_path,
        chat_format="chatml",
        temperature=0.1,
        n_ctx=8192,
        max_tokens=8000,  # maximum: 128000 tokens for Llama 3.1
        seed=42,
        verbose=False,
        n_batch = 100,  # tokens processed in parallel, speed
        n_gpu_layers=-1 if gpu_available else 0,  # Enable GPU acceleration if GPU is available
    )
    print("Model loaded successfully.")
    
    return llm