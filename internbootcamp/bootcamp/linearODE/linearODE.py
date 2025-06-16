import re
import json
import numpy as np
from scipy.integrate import odeint
from internbootcamp.bootcamp.base import Basebootcamp


class LinearODEBootcamp(Basebootcamp):
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
            "只需返回 “dx/dt = <表达式>”。"
        )

    @staticmethod
    def extract_output(output: str) -> str:
        # 用正则提取“dx/dt = …”右侧的表达式
        m = re.search(r"dx/dt\s*=\s*([^\n\r]+)", output)
        return m.group(1).strip() if m else None

    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        # 解析 LLM 给出的系数 c，形如 “c*x”
        sol = solution.replace(" ", "")
        match = re.fullmatch(r"([\-0-9\.eE]+)\*x", sol)
        if not match:
            return False
        c = float(match.group(1))
        # 验证 c ≈ -k
        return abs(c + identity["k"]) < 1e-2


if __name__ == "__main__":
    bootcamp = LinearODEBootcamp(seed=123)
    # 生成几个样例
    examples = [bootcamp.case_generator() for _ in range(3)]

    for identity in examples:
        # 构造“模型”返回答案，模拟 LLM 的输出
        coeff = -identity["k"]
        sol = f"{coeff:.4f}*x"
        # 调用 Basebootcamp 提供的 verify_score 接口进行验证
        score = bootcamp.verify_score(sol, identity, short_threshold=1e-2)
        # 打印结果
        print(json.dumps({
            "identity": identity,
            "solution": sol,
            "verify_score": score
        }, ensure_ascii=False, indent=2))