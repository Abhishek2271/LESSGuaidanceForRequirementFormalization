import re
import json

def extract_list(spec_text, key):
    """
    Extracts a list of items for a given key (e.g., 'Variables', 'Components', 'Objects', 'States')
    from the specification document.
    """
    pattern = key + r":\s*\[([^\]]+)\]"
    match = re.search(pattern, spec_text, re.DOTALL)
    items = []
    if match:
        content = match.group(1)
        tokens = re.split(r",\s*", content)
        for token in tokens:
            token = token.strip()
            # For entries like "user:{stateSpaces: [authorizable]}", take the part before the colon.
            token = token.split(":", 1)[0]
            if token:
                items.append(token)
    return items

def extract_requirements(spec_text):
    """
    Extracts requirement blocks from the specification document.
    Each block is expected to have a "Requirement:" line and a body enclosed in curly braces.
    
    Returns:
        list of tuples: Each tuple contains (requirement_id, block_text).
    """
    pattern = r"Requirement:\s*(\S+).*?\{(.*?)\}"
    requirements = re.findall(pattern, spec_text, re.DOTALL)
    return requirements

def extract_pre_conditions(text, token_set):
    """
    Extracts antecedent (PRE) conditions from the given text.
    
    It uses two patterns:
      - Pattern A (with component): matches when an antecedent keyword is preceded by a token (the component).
      - Pattern B (without component): matches when the text starts with an antecedent keyword.
      
    In Pattern A, if a negation (NOT) is present, the value is False; otherwise True.
    In Pattern B, the token immediately following the keyword is taken as the state.
    
    Returns:
        dict: A flat dictionary with keys like "component:state" (if a component was captured)
              or just "state" (if not), and boolean values.
    """
    conditions = {}
    # Pattern A: with component (expects IF or AND before)
    pattern_with_component = r"(?:IF|AND)\s+(?P<negation>NOT\s+)?(?P<component>\S+)\s+(?P<keyword>FROM|WHILE|IN CASE OF|DURING|IN(?!\s+(?:AS SOON AS|TO|BEFORE)))\s+(?P<state>\S+)(?:\s+STATE)?"
    for match in re.finditer(pattern_with_component, text, re.IGNORECASE):
        negation = match.group("negation") is not None
        component = match.group("component")
        state = match.group("state")
        key = f"{component}:{state}"
        conditions[key] = not negation
    # Pattern B: without component (text starts with one of the keywords)
    pattern_without_component = r"\b(?P<keyword>FROM|WHILE|IN CASE OF|DURING|IN(?!\s+(?:AS SOON AS|TO|BEFORE)))\s+(?P<state>\S+)(?:\s+IS\s+\S+)?(?:\s+STATE)?"
    for match in re.finditer(pattern_without_component, text, re.IGNORECASE):
        # To avoid duplicate matches from Pattern A, only add if not already captured in any key containing a colon.
        state = match.group("state")
        key = state
        conditions.setdefault(key, True)
    return conditions

def extract_post_conditions(text, token_set, default_value):
    """
    Extracts consequence (POST) conditions from the given text by scanning for "TO" clauses.
    
    The pattern optionally captures a component immediately preceding "TO". If a valid component is captured
    (i.e. it exists in token_set), the key becomes "component:state"; otherwise, the key is just "state".
    
    The boolean value for each occurrence is set to default_value.
    """
    post_conditions = {}
    pattern = r"(?:(?P<component>\S+)\s+)?TO\s+(?P<state>\S+)(?:\s+STATE)?"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        component = match.group("component")
        state = match.group("state")
        if component is not None and component in token_set:
            key = f"{component}:{state}"
        else:
            key = state
        post_conditions[key] = default_value
    return post_conditions

def transform_conditions(flat_conditions):
    """
    Transforms a flat dictionary of conditions with keys like "component:state" 
    into a nested dictionary where the outer keys are component names and the inner keys are states.
    
    For example, {"compact_drive:failed": true, "clinical_ui:is_running": true} becomes:
      {
        "compact_drive": { "failed": true },
        "clinical_ui": { "is_running": true }
      }
    """
    nested = {}
    for key, value in flat_conditions.items():
        if ":" in key:
            comp, state = key.split(":", 1)
            if comp in nested:
                nested[comp][state] = value
            else:
                nested[comp] = { state: value }
        else:
            nested[key] = value
    return nested

def filter_conditions_by_states(flat_conditions, valid_states):
    """
    Filters out any condition from the flat dictionary if its state is not in the valid_states set.
    
    For keys in the format "component:state", state is the substring after the colon.
    For keys without a colon, the key itself is the state.
    """
    filtered = {}
    for key, value in flat_conditions.items():
        if ":" in key:
            comp, state = key.split(":", 1)
        else:
            state = key
        if state in valid_states:
            filtered[key] = value
    return filtered

def extract_transition_conditions(text, valid_states):
    """
    Extracts state transition conditions from text for patterns like:
      FROM state_src TO state_target
      
    Returns two flat dictionaries:
      - transition_pre: { state_src: True, state_target: False }
      - transition_post: { state_src: False, state_target: True }
    
    Only applies if both state_src and state_target are in valid_states.
    """
    transition_pre = {}
    transition_post = {}
    pattern = r"FROM\s+(?P<src>\S+)(?:\s+STATE)?\s+TO\s+(?P<tgt>\S+)(?:\s+STATE)?"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        src = match.group("src")
        tgt = match.group("tgt")
        if src in valid_states and tgt in valid_states:
            transition_pre[src] = True
            transition_pre[tgt] = False
            transition_post[src] = False
            transition_post[tgt] = True
    return transition_pre, transition_post

