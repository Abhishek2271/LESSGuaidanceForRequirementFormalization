import re
import json
import os

class generateEss():
    """
    From given partial ESS file (containing specifications other than LESS requirements), generate complete ESS file that contains LESS requirements.
    """
    def __init__(self, _valid_less_req, _ess_path, _new_specs_filepath):
        """
        _valid_less_req: JSON string containing valid LESS requirements.
        _ess_path: Path to the partial ESS file.
        _new_spec_file: Path to the new ESS file that will be generated.
        """
        self.valid_less_req = _valid_less_req
        self.ess_path = _ess_path
        self.new_spec_file = _new_specs_filepath
        
    def get_save_ess(self):
        # Read the original specification file
        with open(self.ess_path, "r") as file:
            spec_content = file.read()

        # Define the pattern to identify the Requirements section
        requirements_pattern = re.compile(r"Requirements\s*:\s*\[.*?\]", re.DOTALL)

        #json_data = json.loads(self.less_req_json)
        # Construct the new `Requirements:` section
        new_requirements = "Requirements : [\n"
        for item in self.valid_less_req:
            req_id = f"Req_gen{item['Line_number']}"
            new_requirements += f"""
            Requirement: {req_id}
            RequirementClassification: SecurityFunctional
            {{
                {item['LESS']}
            }},"""
        new_requirements = new_requirements.rstrip(",")  # Remove trailing comma
        new_requirements += "\n]"

        # Replace the old `Requirements:` section with the new one
        # TODO: CURRENTLY REPLACING WHOLE REQUIREMENTS SECTION BUT THIS SHOULD BE UPDATE TO THE OLD ONE.
        updated_spec_content = re.sub(requirements_pattern, new_requirements, spec_content)

        # Write back the modified specification file
        with open(self.new_spec_file, "w") as file:
            file.write(updated_spec_content)

        print("Updated specification file has been saved.")     