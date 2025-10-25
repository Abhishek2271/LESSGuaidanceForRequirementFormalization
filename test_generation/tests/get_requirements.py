#!/usr/bin/env python3
import sys
from textx import metamodel_from_file

def main():
    if len(sys.argv) < 3:
        print("Usage: {} <grammar_file.tx> <ess_file.ess>".format(sys.argv[0]))
        sys.exit(1)
    
    grammar_file = sys.argv[1]
    ess_file = sys.argv[2]
    
    # Create the meta-model from your TextX grammar file.
    mm = metamodel_from_file(grammar_file)
    
    # Parse the ESS file according to the grammar.
    model = mm.model_from_file(ess_file)
    
    # Access the 'requirements' attribute of the model.
    requirements = getattr(model, 'requirements', None)
    if not requirements:
        print("No requirements found in the ESS file.")
        return
    
    # Print out each requirement as a list element.
    print("Found {} requirements:".format(len(requirements)))
    for req in requirements:
        # The Requirement rule in the grammar defines a requirement with a name and a nested 'req' element.
        print("Requirement Name: {}".format(req.name))
        
        # Access the nested Req element, which contains the classification and specification.
        req_detail = req.req
        
        # Get the requirement classification.
        req_class = req_detail.req_class
        # It might be a reference with a 'name' attribute or a simple ERID string.
        req_class_name = req_class.name if hasattr(req_class, 'name') else req_class
        print("  Classification: {}".format(req_class_name))
        
        # Optionally print the Safety/Security Rank if present.
        if hasattr(req_detail, 'req_rank') and req_detail.req_rank:
            req_rank = req_detail.req_rank
            req_rank_name = req_rank.name if hasattr(req_rank, 'name') else req_rank
            print("  Safety/Security Rank: {}".format(req_rank_name))
        
        # Print the specification (this is an AST node; its printed representation shows its structure).
        print("  Specification: {}".format(req_detail.specification))
        print("-" * 40)

if __name__ == '__main__':
    main()
