import ast
from internbootcamp.bootcamp.base import Basebootcamp
import re
import ast
import random


BLOOD_TEST_REFERENCE = {
    "白细胞计数": {
        "abbr": "WBC",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (3.5, 9.5)
    },
    "红细胞计数": {
        "abbr": "RBC",
        "unit_value": 1e12,
        "unit_name": "/L",
        "reference_range": (4.3, 5.8)
    },
    "血红蛋白": {
        "abbr": "HGB",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (130, 175)
    },
    "红细胞比容": {
        "abbr": "HCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 50)
    },
    "平均红细胞容积": {
        "abbr": "MCV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (82, 100)
    },
    "平均红细胞血红蛋白量": {
        "abbr": "MCH",
        "unit_value": 1,
        "unit_name": "pg",
        "reference_range": (27, 34)
    },
    "平均红细胞血红蛋白浓度": {
        "abbr": "MCHC",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (316, 354)
    },
    "血小板": {
        "abbr": "PLT",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (125, 350)
    },
    "红细胞分布宽度标准差": {
        "abbr": "RDW-SD",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (30, 54)
    },
    "红细胞分布宽度变异系数": {
        "abbr": "RDW-c",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 14.1)
    },
    "血小板体积分布宽度": {
        "abbr": "PDW",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 17)
    },
    "平均血小板体积": {
        "abbr": "MPV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 13)
    },
    "大血小板比率": {
        "abbr": "P-LCR",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (17.5, 30)
    },
    "血小板体积分数": {
        "abbr": "PCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.13, 0.35)
    },
    "中性粒细胞绝对值": {
        "abbr": "NEUT#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.8, 6.3)
    },
    "淋巴细胞绝对值": {
        "abbr": "LYMPH#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.1, 3.2)
    },
    "单核细胞绝对值": {
        "abbr": "MONO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.1, 0.6)
    },
    "嗜酸细胞绝对值": {
        "abbr": "EO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.02, 0.52)
    },
    "嗜碱细胞绝对值": {
        "abbr": "BASO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0, 0.06)
    },
    "中性粒细胞比率": {
        "abbr": "NEUT%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 75)
    },
    "淋巴细胞比率": {
        "abbr": "LYMPH%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (20, 50)
    },
    "单核细胞比率": {
        "abbr": "MONO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (3, 10)
    },
    "嗜酸细胞比率": {
        "abbr": "EO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.4, 8)
    },
    "嗜碱细胞比率": {
        "abbr": "BASO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 1)
    },
}



