import os
import subprocess
import json
import time
from enum import Enum
import re
import argparse

from model_repository.llama_cpp import load_llama_cpp_model
from model_repository.llama_cpp_4 import load_llama_cpp_model as load_llama_cpp_4_model
from model_repository.llama_cpp_3_1 import load_llama_cpp_model as load_llama_cpp_3_1_model 
from dynamic_validation.dynamic_validator import dynamicValidation
from generate_ess import generateEss
from test_generation.get_test import generate_testcases
from test_generation.get_test_zss_01 import generate_zss_testcases
from model_repository.deepseek import load_deepseek_model
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch

output_directory_global = "Results"
grammar_filelocation = "grammar/less.tx"
#specs_location = "grammar/dynamic_grammar.txt" FOR VAD case study
specs_location = r"D:\FOKUS\LESS_2\_LESS_OLD\src\LESS_Req_Generation\less_testgeneration\grammar\EGas\dynamic_grammar.txt" #FOR EGAS case study


class ModelType(Enum):
    LLAMA = "llama"
    LLAMACPP = "llamacpp"
    LLAMACPP4 = "llamacpp4"
    LLAMACPP31 = "llamacpp31"
    PHI = "phi"
    GPT4o = "gpt4o"
    DeepSeek = "deepseek-7b-instruct"

#model_filename = "Meta-Llama-3-8B-Instruct.Q8_0.gguf"
model_filename = "meta-llama_Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00001-of-00002.gguf"
def ensure_directory_exists(directory):
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

#prompt_location = r"D:\FOKUS\LESS_2\_LESS_OLD\src\LESS_Req_Generation\less_testgeneration\prompts\prompt_13.txt" #FOR VAD case study
prompt_location = r"D:\FOKUS\LESS_2\SE_26\Results\requirement_generation\indirect_prompts\llama4\prompt_15.txt" #FOR EGAS case study
#prompt_location = r"D:\FOKUS\LESS\src\LESS_Req_Generation\less_testgeneration\prompts\old\prompt_7.txt"

test_prompt_location = r"D:\FOKUS\LESS_2\SE_26\Results\test_generation\less_test_generation\EGAS\3_llama4\prompt_5_test_gen_llama4.txt"
nlp_to_test =r"Results/logs/test_generation/2_nlp_to_test/prompt_nlp_test.txt"

def is_dict(input_data):
    """
    Check if input data is a dict or list of dict string.
    
    ARGS:
    ---
    input_data: input string or dict or list of dict  
    
    Returns:
    ---
    Bool: true if input_data is dict or a list of dict, false otherwise.    
    """
    if isinstance(input_data, dict): 
        return True
    elif isinstance(input_data, list) and all(isinstance(item, dict) for item in input_data): 
        return True
    return False

def count_tokens_with_llama(llm, text):
    """
    Uses the LlamaCpp model tokenizer to count tokens in the given text.
    
    Args:
    - llm: The loaded LlamaCpp model instance.
    - text (str): The input text to tokenize.
    
    Returns:
    - int: The number of tokens in the text.
    """
    tokens = llm.tokenize(text.encode("utf-8"), add_bos=True)  # Tokenizing the input text
    return len(tokens)

def create_prompt(llm, model_type):
        # Create the system prompt
    #system_prompt = f"""You are an expert in system that reads requirements in natural language and generates LESS formatted requirements."""
    system_prompt = """You are a helpful model that strictly outputs JSON-formatted LESS requirements. You must not provide any explanations or notes or extra text outside the JSON format."""
    prompt_text = ""
    with open(prompt_location, "r", encoding="utf-8") as file:
        prompt_text = file.read().strip()
    user_prompt = prompt_text
    
    if(model_type == ModelType.LLAMACPP):
        # Count tokens using the LlamaCpp model tokenizer
        system_tokens = count_tokens_with_llama(llm, system_prompt)
        user_tokens = count_tokens_with_llama(llm, user_prompt)
        total_tokens = system_tokens + user_tokens
        print(f"Token count:\n- System prompt: {system_tokens}\n- User prompt: {user_tokens}\n- Total: {total_tokens}")
    return system_prompt, user_prompt

