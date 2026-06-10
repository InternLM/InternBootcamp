import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cbarcode.Cbarcode_reward_calculator import CbarcodeRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_min_pixels(n, m, x, y, rows):
    # 转置行以获取各列
    cols = list(zip(*rows))
    u = [col.count('.') for col in cols]  # 每列改为白色所需的修改次数（即列中黑色像素数）
    v = [n - count for count in u]        # 每列改为黑色所需的修改次数（即列中白色像素数）
    
    a = [u[0]]  # 以白色结尾的段的最小修改次数
    b = [v[0]]  # 以黑色结尾的段的最小修改次数
    s = x - 1   # 段长度至少为x，因此需要保留前s个状态
    
    # 处理前x-1列
    for i in range(1, x):
        # 由于段长度必须>=x，此时只能继续延长当前颜色段
        a = [float('inf')] + [prev + u[i] for prev in a]
        b = [float('inf')] + [prev + v[i] for prev in b]
    
    # 处理x到min(y, m)-1列
    for i in range(x, min(y, m)):
        # 可以开始新的颜色段，此时需要取另一种颜色的最小值
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a]
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b]
        a, b = new_a, new_b
    
    # 处理剩下的列（当m > y时）
    for i in range(min(y, m), m):
        # 需要确保段长度不超过y，因此保留前y个状态
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a[:-1]]  # 保留前y-1个状态
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b[:-1]]
        a, b = new_a, new_b
    
    # 最后，取所有可能状态中的最小值
    valid_a = a[s:] if a[s:] else [float('inf')]
    valid_b = b[s:] if b[s:] else [float('inf')]
    return min(min(valid_a), min(valid_b))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CbarcodeVerificationTool(BaseTool):
    """Cbarcode验证工具"""
    
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
            score = CbarcodeRewardCalculator.verify_score(
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
            logger.error(f"CbarcodeVerificationTool执行错误: {str(e)}")
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

