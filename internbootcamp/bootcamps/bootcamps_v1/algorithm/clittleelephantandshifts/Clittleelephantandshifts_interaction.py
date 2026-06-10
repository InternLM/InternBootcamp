from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clittleelephantandshifts.Clittleelephantandshifts_reward_calculator import ClittleelephantandshiftsRewardCalculator

# 导入依赖库
import random
from heapq import heappop
from heapq import heappush




class ClittleelephantandshiftsInteraction(BaseInteraction):
    """Clittleelephantandshifts交互管理器"""
    
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
        score = ClittleelephantandshiftsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Clittleelephantandshifts问题！"""
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
    def compute_expected(n, a, b):
        # Convert to 0-based and precompute positions in a
        a_pos = {num: idx for idx, num in enumerate(a)}
        ia = [0] * n
        for idx, num in enumerate(a):
            ia[num-1] = idx  # since a contains 1-based numbers

        # Convert b to 0-based indices in b list
        b_zero = [num-1 for num in b]  # to 0-based internally

        ans = [float('inf')] * n
        # Priority queues store (-distance, original index)
        pq_left = []  # elements where i <= ia[b[i]]
        pq_right = []  # elements where i > ia[b[i]]

        for i in range(n):
            current_b = b_zero[i]
            pos_in_a = ia[current_b]
            diff = i - pos_in_a
            if i <= pos_in_a:
                heappush(pq_left, (-(pos_in_a - i), i))
            else:
                heappush(pq_right, (-(i - pos_in_a), i))
            ans[0] = min(ans[0], abs(i - pos_in_a))

        for k in range(1, n):
            # Move elements from previous shift out of the window
            prev_idx = k - 1
            current_b_prev = b_zero[prev_idx]
            pos_in_a_prev = ia[current_b_prev]
            shifted_pos = (prev_idx - (k-1)) % n  # was considered for previous k-1 shifts

            new_diff_for_next = (n - pos_in_a_prev - 1) + k
            heappush(pq_right, (-new_diff_for_next, n + prev_idx))

            # Remove elements from pq_right that are now in pq_left due to shift
            while pq_right and -pq_right[0][0] - k < 0:
                dist, idx = heappop(pq_right)
                new_dist = - (-dist - k)
                heappush(pq_left, (-new_dist, idx))

            # Remove elements from pq_left that are out of the valid indices (>=k)
            while pq_left and pq_left[0][1] < k:
                heappop(pq_left)

            current_min = float('inf')
            if pq_left:
                current_min = min(current_min, -pq_left[0][0] + k)
            if pq_right:
                current_min = min(current_min, -pq_right[0][0] - k)

            ans[k] = current_min

        return ans
