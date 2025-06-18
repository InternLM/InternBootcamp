import re
import json
import requests
import random
from internbootcamp.bootcamp.base import Basebootcamp
from sklearn.metrics import r2_score, root_mean_squared_error
import numpy as np
import sympy as sp
import pickle
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

class SymbolicRegressionbootcamp(Basebootcamp):
    def __init__(self, data_path='./internbootcamp/libs/symbolic_regression/train_data.pkl', sample_num_range=[64,144]):
        super().__init__()
        self.data_path = data_path
        self.sample_num_range = sample_num_range
        with open(f'{self.data_path}', 'rb') as f:
            self.formula_data = pickle.load(f)
        
    def case_generator(self) -> object:
        """
        生成一组数字和目标值。
        """
        
        i = random.choice(range(len(self.formula_data)))
        true_formula = self.formula_data[i]['formula']
        dataset = self.formula_data[i]['data']
        sample_num = np.random.randint(self.sample_num_range[0], self.sample_num_range[1])
        rand_idx = np.random.choice(dataset.shape[0], sample_num, replace=False)
        dataset = dataset[rand_idx]
        return {
            # 'id': formula_data[i]['id'],
            'true_formula': true_formula,
            'data':dataset.tolist(),
        }

    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """
        data = np.array(identity['data'])
        length_data = data.shape[0]
        split_idx = int(length_data * 0.97)
        prompt = f"""You will be provided with a set of input-output pairs. Based on these data, infer the mathematical relationship between y and multiple input variables. Please note that the possible mathematical operations include: +, -, *, /, exp, sqrt, sin, arcsin, and constant terms. The input sample data are as follows:
{change_data_to_prompt(data[:split_idx, :])}
Based on the above data, please infer the possible formula. Ensure that your inference applies to all the provided data points, and consider both linear and nonlinear combinations. Verify whether your formula applies to the following new data point and adjust it to ensure accuracy:
{change_data_to_prompt(data[split_idx:, :])}""" + """Finally, please output the formula string you inferred within \\boxed{}(e.g. \\boxed{y=sqrt(x0 + x1) / (2 * pi)}). Note that you should express mathematical formulas using Python syntax(sqrt(x0)) instead of LaTeX format(\sqrt(x_0))."""
        return prompt
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        # infer_formula = llm_translate(output, mllm='gpt-4o')  # gpt-4o Qwen2.5-vl-72b
        output = last_boxed_only_string(output)
        if output is None:
            return None
        return remove_boxed(output)
        
    @classmethod 
    def _verify_correction(self, infer_formula, gt_case, mllm='gpt-4o')->bool:
        """
        Verify the correction of the solution.
        """ 
        gt_formula = gt_case['true_formula']
        data = np.array(gt_case['data'])
        metrics = {
            # 'LLM_Score': None,
            'RMSE': None,
            'NMSE': None,   # 新增：Normalized MSE
            'SymbolicMatch': False,
            'R2': -100000.0,
        }

        # 结构评分（用 LLM）
        # metrics['LLM_Score'] = llm_evaluate(infer_formula, gt_formula, mllm=mllm)

        # 数值拟合
        try:
            func_pred, variable_names = parse_formula(infer_formula)
            func_gt, variable_names = parse_formula(gt_formula)
            var_num = len(variable_names)
            x, y_true = data[:, :var_num], data[:, -1]
        except Exception as e:
            # import traceback
            # print("Exception while parsing symbolic formulas:", e)
            # print("Infer formula:", infer_formula)
            # print("Ground truth formula:", gt_formula)
            # traceback.print_exc()
            return 0.0
        if func_pred is not None:
            try:
                x_vars = [x[:, i] for i in range(var_num)]
                y_pred = func_pred(*x_vars)
                if np.isscalar(y_pred):
                    y_pred = np.full_like(y_true, y_pred)
                ####################################################
                valid_mask = np.isfinite(y_true) & np.isfinite(y_pred)
                y_true, y_pred = y_true[valid_mask], y_pred[valid_mask]
                ####################################################
                metrics['RMSE'] = root_mean_squared_error(y_true, y_pred)
                metrics['R2'] = r2_score(y_true, y_pred)
                metrics['NMSE'] = np.mean((y_true - y_pred) ** 2) / np.var(y_true)
            except Exception as e:
                # print(f"Exception: {e}")
                try:
                    x0_vals, x1_vals = generate_samples()
                    gt_vals = func_gt(x0_vals, x1_vals)
                    pred_vals = func_pred(x0_vals, x1_vals)

                    # 去除非法值（NaN 或 inf）
                    valid_mask = np.isfinite(gt_vals) & np.isfinite(pred_vals)
                    gt_valid = gt_vals[valid_mask]
                    pred_valid = pred_vals[valid_mask]

                    # 计算 RMSE 值
                    metrics['RMSE'] = np.sqrt(np.mean((gt_valid - pred_valid) ** 2))
                    # 计算 R2 值
                    metrics['R2'] = 1 - np.sum((gt_valid - pred_valid) ** 2) / np.var(gt_valid)
                    metrics['NMSE'] = np.mean((gt_valid - pred_valid) ** 2) / np.var(gt_valid)
                except Exception as e:
                    # print(e)
                    pass
        # 判断方程等价性
        metrics['SymbolicMatch'] = is_symbolically_equivalent(infer_formula, gt_formula, var_num)

        if metrics['SymbolicMatch']:
            return 1
        else:
            return max(0, metrics['R2'])


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


if __name__ == '__main__':
    # example
    random.seed(42)  # For reproducibility
    bootcamp = SymbolicRegressionbootcamp()
    case = bootcamp.case_generator()  # 选取1个case
    print(bootcamp.prompt_func(case))
    example_answer = """这道问题的解是：\\boxed{ sqrt(x0)} hahaha"""
    print(f"answer: {example_answer}")
    example_answer = bootcamp.extract_output(example_answer)
    print(f'Extracted answer: {example_answer}')
    metrics = bootcamp._verify_correction(example_answer, case)
    print(f'GT: {case["true_formula"].ljust(40)} | Pred: {example_answer.ljust(40)} | Metrics: {metrics}')
