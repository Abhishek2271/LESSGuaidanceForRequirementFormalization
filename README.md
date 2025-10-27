## LESS-Based Requirement and Test Case Generation

The scripts, prompts, and the requirement and test generation Python application in this project support the replicability of the experiments performed in the paper:

**_LESS is more: Guiding LLMs for Formal Requirement and Test Case Generation_**

<Details>
<summary><strong>Show BibTeX Citation</strong></summary>
  
```bibtex
@inproceedings{less_is_more,
  author       = {Shrestha, Abhishek and Schlingloff, Bernd-Holger and Großmann, Jürgen},
  title        = {LESS is more: Guiding LLMs for Formal Requirement and Test Case Generation},
  booktitle    = {Proceedings of the 3rd International Conference on Communication, Artificial Intelligence and Systems (CAIS 2025)},
  year         = {2025},
  address      = {Baghdad, Iraq},
  month        = sep,
  publisher    = {Springer},
  series       = {Communications in Computer and Information Science (CCIS)},
  volume       = {2693},
  isbn         = {978-3-031-07243-6},
  issn         = {1865-0937},
  doi          = {to be assigned}, 
  pages        = {372--389},
  note         = {Accepted March 2025; conference held September 17--18, 2025; to appear},
  keywords     = {Large Language Models, Controlled Natural Language, Requirements Engineering, Test Case Generation, Verification and Validation},
}
````
</Details>

#### This readme provides short over view of the contents of the repo. For more details please visit the [wiki](https://github.com/Abhishek2271/LESSGuaidanceForRequirementFormalization/wiki) 
---
More specifically, the repository provides the following artefacts:  

 1. Prompts used during the experiments.   
 2. Details of the models used.
 3. Results from the experiments — including both raw outputs from all models and aggregated results (e.g., individual error counts).           
      The raw outputs here not only show the results but also the word document provides analysis of the results. Which lines in the results were correct (exact matches), incorrect, and why they were incorrect.   
 4. Python application that was used to run the experiments
    locally.

***Thus, this documentation not only covers the results but also the analysis of the results.***  

With the python application, you can run the entire experimentation workflow as depicted in the the figure below:

<p align="center">
  <img src="images/workflow.png" alt="Workflow diagram" width="1000"/>
  <br>
  <em>Figure 1: Experimentation Workflow; LESS requirement generated using LLMs followed by test case generation. Blocks using LLM prompts are colored green.</em>
</p>

Additionally, the Repo also contains a [Wiki](https://github.com/Abhishek2271/LESSGuaidanceForRequirementFormalization/wiki) that describes:  
1. Using the python application to perform experiments.
2. The artefacts (prompts, experimental results) for both industrial case studies that were implemented (VAD and E-GAS case studies).

---
## Case Studies and Results
We implemented our approach in two case studies:
1. An industrial case study involving medical devices. The Ventricular Assistive Device (VAD) case study from Berlin Hearts GmbH.
2. A public automotive domain case study based on the Standardized E-GAS Monitoring Concept.
   
The VAD case study is confidential and therefore only aggregated results can be shared. These results and their analysis are available in our paper and at: /Results/Results_VAD.xlsx

*E-GAS case study is public and the results can be shared.*

This repository provides a complete results set of E-GAS case study, which includes:

1. [Prompts used for each model](Results/logs/requirement_generation/indirect_prompts): Grammar definition, FSL, and tasks provided to the model, for example LESS requirements to generate test cases.
2. [Results](Results) from multiple runs for each model for both [requirement](https://github.com/Abhishek2271/LESSGuidance/tree/main/Results/logs/requirement_generation/indirect_prompts) and [test case generation](Results/logs/test_generation): Results are were copied to docx file where we analyzed each generation individually and noted the error type along with reasoning for that error type as comments in the file

The [/Results/Results_EGAS.xlsx](/Results/Results_EGAS.xlsx) presents detailed results along with the location of each individual response from the model which were used to derive the counts. 
The xlsx also provides location of the Ground Truth used for each tasks for each model.

Please follow the wiki for more details on the case studies and LESS as a controlled natural language

