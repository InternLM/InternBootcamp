from agentic_workflow.backend import query
import os
import json
from agentic_workflow.utils import parse_python_code, parse_yaml_code
import argparse
def task_generator(task):
    prompt = f"Please understand the {task} task and generate a task description for {task}."
    task_description = query(prompt)
    return task_description

def case_function(task_description, case_generator):
    prompt = f"Please understand the {task_description} task and write the python code to generate a case for {task_description} according to the {case_generator} case generator as an example."
    case = query(prompt)
    return case

def prompt_function(case, prompt_function):
    prompt = f"Please understand the {case} case and write the python code to generate a prompt for {case} according to the {prompt_function} prompt function as an example."
    prompt = query(prompt)
    return prompt

def prompt_class(task_description,case,prompt,prompt_class):
    prompt = f"Please understand the {task_description} task, {case} case generator and {prompt} prompt function and write the python code to generate a prompt class for {task_description} according to the {prompt_class} prompt class as an example."
    prompt = query(prompt)
    return prompt

def cal_function(task_description,cal_function):
    prompt = f"Please understand the {task_description} task and write the python code to generate a reward calculation function for {task_description} according to the {cal_function} reward function as an example."
    cal_function = query(prompt)
    return cal_function

def verify_correction_function(task_description,reward_function,verify_correction_function):
    prompt = f"Please understand the {task_description} task and {reward_function} reward function and generate a python code to verify correction function according to the {verify_correction_function} verify correction function as an example."
    verify_correction_function = query(prompt)
    return verify_correction_function

def extract_output_function(task_description,extract_output_function):
    prompt = f"Please understand the {task_description} task and write the python code to generate a extract output function for {task_description} according to the {extract_output_function} extract output function as an example."
    extract_output_function = query(prompt)
    return extract_output_function

def reward_class(task_description,reward_function,verify_correction_function,extract_output_function):
    prompt = f"Please understand the {task_description} task and {reward_function} reward function and {verify_correction_function} verify correction function and {extract_output_function} extract output function and generate a python code to reward class for {task_description}."
    reward_class = query(prompt)
    return reward_class

def tools_class(task_description,tool_class):
    prompt = f"Please understand the {task_description} task and write the python code to generate a tools class for {task_description} according to the {tool_class} tools class as an example."
    tools_class = query(prompt)
    return tools_class

def interaction_class(task_description,interaction_class):
    prompt = f"Please understand the {task_description} task and write the python code to generate a interaction class for {task_description} according to the {interaction_class} interaction class as an example."
    interaction_class = query(prompt)
    return interaction_class

def instruction_yaml(task_description,instruction_yaml):
    prompt = f"Please understand the {task_description} task and write the yaml file to generate a instruction yaml for {task_description} according to the {instruction_yaml} instruction yaml as an example."
    instruction_yaml = query(prompt)
    return instruction_yaml

def tool_yaml(task_description,tool_yaml):
    prompt = f"Please understand the {task_description} task and write the yaml file to generate a tool yaml for {task_description} according to the {tool_yaml} tool yaml as an example."
    tool_yaml = query(prompt)
    return tool_yaml

