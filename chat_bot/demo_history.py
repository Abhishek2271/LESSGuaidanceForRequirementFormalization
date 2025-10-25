from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("unsloth/Phi-3-medium-4k-instruct-bnb-4bit")
device = "cuda:0"
# Load the model with 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Phi-3-medium-4k-instruct-bnb-4bit",
    device_map=device,  # Automatically assign layers to GPU
    load_in_4bit=True
)

history = []

def update_history(user_input, bot_response, history):
    history.append(f"User: {user_input}")
    history.append(f"Chatbot: {bot_response}")
    return history


def generate_response_with_history(prompt, history, max_history_length=5):
    # Limit history to the last N exchanges
    context = "\n".join(history[-max_history_length * 2:])  # Two entries per exchange
    full_prompt = f"{context}\nUser: {prompt}\nChatbot:"
    
    # Tokenize and generate response
    inputs = tokenizer(full_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(inputs["input_ids"], temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.replace("<|endoftext|>", "").strip()
    return response

def chatbot(user_input):
    global history
    
    # Generate a response with history
    bot_response = generate_response_with_history(user_input, history)
    
    # Update history
    update_history(user_input, bot_response, history)
    
    return bot_response

import gradio as gr
# Gradio interface
interface = gr.Interface(
    fn=chatbot,
    inputs=gr.Textbox(lines=2, placeholder="Enter your message here..."),
    outputs=gr.Textbox(lines=5, placeholder="The bot's response will appear here..."),
    title="Chatbot with Memory",
    description="A chatbot that remembers recent conversation history."
)

# Launch the app
interface.launch()