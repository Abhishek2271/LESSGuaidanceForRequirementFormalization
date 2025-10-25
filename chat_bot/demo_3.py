from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import gradio as gr
from huggingface_hub import login

access_token = "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"
login(access_token) 

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
"""
july llama 3.1 model
8B params
"""
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",  
    torch_dtype=torch.float16, 
    load_in_4bit=True  
)

def generate_response(prompt):
    """Generates a response using Llama 3.1 8B."""
    if not prompt.strip():
        return "Please enter a valid prompt."

    # Tokenize input
    print("device::::::::::::>", device)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Generate output
    outputs = model.generate(
        inputs["input_ids"],
        max_length=5000,  # Adjust max tokens for response length
        eos_token_id=None
    )

    # Decode output
    response = tokenizer.decode(outputs[0], skip_special_tokens=True, skip_prompt=True)
    
    # Ensure response is trimmed properly
    response = response.replace("<|endoftext|>", "").strip()
    
    return response

# Gradio interface
interface = gr.Interface(
    fn=generate_response,  
    inputs=gr.Textbox(lines=5, placeholder="Enter your prompt here..."),  
    outputs=gr.Textbox(lines=10, placeholder="The model's response will appear here..."),  
    title="Llama 3.1 8B",
    description="Model: Meta-Llama-3-8B-Instruct (4-bit optimized)."
)

# Launch the Gradio app
interface.launch()
