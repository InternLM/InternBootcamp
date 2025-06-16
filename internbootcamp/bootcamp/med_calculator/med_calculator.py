import json
import math
import random
from bootcamp import Basebootcamp

def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]

    return retval

class Medcalculatorbootcamp(Basebootcamp): # 医学计算器类
    def __init__(self, conf_file="./internbootcamp/libs/med_calculator/med_calculator.json", seed=None):
        random.seed(seed)
        with open(conf_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def _gen_a_case(self, category, name):
        details = self.config[category][name]
        indicators = self.config["indicator"]
        inputs = []

        match category:
            case 'equation':
                while 1:
                    formula = details["formula"]
                    for i in details["inputs"]:
                        match indicators[i]["type"]:
                            case "int":
                                v = random.randint(*indicators[i]["range"])
                            case "float":
                                v = random.uniform(*indicators[i]["range"])
                                if 'precision' in indicators[i]:
                                    v = round(v, indicators[i]["precision"])
                            case "choice":
                                v = random.choice(indicators[i]["range"])

                        t = i + str(v) + indicators[i].get("unit", "")
                        inputs.append(t)
                        formula = formula.replace(i, str(v))

                    try:
                        target = eval(formula)
                        break
                    except (ZeroDivisionError, ValueError):
                        pass
                    except Exception as e:
                        raise e
                        # print(name, formula, details["formula"])
                        # breakpoint()
                out_k = name.split('—')[-1]
                if 'precision' in indicators[out_k]:
                    target = round(target, indicators[out_k]["precision"])
            case 'scale':
                target = 0
                for title, options in details["points"].items():
                    if isinstance(options, dict):
                        selected_option = random.choice(list(options.keys()))
                        inputs.append(f'{title}: {selected_option}')
                        target += options[selected_option]
                    else:
                        inputs.append(title)
                        target += options

        ret = {
            "category": category,
            "name": name,
            "inputs": inputs,
            "target": target,
        }
        return ret

    def case_generator(self):
        category = random.choice(['equation', 'scale'])
        name = random.choice(list(self.config[category].keys()))
        return self._gen_a_case(category, name)

    def prompt_func(self, case):
        indicators = self.config["indicator"]
        inp_items = '，'.join(case["inputs"])
        out_item = case["name"]

        other_item = ''
        match case["category"]:
            case 'equation':
                out_name = out_item.split('—')[-1]
                if 'precision' in indicators[out_name]:
                    other_item = f"，保留{indicators[out_name]['precision']}位小数"

        instruction = f"患者信息：{inp_items}。请计算{out_item}{other_item}。"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{xxx:xxx}. For example "\\boxed{BMI: 20.5}"."""
        prompt = instruction + '\n' + instruction_following
        return prompt

    @staticmethod
    def extract_output(output):
        output = last_boxed_only_string(output)
        if output is None:
            return None
        return remove_boxed(output)

    @classmethod
    def _verify_correction(cls, solution, identity):
        if ':' in solution:
            solution = solution.split(':')[-1].strip()
        elif '：' in solution:
            solution = solution.split('：')[-1].strip()

        return solution.strip() == str(identity['target'])

    def gen_all_case(self, k=1):
        cases = []
        for category in ['equation', 'scale']:
            for name in self.config[category]:
                for _ in range(k):
                    case = self._gen_a_case(category, name)
                    cases.append(case)
        return cases

if __name__ == '__main__':
    bootcamp = MedCalculatorbootcamp(seed=42)
    identity = bootcamp.case_generator()
    print(f'{identity = }')

    prompt = bootcamp.prompt_func(identity)
    print(f"Prompt: \n{prompt}")

    response = "...some reasoning process...\\boxed{BMI: 134.7}"
    print(f"Response: \n{response}")
    score = bootcamp.verify_score(response, identity, short_penalty=False, format_penalty=False)
    print(f"Score: {score}")
