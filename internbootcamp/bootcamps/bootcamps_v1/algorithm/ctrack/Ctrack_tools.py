import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctrack.Ctrack_reward_calculator import CtrackRewardCalculator

# 导入依赖库
import random
import re
from heapq import heappop
from heapq import heappush

# === 源文件中的全局函数 ===

def manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def solve(n, m, k, mat):
    start = None
    end = None
    for i in range(n):
        for j in range(m):
            if mat[i][j] == 'S':
                start = (i, j)
            elif mat[i][j] == 'T':
                end = (i, j)
    if not start or not end:
        return "-1"
    br, bc = start
    er, ec = end

    heap = []
    initial_priority = manhattan(br, bc, er, ec)
    heappush(heap, (initial_priority, '', 0, br, bc, 0, ''))
    ha = {i: {j: set() for j in range(m)} for i in range(n)}

    while heap:
        priority, path, steps, r, c, cu, used_str = heappop(heap)
        if (r, c) == (er, ec):
            return path
        if used_str in ha[r][c]:
            continue
        ha[r][c].add(used_str)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                ch = mat[nr][nc]
                if ch == 'S':
                    continue
                new_steps = steps + 1
                new_priority = new_steps + manhattan(nr, nc, er, ec)
                if ch == 'T':
                    heappush(heap, (new_priority, path, new_steps, nr, nc, cu, used_str))
                else:
                    if ch in used_str:
                        new_used = used_str
                        new_cu = cu
                    else:
                        new_cu = cu + 1
                        if new_cu > k:
                            continue
                        new_used = ''.join(sorted(set(used_str) | {ch}))
                    new_path = path + ch
                    if new_used not in ha[nr][nc]:
                        heappush(heap, (new_priority, new_path, new_steps, nr, nc, new_cu, new_used))
    return "-1"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CtrackVerificationTool(BaseTool):
    """Ctrack验证工具"""
    
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
            score = CtrackRewardCalculator.verify_score(
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
            logger.error(f"CtrackVerificationTool执行错误: {str(e)}")
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

