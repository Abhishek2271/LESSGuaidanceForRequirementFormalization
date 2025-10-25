import re
import sys
import json
from textx import metamodel_from_file

class RequirementProcessor:
    def __init__(self, pathToEss):
        self.pathToEss = pathToEss
        self.testNr = 0

    def generateTestNr(self, reqID):
        self.testNr += 1
        return "TC_00{} ({})".format(self.testNr, reqID)

    def get_cond_from_file(self, reqID):
        """
        Reads the file and returns the first line (inside the requirement block)
        that contains one of the conditional keywords.
        """
        with open(self.pathToEss, 'r') as f:
            lines = f.readlines()

        reqFound = False
        condition_line = None
        for line in lines:
            # Look for the requirement ID in the line.
            if reqID in line:
                reqFound = True
                continue

            # Once inside the requirement block, break if we hit a new requirement or closing brace.
            if reqFound and (line.strip().startswith("Requirement:") or line.strip() == "}" or line.strip() == "],"):
                break

            if reqFound and re.search(r'\b(IF|WHILE|BEFORE|DURING|AFTER)\b', line, re.IGNORECASE):
                condition_line = line.strip()
                break
        return condition_line

    def parse_conditional_line(self, line):
        """
        Given a conditional line such as:
          IF FROM manual_mode TO auto_mode THE user SHALL BE ABLE TO adjust THE current systolic_pressure
        this function splits it into:
          precondition: FROM manual_mode TO auto_mode
          behaviour: THE user SHALL BE ABLE TO adjust THE current systolic_pressure

        The method:
          1. Removes the leading conditional keyword.
          2. Splits the remaining text at the first occurrence of whitespace that precedes an article
             (THEN, THE, A, or AN) using a positive lookahead with a non-capturing group.
        """
        # Remove the leading conditional keyword and any extra spaces.
        line_no_cond = re.sub(r'^(IF|WHILE|BEFORE|DURING|AFTER)\s+', '', line, flags=re.IGNORECASE)
        # Split on the first whitespace before an article (THE, A, or AN).
        parts = re.split(r'\s+(?=(?:THEN|THE|A|AN)\b)', line_no_cond, maxsplit=1)
        if len(parts) >= 2:
            pre = parts[0].strip()
            beh = parts[1].strip()
            return pre, beh
        else:
            return None, None

    def process_requirement(self, reqID):
        condition_line = self.get_cond_from_file(reqID)
        if not condition_line:
            print("No conditional found for requirement {}".format(reqID))
            return

        pre, beh = self.parse_conditional_line(condition_line)
        if pre is None:
            print("Could not parse conditional line for requirement {}: {}".format(reqID, condition_line))
            return

        test_case_id = self.generateTestNr(reqID)
        print("Test Case ID: {}".format(test_case_id))
        print("Requirement ID: {}".format(reqID))
        print("Precondition: {}".format(pre))
        print("Behaviour: {}".format(beh))
        print("Test Input: None")
        print("-" * 60)
        
        #generate json as well:
        
        test_case = {
            "test_case_id": test_case_id,
            "requirement_id": reqID,
            "precondition": pre,
            "behaviour": beh,
            "test_input": None
        }
        return test_case


def generate_testcases(grammar_file, ess_file, output_testcases_json):        
    #if len(sys.argv) < 3:
    #    print("Usage: {} <grammar_file.tx> <ess_file.ess>".format(sys.argv[0]))
    #    sys.exit(1)
    
    #grammar_file = sys.argv[1]
    #ess_file = sys.argv[2]
    processor = RequirementProcessor(ess_file)
    mm = metamodel_from_file(grammar_file)    
    model = mm.model_from_file(ess_file)
    
    # get the 'requirements' attribute of the meta model.
    requirements = getattr(model, 'requirements', None)
    if not requirements:
        print("No requirements found in the ESS file.")
        return
    
    # Print out each requirement as a list element.
    print("Found {} requirements:".format(len(requirements)))
    
    test_cases = []
    for req in requirements:
        test_case = processor.process_requirement(req.name)
        if test_case is not None:
            test_cases.append(test_case)

    #write to json file
    with open(output_testcases_json, 'w') as outfile:
        json.dump(test_cases, outfile, indent=4)
        
if __name__ == '__main__':
    tex_file = "LESS.tex"
    ess_file = "berlin_heart.ess"
    generate_testcases(tex_file, ess_file, "testcases.json")
