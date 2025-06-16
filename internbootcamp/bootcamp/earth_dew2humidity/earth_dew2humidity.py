import re
import json
import numpy as np
from internbootcamp.bootcamp.base import Basebootcamp


class Earthdew2humiditybootcamp(Basebootcamp):
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
            "以\\boxed{relative humidity = ？%} 格式输出你的最终答案，例如\\boxed{relative humidity = your answer%}。"
        )

    @staticmethod
    def extract_output(output):
        boxed_start_index = output.find('\\boxed{')
        boxed_end_index = output.rfind('}', boxed_start_index)
        boxed = output[boxed_start_index + 7:boxed_end_index]
        # print(boxed)
        # 提取数字（含小数点）
        number_match = re.findall(r'\d+(?:\.\d+)?', boxed)[-1]
        if number_match:
            try:
                return float(number_match)
            except ValueError:
                return None
        return None

    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        # 解析 LLM 给出的系数 c，形如 “c*x”
        try:
            c = float(solution)
        except:
            return False
        # print(c)
        # 验证 c ≈ k
        return abs(c - identity["humidity"]) < 1e-1


if __name__ == "__main__":
    # bootcamp = Earthdew2humiditybootcamp(seed=123)
    # # 生成几个样例
    # examples = [bootcamp.case_generator() for _ in range(3)]
    # print(examples)
    # print(bootcamp.prompt_func(examples[0]))
    # print(bootcamp.extract_output("xxxxx relative humidity = 111222 "))
    # solution = bootcamp.extract_output("xxxxx relative humidity = 84.79 ")
    # print(bootcamp._verify_correction(solution, examples[0]))
    # solution = bootcamp.extract_output("[answer]relative humidity = relative humidity = 83.79%[/answer]")
    # print(bootcamp._verify_correction(solution, examples[0]))

    # for identity in examples:
    #     # 构造“模型”返回答案，模拟 LLM 的输出
    #     humidity = identity["humidity"]
    #     sol = f"\\boxed{{relative humidity = {humidity:.4f}%}}"
    #     # 调用 Basebootcamp 提供的 verify_score 接口进行验证
    #     score = bootcamp.verify_score(sol, identity, short_penalty=False,format_penalty=False)
    #     # 打印结果
    #     print(json.dumps({
    #         "identity": identity,
    #         "solution": sol,
    #         "extract_output": Earthdew2humiditybootcamp.extract_output(sol),
    #         "verify_score": score
    #     }, ensure_ascii=False, indent=2))
    case = {
  "id": 49,
  "prompt": "下面给出露点温度（dewpoint）=13.225845924995145 (摄氏度)\n温度（temperature）=13.427933720529904 (摄氏度)\n请计算湿度，计算公式为：\ndewpoint = dewpoint + 273.15，temperature = temperature + 273.15\ne = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))\ne_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))\nrelative humidity = e / e_s * 100\n以 \\boxed{relative humidity = ？%} 格式输出你的最终答案，例如 \\boxed{relative humidity = your answer%}。",
  "output_len": 130,
  "score": 0,
  "ground_truth": {
    "dewpoint": 13.225845924995145,
    "temperature": 13.427933720529904,
    "humidity": 98.69041013549538
  },
  "output": "首先，将露点温度和温度转换为绝对温度。露点温度为13.225845924995145摄氏度，加上273.15得到露点温度的绝对温度，即为286.37584592499516 K。同样地，温度13.427933720529904摄氏度加上273.15，得到绝对温度286.5779337205299 K。\n\n接下来，计算露点温度对应的饱和水蒸气压。使用公式e = 611.2 * np.exp(17.67 * (dewpoint - 273.15) / (dewpoint - 29.65))，其中dewpoint为286.37584592499516 K。计算得到e的值约为654.54 hPa。\n\n然后，计算温度对应的饱和水蒸气压。使用公式e_s = 611.2 * np.exp(17.67 * (temperature - 273.15) / (temperature - 29.65))，其中temperature为286.5779337205299 K。计算得到e_s的值约为656.53 hPa。\n\n最后，计算相对湿度。相对湿度等于e除以e_s，再乘以100，即(654.54 / 656.53) * 100 ≈ 99.69%。\n</think>\n\n好的，我们按照给定的公式计算相对湿度。\n\n**步骤如下：**\n\n1. **将露点温度和温度转换为绝对温度：**\n   \n   \\[\n   \\text{dewpoint} = 13.225845924995145\\,^\\circ\\text{C} + 273.15 = 286.37584592499516\\,\\text{K}\n   \\]\n   \n   \\[\n   \\text{temperature} = 13.427933720529904\\,^\\circ\\text{C} + 273.15 = 286.5779337205299\\,\\text{K}\n   \\]\n\n2. **计算露点温度对应的饱和水蒸气压 \\( e \\)：**\n   \n   \\[\n   e = 611.2 \\times \\exp\\left(\\frac{17.67 \\times (286.37584592499516 - 273.15)}{286.37584592499516 - 29.65}\\right) \\approx 654.54\\,\\text{hPa}\n   \\]\n\n3. **计算温度对应的饱和水蒸气压 \\( e_s \\)：**\n   \n   \\[\n   e_s = 611.2 \\times \\exp\\left(\\frac{17.67 \\times (286.5779337205299 - 273.15)}{286.5779337205299 - 29.65}\\right) \\approx 656.53\\,\\text{hPa}\n   \\]\n\n4. **计算相对湿度：**\n   \n   \\[\n   \\text{relative humidity} = \\left( \\frac{e}{e_s} \\right) \\times 100 = \\left( \\frac{654.54}{656.53} \\right) \\times 100 \\approx 99.69\\%\n   \\]\n\n**最终答案：**\n\n\\[\n\\boxed{\\text{relative humidity} = 99.69\\%}\n\\]"
}
    print(Earthdew2humiditybootcamp.extract_output(case['output']))