import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cereaderdisplay.Cereaderdisplay_reward_calculator import CereaderdisplayRewardCalculator

# 导入依赖库
import random
import re
from typing import List



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CereaderdisplayVerificationTool(BaseTool):
    """Cereaderdisplay验证工具"""
    
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
            score = CereaderdisplayRewardCalculator.verify_score(
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
            logger.error(f"CereaderdisplayVerificationTool执行错误: {str(e)}")
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
    def generate_valid_commands(self, n: int) -> List[tuple]:
        """基于参考算法逻辑生成最小命令集合"""
        # 根据题目参考算法逆向生成命令
        commands = []
        # 随机选择对角线操作概率
        if random.random() < 0.3:
            diag_count = random.randint(0, n)
            commands += [(i+1, i+1) for i in random.sample(range(n), diag_count)]

        # 随机生成非对角线操作
        non_diag = [(i+1, j+1) for i in range(n) for j in range(n) if i != j]
        commands += random.sample(non_diag, k=random.randint(0, len(non_diag)))
        return list(set(commands))  # 去重后返回

    def simulate_commands(self, n: int, commands: List[tuple]) -> List[List[int]]:
        """精确模拟命令作用效果"""
        grid = [[0]*n for _ in range(n)]
        for x, y in commands:
            # 处理行x的区域
            start_col = min(x, y) - 1
            end_col = max(x, y) - 1
            for col in range(start_col, end_col + 1):
                if 0 <= col < n:
                    grid[x-1][col] ^= 1

            # 处理列y的区域
            start_row = min(x, y) - 1
            end_row = max(x, y) - 1
            for row in range(start_row, end_row + 1):
                if 0 <= row < n:
                    grid[row][y-1] ^= 1
        return grid

    @staticmethod
    def calculate_min_commands(n: int, grid: List[List[int]]) -> int:
        """完整实现参考算法"""
        a = [[0]*(n+2) for _ in range(n+2)]
        b = [[0]*(n+2) for _ in range(n+2)]
        A = [[0]*(n+2) for _ in range(n+2)]
        B = [[0]*(n+2) for _ in range(n+2)]
        ans = 0

        # 处理右上三角区域
        for J in range(n, 1, -1):
            i, j = 1, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (a[i][j] + b[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    a[i][j-1] = a[i][j] + 1
                    b[i+1][j] = b[i][j] + 1
                else:
                    a[i][j-1] = a[i][j]
                    b[i+1][j] = b[i][j]
                i += 1
                j += 1

        # 处理左下三角区域
        for J in range(2, n+1):
            i, j = n, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (A[i][j] + B[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    A[i][j+1] = A[i][j] + 1
                    B[i-1][j] = B[i][j] + 1
                else:
                    A[i][j+1] = A[i][j]
                    B[i-1][j] = B[i][j]
                i -= 1
                j -= 1

        # 处理对角线元素
        for i in range(1, n+1):
            current_value = grid[i-1][i-1]
            total = (a[i][i] + b[i][i] + A[i][i] + B[i][i]) % 2
            if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                ans += 1

        return ans
