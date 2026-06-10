from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.edoegraphs.Edoegraphs_reward_calculator import EdoegraphsRewardCalculator

# 导入依赖库
import random
from functools import lru_cache
import re




class EdoegraphsInteraction(BaseInteraction):
    """Edoegraphs交互管理器"""
    
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
        score = EdoegraphsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Edoegraphs问题！"""
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
    @classmethod
    def _ensure_f(cls, n):
        while len(cls._f) <= n:
            next_val = cls._f[-1] + cls._f[-2]
            cls._f.append(next_val)

    @staticmethod
    @lru_cache(maxsize=None)
    def compute_shortest_path(a, b, n):
        if a == b:
            return 0
        if a > b:
            a, b = b, a
        if n == 0:
            return 0
        if n == 1:
            return 1

        Edoegraphsbootcamp._ensure_f(n - 1)
        fn_minus_1 = Edoegraphsbootcamp._f[n - 1]
        a_in_B = a > fn_minus_1
        b_in_B = b > fn_minus_1

        if a_in_B and b_in_B:
            new_a = a - fn_minus_1
            new_b = b - fn_minus_1
            return Edoegraphsbootcamp.compute_shortest_path(new_a, new_b, n - 2)
        elif b_in_B:
            part_b = Edoegraphsbootcamp.compute_shortest_path(1, b - fn_minus_1, n - 2)
            option1 = Edoegraphsbootcamp.compute_shortest_path(a, fn_minus_1, n - 1)
            option2 = Edoegraphsbootcamp.compute_shortest_path(a, 1, n - 1)
            part_a = min(option1, option2)
            return part_a + part_b + 1
        else:
            option1 = Edoegraphsbootcamp.compute_shortest_path(a, b, n - 1)
            optionA = Edoegraphsbootcamp.compute_shortest_path(a, fn_minus_1, n - 1) + \
                      Edoegraphsbootcamp.compute_shortest_path(1, b, n - 1) + 2
            optionB = Edoegraphsbootcamp.compute_shortest_path(a, 1, n - 1) + \
                      Edoegraphsbootcamp.compute_shortest_path(fn_minus_1, b, n - 1) + 2
            option2 = min(optionA, optionB)
            return min(option1, option2)
