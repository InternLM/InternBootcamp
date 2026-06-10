import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ddensesubsequence.Ddensesubsequence_reward_calculator import DdensesubsequenceRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve(m, s):
    n = len(s)
    if n == 0 or m == 0:
        return ""
    
    # Frequency list generation
    sorted_chars = sorted(s)
    freq = []
    current_char = sorted_chars[0]
    count = 1
    
    for c in sorted_chars[1:]:
        if c == current_char:
            count += 1
        else:
            freq.append((current_char, count))
            current_char = c
            count = 1
    freq.append((current_char, count))
    
    # Find minimal solution
    for idx, (char, total) in enumerate(freq):
        required = 0
        last_covered = -1
        last_candidate = -1
        valid = True
        
        for i in range(n):
            if s[i] < char:
                last_covered = i
                last_candidate = i
            elif s[i] == char:
                last_candidate = i
            
            # Check window violation
            if i - last_covered >= m:
                if last_candidate > last_covered:
                    required += 1
                    last_covered = last_candidate
                else:
                    valid = False
                    break
        
        # Final check for the last window
        if valid and (n - last_covered) > m:
            valid = False
        
        if valid:
            # Calculate required count
            min_chars = []
            for c, _ in freq[:idx+1]:
                if c < char:
                    min_chars.append(c)
            return char * required + ''.join(sorted(min_chars))
        else:
            continue
    
    # Fallback to all smallest characters
    return ''.join(sorted(s))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DdensesubsequenceVerificationTool(BaseTool):
    """Ddensesubsequence验证工具"""
    
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
            score = DdensesubsequenceRewardCalculator.verify_score(
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
            logger.error(f"DdensesubsequenceVerificationTool执行错误: {str(e)}")
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

