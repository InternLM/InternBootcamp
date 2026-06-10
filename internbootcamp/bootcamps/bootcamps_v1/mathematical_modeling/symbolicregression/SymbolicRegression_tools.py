import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.symbolicregression.SymbolicRegression_reward_calculator import SymbolicregressionRewardCalculator

# 导入依赖库
import re
import json
import requests
import random
from sklearn.metrics import r2_score
from sklearn.metrics import root_mean_squared_error
import numpy as np
import sympy as sp
import pickle

# === 源文件中的全局函数 ===

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

def _send_request(messages, mllm='gpt-4o'):
    URL = f"" # TODO your API URL
    API_KEY = "" # TODO your API key
    if URL is None or API_KEY is None:
        raise ValueError("Please provide your API URL or API key.")
    HEADERS = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    MLLM_claudeshop = {
        'gpt-4o': 'chatgpt-4o-latest',
    }
    model = MLLM_claudeshop[mllm]
    count = 0
    while True and count < 20:
        count += 1
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1024
        })
        session = requests.Session()
        session.keep_alive = False
        response = session.post(URL, headers=HEADERS, data=payload, verify=True)
        try:
            content = response.json()['choices'][0]['message']['content']
            break
        except Exception as e:
            # print(f"Error: {e}, {response.json()}")
            pass
    return content

def clean_formula_string(formula_str):
    # 1. 删除 Markdown 残留符号
    formula_str = formula_str.replace('×', '*').replace('·', '*').replace('÷', '/')
    formula_str = formula_str.replace('−', '-').replace('^', '**')
    formula_str = formula_str.replace('“', '"').replace('”', '"').replace('’', "'")

    # 2. 去除 markdown 反引号 ``` 和 $ 符号
    formula_str = formula_str.replace('`', '').replace('$', '').strip()

    # 3. 提取第一行公式（防止有多行解释性输出）
    formula_str = formula_str.split('\n')[0].strip()

    # 4. 用正则去除非合法字符（保留基本数学表达式）
    formula_str = re.sub(r'[^\w\s\+\-\*/\^\=\.\(\)]', '', formula_str)

    # 5. 确保左右去空格
    return formula_str.strip()

def llm_translate(dirty_formula, mllm='gpt-4o'):
    content = f'''
        This is a language model's judgment on a mathematical formula. Please help me extract the mathematical formula from this judgment and return it:
        {dirty_formula}
        Please serve pi as pi and use x0, x1, x2,... to represent the variable names.
        ONLY RETURN THE FORMULA STRING (Not LATEX).
    '''
    messages = [{"role": "user", "content": content}]
    clean_formula = _send_request(messages, mllm=mllm)
    return clean_formula

def llm_evaluate(inferred_formula, true_formula, mllm='gpt-4o'):
    content = f'''
        You are given two mathematical formulas. Your task is to evaluate how structurally similar they are, and return a similarity score between 0 and 1.

        The score should reflect how closely the formulas match in terms of:
        - Mathematical operations and structure (e.g., same use of +, *, sin, etc.)
        - Term arrangement and complexity
        - Overall symbolic expression and intent

        A score of:
        - 1 means the formulas are structurally identical or mathematically equivalent
        - Around 0.8-0.9 means they are very similar but not identical
        - Around 0.5 means moderately similar (e.g., same overall shape but different terms)
        - Near 0 means structurally unrelated formulas

        Do not consider numerical evaluation or specific input values — only the symbolic structure and mathematical form.

        Formulas:
        Inferred Formula: {inferred_formula}
        True Formula: {true_formula}

        ONLY RETURN [THE SIMILARITY SCORE]
    '''
    messages = [{"role": "user", "content": content}]
    similarity_score = _send_request(messages, mllm=mllm)
    return similarity_score[-4:]

def is_symbolically_equivalent(formula1, formula2, n_var=2):
    try:
        x = [sp.Symbol(f'x{i}') for i in range(n_var)]

        expr1 = sp.sympify(formula1.split('=')[1] if '=' in formula1 else formula1)
        expr2 = sp.sympify(formula2.split('=')[1] if '=' in formula2 else formula2)

        return sp.simplify(expr1 - expr2) == 0
    except Exception:
        return False

def parse_formula(formula_str: str):
    try:
        if '=' in formula_str:
            expr_str = formula_str.split('=', 1)[1].strip()
        else:
            expr_str = formula_str.strip()

        if not expr_str:
            # print(f"[Parse Error] 公式字符串为空或剥离后为空: '{formula_str}'")
            return None

        local_dict = {"sin": sp.sin, "cos": sp.cos, "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log,
                      "arccos": sp.acos, "arcsin": sp.asin, "tan": sp.tan, "pi": sp.pi}
        expr = sp.sympify(expr_str, locals=local_dict)
        # 生成定义域
        variable_names = sorted([str(sym) for sym in expr.free_symbols])
        symbols = [sp.Symbol(name) for name in variable_names]
        for sym in symbols:
            local_dict[str(sym)] = sym
        # 转换为 numpy 表达式
        numpy_modules = ['numpy', {'sqrt': np.sqrt, 'exp': np.exp, 'sin': np.sin, 'cos': np.cos, 'log': np.log,
                                     'arcsin': np.arcsin, 'arccos': np.arccos, 'tan': np.tan, 'pi': np.pi}]
        func = sp.lambdify(symbols, expr, modules=numpy_modules)
        return func, variable_names
    except (SyntaxError, TypeError, AttributeError, sp.SympifyError) as e:
        # print(f'[Parse Error] 无法解析公式 "{formula_str}": {e}')
        # import traceback
        # traceback.print_exc()
        return None
    except Exception as e:
        # print(f'[Parse Error] 解析公式 "{formula_str}" 时发生意外错误: {e}')
        return None  

def generate_samples(x0_range=(-10, 10), x1_range=(-10, 10), num_points=1000):
    """
    返回在定义域内的样本点 (x0, x1)
    """
    x0_range = np.linspace(x0_range[0], x0_range[1], num_points)
    x1_range = np.linspace(x1_range[0], x1_range[1], num_points)
    x0, x1 = np.meshgrid(x0_range, x1_range)
    x0_vals = x0.flatten()
    x1_vals = x1.flatten()
    return x0_vals, x1_vals

def change_data_to_prompt(points):
    data_prompt = ""
    for i in range(points.shape[0]):  # 这行要根据变量数量改
        if points.shape[1] == 2:
            data_prompt += f"""x0={points[i, 0]:.5f}, y={points[i, 1]:.5f}\n"""
        elif points.shape[1] == 3:
            data_prompt += f"""x0={points[i, 0]:.5f}, x1={points[i, 1]:.5f}, y={points[i, 2]:.5f}\n"""
        elif points.shape[1] == 4:
            data_prompt += f"""x0={points[i, 0]:.5f}, x1={points[i, 1]:.5f}, x2={points[i, 2]:.5f}, y={points[i, 3]:.5f}\n"""
        elif points.shape[1] == 5:
            data_prompt += f"""x0={points[i, 0]:.5f}, x1={points[i, 1]:.5f}, x2={points[i, 2]:.5f}, x3={points[i, 3]:.5f}, y={points[i, 4]:.5f}\n"""
    return data_prompt

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class SymbolicregressionVerificationTool(BaseTool):
    """Symbolicregression验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = SymbolicregressionRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"SymbolicregressionVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

