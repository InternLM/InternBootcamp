from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drearrange.Drearrange_reward_calculator import DrearrangeRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class DrearrangeInteraction(BaseInteraction):
    """Drearrange交互管理器"""
    
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
        score = DrearrangeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Drearrange问题！"""
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
    def _generate_solution(original):
        """参考代码算法实现，返回解矩阵或None"""
        n, m = len(original), len(original[0])
        c = dict()  # 行最大值标记
        r = dict()  # 列最大值标记

        # 计算原矩阵的行和列最大值
        for i in range(n):
            max_row = max(original[i])
            c[max_row] = True
        for j in range(m):
            max_col = max(original[i][j] for i in range(n))
            r[max_col] = True

        ans = [[0]*m for _ in range(n)]
        q = deque()
        x = 0
        y = 0

        for num in range(n*m, 0, -1):
            is_row_max = c.get(num, False)
            is_col_max = r.get(num, False)
            x += is_row_max
            y += is_col_max

            if is_row_max or is_col_max:
                ans_x = x - 1
                ans_y = y - 1
                ans[ans_x][ans_y] = num
                # 填充队列
                if is_row_max:
                    for j in range(ans_y-1, -1, -1):
                        q.append( (ans_x, j) )
                if is_col_max:
                    for i in range(ans_x-1, -1, -1):
                        q.append( (i, ans_y) )
            else:
                if not q:
                    return None  # 无解
                i, j = q.popleft()
                ans[i][j] = num

        # 验证生成的解矩阵
        if Drearrangebootcamp._validate_solution(ans, original):
            return ans
        return None

    @classmethod
    def _validate_solution(cls, solution, original):
        """验证解矩阵是否满足所有条件"""
        # 元素唯一性
        flat = [num for row in solution for num in row]
        if len(set(flat)) != len(flat) or set(flat) != set(range(1, len(flat)+1)):
            return False

        # Bitonic验证
        for row in solution:
            if not cls.is_bitonic(row):
                return False
        for col in zip(*solution):
            if not cls.is_bitonic(col):
                return False

        # 谱集验证
        X_sol = {max(row) for row in solution}
        Y_sol = {max(col) for col in zip(*solution)}
        X_ori = {max(row) for row in original}
        Y_ori = {max(col) for col in zip(*original)}
        return X_sol == X_ori and Y_sol == Y_ori

    @staticmethod
    def is_bitonic(arr):
        if len(arr) <= 1:
            return True
        peak = arr.index(max(arr))
        # 递增部分
        for i in range(1, peak+1):
            if arr[i] <= arr[i-1]:
                return False
        # 递减部分
        for i in range(peak, len(arr)-1):
            if arr[i] <= arr[i+1]:
                return False
        return True
