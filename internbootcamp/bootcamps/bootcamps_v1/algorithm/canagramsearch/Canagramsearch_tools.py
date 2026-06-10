import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.canagramsearch.Canagramsearch_reward_calculator import CanagramsearchRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict

# === 源文件中的全局函数 ===

def calculate_answer(s, p):
    m = len(p)
    n = len(s)
    if m == 0 or n < m:
        return 0
    
    # Initialize frequency counter for p
    count_p = defaultdict(int)
    for c in p:
        count_p[c] += 1
    
    # Initialize sliding window parameters
    current_counts = defaultdict(int)
    required = len(count_p)
    formed = 0
    ans = 0
    q_count = 0  # number of '?' in current window
    
    left = 0
    for right in range(n):
        # Add right character
        char = s[right]
        if char == '?':
            q_count += 1
        else:
            current_counts[char] += 1
            if current_counts[char] == count_p.get(char, 0):
                formed += 1
        
        # Maintain window size m
        if right - left + 1 > m:
            # Remove left character
            left_char = s[left]
            if left_char == '?':
                q_count -= 1
            else:
                if current_counts[left_char] == count_p.get(left_char, 0):
                    formed -= 1
                current_counts[left_char] -= 1
            left += 1
        
        # Check window validity when window size is exactly m
        if right - left + 1 == m:
            # Calculate needed characters
            needed = sum(max(0, count_p[c] - current_counts[c]) for c in count_p)
            if needed <= q_count and formed == required:
                ans += 1
    
    return ans

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CanagramsearchVerificationTool(BaseTool):
    """Canagramsearch验证工具"""
    
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
            score = CanagramsearchRewardCalculator.verify_score(
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
            logger.error(f"CanagramsearchVerificationTool执行错误: {str(e)}")
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

