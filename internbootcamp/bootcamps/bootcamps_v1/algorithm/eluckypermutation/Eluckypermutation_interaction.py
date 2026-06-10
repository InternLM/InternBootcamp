from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eluckypermutation.Eluckypermutation_reward_calculator import EluckypermutationRewardCalculator

# 导入依赖库
import re
import random
from collections import deque




class EluckypermutationInteraction(BaseInteraction):
    """Eluckypermutation交互管理器"""
    
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
        score = EluckypermutationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eluckypermutation问题！"""
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
    def _calculate_expected(cls, n, k_input):
        # Generate all lucky numbers up to n
        lucky = []
        q = deque([0])
        while q:
            u = q.popleft()
            if u > n:
                continue
            if u > 0:
                lucky.append(u)
            q.append(u * 10 + 4)
            q.append(u * 10 + 7)
        lucky = sorted(lucky)

        L = min(13, n)
        s = n - L + 1
        if s < 1:
            s = 1

        # Count lucky indices before s
        pre_count = sum(1 for x in lucky if x < s)

        # Check if permutation is possible
        if L == 0 or k_input > cls._factorials[L]:
            return -1 if L > 0 else 0

        # Generate permutation suffix
        suffix = list(range(s, n+1))
        k = k_input - 1
        perm = []
        while suffix and k > 0:
            fact = cls._factorials[len(suffix)-1]
            idx = 0
            while (idx + 1) * fact <= k:
                idx += 1
            perm.append(suffix[idx])
            del suffix[idx]
            k -= idx * fact
        perm += suffix

        # Count valid positions in permutation
        count = 0
        for i in range(len(perm)):
            pos = s + i
            if pos > n:
                break
            if pos in lucky and perm[i] in lucky:
                count += 1

        return pre_count + count if len(perm) == L else -1
