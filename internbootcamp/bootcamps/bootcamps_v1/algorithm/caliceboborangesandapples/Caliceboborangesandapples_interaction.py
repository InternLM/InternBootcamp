from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.caliceboborangesandapples.Caliceboborangesandapples_reward_calculator import CaliceboborangesandapplesRewardCalculator

# 导入依赖库
import re
import random




class CaliceboborangesandapplesInteraction(BaseInteraction):
    """Caliceboborangesandapples交互管理器"""
    
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
        score = CaliceboborangesandapplesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Caliceboborangesandapples问题！"""
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
    @staticmethod
    def vec(a, b):
        return a[0] * b[1] - a[1] * b[0]

    @classmethod
    def check_solution_exists(cls, x, y):
        a = [1, 0]
        b = [0, 1]
        while True:
            sum_a = a[0] + b[0]
            sum_b = a[1] + b[1]
            if sum_a > x or sum_b > y:
                break
            v = [x, y]
            q = cls.vec(a, v)
            w = abs(cls.vec(b, v))
            if q < w:
                c = (w - 1) // q
                b = [b[0] + c * a[0], b[1] + c * a[1]]
            elif q > w:
                c = (q - 1) // w
                a = [a[0] + c * b[0], a[1] + c * b[1]]
            else:
                return sum_a == x and sum_b == y
        return a[0] + b[0] == x and a[1] + b[1] == y

    @staticmethod
    def decompress_solution(solution):
        if solution == 'Impossible':
            return solution
        parts = re.findall(r'(\d+)([AB])', solution)
        if not parts:
            return None
        decompressed = []
        for cnt, c in parts:
            if not cnt.isdigit() or cnt.startswith('0'):
                return None
            count = int(cnt)
            if count < 1:
                return None
            decompressed.append(c * count)
        return ''.join(decompressed) if decompressed else None
