from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cluckypermutation.Cluckypermutation_reward_calculator import CluckypermutationRewardCalculator

# 导入依赖库
from math import factorial
import random
import re




class CluckypermutationInteraction(BaseInteraction):
    """Cluckypermutation交互管理器"""
    
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
        score = CluckypermutationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cluckypermutation问题！"""
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
    def calculate_answer(cls, n, k):
        # 验证排列是否存在
        m = 1
        while True:
            try:
                if factorial(m) >= k:
                    break
                m += 1
                if m > min(20, n+1):  # 防止无限循环
                    break
            except OverflowError:
                break
        if m > n:
            return -1

        # 生成排列后缀部分
        suffix = list(range(n-m+1, n+1))
        remaining_k = k
        for i in range(m):
            available = sorted(suffix[i:])
            slot_size = factorial(m - i - 1)

            # 计算当前块的位置
            pos = 0
            while remaining_k > slot_size:
                remaining_k -= slot_size
                pos += 1
                if pos >= len(available):
                    return -1  # 防止越界

            # 交换元素位置
            available[0], available[pos] = available[pos], available[0]
            # 保持后续元素有序
            suffix = suffix[:i] + available

        # 计算幸运数数量
        count = cls.count_lucky_numbers(n - m)

        # 检查后缀部分
        for idx, num in enumerate(suffix, start=n-m+1):
            if cls.is_lucky(idx) and cls.is_lucky(num):
                count += 1

        return count

    @staticmethod
    def is_lucky(x):
        return x > 0 and all(c in {'4', '7'} for c in str(x))

    @classmethod
    def count_lucky_numbers(cls, max_num):
        """使用BFS生成所有幸运数"""
        count = 0
        queue = ['4', '7']
        while queue:
            num = queue.pop(0)
            value = int(num)
            if value > max_num:
                continue
            count += 1
            queue.append(num + '4')
            queue.append(num + '7')
        return count
