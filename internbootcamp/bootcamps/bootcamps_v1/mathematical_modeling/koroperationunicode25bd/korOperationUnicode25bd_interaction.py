from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25bd.korOperationUnicode25bd_reward_calculator import Koroperationunicode25bdRewardCalculator

# 导入依赖库
import sympy as sp
import random




class Koroperationunicode25bdInteraction(BaseInteraction):
    """Koroperationunicode25bd交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = Koroperationunicode25bdRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode25bd问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
