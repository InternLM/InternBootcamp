from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bsifidandstrangesubsequences.Bsifidandstrangesubsequences_reward_calculator import BsifidandstrangesubsequencesRewardCalculator

# 导入依赖库
import random
import re




class BsifidandstrangesubsequencesInteraction(BaseInteraction):
    """Bsifidandstrangesubsequences交互管理器"""
    
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
        score = BsifidandstrangesubsequencesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bsifidandstrangesubsequences问题！"""
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
    def _generate_special_case(self):
        case_type = random.choice([
            'all_positive', 'all_negative', 'mixed_signs',
            'single_element', 'with_zero_edge'
        ])

        n = random.randint(self.min_n, self.max_n)

        if case_type == 'all_positive':
            a = [random.randint(1, self.element_max) for _ in range(n)]
        elif case_type == 'all_negative':
            a = [random.randint(self.element_min, -1) for _ in range(n)]
        elif case_type == 'mixed_signs':
            a = [random.choice([-1, 1]) * random.randint(0, self.element_max) 
                for _ in range(n)]
        elif case_type == 'single_element':
            a = [random.randint(self.element_min, self.element_max)]
        else:  # with_zero_edge
            a = [0] + sorted([random.randint(-10, 10) for _ in range(n-1)])

        expected = self._compute_expected(a)
        return {'a': a, 'expected': expected}

    @staticmethod
    def _compute_expected(a):
        a_sorted = sorted(a)
        n = len(a_sorted)

        if a_sorted[0] > 0:
            return 1

        min_diff = float('inf')
        for i in range(1, n):
            diff = a_sorted[i] - a_sorted[i-1]
            min_diff = min(min_diff, diff)
            if a_sorted[i] > 0:
                return i+1 if min_diff >= a_sorted[i] else i
        return n
