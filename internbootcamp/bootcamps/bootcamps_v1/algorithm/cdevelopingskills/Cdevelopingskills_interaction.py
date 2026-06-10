from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdevelopingskills.Cdevelopingskills_reward_calculator import CdevelopingskillsRewardCalculator

# 导入依赖库
import random
import re
import math




class CdevelopingskillsInteraction(BaseInteraction):
    """Cdevelopingskills交互管理器"""
    
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
        score = CdevelopingskillsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdevelopingskills问题！"""
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
    def _generate_edge_case(self):
        case_type = random.choice([
            'max_skills', 'zero_improvements', 'all_maxed', 
            'large_k', 'minimum_values'
        ])

        if case_type == 'max_skills':
            return {
                'n': self.max_n,
                'k': self.max_k,
                'a_list': [100] * self.max_n,
                'correct_output': 10 * self.max_n
            }
        elif case_type == 'zero_improvements':
            a_list = [random.randint(0, 100) for _ in range(random.randint(1, self.max_n))]
            return {
                'n': len(a_list),
                'k': 0,
                'a_list': a_list,
                'correct_output': sum(x//10 for x in a_list)
            }
        elif case_type == 'all_maxed':
            n = random.randint(1, self.max_n)
            return {
                'n': n,
                'k': random.randint(0, self.max_k),
                'a_list': [100]*n,
                'correct_output': 10*n
            }
        elif case_type == 'large_k':
            n = random.randint(1, 100)
            return {
                'n': n,
                'k': 10**7,
                'a_list': [0]*n,
                'correct_output': min(10*n, (sum(0//10 for _ in range(n)) + 10**7//10))
            }
        else:
            return {
                'n': 1,
                'k': 0,
                'a_list': [0],
                'correct_output': 0
            }

    @staticmethod
    def _calculate_solution(n, k, a_list):
        total = sum(x // 10 for x in a_list)
        remainder_counts = [0] * 10  # 索引对应delta值1-9（0位置不使用）

        for x in a_list:
            rem = x % 10
            if rem != 0:
                delta = 10 - rem
                if 1 <= delta <= 9:
                    remainder_counts[delta] += 1

        # 按delta从大到小处理（9到1）
        for delta in range(9, 0, -1):
            if k <= 0:
                break
            count = remainder_counts[delta]
            if count == 0:
                continue

            max_possible = min(k // delta, count)
            total += max_possible
            k -= max_possible * delta

        # 处理剩余k值
        total += k // 10
        return min(total, 10 * n)