def generate_test_cases(spec_text):
    """
    Generates test cases by extracting each requirement and identifying the Testobjects, PRE, and POST conditions.
    
    The requirement block is split into two parts based on the first occurrence of "SHALL" or "SHALL NOT":
      - condition_part: everything before the split keyword
      - action_part: everything after the split keyword
    
    The splitting keyword (captured from the regex) determines the default value for the action part:
      - "SHALL" implies a default of True.
      - "SHALL NOT" implies a default of False.
    
    From the condition_part:
      - PRE conditions are extracted using antecedent keywords (including those that appear at the start).
      - "TO" clauses are also extracted as POST conditions with a default True value.
    
    From the action_part:
      - "TO" clauses are extracted as POST conditions with the default determined by the splitting keyword.
    
    Then, if a state transition pattern (FROM state_src TO state_target) is detected,
    the conditions are updated such that:
      - In PRE: source state becomes true and target state becomes false.
      - In POST: source state becomes false and target state becomes true.
    
    Testobjects are determined by matching tokens from Variables, Components, and Objects anywhere in the block.
    
    Returns:
        list: A list of test case dictionaries.
    """
    # Extract tokens from the spec.
    variables = extract_list(spec_text, "Variables")
    components = extract_list(spec_text, "Components")
    objects = extract_list(spec_text, "Objects")
    errors = extract_list(spec_text, "Errors")
    token_set = set(variables + components + objects + errors)
    
    # Extract valid states from the specification.
    valid_states = set(extract_list(spec_text, "States"))
    
    # Extract requirement blocks.
    requirement_blocks = extract_requirements(spec_text)
    test_cases = []
    
    # Split using "SHALL" or "SHALL NOT" (capturing which one is used).
    split_re = r"\b(SHALL(?:\s+NOT)?)\b"
    
    for req_id, block_text in requirement_blocks:
        parts = re.split(split_re, block_text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 3:
            condition_part = parts[0]
            splitting_keyword = parts[1]
            action_part = parts[2]
        else:
            condition_part = block_text
            splitting_keyword = "SHALL"  # default if not found
            action_part = ""
        
        # Determine default value for the action part based on the splitting keyword.
        action_default = False if "NOT" in splitting_keyword.upper() else True
        
        # Extract PRE from condition part (using our updated extraction that handles both patterns).
        pre_conditions = extract_pre_conditions(condition_part, token_set)
        # Extract POST conditions:
        # From condition part: any "TO" clauses get default True.
        # This handles cases where the conditional has both ante
        post_conditions_condition = extract_post_conditions(condition_part, token_set, True)
        # From action part: default as determined by the splitting keyword.
        post_conditions_action = extract_post_conditions(action_part, token_set, action_default)
        
        # Combine POST conditions; if the same key appears, action part takes precedence.
        post_conditions = {**post_conditions_condition, **post_conditions_action}
        
        # Filter conditions to only include states present in valid_states.
        pre_conditions = filter_conditions_by_states(pre_conditions, valid_states)
        post_conditions = filter_conditions_by_states(post_conditions, valid_states)
        
        # Apply state transition adjustments.
        transition_pre, transition_post = extract_transition_conditions(block_text, valid_states)
        for state, value in transition_pre.items():
            pre_conditions[state] = value
        for state, value in transition_post.items():
            post_conditions[state] = value
        
        # Determine Testobjects by scanning the entire block for tokens in token_set.
        found_tokens = set()
        for token in token_set:
            if re.search(r'\b' + re.escape(token) + r'\b', block_text):
                found_tokens.add(token)
        
        # Transform the flat condition dictionaries to nested ones.
        pre_nested = transform_conditions(pre_conditions)
        post_nested = transform_conditions(post_conditions)
        
        test_case = {
            "Reference": f"test-{req_id}",
            "Requirement": req_id,
            "Testobjects": list(found_tokens),
            "PRE": pre_nested,
            "POST": post_nested
        }
        test_cases.append(test_case)
    return test_cases

def generate_zss_testcases(spec_file, outfile):
    try:
        with open(spec_file, "r") as f:
            spec_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{spec_file}' not found.")
        exit(1)
    
    test_cases = generate_test_cases(spec_text)
    #save generated test cases to disc
    with open(outfile, "w") as f:
        json.dump(test_cases, f, indent=2)
    print(f"Test cases successfully generated...\nSaved to location {outfile}")

if __name__ == "__main__":
    spec_file = r"D:\FOKUS\LESS\src\LESS_Req_Generation\less_testgeneration\test_generation\tests\berlin_heart_test_with_grammar.ess"  # Update with the path to your specification document.
    outfile = r"D:\FOKUS\LESS\src\LESS_Req_Generation\less_testgeneration\test_generation\tests\test_cases_zss_01.json"  # Update with the path to your output file.
    try:
        with open(spec_file, "r") as f:
            spec_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{spec_file}' not found.")
        exit(1)
    
    test_cases = generate_test_cases(spec_text)
    print(json.dumps(test_cases, indent=2))
