# InternBootcampv2 Agent Workflow Usage

## TL;DR
This workflow uses the Deepseek-V3.1-teminus model as the base model, which automatically generates tasks in the BootcampV2 environment.

## Pipeline

### Run command
```
python verl-bootcampv2/agentic_workflow/main.py --task_name <> --task_description <>
```

### LLM Configuration
Ensure you can access the base model (for internal usage) by running the following curl command:
```
curl http://100.96.35.28:18889/v1/
```

### Task Definition
We offer two approaches to accommodate different usage scenarios:

1. **Clear Task Definition**  
   If you already have a well-defined task, input your task details into the `--task_description` field and specify the task name using the `--task_name` field.

2. **Unclear Task Requirement**  
   If you do not have a clear task in mind, simply provide the task name using `--task_name`, and we will use the LLM to automatically generate the task description (`--task_description`).