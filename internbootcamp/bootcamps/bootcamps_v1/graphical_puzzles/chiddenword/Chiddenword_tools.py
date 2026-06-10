import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.chiddenword.Chiddenword_reward_calculator import ChiddenwordRewardCalculator

# 导入依赖库
import re
import string
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ChiddenwordVerificationTool(BaseTool):
    """Chiddenword验证工具"""
    
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
            score = ChiddenwordRewardCalculator.verify_score(
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
            logger.error(f"ChiddenwordVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def generate_solution(s_input):
        s = s_input
        st = 0
        en = 0
        ans = [['.' for _ in range(13)] for _ in range(2)]
        found = False
        for i in range(ord('A'), ord('Z') + 1):
            c = chr(i)
            st = s.find(c)
            if st == -1:
                continue
            en = s.find(c, st + 1)
            if en != -1:
                found = True
                break
        if not found:
            return "Impossible"

        if st + 1 == en:
            return "Impossible"
        else:
            l = (en - st)
            l += l % 2
            ss = 13 - (l // 2)
            p = [ss, 0]
            dr = 1
            for i in range(st, en):
                ans[p[1]][p[0]] = s[i]
                if p[0] + dr == 13:
                    p[1] += 1
                    dr *= -1
                else:
                    p[0] += dr
            p = [ss - 1, 0]
            dr = -1
            a = s[:st]
            b = s[en + 1:]
            bf = a[::-1] + b[::-1]
            for i in range(len(bf)):
                if p[0] < 0:
                    p[0] = 0
                    p[1] = 1
                    dr = 1
                ans[p[1]][p[0]] = bf[i]
                p[0] += dr
            row0 = ''.join(ans[0])
            row1 = ''.join(ans[1])
            return [row0, row1]
