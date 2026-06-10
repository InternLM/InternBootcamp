import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cfractaldetector.Cfractaldetector_reward_calculator import CfractaldetectorRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CfractaldetectorVerificationTool(BaseTool):
    """Cfractaldetector验证工具"""
    
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
            score = CfractaldetectorRewardCalculator.verify_score(
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
            logger.error(f"CfractaldetectorVerificationTool执行错误: {str(e)}")
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
    def generate_fractal(mask, steps):
        size = 2 ** (steps + 1)
        grid = [['.' for _ in range(size)] for _ in range(size)]
        kx = [0, 0, 1, 1]
        ky = [0, 1, 0, 1]

        def fill(x, y, block_size, current_step, is_black):
            if current_step > steps:
                for i in range(x, x + block_size):
                    for j in range(y, y + block_size):
                        grid[i][j] = '*' if is_black else '.'
                return

            new_size = block_size // 2
            for q in range(4):
                dx = kx[q] * new_size
                dy = ky[q] * new_size
                nx = x + dx
                ny = y + dy
                if is_black:
                    fill(nx, ny, new_size, current_step + 1, True)
                else:
                    bit = (mask >> (3 - q)) & 1
                    sub_black = bit == 1
                    fill(nx, ny, new_size, current_step + 1, sub_black)

        fill(0, 0, size, 0, False)
        return grid

    @staticmethod
    def count_valid_fractals(grid):
        n, m = len(grid), len(grid[0]) if grid else 0
        if n < 8 or m < 8:
            return 0

        # 修正二维前缀和计算
        sum_ = [[0]*(m+1) for _ in range(n+1)]
        for i in range(1, n+1):
            for j in range(1, m+1):
                sum_[i][j] = sum_[i-1][j] + sum_[i][j-1] - sum_[i-1][j-1] + (1 if grid[i-1][j-1] == '*' else 0)

        MAX_ST = 10
        K = 16
        # 调整DP数组维度顺序
        dp = [[[[False]*m for _ in range(n)] for __ in range(K)] for ___ in range(MAX_ST)]

        # 初始化st=0的状态
        for i in range(n):
            for j in range(m):
                for mask in range(K):
                    dp[0][mask][i][j] = (grid[i][j] == '.')

        # 动态规划状态转移
        for st in range(1, MAX_ST):
            w = 1 << (st-1)
            if 2*w > min(n, m):
                continue
            for mask in range(K):
                for i in range(n - 2*w +1):
                    for j in range(m - 2*w +1):
                        valid = True
                        for q in range(4):
                            x = i + (q//2)*w
                            y = j + (q%2)*w
                            if (mask >> (3-q)) & 1:  # 检查当前象限是否需要全黑
                                # 计算区域全黑的正确公式
                                a, b = x+1, y+1
                                c, d = x + w, y + w
                                total = sum_[c][d] - sum_[a-1][d] - sum_[c][b-1] + sum_[a-1][b-1]
                                if total != w*w:
                                    valid = False
                                    break
                            else:
                                if x >=n or y >=m or not dp[st-1][mask][x][y]:
                                    valid = False
                                    break
                        dp[st][mask][i][j] = valid

        # 统计有效解
        count = 0
        for st in range(2, MAX_ST):
            w = 1 << st
            if 2*w > min(n, m):
                continue
            for i in range(n - 2*w +1):
                for j in range(m - 2*w +1):
                    for mask in range(K):
                        if dp[st][mask][i][j]:
                            count +=1
        return count
