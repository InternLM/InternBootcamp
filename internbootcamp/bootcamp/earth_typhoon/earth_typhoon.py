import re
import json
import numpy as np
from internbootcamp.bootcamp.base import Basebootcamp


class earth_typhoon(Basebootcamp):
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
            "请计算海平面气压，计算公式为：\n"
            "风半径（单位是 Pa） mslp = 1021.36 - 0.36*v - (v/20.16)**2\n"
            "只需返回 “mslp = ”。"
        )

    @staticmethod
    def extract_output(output: str) -> str:
        # 用正则提取“mslp = …”右侧的表达式
        m = re.search(r"mslp\s*=\s*([^\n\r]+)", output)
        return m.group(1).strip() if m else None

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
        return abs(c - identity["mslp"]) < 0.1


if __name__ == "__main__":
    bootcamp = earth_typhoon(seed=123)
    # 生成几个样例
    examples = [bootcamp.case_generator() for _ in range(3)]
    print(examples)
    print(bootcamp.prompt_func(examples[0]))
    print(bootcamp.extract_output("xxxxx relative mslp = 111222 "))
    solution = bootcamp.extract_output("xxxxx relative mslp = 984.35 ")
    print(bootcamp._verify_correction(solution, examples[0]))
    solution = bootcamp.extract_output("xxxxx relative mslp = 985.35 ")
    print(bootcamp._verify_correction(solution, examples[0]))

    for identity in examples:
        # 构造“模型”返回答案，模拟 LLM 的输出
        humidity = identity["r"]
        sol = f"{humidity:.4f}"
        # 调用 Basebootcamp 提供的 verify_score 接口进行验证
        score = bootcamp.verify_score(sol, identity, short_threshold=1e-2)
        # 打印结果
        print(json.dumps({
            "identity": identity,
            "solution": sol,
            "verify_score": score
        }, ensure_ascii=False, indent=2))