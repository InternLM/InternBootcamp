import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25bd.korOperationUnicode25bd_reward_calculator import Koroperationunicode25bdRewardCalculator

# 导入依赖库
import sympy as sp
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode25bdVerificationTool(BaseTool):
    """Koroperationunicode25bd验证工具"""
    
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
            score = Koroperationunicode25bdRewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicode25bdVerificationTool执行错误: {str(e)}")
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
    def safe_generate(self, func_type):
        """生成定义域安全的函数表达式"""
        x = sp.symbols('x')

        # 控制函数生成范围
        if func_type == 'logarithm':
            base = random.choice([sp.E, 10])
            return random.randint(1,3)*sp.log(base**random.randint(1,3)*x)
        elif func_type == 'polynomial':
            return sum(random.randint(1,3)*x**i for i in range(3))
        elif func_type == 'trigonometric':
            choice = random.choice([sp.sin, sp.cos])
            return random.randint(1,3)*choice(random.randint(1,3)*x)
        else:  # 指数函数
            return random.randint(1,3)*sp.exp(random.randint(1,3)*x)

    def generate_case_components(self):
        """生成合法的问题组件"""
        x = sp.symbols('x')
        for _ in range(100):  # 尝试次数限制
            # 控制函数类型组合
            f_type = random.choice(['polynomial', 'trigonometric', 'exponential'])
            g_type = random.choice(['polynomial', 'trigonometric', 'logarithm'])

            f_expr = self.safe_generate(f_type)
            g_expr = self.safe_generate(g_type)

            # 计算二阶导数
            try:
                g_double_prime = sp.diff(g_expr, x, 2)
            except:
                continue

            # 生成合法的x值
            x_value = self.find_valid_x(f_expr, g_expr)
            if x_value is None:
                continue

            return f_expr, g_expr, g_double_prime, x_value

        # 保底返回
        return x, sp.sin(x), 0, 1.0

    def find_valid_x(self, f_expr, g_expr):
        """寻找满足所有条件的x值"""
        x = sp.symbols('x')
        for _ in range(100):
            # 根据函数类型调整取值范围
            if any(func.has(sp.log(x)) for func in [g_expr]):
                x_candidate = random.uniform(0.1, 5)
            else:
                x_candidate = random.uniform(-3, 3)

            try:
                f_expr.subs(x, x_candidate)
                g_expr.subs(x, x_candidate)
                return round(x_candidate, 2)
            except:
                continue
        return None
