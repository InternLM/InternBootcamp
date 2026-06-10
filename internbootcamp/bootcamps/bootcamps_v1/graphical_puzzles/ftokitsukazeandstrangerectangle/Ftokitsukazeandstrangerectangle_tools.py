import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ftokitsukazeandstrangerectangle.Ftokitsukazeandstrangerectangle_reward_calculator import FtokitsukazeandstrangerectangleRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_answer(points):
    if not points:
        return 0
    
    # 离散化坐标
    x_coords = sorted({x for x, y in points})
    y_coords = sorted({y for x, y in points})
    
    x_map = {x: i for i, x in enumerate(x_coords)}
    y_map = {y: i for i, y in enumerate(y_coords)}
    
    # 按y分层存储x坐标
    y_buckets = [[] for _ in range(len(y_coords))]
    for x, y in points:
        y_idx = y_map[y]
        y_buckets[y_idx].append(x_map[x])
    
    for bucket in y_buckets:
        bucket.sort()
    
    total = 0
    st = SegmentTree(len(x_coords))
    
    # 按y降序处理
    for bucket in reversed(y_buckets):
        # 添加当前层的点
        for x in bucket:
            if st.query_range(x, x+1) == 0:
                st.update(x, 1)
        
        prev_x = -1
        for x in bucket:
            # 计算左区域贡献
            left = st.query_range(prev_x + 1, x + 1)
            # 计算右区域贡献（包括无穷大情况）
            right = st.query_range(x + 1, len(x_coords)) + 1
            total += left * right
            prev_x = x
    
    return total



# === 源文件中的其他类 ===

class SegmentTree:
    def __init__(self, size):
        self.m = 1
        while self.m < size:
            self.m <<= 1
        self.data = [0] * (2 * self.m)
    
    def update(self, index, value):
        index += self.m
        while index > 0:
            self.data[index] += value
            index >>= 1
    
    def query_range(self, l, r):
        res = 0
        l += self.m
        r += self.m
        while l < r:
            if l % 2 == 1:
                res += self.data[l]
                l += 1
            if r % 2 == 1:
                r -= 1
                res += self.data[r]
            l >>= 1
            r >>= 1
        return res

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FtokitsukazeandstrangerectangleVerificationTool(BaseTool):
    """Ftokitsukazeandstrangerectangle验证工具"""
    
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
            score = FtokitsukazeandstrangerectangleRewardCalculator.verify_score(
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
            logger.error(f"FtokitsukazeandstrangerectangleVerificationTool执行错误: {str(e)}")
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

