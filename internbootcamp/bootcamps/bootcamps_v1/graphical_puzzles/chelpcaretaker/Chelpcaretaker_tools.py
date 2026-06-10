import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.chelpcaretaker.Chelpcaretaker_reward_calculator import ChelpcaretakerRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_turboplow(n, m):
    rf = False
    if n > m:
        n, m, rf = m, n, True
    w = -1 if m == 9 else 1
    Z = ((7, 2, 2), (2, 2, 7), (1, 7, 1), (4, 7, 4))
    Zx = []
    for x in range(n):
        current = []
        for i, j, k in Z:
            current.append((i << x, j << x, k << x))
        Zx.append(current)
    q = [tuple([0] * m)]
    d = {q[0]: 0}
    pr = {q[0]: None}

    def put(p, x, y, i, j, k):
        res = False
        pp = list(p)
        for vi, vj, vk in Zx[x]:
            if (i & vi) or (j & vj) or (k & vk):
                continue
            pp[y] = i | vi
            if y + 1 >= m:
                continue
            pp[y+1] = j | vj
            if y + 2 >= m:
                continue
            pp[y+2] = k | vk
            pc = tuple(pp)
            if pc in d:
                continue
            d[pc] = d[p] + 1
            pr[pc] = p
            q.append(pc)
            res = True
        return res

    for p in q:
        jm = m
        im = n
        for j in range(1, m - 1):
            if j > jm:
                break
            if j + 1 >= m:
                continue
            p1, p2, p3 = p[j-1], p[j], p[j+1]
            for i in range(1, n - 1):
                if i > im:
                    break
                if p2 & (3 << i):
                    continue
                if (p1 & (1 << i)) and (p2 & (1 << (i-1))):
                    continue
                if put(p, i-1, j-1, p1, p2, p3) and im == n:
                    im = i + w
                    jm = j - 1

    max_k = -1
    best_key = None
    for key, value in d.items():
        if value > max_k:
            max_k = value
            best_key = key

    if best_key is None:
        return 0, ['.' * m for _ in range(n)]

    r = [['.'] * m for _ in range(n)]
    current = best_key
    l = 'A'
    while pr.get(current) is not None:
        prev = pr[current]
        for y in range(m):
            for x in range(n):
                if (current[y] & (1 << x)) and not (prev[y] & (1 << x)):
                    r[x][y] = l
        current = prev
        l = chr(ord(l) + 1)

    if rf:
        transposed = []
        for col in range(m):
            transposed_row = []
            for row in range(n):
                transposed_row.append(r[row][col])
            transposed.append(''.join(transposed_row))
        r = transposed
    else:
        r = [''.join(row) for row in r]

    return max_k, r

def is_valid_t_shape(coords):
    if len(coords) != 5:
        return False
    min_r = min(r for r, _ in coords)
    min_c = min(c for _, c in coords)
    translated = set((r - min_r, c - min_c) for r, c in coords)
    patterns = [
        {(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)},
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
        {(0, 1), (1, 1), (2, 0), (2, 1), (2, 2)},
        {(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)},
    ]
    return translated in patterns

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ChelpcaretakerVerificationTool(BaseTool):
    """Chelpcaretaker验证工具"""
    
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
            score = ChelpcaretakerRewardCalculator.verify_score(
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
            logger.error(f"ChelpcaretakerVerificationTool执行错误: {str(e)}")
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

