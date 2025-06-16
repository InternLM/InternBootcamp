import re
import json
import numpy as np
from scipy.integrate import odeint
from internbootcamp.bootcamp.base import Basebootcamp


class LinearODEbootcamp(Basebootcamp):
    def __init__(
        self,
        k_range=(0.1, 1.0),
        x0_range=(0.5, 2.0),
        t_span=(0, 5),
        n_points=50,
        seed=None
    ):
        self.k_range, self.x0_range = k_range, x0_range
        self.t0, self.t1 = t_span
        self.n_points = n_points
        if seed is not None:
            np.random.seed(seed)

    def case_generator(self):
        # 1. 随机采样参数 k 和初始值 x0
        k = float(np.random.uniform(*self.k_range))
        x0 = float(np.random.uniform(*self.x0_range))
        # 2. 构造时间序列并模拟 dx/dt = -k * x
        t = np.linspace(self.t0, self.t1, self.n_points).tolist()
        def model(x, t_val):
            return -k * x
        x = odeint(model, x0, t).flatten().tolist()
        return {"t": t, "x": x, "k": k}

    def prompt_func(self, identity) -> str:
        # 将 (t, x) 对格式化为提示
        points = ", ".join(f"({t:.2f}, {x:.2f})"
                           for t, x in zip(identity["t"], identity["x"]))
        return (
            f"下面给出变量 x(t) 的观测数据点：\n{points}\n\n"
            "请找出其满足的微分方程，形式为：dx/dt = f(x)。\n"
            "以dx/dt = <表达式>格式表示你的答案。"
            "并且使用[answer]标签包裹你的最终答案, 例如[answer]dx/dt = <表达式>[/answer]."
        )

    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            raw_expr = last_match.replace('dx/dt = ', '').strip()
            expr = raw_expr.strip()
            pattern = re.fullmatch(
                r"""
                ([+-]?\s*            # 可选的正负号，后可带空格
                (?:\d+(?:\.\d*)?     # 整数或小数点后数字
                |\.\d+)?             # 或只有小数部分
                (?:[eE][+-]?\d+)?    # 可选的科学计数部分
                )?                   # 整个系数是可选的（允许直接 x 或 -x）
                \s*\*?\s*            # 可选乘号，前后允许空格
                [xX]                 # x 或 X
                """,
                expr,
                re.VERBOSE
            )

            if pattern:
                raw = pattern.group(1)
                if raw is None or raw.strip() == '':
                    return 1.0
                elif raw.strip() in ['+', '+1']:
                    return 1.0
                elif raw.strip() in ['-', '-1']:
                    return -1.0
                else:
                    return float(raw)
            else:
                return None 
        except ValueError:
            return None

    @classmethod
    def _verify_correction(cls, solution: float, identity: dict) -> bool:
        delta = abs(solution + identity["k"])
        return delta < 1e-2


if __name__ == "__main__":
    bootcamp = LinearODEbootcamp(seed=123)
    # 生成几个样例
    examples = [bootcamp.case_generator() for _ in range(3)]

    for identity in examples:
        # 构造“模型”返回答案，模拟 LLM 的输出
        coeff = -identity["k"]
        sol = f"[answer]dx/dt = {coeff:.2f}*x[/answer]"
        # 调用 Basebootcamp 提供的 verify_score 接口进行验证
        score = bootcamp.verify_score(sol, identity, short_penalty=False,format_penalty=False)
        # 打印结果
        print(json.dumps({
            "identity": identity,
            "solution": sol,
            "extract_output": LinearODEbootcamp.extract_output(sol),
            "verify_score": score
        }, ensure_ascii=False, indent=2))