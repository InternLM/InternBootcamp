import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.dsashaandonemorename.Dsashaandonemorename_reward_calculator import DsashaandonemorenameRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_palindrome(min_length=1, max_length=50):
    """Generate palindrome with controlled diversity"""
    length = random.randint(min_length, max_length)
    
    # Ensure non-uniform characters for 90% cases
    if random.random() < 0.9:
        chars = []
        while len(chars) < (length + 1)//2:
            c = random.choice('abcdefghijklmnopqrstuvwxyz')
            if not chars or c != chars[-1]:
                chars.append(c)
        
        # Ensure palindrome structure
        return ''.join(chars + chars[:-1][::-1]) if length%2 else ''.join(chars + chars[::-1])
    
    # Generate uniform palindrome for 10% cases
    c = random.choice('abcdefghijklmnopqrstuvwxyz')
    return c * length

def solve_puzzle(s):
    n = len(s)
    if n <= 1:
        return "Impossible"
    
    # Frequency analysis
    freq = defaultdict(int)
    for c in s:
        freq[c] += 1
    
    # Case 1: All characters same
    if len(freq) == 1:
        return "Impossible"
    
    # Case 2: Check for special odd-length cases
    if n % 2 == 1:
        odd_count = sum(1 for cnt in freq.values() if cnt % 2 != 0)
        if odd_count == 1 and len(freq) == 2:
            return "Impossible"
    
    # Try single cut solutions
    original = list(s)
    for i in range(n//2):
        rotated = s[i+1:] + s[:i+1]
        if rotated != s and rotated == rotated[::-1]:
            return 1
    
    # Default case needs 2 cuts
    return 2

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DsashaandonemorenameVerificationTool(BaseTool):
    """Dsashaandonemorename验证工具"""
    
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
            score = DsashaandonemorenameRewardCalculator.verify_score(
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
            logger.error(f"DsashaandonemorenameVerificationTool执行错误: {str(e)}")
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