class BloodTestJudgementbootcamp(Basebootcamp):
    def __init__(self, seed: int=0, max_num_items=24, augment_unit=False):
        random.seed(seed)
        self.references = BLOOD_TEST_REFERENCE
        self.max_num_items = min(max(max_num_items, 1), len(self.references))
        self.augment_unit = augment_unit

    def case_generator(self):
        """
        Randomly select ≥1 blood-test items from self.references, generate a reasonable
        random value for each (within/slightly out/greatly out of the reference range),
        then for non-percentaged units apply a random power-of-10 scaling to (value, unit_value).
        
        Returns:
            dict: {
            "item_names":  [<item_name>, ...],
            "values": [<float>, ...],
            "unit_names":  [<unit_str>, ...],
            "unit_value":  [<unit_val>, ...],
            "ground_truths": [<int>, ...]
            }
        """

        # 1. pick a random non‐empty subset of items
        all_items = list(self.references.keys())
        k = random.randint(1, self.max_num_items)
        items = random.sample(all_items, k)

        # 2. randomly generate value and unit for each item
        out_item_names, out_values = [], []
        out_unit_names, out_unit_values = [], []
        out_results = []
        for item_name in items:
            ref_min, ref_max = self.references[item_name]["reference_range"]

            # generate a plausible value
            mean = (ref_min + ref_max) / 2
            std  = (ref_max - ref_min) / 2
            
            low  = max(0.1 * ref_min, mean - 4 * std)
            high = mean + 4 * std
            val  = random.uniform(low, high)

            if ref_min < val < ref_max:
                result = 0
            elif val <= ref_min:
                result = -1
            else:
                result = 1
            
            # fetch original unit
            uv = self.references[item_name]["unit_value"]
            un = self.references[item_name]["unit_name"]
            
            # apply random power‐of‐10 rescaling for non-% units
            if self.augment_unit and (un != "%"):
                exp = random.choice([-2, -1, 0, 1, 2])
                new_val = val / (10 ** exp)
                new_uv  = uv  * (10 ** exp)
            else:
                new_val = val
                new_uv = uv
            
            new_val = round(new_val, 2)
            if un == '%':
                new_val = min(max(new_val, 0), 1)

            out_item_names.append(item_name)
            out_values.append(new_val)
            out_unit_values.append(new_uv)
            out_unit_names.append(un)
            out_results.append(result)
        
        return {
            "item_names": out_item_names,
            "values": out_values,
            "unit_values": out_unit_values, 
            "unit_names": out_unit_names, 
            "ground_truths": out_results
        }

    def prompt_func(self, identity):
        """
        Build a human-readable prompt asking an LLM to judge each blood test item
        as low/normal/high. The LLM should rely on its own internal knowledge of
        human physiology. 
        """
        
        lines = []
        for name, val, uv, un in zip(
            identity["item_names"],
            identity["values"],
            identity["unit_values"],
            identity["unit_names"]
        ):
            unit_str = un if uv == 1 else f"{uv:.0e}{un}"
            abbr = self.references[name]["abbr"]
            lines.append(f"- {name} ({abbr}): {val} ({unit_str})")
        
        prompt = (
            "You are a medical expert in hematology and clinical laboratory interpretation. Below are "
            "several blood test results:\n\n"
            + "\n".join(lines) 
            + "\n\nFor each result, use your knowledge of healthy reference ranges of each item to determine " 
            "whether the value is too low, normal, or too high. Use one of the following integers for each "
            "judgement: -1 (too low), 0 (within heathly reference range), or 1 (too high). You MUST output "
            "**ONLY ONE** Python-style list for your judgements (e.g. `[-1, 0, 1]`) in the same order as "
            "the input blood test results."
        )

        return prompt

    @staticmethod
    def extract_output(output: str):
        """
        Parse the LLM's raw text and return the last valid Python list of ints [-1,0,1].
        Ignores surrounding commentary and any earlier lists.
        """
        pattern = re.compile(r'\[\s*-?\d+\s*(?:,\s*-?\d+\s*)*\]')
        matches = pattern.findall(output)
        if not matches:
            return []

        last_literal = matches[-1]
        try:
            solution = ast.literal_eval(last_literal)        # safely turn the string into a list
            if isinstance(solution, (list, tuple)) and all(isinstance(x, (int, float)) for x in solution):
                return [int(t) for t in solution]
        except Exception as err:
            return []

    @classmethod
    def _verify_correction(cls, solution, identity):
        ground_truths = identity['ground_truths']

        if len(solution) != len(ground_truths):
            return False
        
        return all(x == y for x, y in zip(solution, ground_truths))

if __name__ == "__main__":
    # 初始化 Bootcamp 任务
    bootcamp = BloodTestJudgementbootcamp(seed=42)  # 使用固定种子以便结果可复现

    # 生成测试用例
    case = bootcamp.case_generator()
    print("--------------------------------")
    print("Generated Case:", case)

    # 构造题面
    prompt = bootcamp.prompt_func(case)
    print("Prompt:", prompt)
    print("--------------------------------")
    # 模拟模型输出（使用ground_truths作为模拟输出）
    model_output = f"some reasoning process...{case['ground_truths']}"
    extracted_answer = bootcamp.extract_output(model_output)
    print("Extracted Answer:", extracted_answer)
    print("--------------------------------")
    # 验证答案
    is_correct = bootcamp._verify_correction(extracted_answer, case)
    print("Is Correct:", is_correct)
    print("--------------------------------")
    # 验证分数
    score = bootcamp.verify_score(model_output , case)
    print("Score:", score)
    print("--------------------------------")
    # 错误答案
    model_output_error = f"some reasoning process...(-1, 1, 1, 0, 0, -1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, -1)"
    extracted_answer_error = bootcamp.extract_output(model_output_error)
    print("Extracted Answer Error:", extracted_answer_error)
    print("--------------------------------")
    # 验证错误答案
    is_correct_error = bootcamp._verify_correction(extracted_answer_error, case)
    print("Is Correct Error:", is_correct_error)
    print("--------------------------------")
    # 验证错误答案分数
    score_error = bootcamp.verify_score(model_output_error , case)
    print("Score Error:", score_error)
    print("--------------------------------")