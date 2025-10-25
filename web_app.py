import gradio as gr
import os
from core import (
    run_full_pipeline,
    run_from_less_json,
    run_test_generation_llm,
    run_test_generation_nlp,
    ModelType
)

def pipeline_interface(mode, file_input, model_type_str):
    model_type = getattr(ModelType, model_type_str)
    result = None
    if mode == "Full Pipeline (NLP to LESS to ESS to Tests)":
        result = run_full_pipeline(model_type)
    elif mode == "From LESS JSON (Validation, ESS, Tests)":
        if file_input is None:
            return {"error": "Please upload a LESS requirements JSON file."}
        # Save uploaded file to disk
        file_path = file_input.name
        result = run_from_less_json(file_path, model_type)
    elif mode == "Test Generation from LESS (LLM)":
        result = run_test_generation_llm(model_type)
    elif mode == "Test Generation from NLP (LLM)":
        result = run_test_generation_nlp(model_type)
    else:
        return {"error": "Invalid mode selected."}
    return result

modes = [
    "Full Pipeline (NLP to LESS to ESS to Tests)",
    "From LESS JSON (Validation, ESS, Tests)",
    "Test Generation from LESS (LLM)",
    "Test Generation from NLP (LLM)"
]

model_types = [m.name for m in ModelType]

def build_interface():
    with gr.Blocks() as demo:
        gr.Markdown("""
        # LESS Requirement Generation Web Interface
        Select a mode, upload your requirements (if needed), and run the pipeline.
        """)
        mode = gr.Dropdown(modes, label="Mode", value=modes[0])
        model_type = gr.Dropdown(model_types, label="Model Type", value="LLAMACPP")
        file_input = gr.File(label="Upload LESS Requirements JSON (for 'From LESS JSON' mode)", file_types=[".json"])
        run_btn = gr.Button("Run Pipeline")
        output = gr.JSON(label="Results (paths, errors, etc.)")
        run_btn.click(
            pipeline_interface,
            inputs=[mode, file_input, model_type],
            outputs=output
        )
    return demo

if __name__ == "__main__":
    demo = build_interface()
    demo.launch() 