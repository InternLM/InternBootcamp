import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esuperiorperiodicsubarrays.Esuperiorperiodicsubarrays_reward_calculator import EsuperiorperiodicsubarraysRewardCalculator

# 导入依赖库
import math
from collections import defaultdict
import random
import re

# === 源文件中的全局函数 ===

def solve_puzzle(n, a):
    if n == 1:
        return 0  # s必须≥1且<1，无解

    a_extended = a.copy()
    a_extended.extend(a)
    inf = min(a) - 1
    a_extended[-1] = inf  # 保证最后元素最小
    result = 0

    numbers_by_gcd = defaultdict(list)
    for i in range(1, n):
        current_gcd = math.gcd(i, n)
        numbers_by_gcd[current_gcd].append(i)

    for d in numbers_by_gcd:  # 遍历每个可能的gcd值
        if n % d != 0:
            continue
        
        # 计算每个模位的最大值
        m = [-math.inf] * d
        for i in range(n):
            mod = i % d
            if a_extended[i] > m[mod]:
                m[mod] = a_extended[i]
        
        l = 0
        r = 0
        max_r = len(a_extended) - 1  # 防止越界
        while l < n and r <= max_r:
            if a_extended[r] < m[r % d]:
                # 处理当前有效区间
                sorted_s = sorted(numbers_by_gcd[d])
                for s in sorted_s:
                    if s > (r - l):
                        break
                    # 计算有效区间长度
                    start = l
                    end = min(r - s, n - 1)
                    if start <= end:
                        result += end - start + 1
                l = r + 1
                r = l
            else:
                r += 1
    return result

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EsuperiorperiodicsubarraysVerificationTool(BaseTool):
    """Esuperiorperiodicsubarrays验证工具"""
    
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
            score = EsuperiorperiodicsubarraysRewardCalculator.verify_score(
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
            logger.error(f"EsuperiorperiodicsubarraysVerificationTool执行错误: {str(e)}")
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

