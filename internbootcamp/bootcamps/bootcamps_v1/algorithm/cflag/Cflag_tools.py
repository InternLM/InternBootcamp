import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cflag.Cflag_reward_calculator import CflagRewardCalculator

# 导入依赖库
import random
import re
from string import ascii_lowercase



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CflagVerificationTool(BaseTool):
    """Cflag验证工具"""
    
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
            score = CflagRewardCalculator.verify_score(
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
            logger.error(f"CflagVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def _calculate_correct_answer(cls, grid):
        n = len(grid)
        if n == 0:
            return 0
        m = len(grid[0])
        down = [[None] * m for _ in range(n)]

        for c in range(m):
            szs = []
            cnt = 1
            for r in range(1, n):
                if grid[r][c] == grid[r-1][c]:
                    cnt += 1
                else:
                    szs.append(cnt)
                    cnt = 1
            szs.append(cnt)

            st = 0
            for i in range(1, len(szs)-1):
                if szs[i] > min(szs[i-1], szs[i+1]):
                    st += szs[i-1]
                    continue
                sz = szs[i]
                top_start = st
                top_end = st + szs[i-1] - 1
                mid_start = top_end + 1
                mid_end = mid_start + sz - 1
                if mid_end >= n:
                    st += szs[i-1]
                    continue
                bot_start = mid_end + 1
                bot_end = bot_start + sz - 1
                if bot_end >= n:
                    st += szs[i-1]
                    continue
                top_color = grid[top_start][c]
                mid_color = grid[mid_start][c]
                bot_color = grid[bot_start][c]
                if top_color != mid_color and mid_color != bot_color:
                    for r in range(top_start, top_end + 1):
                        down[r][c] = (sz, top_color, mid_color, bot_color)
                st += szs[i-1]

        out = 0
        for r in range(n):
            st = 0
            cnt = 0
            cur = None
            while st < m:
                cell = down[r][st]
                if cell is None:
                    if cnt > 0:
                        out += (cnt + 1) * cnt // 2
                        cnt = 0
                    st += 1
                else:
                    if cell == cur:
                        cnt += 1
                    else:
                        if cnt > 0:
                            out += (cnt + 1) * cnt // 2
                        cur = cell
                        cnt = 1
                    st += 1
            if cnt > 0:
                out += (cnt + 1) * cnt // 2
        return out
