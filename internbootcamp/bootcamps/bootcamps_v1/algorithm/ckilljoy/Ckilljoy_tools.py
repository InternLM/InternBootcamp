import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ckilljoy.Ckilljoy_reward_calculator import CkilljoyRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CkilljoyVerificationTool(BaseTool):
    """Ckilljoy验证工具"""
    
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
            score = CkilljoyRewardCalculator.verify_score(
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
            logger.error(f"CkilljoyVerificationTool执行错误: {str(e)}")
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
    def _generate_case_0(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        return {'n': n, 'x': x, 'a': [x]*n}

    def _generate_case_1_initial_infect(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(*self.x_range)
        num_infect = random.randint(1, n-1)
        a = [x]*num_infect
        remaining = n - num_infect
        for _ in range(remaining):
            while True:
                ai = random.randint(*self.a_range)
                if ai != x:
                    a.append(ai)
                    break
        random.shuffle(a)
        return {'n': n, 'x': x, 'a': a}

    def _generate_case_1_balance_sum(self):
        for _ in range(100):
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            sum_total = n * x
            a = []
            for _ in range(n-1):
                ai = random.randint(*self.a_range)
                while ai == x:
                    ai = random.randint(*self.a_range)
                a.append(ai)
            last = sum_total - sum(a)
            if last != x and self.a_range[0] <= last <= self.a_range[1]:
                a.append(last)
                return {'n': n, 'x': x, 'a': a}
        return {'n': 2, 'x': 0, 'a': [1, -1]}

    def _generate_case_2(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            x = random.randint(*self.x_range)
            a = [random.randint(*self.a_range) for _ in range(n)]
            sum_total = sum(a)
            has_x = x in a
            if not has_x and sum_total != n * x:
                return {'n': n, 'x': x, 'a': a}
