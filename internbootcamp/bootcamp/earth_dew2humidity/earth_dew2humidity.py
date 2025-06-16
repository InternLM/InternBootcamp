import re
import json
import numpy as np
from internbootcamp.bootcamp.base import Basebootcamp


class earth_dew2humidity(Basebootcamp):
    def __init__(
        self,
        temperature_range=(-20, 40),
        temperature_dewpoint_range=(0, 10),
        seed=None
    ):
        self.temperature_range, self.temperature_dewpoint_range = temperature_range, temperature_dewpoint_range
        if seed is not None:
            np.random.seed(seed)

    def case_generator(self):
        # 1. 随机采样参数 dewpoint 和 temperature
        temperature_original = float(np.random.uniform(*self.temperature_range))
        dewpoint_original = temperature_original - float(np.random.uniform(*self.temperature_dewpoint_range))
        # 2. 计算湿度
        dewpoint = dewpoint_original + 273.15
        temperature = temperature_original + 273.15
        e = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))
        e_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))
        rh = e / e_s * 100
        return {"dewpoint": dewpoint_original, "temperature": temperature_original, "humidity": float(rh)}

    def prompt_func(self, identity) -> str:
        dewpoint = identity["dewpoint"]
        temperature = identity["temperature"]
        return (
            f"下面给出露点温度（dewpoint）={dewpoint} (摄氏度)\n温度（temperature）={temperature} (摄氏度)\n"
            "请计算湿度，计算公式为：\n"
            "dewpoint = dewpoint + 273.15，temperature = temperature + 273.15\n"
            "e = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))\n"
            "e_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))\n"
            "relative humidity = e / e_s * 100\n"
            "只需返回 “relative humidity = ”。"
        )

    @staticmethod
    def extract_output(output: str) -> str:
        # 用正则提取“relative humidity = …”右侧的表达式
        m = re.search(r"relative humidity\s*=\s*([^\n\r]+)", output)
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
        return abs(c - identity["humidity"]) < 1e-2


if __name__ == "__main__":
    bootcamp = earth_dew2humidity(seed=123)
    # 生成几个样例
    examples = [bootcamp.case_generator() for _ in range(3)]
    print(examples)
    print(bootcamp.prompt_func(examples[0]))
    print(bootcamp.extract_output("xxxxx relative humidity = 111222 "))
    solution = bootcamp.extract_output("xxxxx relative humidity = 84.79 ")
    print(bootcamp._verify_correction(solution, examples[0]))
    solution = bootcamp.extract_output("xxxxx relative humidity = 83.79 ")
    print(bootcamp._verify_correction(solution, examples[0]))

    for identity in examples:
        # 构造“模型”返回答案，模拟 LLM 的输出
        humidity = identity["humidity"]
        sol = f"{humidity:.4f}"
        # 调用 Basebootcamp 提供的 verify_score 接口进行验证
        score = bootcamp.verify_score(sol, identity, short_threshold=1e-2)
        # 打印结果
        print(json.dumps({
            "identity": identity,
            "solution": sol,
            "verify_score": score
        }, ensure_ascii=False, indent=2))