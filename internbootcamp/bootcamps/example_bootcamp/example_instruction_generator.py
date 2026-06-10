import random
import math
from typing import Dict, Any, Optional, List
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


class ExampleInstructionGenerator(BaseInstructionGenerator):
    """示例指令管理器，用于生成算术运算任务的训练数据"""
    
    def __init__(self, 
                 min_operand: int = 1, 
                 max_operand: int = 100,
                 operations: list = None,
                 num_operands_range: list = [2, 4],
                 tolerance: float = 1e-4,
                 seed: Optional[int] = None):
        """
        初始化示例指令管理器
        
        Args:
            min_operand (int): 操作数的最小值
            max_operand (int): 操作数的最大值
            operations (list): 支持的运算操作列表，默认为 ['add', 'minus', 'multiply', 'divide']
            num_operands_range (list): 操作数数量的范围，格式为[min, max]，默认为[2, 4]
            tolerance (float): 结果允许的误差容忍度，默认为1e-4
            seed (Optional[int]): 随机种子，默认为None
        """
        super().__init__()
        self.min_operand = min_operand
        self.max_operand = max_operand
        self.operations = operations or ['add', 'minus', 'multiply', 'divide']
        self.num_operands_range = num_operands_range
        self.tolerance = tolerance
        self.seed = seed
        
        if self.seed is not None:
            random.seed(self.seed)
        
        # 验证参数
        if min_operand >= max_operand:
            raise ValueError(f"最小操作数({min_operand})必须小于最大操作数({max_operand})")
        
        if not self.operations:
            raise ValueError("至少需要指定一个运算操作")
        
        if num_operands_range[0] < 2:
            raise ValueError("操作数数量必须至少为2")
        
        if num_operands_range[1] < num_operands_range[0]:
            raise ValueError("操作数数量范围必须至少为2")
        
    def case_generator(self) -> Dict[str, Any]:
        """
        生成算术运算任务案例
        
        Returns:
            Dict[str, Any]: 包含运算任务信息的字典
        """
        self.num_operands = random.randint(self.num_operands_range[0], self.num_operands_range[1])
        # 统一生成方法，适配所有操作数数量
        return self._generate_operation()
    
    def _generate_operation(self) -> Dict[str, Any]:
        """生成算术运算任务，适配任意操作数数量"""
        # 生成操作数
        operands = [random.randint(self.min_operand, self.max_operand) for _ in range(self.num_operands)]
        
        # 生成运算序列（操作数数量-1个运算）
        operation_sequence = [random.choice(self.operations) for _ in range(self.num_operands - 1)]
        
        # 构建表达式
        expression_parts = []
        
        for i, operation in enumerate(operation_sequence):
            operand = operands[i]
            next_operand = operands[i + 1]
            
            # 根据运算类型调整操作数
            if operation == "minus" and next_operand > operand:
                if operand >= 1:
                    next_operand = random.randint(1, operand)
                else:
                    next_operand = 1
                operands[i + 1] = next_operand
            elif operation == "divide":
                if next_operand == 0:
                    next_operand = random.randint(1, min(operand, 10))
                    operands[i + 1] = next_operand
            
            expression_parts.append(str(operands[i]))
            expression_parts.append(self._get_operation_symbol(operation))
        
        expression_parts.append(str(operands[-1]))
        expression = " ".join(expression_parts)
        
        # 根据表达式计算期望结果
        expected_result = self._evaluate_expression(expression)
        
        # identity
        return {
            "expression": expression,
            "expected_result": expected_result,
            "tolerance": self.tolerance
        }
    
    def prompt_func(self, identity: Dict[str, Any]) -> str:
        """
        根据任务信息生成提示语
        
        Args:
            identity (Dict[str, Any]): 任务信息
            
        Returns:
            str: 生成的提示语
        """
        expression = identity['expression']
        tolerance = identity['tolerance']
        
        prompt = f"""你是一位数学专家，擅长进行算术运算。

任务：计算表达式 {expression} 的结果，相对误差比例不超过 {tolerance}

最终答案格式：请以``json
{{
    "result": your_result
}}
``格式返回结果，且在必要时使用科学计数法（如1e-4、2.5E+3）。

计算建议：
1. 因为工具使用次数有限，请慎重选择某个计算是否使用工具。
2. 请在合适的时机运用算术工具，如需要计算大数等自信程度不高计算时才使用工具，以避免计算错误或无意义的工具调用。
3. 若需要计算的表达式较长，请在实际计算开始前，先进行计算规划，以避免计算错误和无意义的工具调用。
下面请开始计算。"""
        
        return prompt
    
    def _calculate_result(self, operand1: float, operand2: float, operation: str) -> float:
        """
        计算运算结果
        
        Args:
            operand1 (float): 第一个操作数
            operand2 (float): 第二个操作数
            operation (str): 运算操作，支持 "add", "minus", "multiply", "divide" 或 "+", "-", "*", "/"
            
        Returns:
            float: 计算结果
        """
        # 支持字符串格式的运算符
        if operation in ["add", "+"]:
            return float(operand1 + operand2)
        elif operation in ["minus", "-"]:
            return float(operand1 - operand2)
        elif operation in ["multiply", "*"]:
            return float(operand1 * operand2)
        elif operation in ["divide", "/"]:
            if operand2 == 0:
                raise ValueError("除数不能为零")
            return float(operand1 / operand2)
        else:
            raise ValueError(f"不支持的运算操作: {operation}")
    
    
    def _get_operation_symbol(self, operation: str) -> str:
        """获取运算符号"""
        symbols = {
            "add": "+",
            "minus": "-",
            "multiply": "×", 
            "divide": "÷"
        }
        return symbols.get(operation, operation)

    def _evaluate_expression(self, expression: str) -> float:
        """
        根据表达式计算结果（遵循数学运算优先级，先算乘除后算加减）
        支持直接用Python内置eval安全计算（仅限本场景简单表达式）
        
        Args:
            expression (str): 数学表达式，格式如 "5 + 3" 或 "10 × 2 ÷ 4"
            
        Returns:
            float: 计算结果
        """
        # 将表达式转换为Python可计算的格式
        python_expression = expression.replace("×", "*").replace("÷", "/")
        
        # 推荐做法：直接用Python内置eval安全计算
        # 仅允许数字、加减乘除和小数点，防止安全风险
        import re
        if not re.fullmatch(r'[\d\.\s\+\-\*\/]+', python_expression):
            raise ValueError("表达式包含非法字符，仅支持数字和加减乘除")
        try:
            result = eval(python_expression)
        except Exception as e:
            raise ValueError(f"表达式计算出错: {e}")
        return float(result)

    