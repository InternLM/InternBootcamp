import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cservalandparenthesissequence.Cservalandparenthesissequence_reward_calculator import CservalandparenthesissequenceRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CservalandparenthesissequenceVerificationTool(BaseTool):
    """Cservalandparenthesissequence验证工具"""
    
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
            score = CservalandparenthesissequenceRewardCalculator.verify_score(
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
            logger.error(f"CservalandparenthesissequenceVerificationTool执行错误: {str(e)}")
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
    def solve_parenthesis(s):
        n = len(s)
        if n % 2 != 0:
            return ':('
        h = n // 2
        no = s.count('(')
        nc = s.count(')')
        nq = n - no - nc
        if no > h or nc > h or s[0] == ')':
            return ':('
        res = list(s)
        open_needed = h - no
        close_needed = h - nc
        if open_needed < 0 or close_needed < 0:
            return ':('
        # 遍历填充?
        cur_balance = 0
        for i in range(n):
            if res[i] == '(':
                cur_balance += 1
            elif res[i] == ')':
                cur_balance -= 1
                if cur_balance < 1 and i < n-1:
                    return ':('
            elif res[i] == '?':
                # 优先填 ( 的条件
                if open_needed > 0:
                    res[i] = '('
                    cur_balance += 1
                    open_needed -= 1
                else:
                    res[i] = ')'
                    cur_balance -= 1
                    close_needed -= 1
                # 检查中间非法情况
                if cur_balance < 0 or (cur_balance < 1 and i < n-1):
                    return ':('
        # 最终平衡检查
        return ''.join(res) if cur_balance == 0 else ':('

    @staticmethod
    def is_valid_parenthesis(s):
        balance = 0
        for c in s:
            balance += 1 if c == '(' else -1
            if balance < 0:
                return False
        return balance == 0