def create_testcases_prompt(llm, prompt_location):
    # Create the system prompt
    #system_prompt = f"""You are an expert in system that reads requirements in natural language and generates LESS formatted requirements."""
    system_prompt = """You are a helpful model that strictly outputs JSON-formatted test cases like in few-shot examples below. You must not provide any explanations or notes or extra text outside the JSON format."""
    prompt_text = ""
    #with open(test_prompt_location, "r", encoding="utf-8") as file:
    with open(prompt_location, "r", encoding="utf-8") as file:
        prompt_text = file.read().strip()
    user_prompt = prompt_text
    
    # Count tokens using the LlamaCpp model tokenizer
    system_tokens = count_tokens_with_llama(llm, system_prompt)
    user_tokens = count_tokens_with_llama(llm, user_prompt)
    total_tokens = system_tokens + user_tokens

    print(f"Token count:\n- System prompt: {system_tokens}\n- User prompt: {user_tokens}\n- Total: {total_tokens}")

    return system_prompt, user_prompt


#def create_testcases_from_nlp_prompt(llm):
#    # Create the system prompt
#    #system_prompt = f"""You are an expert in system that reads requirements in natural language and generates LESS formatted requirements."""
#    system_prompt = """You are a helpful model that strictly outputs JSON-formatted test cases like in few-shot examples below. You must not provide any explanations or notes or extra text outside the JSON format."""
#    prompt_text = ""
#    with open(test_prompt_location, "r", encoding="utf-8") as file:
#        prompt_text = file.read().strip()
#    user_prompt = prompt_text
#    
#    # Count tokens using the LlamaCpp model tokenizer
#    system_tokens = count_tokens_with_llama(llm, system_prompt)
#    user_tokens = count_tokens_with_llama(llm, user_prompt)
#    total_tokens = system_tokens + user_tokens
#
#    print(f"Token count:\n- System prompt: {system_tokens}\n- User prompt: {user_tokens}\n- Total: {total_tokens}")
#
#    return system_prompt, user_prompt

