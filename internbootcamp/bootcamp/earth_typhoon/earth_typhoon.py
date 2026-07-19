import re
import json
import numpy as np
from internbootcamp.bootcamp.base import Basebootcamp


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


def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]


class Earthtyphoonbootcamp(Basebootcamp):
    def __init__(
        self,
        v_range=(0, 100),
        seed=None
    ):
        self.v_range = v_range
        if seed is not None:
            np.random.seed(seed)

    def case_generator(self):
        # 1. 随机采样参数 v
        v = float(np.random.uniform(*self.v_range))
        mslp = 1021.36 - 0.36*v - (v/20.16)**2
        return {"v": v, "mslp": mslp}

    def prompt_func(self, identity) -> str:
        v = identity["v"]
        return (
            f"下面给出最大风速（v）={v} (kt)\n\n"
            "请计算平均海平面气压（单位是 百帕 hPa），计算公式为：\n"
            "mslp = 1021.36 - 0.36*v - (v/20.16)**2\n"
            "请将最终计算结果放入\\boxed{}中，例如：\\boxed{1234.56}"
        )

    @staticmethod
    def extract_output(output: str) -> str:
        # 用正则提取“mslp = …”右侧的表达式
        output = last_boxed_only_string(output)
        if output is None:
            return ""
        return remove_boxed(output)

    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        # 解析 LLM 给出的系数 c，形如 “c*x”
        solution = solution.replace(" ", "")
        try:
            c = float(solution)
        except:
            return False
        # print(c)
        # 验证 c ≈ k
        if abs(c - identity["mslp"]) < 1e-2:
            return 1
        return 0


if __name__ == "__main__":
    bootcamp = Earthtyphoonbootcamp(seed=123)
    # 生成几个样例
    examples = [bootcamp.case_generator() for _ in range(3)]
    print(examples)
    print(bootcamp.prompt_func(examples[0]))
    solution = bootcamp.extract_output("xxxxx relative mslp = \\boxed{984.35},that is true ")
    print(solution ,bootcamp._verify_correction(solution, examples[0]))
    solution = bootcamp.extract_output("xxxxx relative mslp = \\boxed{985.35}, haha ")
    print(solution, bootcamp._verify_correction(solution, examples[0]))

    # for identity in examples:
    #     # 构造“模型”返回答案，模拟 LLM 的输出
    #     humidity = identity["v"]
    #     sol = f"{humidity:.4f}"
    #     # 调用 Basebootcamp 提供的 verify_score 接口进行验证
    #     score = bootcamp.verify_score(sol, identity, short_threshold=1e-2)
    #     # 打印结果
    #     print(json.dumps({
    #         "identity": identity,
    #         "solution": sol,
    #         "verify_score": score
    #     }, ensure_ascii=False, indent=2))