from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import gradio as gr


device = "cuda:0"


model_id = "unsloth/Phi-3-medium-4k-instruct-bnb-4bit"
#ref: https://colab.research.google.com/drive/1hhdhBa1j_hsymiW9m-WzxQtgqTH_NHqi?usp=sharing#scrollTo=QmUBVEnvCDJv
"""
phi-3 is SLM from microsoft with performance equ to GPT 3.5
phi-3-small (7B parameters), and phi-3-medium (14B parameters). 
more: https://kili-technology.com/large-language-models-llms/what-can-we-learn-from-microsoft-phi-3-s-training-process#6
https://export.arxiv.org/abs/2404.14219
"""

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map=device,  # Automatically assign layers to GPU
    load_in_4bit=True
)

def generate_response(prompt):
    # get inputs
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    # gen output based on input
    outputs = model.generate(inputs["input_ids"])

    # final response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #need to check endoftoken since model was sometimes giving more info than asked
    response = response.replace("<|endoftext|>", "").strip()
    return response

# Gradio interface
interface = gr.Interface(
    fn=generate_response,  
    inputs=gr.Textbox(lines=5, placeholder="Enter your prompt here..."),  
    outputs=gr.Textbox(lines=10, placeholder="The model's response will appear here..."),  
    title="LESS requirement.",
    description="Model: unsloth/Phi-3-medium-4k-instruct-bnb-4bit."
)

interface.launch()