import json
import re
def load_prompt_NP_template(prompt_type: str) -> dict:
    # load json
    json_path = 'internbootcamp/bootcamps/NP/prompt_NP.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        prompt_list = json.load(f)
    # find type
    for item in prompt_list:
        if item['type'] == prompt_type:
            prompt = item['prompt']
            break
    else:
        raise ValueError(f"Prompt type {prompt_type} not found in prompt_NP.json")
    return prompt

def get_prompt(task_type, task_info, NP_question):
    prompt = load_prompt_NP_template("cons_NP")
    prompt["Introduction"] = prompt["Introduction"].format(task_type=task_type)
    prompt["Task description"] = prompt["Task description"].format(description=task_info["description"])
    prompt["Example Input and Output"] = prompt["Example Input and Output"].format(example_input=task_info["example_input"],example_output=task_info["example_output"])   
    prompt["Submission Format"] = prompt["Submission Format"].format(submission_format=task_info["submission_format"])
    prompt["Question"] = prompt["Question"].format(task_type=task_type,question=NP_question)
    return prompt

def extract_markdown_content_NP(md_file_path: str) -> dict:
    # Read the content of the Markdown file
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define a dictionary to store the task description information
    task_des = {}

    # Match the content of each section (starting with '##' headers)
    sections = {
        "description": r"## Description\n(.*?)## Submission Format",
        "submission_format": r"## Submission Format\n(.*?)## Example Input",
        "example_input": r"## Example Input\n(.*?)## Example Output",
        "example_output": r"## Example Output\n(.*?)(##|$)",
    }

    # Extract and store the corresponding content for each section
    for key, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            task_des[key] = match.group(1).strip()
        else:
            task_des[key] = None

    return task_des