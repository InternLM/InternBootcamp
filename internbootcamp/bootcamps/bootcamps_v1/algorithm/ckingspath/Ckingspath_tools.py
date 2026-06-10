import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ckingspath.Ckingspath_reward_calculator import CkingspathRewardCalculator

# 导入依赖库
import re
import random
from collections import deque
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CkingspathVerificationTool(BaseTool):
    """Ckingspath验证工具"""
    
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
            score = CkingspathRewardCalculator.verify_score(
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
            logger.error(f"CkingspathVerificationTool执行错误: {str(e)}")
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
    def _generate_king_path(self, start, end):
        """生成国王移动的合法路径"""
        path = [start]
        x, y = start
        tx, ty = end

        while (x, y) != (tx, ty):
            dx = 0 if x == tx else (1 if tx > x else -1)
            dy = 0 if y == ty else (1 if ty > y else -1)
            x += dx
            y += dy
            path.append((x, y))
        return path

    def _merge_segments(self, path):
        """合并连续列形成线段"""
        row_dict = defaultdict(list)
        for x, y in path:
            row_dict[x].append(y)

        segments = []
        for row in row_dict:
            cols = sorted(row_dict[row])
            start = cols[0]
            for i in range(1, len(cols)):
                if cols[i] > cols[i-1] + 1:
                    segments.append([row, start, cols[i-1]])
                    start = cols[i]
            segments.append([row, start, cols[-1]])
        return segments

    def _generate_disjoint_segments(self, start, end):
        """生成隔离区域确保无解"""
        segments = []
        # 单独包裹起点
        segments.append([start[0], start[1]-1, start[1]+1])
        # 单独包裹终点（不同行）
        segments.append([end[0]+2, end[1]-1, end[1]+1])
        # 添加干扰线段
        for _ in range(random.randint(1,3)):
            r = random.randint(1, self.max_coord)
            a = random.randint(1, self.max_coord//2)
            b = random.randint(a+2, self.max_coord)
            segments.append([r, a, b])
        return segments
