from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.d1frequencyproblemeasyversion.D1frequencyproblemeasyversion_reward_calculator import D1frequencyproblemeasyversionRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re




class D1frequencyproblemeasyversionInteraction(BaseInteraction):
    """D1frequencyproblemeasyversion交互管理器"""
    
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
        score = D1frequencyproblemeasyversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个D1frequencyproblemeasyversion问题！"""
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
    def calculate_answer(a):
        """完全对齐参考代码的实现逻辑"""
        freq = defaultdict(int)
        for num in a:
            freq[num] += 1
        if not freq:
            return 0

        # 确定最大频率元素
        mx = max(freq.values())
        cnt = sum(1 for v in freq.values() if v == mx)
        ele = next(k for k, v in freq.items() if v == mx)

        # Case 1: 多个元素达到最大频率
        if cnt >= 2:
            return len(a)

        # Case 2: 单个最大频率元素时
        max_length = 0
        for candidate in range(1, 101):
            if candidate == ele:
                continue

            # 使用前缀和算法查找最长子数组
            prefix_sum = {0: -1}
            current_sum = 0
            for idx, num in enumerate(a):
                if num == ele:
                    current_sum += 1
                elif num == candidate:
                    current_sum -= 1

                if current_sum in prefix_sum:
                    max_length = max(max_length, idx - prefix_sum[current_sum])
                else:
                    prefix_sum[current_sum] = idx

        return max_length