def interaction_yaml(task_description,interaction_yaml):
    prompt = f"Please understand the {task_description} task and write the yaml file to generate a interaction yaml for {task_description} according to the {interaction_yaml} interaction yaml as an example."
    interaction_yaml = query(prompt)
    return interaction_yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate the task scripts and yaml files.")
    parser.add_argument("--task_name", type=str, default="hamiltonian_circuit_synthesis", help="The name of the task.")
    parser.add_argument("--task_description", type=str, default="The task is to synthesize a hamiltonian circuit.", help="The description of the task.")
    args = parser.parse_args()
    task_name = args.task_name
    task_description = args.task_description
    task_name = task_name.replace(" ", "_")
    mkdir_path = f"Bootcampv2/{task_name}"
    os.makedirs(mkdir_path, exist_ok=True)
    yaml_path = os.path.join(mkdir_path, "configs")
    os.makedirs(yaml_path, exist_ok=True)
    prompt_example = json.load(open("agentic_workflow/prompt_example.json"))
    mkdir_path = f"Bootcampv2/{task_name}"
    os.makedirs(mkdir_path, exist_ok=True)
    yaml_path = os.path.join(mkdir_path, "configs")
    os.makedirs(yaml_path, exist_ok=True)
    # yaml configs
    yaml_instruction = f"{task_name}_instruction.yaml"
    yaml_tool = f"{task_name}_tool.yaml"
    yaml_interaction = f"{task_name}_interaction.yaml"
    # python scripts
    instruction_generator_class = f"{task_name}_instruction_generator.py"
    interaction_class =  f"{task_name}_interaction.py"
    tool_class =  f"{task_name}_tools.py"
    reward_calculator_class =  f"{task_name}_reward_calculator.py"
    # task description
    task_description = task_generator(task_name) # generate the task description which can skip if you have the task description already
    print(task_description)
    # case generator
    case = case_function(task_description,prompt_example['case_generator'])
    print(case)
    # prompt function
    prompt = prompt_function(task_description,prompt_example['prompt_function'])
    print(prompt)
    # prompt class
    prompt_class = prompt_class(task_description,case,prompt,prompt_example['prompt_class'])
    print(prompt_class)   
    # instruction generator class
    with open(os.path.join(mkdir_path, instruction_generator_class), "w") as f:
        prompt_class = parse_python_code(prompt_class)
        f.write(prompt_class)
        print("Successfully generate instructor scripts.")
    # extract output function
    extract_output_function = extract_output_function(task_description,prompt_example['extract_output'])
    print(extract_output_function)
    # reward calculator class
    cal_function = cal_function(task_description,prompt_example['cal_function'])
    print(cal_function)
    # verify correction function
    verify_correction_function = verify_correction_function(task_description,cal_function,prompt_example['verify_correction'])
    print(verify_correction_function)
    # reward class
    reward_class = reward_class(task_description,verify_correction_function,extract_output_function,prompt_example['reward_class'])
    with open(os.path.join(mkdir_path, reward_calculator_class), "w") as f:
        reward_class = parse_python_code(reward_class)
        f.write(reward_class)
        print("Successfully generate reward calculator scripts.")
    # tools class
    tools_class = tools_class(task_description,prompt_example['tools_class'])
    with open(os.path.join(mkdir_path, tool_class), "w") as f:
        tools_class = parse_python_code(tools_class)
        f.write(tools_class)
        print("Successfully generate tools scripts.")
    # interaction class
    interaction_class = interaction_class(task_description,prompt_example['interaction_class'])
    with open(os.path.join(mkdir_path, interaction_class), "w") as f:
        interaction_class = parse_python_code(interaction_class)
        f.write(interaction_class)
        print("Successfully generate interaction scripts.")
    # instruction yaml
    instruction_yaml = instruction_yaml(task_description,prompt_example['instruction_yaml'])
    with open(os.path.join(yaml_path, yaml_instruction), "w") as f:
        instruction_yaml = parse_yaml_code(instruction_yaml)
        f.write(instruction_yaml)
        print("Successfully generate instruction yaml.")
    # tool yaml
    tool_yaml = tool_yaml(task_description,prompt_example['tool_yaml'])
    with open(os.path.join(yaml_path, yaml_tool), "w") as f:
        tool_yaml = parse_yaml_code(tool_yaml)
        f.write(tool_yaml)
        print("Successfully generate tool yaml.")
    # interaction yaml
    interaction_yaml = interaction_yaml(task_description,prompt_example['interaction_yaml'])
    with open(os.path.join(yaml_path, yaml_interaction), "w") as f:
        interaction_yaml = parse_yaml_code(interaction_yaml)
        f.write(interaction_yaml)
        print("Successfully generate interaction yaml.")