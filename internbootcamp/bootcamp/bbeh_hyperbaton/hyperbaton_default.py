import random
import json
import re
import os
import sys
import traceback
from typing import Dict, Any, List, Union
from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.bbeh_hyperbaton.bbeh_hyperbaton_generator import HyperbatonGenerator
from internbootcamp.libs.bbeh_hyperbaton.bbeh_hyperbaton_solver import HyperbatonSolver
from internbootcamp.libs.bbeh_hyperbaton.bbeh_hyperbaton_validor import HyperbatonValidator


class BBEHHyperbatonbootcamp(Basebootcamp):
    _generator = HyperbatonGenerator()
    _solver = HyperbatonSolver()
    _validator = HyperbatonValidator()

    def __init__(self):

        self.generator = self._generator
        self.solver = self._solver
        self.validator = self._validator

    @classmethod
    def case_generator(cls) -> Dict[str, Any]:
        if cls._generator is None:
            raise RuntimeError("Generator not initialized. Create an instance of BBEHHyperbatonbootcamp first.")
        return cls._generator.generate_task()

    @classmethod
    def extract_output(cls,output: str) -> Union[str, None]:
        try:
            if not output or output.strip() == "" or "null" in output.lower():
                return None

            # 查找最终答案部分
            answer_match = re.search(r'最终答案:\s*([A-K]+)(?:\n|$)', output, re.MULTILINE)
            if answer_match:
                answer_text = answer_match.group(1).strip().strip('"\'')
                # 验证答案格式是否正确（只包含A-K的字母）
                if re.match(r'^[A-K]+$', answer_text):
                    return answer_text
            return None

        except Exception as e:
            return None

    @classmethod
    def _verify_correction(cls, answer: Any, identity: Dict[str, Any]) -> bool:
        if cls._solver is None or cls._validator is None:
            raise RuntimeError(
                "Solver or Validator not initialized. Create an instance of BBEHHyperbatonbootcamp first.")

        test_case = {
            "input": identity["input"],
            "target": identity["target"]
        }

        # 使用验证器验证答案
        validation_result = cls._validator.validate_batch([test_case], [answer])
        return validation_result["detailed_results"][0]["is_correct"]

    @staticmethod
    def prompt_func(identity: Dict[str, Any]) -> str:
        question = identity['input']
        prompt = f"""你是一个擅长分析英语形容词顺序的AI助手。请解决以下形容词顺序问题:

问题:
{question}

请仔细分析示例中的形容词顺序规律，并判断哪些选项符合这个规律。

请按以下格式输出你的答案:
最终答案: [你的答案]

注意：答案应该是由正确选项的字母组成的字符串（如"ABC"），如果没有正确选项则输出"K"。
"""
        return prompt


