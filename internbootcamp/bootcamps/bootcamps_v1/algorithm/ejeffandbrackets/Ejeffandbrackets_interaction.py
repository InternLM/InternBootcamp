from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ejeffandbrackets.Ejeffandbrackets_reward_calculator import EjeffandbracketsRewardCalculator

# 导入依赖库
import random
import re




class EjeffandbracketsInteraction(BaseInteraction):
    """Ejeffandbrackets交互管理器"""
    
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
        score = EjeffandbracketsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ejeffandbrackets问题！"""
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
    def compute_min_ink(n, m, a, b):
        class Uzi:
            def __init__(self):
                self.A = [[float('inf')] * 41 for _ in range(41)]

        def multiply(a_mat, b_mat):
            res = Uzi()
            for i in range(41):
                for j in range(41):
                    min_val = float('inf')
                    for k in range(41):
                        if a_mat.A[i][k] + b_mat.A[k][j] < min_val:
                            min_val = a_mat.A[i][k] + b_mat.A[k][j]
                    res.A[i][j] = min_val
            return res

        G = Uzi()
        for i in range(41):
            dp = [[float('inf')] * 41 for _ in range(n+1)]
            dp[0][i] = 0
            for j in range(1, n+1):
                for k in range(41):
                    if dp[j-1][k] == float('inf'):
                        continue
                    # Open bracket
                    if k < 40:
                        new_k = k + 1
                        cost = a[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
                    # Close bracket
                    if k > 0:
                        new_k = k - 1
                        cost = b[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
            for k in range(41):
                G.A[i][k] = dp[n][k]

        # Matrix exponentiation
        result = Uzi()
        for i in range(41):
            result.A[i][i] = 0
        exponent = m
        current = G
        while exponent > 0:
            if exponent % 2 == 1:
                result = multiply(result, current)
            current = multiply(current, current)
            exponent = exponent // 2
        return result.A[0][0]
