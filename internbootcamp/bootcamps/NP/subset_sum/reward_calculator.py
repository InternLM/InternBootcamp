import sys
import ast
from pathlib import Path
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
import re

class NpSubsetSumRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" in response:
            indices_str = response.split("Answer:")[-1].strip()
        else:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}

        import re

        indices_str = indices_str.strip().replace("'", "").replace('"', '')
        pattern = r'[{\[\(]([^)}\]]*)[}\])]'
        match = re.search(pattern, indices_str)
        if match:
            indices_str = match.group(1)
        try:
            indices = [int(x.strip()) for x in indices_str.split(',') if x.strip() != '']
        except:
            return {"format": True, "answer": False, "str": "invalid index list: should be a list of integers"}

        if not indices:
            return {"format": True, "answer": False, "str": "index list is empty"}
        
        return {"format": True, "answer": True, "str": str(indices_str)}
    
    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        if extracted_output['format'] is False:
            format_reward = -1
        else:
            format_reward = 1
        if extracted_output['answer'] is False:
            answer_reward = -1.5
        else:
            numbers = identity.get("numbers", {})
            target = identity.get("target", None)
            indices = [int(x.strip()) for x in extracted_output['str'].split(',') if x.strip() != '']
            submitted_sum = sum(numbers[str(i)] for i in indices)
            if submitted_sum != target:
                answer_reward = -1.5
            else:
                actual_subset_size = len(indices)
                answer_reward = actual_subset_size / identity.get("ground_truth")            

        total_reward = format_reward + answer_reward
        return total_reward
        
    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        score = cls._calculate_score(extracted_output, identity)
        return score
        
        


def runtest():
    # 测试数据
    # response = "Answer: [2, 3, 5]"
    response = "Answer: [0, 1, 4, 5]"
    identity = {
    "target": 29,
      "numbers": {
        "0": 10,
        "1": 9,
        "2": 8,
        "3": 16,
        "4": 5,
        "5": 5
      },
      "ground_truth": 4,
      
    }
    calculator = NpSubsetSumRewardCalculator()
    extracted_output = calculator.extract_output(response)
    score = calculator._verify_correction(extracted_output, identity)
    print(f"Extracted Output: {extracted_output}")
    print(f"Score: {score}")
    extracted_output = calculator.extract_output(response)
    score = calculator._verify_correction(extracted_output, identity)
    print(f"Extracted Output: {extracted_output}")
    print(f"Score: {score}")

if __name__ == "__main__":
    runtest()