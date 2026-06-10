from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dratingcompression.Dratingcompression_reward_calculator import DratingcompressionRewardCalculator

# 导入依赖库
import random
from collections import deque




class DratingcompressionInteraction(BaseInteraction):
    """Dratingcompression交互管理器"""
    
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
        score = DratingcompressionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dratingcompression问题！"""
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
    def optimized_solve(self, n, a):
        """准确高效的解法实现"""
        answer = ['0'] * n

        # 预处理k=1的情况
        k1_valid = (sorted(a) == list(range(1, n+1)))
        answer[0] = '1' if k1_valid else '0'

        # 预处理每个位置的next smaller元素
        next_smaller = [n] * n
        prev_smaller = [-1] * n
        stack = []

        for i in range(n):
            while stack and a[i] < a[stack[-1]]:
                next_smaller[stack.pop()] = i
            prev_smaller[i] = stack[-1] if stack else -1
            stack.append(i)

        # 统计每个元素作为最小值的影响范围
        min_intervals = {}
        for i in range(n):
            left = prev_smaller[i] + 1
            right = next_smaller[i] - 1
            min_intervals[a[i]] = max(min_intervals.get(a[i], 0), right - left + 1)

        # 根据定理：当且仅当存在元素只能在窗口大小>=某个值时出现
        for m in range(1, n):
            max_k = n - m + 1
            if m in min_intervals and min_intervals[m] >= m:
                for k in range(max(1, m), max_k+1):
                    if k <= min_intervals[m]:
                        answer[k-1] = '1'

        # 最终验证每个k的结果
        for k in range(1, n+1):
            m = n - k + 1
            if m < 1:
                continue
            if answer[k-1] == '1':
                # 二次验证确保正确性
                window_min = self.sliding_window_min(a, k)
                if not self.is_permutation(window_min, m):
                    answer[k-1] = '0'
        return ''.join(answer)

    @staticmethod
    def sliding_window_min(arr, k):
        """精确计算滑动窗口的最小值"""
        dq = deque()
        result = []
        for i, num in enumerate(arr):
            while dq and arr[dq[-1]] >= num:
                dq.pop()
            dq.append(i)

            if dq[0] == i - k:
                dq.popleft()

            if i >= k - 1:
                result.append(arr[dq[0]])
        return result

    @staticmethod
    def is_permutation(nums, m):
        """验证是否为1~m的排列"""
        return len(nums) == m and set(nums) == set(range(1, m+1)) and len(set(nums)) == m
