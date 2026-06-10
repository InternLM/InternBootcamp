import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drearrange.Drearrange_reward_calculator import DrearrangeRewardCalculator

# 导入依赖库
import random
import re
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DrearrangeVerificationTool(BaseTool):
    """Drearrange验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = DrearrangeRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"DrearrangeVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