if __name__ == '__main__':
    # try:
    #     # 抑制其他模块的输出
    #     original_stdout = sys.stdout
    #     sys.stdout = open(os.devnull, 'w')

    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     intern_bootcamp_dir = os.path.abspath(os.path.join(current_dir, '..'))

    #     sys.path.append(intern_bootcamp_dir)

    #     bootcamp = BBEHHyperbatonbootcamp()
    #     identity = BBEHHyperbatonbootcamp.case_generator()

    #     if identity is None:
    #         sys.stdout = original_stdout
    #         print("Error: Failed to generate test case")
    #         exit(1)

    #     correct_solution = bootcamp.solver.solve_puzzle(identity["input"])
    #     extracted_answer = BBEHHyperbatonbootcamp.extract_output(f"最终答案: {correct_solution}")
    #     is_correct = BBEHHyperbatonbootcamp._verify_correction(extracted_answer, identity)
    #     score = bootcamp.verify_score(f"最终答案: {correct_solution}", identity, short_penalty=False, format_penalty=False)
    #     sys.stdout = original_stdout

    #     # 简洁输出
    #     print(f"问题: {identity['input']}")
    #     print(f"答案: {correct_solution}")
    #     print(f"验证: {'✓' if is_correct else '✗'}")
    #     print(f"得分: {score}")

    # except Exception as e:
    #     if 'original_stdout' in locals():
    #         sys.stdout = original_stdout
    #     print(f"错误: {str(e)}")
    case = {
  "id": 5,
  "prompt": "你是一个擅长分析英语形容词顺序的AI助手。请解决以下形容词顺序问题:\n\n问题:\nIn a variant of English, we are given that the following sentences have correct adjective order:\nbrand-new good huge computer old-fashioned mysterious enormous square violet box new repulsive tiny knife new ridiculous small pyramidal teal plate old-fashioned repulsive midsize circular shoe old wonderful medium-size canvas brand-new silly huge rectangular knife old silly small watch ancient awful tiny rectangular white bicycle old-fashioned awful little spherical pink bicycle new awful massive book archaic repulsive normal-size prismlike blue flower pot old-fashioned ridiculous large prismlike bottle archaic lovely massive prismlike piano archaic awful small fire extinguisher new ridiculous normal-size prismlike crimson pen brand-new awful large spoon brand-new awful massive bottle old repulsive huge triangular white hammer ancient silly big prismlike maroon lamp new good big saw brand-new wonderful massive spherical hammer old nice enormous bird archaic silly enormous key archaic mysterious large screwdriver ancient wonderful midsize prismlike bicycle old good enormous ruler archaic repulsive medium-size square cyan box new good little prismlike teal canvas archaic nice massive square pink speaker old-fashioned nice midsize banana brand-new nice large pyramidal banana ancient mysterious massive guitar brand-new wonderful massive prismlike calculator ancient awful little bed old repulsive huge square black sunglasses old-fashioned obnoxious little square camera brand-new repulsive little square gray piano old-fashioned awful large triangular gray clock old-fashioned terrible midsize screwdriver brand-new wonderful medium-size rectangular speaker brand-new nice big square indigo box archaic awful massive rectangular magenta pencil brand-new repulsive midsize spherical green fire extinguisher ancient ridiculous big triangular green stapler new good medium-size square wrench archaic good massive prismlike white toolbox ancient wonderful midsize spherical aqua piano archaic repulsive enormous prismlike piano archaic awful massive triangular necklace ancient ridiculous big square bicycle old good huge rectangular key\n\nIn this variant of English, which of the following sentences (Options A-J) use the correct adjective order? If none of the sentences (Options A-J) use the correct adjective order, select option K. Select all that apply.\n(A) indigo spherical brand-new lamp (B) archaic ridiculous huge table (C) nice whittling small archaic violet iron square screwdriver (D) old awful big drill (E) square little pink ring (F) old-fashioned mysterious midsize rectangular yellow leather speaker (G) drinking indigo cloth ancient spherical repulsive pen (H) archaic terrible little circular black iron american box (I) ancient lovely normal-size pyramidal cyan rubber chinese hammer (J) old-fashioned awful large prismlike indigo wood congolese stapler\n(K) None of the above\n\nProvide your final answer as a concatenation of all the correct choices. For example, if B and C have correct adjective order, then your final answer must be \"BC\".\n\n请仔细分析示例中的形容词顺序规律，并判断哪些选项符合这个规律。\n\n请按以下格式输出你的答案:\n最终答案: [你的答案]\n\n注意：答案应该是由正确选项的字母组成的字符串（如\"ABC\"），如果没有正确选项则输出\"K\"。",
  "output_len": 386,
  "score": 0,
  "extracted_output": "BDFHIJ",
  "ground_truth": {
    "input": "In a variant of English, we are given that the following sentences have correct adjective order:\nbrand-new good huge computer old-fashioned mysterious enormous square violet box new repulsive tiny knife new ridiculous small pyramidal teal plate old-fashioned repulsive midsize circular shoe old wonderful medium-size canvas brand-new silly huge rectangular knife old silly small watch ancient awful tiny rectangular white bicycle old-fashioned awful little spherical pink bicycle new awful massive book archaic repulsive normal-size prismlike blue flower pot old-fashioned ridiculous large prismlike bottle archaic lovely massive prismlike piano archaic awful small fire extinguisher new ridiculous normal-size prismlike crimson pen brand-new awful large spoon brand-new awful massive bottle old repulsive huge triangular white hammer ancient silly big prismlike maroon lamp new good big saw brand-new wonderful massive spherical hammer old nice enormous bird archaic silly enormous key archaic mysterious large screwdriver ancient wonderful midsize prismlike bicycle old good enormous ruler archaic repulsive medium-size square cyan box new good little prismlike teal canvas archaic nice massive square pink speaker old-fashioned nice midsize banana brand-new nice large pyramidal banana ancient mysterious massive guitar brand-new wonderful massive prismlike calculator ancient awful little bed old repulsive huge square black sunglasses old-fashioned obnoxious little square camera brand-new repulsive little square gray piano old-fashioned awful large triangular gray clock old-fashioned terrible midsize screwdriver brand-new wonderful medium-size rectangular speaker brand-new nice big square indigo box archaic awful massive rectangular magenta pencil brand-new repulsive midsize spherical green fire extinguisher ancient ridiculous big triangular green stapler new good medium-size square wrench archaic good massive prismlike white toolbox ancient wonderful midsize spherical aqua piano archaic repulsive enormous prismlike piano archaic awful massive triangular necklace ancient ridiculous big square bicycle old good huge rectangular key\n\nIn this variant of English, which of the following sentences (Options A-J) use the correct adjective order? If none of the sentences (Options A-J) use the correct adjective order, select option K. Select all that apply.\n(A) indigo spherical brand-new lamp (B) archaic ridiculous huge table (C) nice whittling small archaic violet iron square screwdriver (D) old awful big drill (E) square little pink ring (F) old-fashioned mysterious midsize rectangular yellow leather speaker (G) drinking indigo cloth ancient spherical repulsive pen (H) archaic terrible little circular black iron american box (I) ancient lovely normal-size pyramidal cyan rubber chinese hammer (J) old-fashioned awful large prismlike indigo wood congolese stapler\n(K) None of the above\n\nProvide your final answer as a concatenation of all the correct choices. For example, if B and C have correct adjective order, then your final answer must be \"BC\".",
    "target": "BDFHIJ"
  },
  "output": "To determine which options have the correct adjective order, we need to analyze the given sentences and extract the adjective order rules for this variant of English. Here's the observed order based on the examples:\n\n1. Age/Time (brand-new, new, old, old-fashioned, ancient, archaic)\n2. Opinion (good, repulsive, ridiculous, awful, lovely, mysterious, nice, obnoxious, terrible)\n3. Size (tiny, small, little, midsize, medium-size, normal-size, big, large, huge, enormous, massive)\n4. Shape (square, circular, rectangular, pyramidal, prismlike, spherical, triangular)\n5. Color (violet, teal, crimson, maroon, cyan, pink, indigo, magenta, green, aqua, black, white, gray, yellow)\n6. Material/Origin (canvas, leather, iron, wood, rubber, american, chinese, congolese)\n7. Purpose (drinking, whittling) - appears right before the noun\n\nNow let's evaluate each option:\n\n(A) indigo spherical brand-new lamp  \n- Incorrect: \"brand-new\" (age) should come before \"spherical\" (shape) and \"indigo\" (color).  \nCorrect order: brand-new spherical indigo lamp  \n\n(B) archaic ridiculous huge table  \n- Correct: archaic (age) → ridiculous (opinion) → huge (size)  \n\n(C) nice whittling small archaic violet iron square screwdriver  \n- Incorrect: \"archaic\" (age) should come first, \"whittling\" (purpose) should be right before noun.  \nCorrect order: archaic nice small square violet iron whittling screwdriver  \n\n(D) old awful big drill  \n- Correct: old (age) → awful (opinion) → big (size)  \n\n(E) square little pink ring  \n- Incorrect: \"little\" (size) should come before \"square\" (shape).  \nCorrect order: little square pink ring  \n\n(F) old-fashioned mysterious midsize rectangular yellow leather speaker  \n- Correct: old-fashioned (age) → mysterious (opinion) → midsize (size) → rectangular (shape) → yellow (color) → leather (material)  \n\n(G) drinking indigo cloth ancient spherical repulsive pen  \n- Incorrect: \"ancient\" (age) should come first, \"drinking\" (purpose) should be right before noun.  \nCorrect order: ancient repulsive spherical indigo cloth drinking pen  \n\n(H) archaic terrible little circular black iron american box  \n- Correct: archaic (age) → terrible (opinion) → little (size) → circular (shape) → black (color) → iron (material) → american (origin)  \n\n(I) ancient lovely normal-size pyramidal cyan rubber chinese hammer  \n- Correct: ancient (age) → lovely (opinion) → normal-size (size) → pyramidal (shape) → cyan (color) → rubber (material) → chinese (origin)  \n\n(J) old-fashioned awful large prismlike indigo wood congolese stapler  \n- Correct: old-fashioned (age) → awful (opinion) → large (size) → prismlike (shape) → indigo (color) → wood (material) → congolese (origin)  \n\nThe correct options are B, D, F, H, I, J.\n\n最终答案: BDFHIJ"
}
    bootcamp = BBEHHyperbatonbootcamp
    score = bootcamp.verify_score(case["output"], case["ground_truth"], short_penalty=False, format_penalty=False)
    print(f"Score: {score}")