def generate_less_req(llm, system_prompt, user_prompt, model_type, tokenizer=None):
    # Create the prompt
    if (model_type == ModelType.LLAMACPP or model_type == ModelType.LLAMACPP4 or model_type == ModelType.LLAMACPP31):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "nlp":  {"type": "string"},
                        "LESS": {"type": "string"},
                        },
                    }
                }
            

        # Measure the time taken for inference
        start_time = time.time()

        # Generate the response using the Llama model
        print("Generate response...")
        response = llm.create_chat_completion(
            messages=messages,
            #response_format=response_format,
            temperature=0.1,
            stop=["<|eot_id|>"]
        )
        print("prompt:", messages)
        end_time = time.time()

        # Calculate and print the time for inference
        elapsed_time = end_time - start_time
        print(f"Time for inference: {elapsed_time:.2f} seconds")

        # Print the usage details
        print(json.dumps(response['usage'], indent=2))

        # Print the content of the response
        content_str = response['choices'][0]['message']['content']
        print("complete model output::: ", content_str)
        #content = json.loads(content_str)
        #generated_model = json.dumps(content_str, indent=4)    
    elif (model_type == ModelType.DeepSeek):
        prompt = user_prompt #f"<|user|>\n{user_prompt}\n<|assistant|>"
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to("cuda")
        llm.generation_config = GenerationConfig.from_pretrained("deepseek-ai/deepseek-llm-7b-base")
        llm.generation_config.pad_token_id = llm.generation_config.eos_token_id
        # Count input tokens
        num_input_tokens = inputs.input_ids.shape[1]
        print(f"Number of input tokens: {num_input_tokens}")

        # Measure inference time
        start_time = time.time()

        print("Generating response...")
        with torch.no_grad():
            output = llm.generate(
                **inputs,
                max_new_tokens=4000,  # Limit output to prevent excessive generation
                temperature=0.6,  # Low temp for stable deterministic output
                #do_sample=False  # Greedy decoding for consistency
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time for inference: {elapsed_time:.2f} seconds")

        # Count output tokens
        num_output_tokens = output.shape[1] - num_input_tokens
        print(f"Number of output tokens: {num_output_tokens}")

        # Decode and print response
        content_str = tokenizer.decode(output[0], skip_special_tokens=True)
        print("Complete Model Output:\n", content_str)
    return content_str 


def save_generated_model(generated_model, model_type, output_filename_prefix = "OUTPUT"):
    
    #if json data is dict, convert it to string to write to file.
    #generated_model could be either a list of dict after validation (valid, invalid less) or could be json formatted string generated from the model
    if is_dict(generated_model):
        generated_model = json.dumps(generated_model, indent=4)
    # Truncate any appended note that is not part of the valid JSON.
    # Here we assume the note starts with "Note:" (case-insensitive).
    
    note_match = re.search(r'\bNote:', generated_model, re.IGNORECASE)
    if note_match:
        generated_model = generated_model[:note_match.start()].strip()
    ensure_directory_exists(output_directory_global)
    output_filename = f"{output_filename_prefix}_{model_type}.json"
    #output_path = os.path.join(output_directory, output_filename)
    output_path = os.path.join(output_directory_global, output_filename)
    
    # Save the generated model to the file
    with open(output_path, 'w', encoding='utf-8') as file:        
        file.write(generated_model)
    
    print(f"Generated requirements are saved to: {output_path}")
    return output_path

def get_less_requirements(model_type):
    #print("Create prompt...")
    #system_prompt, user_prompt = create_prompt()
    
    print("Load model...")
    if (model_type == ModelType.LLAMACPP):
        llm = load_llama_cpp_model()
        tokenizer = None
    elif (model_type == ModelType.LLAMACPP4):
        llm = load_llama_cpp_4_model()
        tokenizer = None
    elif (model_type == ModelType.LLAMACPP31):
        llm = load_llama_cpp_3_1_model()
        tokenizer = None
    elif (model_type == ModelType.DeepSeek):
        llm, tokenizer = load_deepseek_model()
    else:
        llm = None
        print("Model type not supported")
        return None
    print("Create prompt...")
    system_prompt, user_prompt = create_prompt(llm, model_type)
    
    print("Generate LESS requirements for NLP requirements...\n")
    generated_model = generate_less_req(llm, system_prompt, user_prompt, model_type, tokenizer)
    
    #cleanup
    if (model_type == ModelType.LLAMACPP):
        llm.close()
        del llm
    #return resutls
    return generated_model

def get_test_cases(model_type, prompt_location):    
    print("Load model...")
    if (model_type == ModelType.LLAMACPP):
        llm = load_llama_cpp_model()
    elif (model_type == ModelType.LLAMACPP4):
        llm = load_llama_cpp_4_model()
    elif (model_type == ModelType.LLAMACPP31):
        llm = load_llama_cpp_3_1_model()
    elif (model_type == ModelType.DeepSeek):
        llm = load_deepseek_model()
    else:
        llm = None
        print("Model type not supported")
        return None
    print("Create prompt...")
    system_prompt, user_prompt = create_testcases_prompt(llm, prompt_location)
    
    print("Generate test cases from the given LESS requirements...\n")
    generated_model = generate_less_req(llm, system_prompt, user_prompt, model_type, None)
    
    #cleanup
    llm.close()
    del llm
    #return resutls
    return generated_model

def validate_generated_model(generated_model, model_type):
    dm = dynamicValidation(generated_model, grammar_filelocation, specs_location)
    validaton_errors, correct_lines = dm.startValidation()
    # Print validation errors
    if validaton_errors:
        #print("Validation Errors:")
        #for error in validaton_errors:
        #    print(f"Line{error['Line_number']}, LESS: {error['LESS']}, Error: {error['Error']}")
        save_generated_model(validaton_errors, model_type, "Validation_Errors")
        
    if correct_lines:
        print
        #print("Correct Lines:")
        #for line in correct_lines:
        #    print(f"Line{line['Line_number']}, LESS: {line['LESS']}")
        save_generated_model(correct_lines, model_type, "Correct_Lines")
    return validaton_errors, correct_lines

# --- WEB INTERFACE WRAPPERS ---
def run_full_pipeline(model_type=ModelType.LLAMACPP or ModelType.LLAMACPP4 or ModelType.LLAMACPP31):
    generated_model = get_less_requirements(model_type)
    if generated_model is None:
        return {"error": "Error generating requirements. Check if given model is supported. If you are giving the requirements in json format, check the file."}
    output_path = save_generated_model(generated_model, model_type)
    validaton_errors, correct_lines = validate_generated_model(generated_model, model_type)
    ess_path = None
    testcases_itps_path = None
    testcases_zss_path = None
    if(len(correct_lines) > 0):
        new_specs_filename = "berlin_heart.ess"
        new_specs_filepath = os.path.join(output_directory_global, new_specs_filename)
        ess = generateEss(correct_lines, specs_location, new_specs_filepath)
        ess.get_save_ess()
        ess_path = new_specs_filepath
        test_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_IPTS.json")
        test_cases_ITPS = generate_testcases(grammar_filelocation, new_specs_filepath, test_json_fullpath)
        testcases_itps_path = test_json_fullpath
        test_zss_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_ZSS01.json")
        test_cases_ZSS = generate_zss_testcases(new_specs_filepath, test_zss_json_fullpath)
        testcases_zss_path = test_zss_json_fullpath
    return {
        "requirements_path": output_path,
        "validation_errors": validaton_errors,
        "correct_lines": correct_lines,
        "ess_path": ess_path,
        "testcases_itps_path": testcases_itps_path,
        "testcases_zss_path": testcases_zss_path
    }

def run_from_less_json(requirement_json_path, model_type=ModelType.LLAMACPP):
    try:
        with open(requirement_json_path, "r") as file:
            generated_model = json.dumps(json.load(file))
    except Exception as e:
        return {"error": f"Error reading the provided requirement file: {e}"}
    output_path = save_generated_model(generated_model, model_type)
    validaton_errors, correct_lines = validate_generated_model(generated_model, model_type)
    ess_path = None
    testcases_itps_path = None
    testcases_zss_path = None
    if(len(correct_lines) > 0):
        new_specs_filename = "berlin_heart.ess"
        new_specs_filepath = os.path.join(output_directory_global, new_specs_filename)
        ess = generateEss(correct_lines, specs_location, new_specs_filepath)
        ess.get_save_ess()
        ess_path = new_specs_filepath
        test_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_IPTS.json")
        test_cases_ITPS = generate_testcases(grammar_filelocation, new_specs_filepath, test_json_fullpath)
        testcases_itps_path = test_json_fullpath
        test_zss_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_ZSS01.json")
        test_cases_ZSS = generate_zss_testcases(new_specs_filepath, test_zss_json_fullpath)
        testcases_zss_path = test_zss_json_fullpath
    return {
        "requirements_path": output_path,
        "validation_errors": validaton_errors,
        "correct_lines": correct_lines,
        "ess_path": ess_path,
        "testcases_itps_path": testcases_itps_path,
        "testcases_zss_path": testcases_zss_path
    }

def run_test_generation_llm(model_type=ModelType.LLAMACPP):
    generated_model = get_test_cases(model_type, test_prompt_location)
    output_path = save_generated_model(generated_model, model_type)
    return {"testcases_path": output_path}

def run_test_generation_nlp(model_type=ModelType.LLAMACPP):
    generated_model = get_test_cases(model_type, nlp_to_test)
    output_path = save_generated_model(generated_model, model_type)
    return {"testcases_path": output_path}

def main():     
    """
    If *no* arguments are given:    \n
        Prompt with NLP Requiements -> LLM -> LESS Requirements -> ESS file -> Validation -> Correct LESS specs -> pyscripts -> Test Cases  \n
        1. the program will run in the default mode: This mode will use prompts in the /prompts to generate LESS requirements using given NLP requirements.   
        2. The requirements are then validated using lex grammar, correct and incorrect requirements are saved in separate files.  
        3. The correct requirements are then used to generate ESS file and test cases.  
        4. The generated test cases are saved in the Results folder.  
        
    If *-r ".json with less, NLP pair* argument is given:  \n
        LESS Requirements -> validation -> ESS file -> Test Cases  \n
        1. The program will run in the "requirement parsing" mode  
        2. This mode will directly use the LESS requirements provided after -r argument to generate ESS file and test cases.   
        3. The given requirements are validated using lex grammar, correct and incorrect requirements are saved in separate files.  
        4. The correct requirements are then used to generate ESS file and test cases.  
        5. The generated test cases are saved in the Results folder. 
         
    If *-t* argument is given: \n
        Prompt with LESS Requirements and FSL with equivalent test cases -> LLM -> Test Cases  \n
        1. The program will run in the "test generation" mode  
        2. This mode will directly use the prompt "prompt_2_test_gen.txt" prepared within the test_generation/1_through_less folder. in this case the contents of "test_prompt_location" variable.
        3. The given requirements converted to test cases based on test_ZSS_01.
        4. Results are saved in /results folder 
        
    If *-n* argument is given: \n        
        Prompt with NLP Requirements and FSL with equivalent test cases -> LLM -> Test Cases  \n
        1. The program will run in the "test generation but will convert nlp directly to test" mode  
        2. This mode will directly use the prompt "prompt_nlp_test.txt" prepared within the test_generation/1_through_less folder. in this case the contents of "nlp_to_test" variable.
        3. The given requirements converted to test cases based on test_ZSS_01.
        4. Results are saved in /results folder 
    
    """   
    model_type = ModelType.LLAMACPP4#ModelType.LLAMACPP31 #ModelType.LLAMACPP
    parser = argparse.ArgumentParser(description="Generate and save LESS requirements model")

    parser.add_argument("-r", "--requirement-location_manual", type=str, required= False, help="Optional: Specify file location containing LESS requirements JSON to create deterministic test cases out of them.")
    parser.add_argument("-t", "--requirement-location_llm", action="store_true", required=False, help="Optional: Execute program in test case generation mode. The prompt in this case will already have LESS requirements (so no validations required) from which LLM is used to generate test cases.")
    parser.add_argument("-n", "--requirement-location_nlp", action="store_true", required=False, help="Optional: Execute program in test case generation mode. The prompt in this case will have NLP requirements from which LLM is used to generate test cases directly.")
    args = parser.parse_args()
    
    
    if args.requirement_location_manual:
        #if less requirements (in json format) is already given then no need to call for the model. Just use the json data.
        #this is helpful when using output from GPT where we already have the json data.
        try:
            with open(args.requirement_location_manual, "r") as file:
                #need to do dumps here to convert the json data in python to json string because in validation i assume that the incoming value is json string not python dict 
                generated_model = json.dumps(json.load(file))
            print(f"Loaded LESS requirements from file: {args.requirement_location_manual}")
        except Exception as e:
            print(f"Error reading the provided requirement file: {e}")
            return
    elif args.requirement_location_llm:
        generated_model = get_test_cases(model_type, test_prompt_location)
        save_generated_model(generated_model, model_type)
        return
    elif args.requirement_location_nlp:
        generated_model = get_test_cases(model_type, nlp_to_test)
        save_generated_model(generated_model, model_type)
        return
    else:        
        #step 1: get the less requrements from the LLM
        generated_model = get_less_requirements(model_type)
        
    if generated_model is None:
        print("Error generating requirements. Check if given model is supported. If you are giving the requirements in json format, check the file.")
    else:
        #step2: save the generated model (less requirements) 
        save_generated_model(generated_model, model_type)
        
        #step 3: validate the resutls from the model (less requirements)
        validaton_errors, correct_lines = validate_generated_model(generated_model, model_type)
        if(len(correct_lines) > 0):
            print("Number of correct lines: ", len(correct_lines))
            print("Generating ess file based on the valid requirements...")
            
            #step 4: generate ess file based on the valid requirements
            new_specs_filename = "berlin_heart.ess"
            new_specs_filepath = os.path.join(output_directory_global, new_specs_filename)
            ess = generateEss(correct_lines, specs_location, new_specs_filepath)
            ess.get_save_ess()
            print(f"ESS file generated successfully: {new_specs_filepath}")
            print(f"Generating test cases based on the valid requirements...")
            
            #step 5: Test Generation for requirements with a (temporal) condition (IF, WHILE, DURING, BEFORE, AFTER)
            test_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_IPTS.json")
            test_cases_ITPS = generate_testcases(grammar_filelocation, new_specs_filepath, test_json_fullpath)
            
            #step 6: Positive test generation based on the safety and security requirements with the usage of the state spaces concept. 
            test_zss_json_fullpath = os.path.join(output_directory_global, "generated_testcases_deterministic_ZSS01.json")
            test_cases_ZSS = generate_zss_testcases(new_specs_filepath, test_zss_json_fullpath)
            
if __name__ == '__main__':
    main()