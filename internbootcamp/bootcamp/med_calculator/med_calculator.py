import json
import math
import random
from internbootcamp.bootcamp.base import Basebootcamp

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
    def __init__(self, conf_file="./internbootcamp/libs/med_calculator/med_calculator.json", seed=None, add_rule_ratio=0.25):
        random.seed(seed)
        self.add_rule_ratio = add_rule_ratio
        with open(conf_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.rules = self._construct_rules()

    def _gen_a_case(self, category, name):
        details = self.config[category][name]
        indicators = self.config["indicator"]
        inputs = []

        match category:
            case 'equation':
                while 1:
                    formula = details["formula"]
                    try:
                        for i in details["inputs"]:
                            match indicators[i]["type"]:
                                case "int":
                                    k = v = random.randint(*indicators[i]["range"])
                                case "float":
                                    v = random.uniform(*indicators[i]["range"])
                                    if 'precision' in indicators[i]:
                                        v = round(v, indicators[i]["precision"])
                                    k = v
                                case "choice":
                                    rg = indicators[i]["range"]
                                    if (t := type(rg)) is list:
                                        k = v = random.choice(indicators[i]["range"])
                                    elif t is dict:
                                        k = random.choice(list(rg.keys()))
                                        v = rg[k]

                            inp = i.split('[')[0] + str(k) + indicators[i].get("unit", "")
                            inputs.append(inp)
                            formula = formula.replace(i, str(v))

                        target = eval(formula)
                        break
                    except (ZeroDivisionError, ValueError):
                        pass
                    except Exception as e:
                        e.args=(*e.args, name, '公式：'+details["formula"], '带入数值：'+formula)
                        raise e
                out_k = name.split('—')[-1]
                if 'precision' in indicators[out_k]:
                    target = round(target, indicators[out_k]["precision"])
            case 'scale':
                target = 0
                try:
                    for title, options in details["points"].items():
                        if options['type'] == '单选':
                            selected_option = random.choice(list(options['items'].keys()))
                            inputs.append(f'{title}: {selected_option}')
                            target += options['items'][selected_option]
                        elif options['type'] == '多选':
                            selected_options = random.sample(list(options['items'].keys()), k=random.randint(1, len(options['items'])))
                            inputs.append(f'{title}: {"、".join(selected_options)}')
                            target += sum(options['items'][opt] for opt in selected_options)
                except Exception as e:
                    e.args=(*e.args, name)
                    raise e

        ret = {
            "category": category,
            "name": name,
            "inputs": inputs,
            "add_rule": random.random() < self.add_rule_ratio,
            "target": target,
        }
        return ret

    def case_generator(self):
        category = random.choice(['equation', 'scale'])
        name = random.choice(list(self.config[category].keys()))
        return self._gen_a_case(category, name)

    def _construct_rules(self):
        rules = {}
        for name, details in self.config["equation"].items():
            formula = details["formula"]
            explanation_arr = []
            for i in details["inputs"]:
                indicator = self.config["indicator"][i]
                if indicator["type"] == "choice":
                    j = i.split('[')[0]
                    t = f'{j}：'+ '，'.join([f'{k}：{v}' for k,v in indicator["range"].items()])
                    formula = formula.replace(i, j)
                    explanation_arr.append(t)
            formula = formula.replace('math.', '')

            explanation = ''
            if explanation_arr:
                explanation = "公式说明：" + '；'.join(explanation_arr) + "\n"

            rules[name] = f"{name}的计算公式：{formula}\n{explanation}\n"
        for name, details in self.config["scale"].items():
            rules[name] = f"{name}量表的评分标准：\n"
            for title, options in details["points"].items():
                rules[name] += f"[{title}][{options['type']}]\n"
                rules[name] += '\n'.join([f'{k}（{v}分）' for k, v in options['items'].items()]) + "\n"
            rules[name] += "\n"
        return rules

    def prompt_func(self, case):
        indicators = self.config["indicator"]
        random.shuffle(case["inputs"])
        inp_items = '，'.join(case["inputs"])
        out_item = case["name"]

        other_item = ''
        match case["category"]:
            case 'equation':
                out_name = out_item.split('—')[-1]
                if 'precision' in indicators[out_name]:
                    other_item = f"，保留{indicators[out_name]['precision']}位小数"

        rule = self.rules[case["name"]] if case["add_rule"] else ""
        instruction = f"{rule}患者信息：{inp_items}。请计算{out_item}{other_item}。"
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
    bootcamp = Medcalculatorbootcamp(seed=42)
    identity = bootcamp.case_generator()
    print(f'{identity = }')

    prompt = bootcamp.prompt_func(identity)
    print(f"Prompt: \n{prompt}")

    response = "...some reasoning process...\\boxed{BMI: 134.7}"
    print(f"Response: \n{response}")
    score = bootcamp.verify_score(response, identity, short_penalty=False, format_penalty=False)
    print(f"Score: {score}")
