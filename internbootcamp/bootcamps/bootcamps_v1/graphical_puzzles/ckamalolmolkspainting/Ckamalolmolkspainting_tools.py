import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ckamalolmolkspainting.Ckamalolmolkspainting_reward_calculator import CkamalolmolkspaintingRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n, m, grid):
    a = [[1 if cell == 'X' else 0 for cell in row] for row in grid]
    original_n, original_m = n, m

    def work(a, n, m):
        found = False
        x = y = 0
        for i in range(n):
            for j in range(m):
                if a[i][j]:
                    x, y = i, j
                    found = True
                    break
            if found:
                break
        if not found:
            return n * m * 2  # 无效情况

        lenx = 1
        while x + lenx < n and a[x + lenx][y]:
            lenx += 1

        l = 0
        r = 1
        while y + r < m and a[x][y + r]:
            r += 1
        r += 1  # 初始右边界

        def all_cells(x_check, y_check, lx_check, ly_check):
            if x_check < 0 or y_check < 0 or x_check + lx_check > n or y_check + ly_check > m:
                return False
            for i in range(x_check, x_check + lx_check):
                for j in range(y_check, y_check + ly_check):
                    if not a[i][j]:
                        return False
            return True

        def chk(lx_brush, ly_brush):
            if not all_cells(x, y, lx_brush, ly_brush):
                return 2
            b = [[0] * m for _ in range(n)]
            for i in range(x, x + lx_brush):
                for j in range(y, y + ly_brush):
                    b[i][j] = 1

            current_x, current_y = x, y
            t = 0  # 移动方向标记，0右优先，1下优先
            while True:
                can_right = False
                if current_y + ly_brush < m:
                    can_right = all_cells(current_x, current_y + ly_brush, lx_brush, 1)
                can_down = False
                if current_x + lx_brush < n:
                    can_down = all_cells(current_x + lx_brush, current_y, 1, ly_brush)
                
                if not can_right and not can_down:
                    break

                moved = False
                if can_right and (t == 0 or (not can_down and t == 1)):
                    valid = True
                    for i in range(current_x):
                        if a[i][current_y + ly_brush]:
                            valid = False
                            break
                    if valid:
                        for i in range(current_x, current_x + lx_brush):
                            b[i][current_y + ly_brush] = 1
                        current_y += 1
                        moved = True
                        t = 0
                    else:
                        return 0  # 无效移动路径

                if not moved and can_down and (t == 1 or (not can_right and t == 0)):
                    valid = True
                    for j in range(current_y):
                        if a[current_x + lx_brush][j]:
                            valid = False
                            break
                    if valid:
                        for j in range(current_y, current_y + ly_brush):
                            b[current_x + lx_brush][j] = 1
                        current_x += 1
                        moved = True
                        t = 1
                    else:
                        return 0  # 无效移动路径

                if not moved:
                    break  # 无法移动

            for i in range(n):
                for j in range(m):
                    if a[i][j] != b[i][j]:
                        return 2
            return 1

        left, right = 1, r
        answer = n * m * 2
        while left <= right:
            mid = (left + right) // 2
            res = chk(lenx, mid)
            if res == 1:
                answer = lenx * mid
                right = mid - 1
            elif res == 0:  # 路径无效，需要扩大ly
                left = mid + 1
            else:  # 覆盖不全，需要扩大ly
                left = mid + 1
        return answer if answer <= n * m else n * m * 2

    res1 = work(a, n, m)
    # 转置处理列优先的情况
    a_transposed = [list(row) for row in zip(*a)]
    res2 = work(a_transposed, m, n)
    min_res = min(res1, res2)
    return min_res if min_res <= max(n, m) * max(n, m) else -1

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CkamalolmolkspaintingVerificationTool(BaseTool):
    """Ckamalolmolkspainting验证工具"""
    
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
            score = CkamalolmolkspaintingRewardCalculator.verify_score(
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
            logger.error(f"CkamalolmolkspaintingVerificationTool执行错误: {str(e)}")
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

