import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dmahmoudandehabandanotherarrayconstructiontask.Dmahmoudandehabandanotherarrayconstructiontask_reward_calculator import DmahmoudandehabandanotherarrayconstructiontaskRewardCalculator

# 导入依赖库
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DmahmoudandehabandanotherarrayconstructiontaskVerificationTool(BaseTool):
    """Dmahmoudandehabandanotherarrayconstructiontask验证工具"""
    
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
            score = DmahmoudandehabandanotherarrayconstructiontaskRewardCalculator.verify_score(
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
            logger.error(f"DmahmoudandehabandanotherarrayconstructiontaskVerificationTool执行错误: {str(e)}")
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
    def generate_b(a):
        MAX_NUM = 2000000
        prime_str = ('2 3 5 7 11 13 17 19 23 29 '
                     '31 37 41 43 47 53 59 61 67 71 '
                     '73 79 83 89 97 101 103 107 109 113 '
                     '127 131 137 139 149 151 157 163 167 173 '
                     '179 181 191 193 197 199 211 223 227 229 '
                     '233 239 241 251 257 263 269 271 277 281 '
                     '283 293 307 311 313 317')
        prime_list = [int(p) for p in prime_str.split()]
        used = [False] * (MAX_NUM + 1)
        n = len(a)
        b = []

        def record(x):
            t = []
            tmp_x = x
            for p in prime_list:
                if tmp_x % p == 0:
                    while tmp_x % p == 0:
                        tmp_x = tmp_x // p
                    t.append(p)
                    if tmp_x == 1:
                        break
            if tmp_x != 1:
                t.append(tmp_x)
            for ti in t:
                if ti > MAX_NUM:
                    continue
                for i in range(ti, MAX_NUM + 1, ti):
                    used[i] = True

        for ai in a:
            if ai <= MAX_NUM and not used[ai]:
                b.append(ai)
                record(ai)
            else:
                temp = ai + 1
                while temp <= MAX_NUM and used[temp]:
                    temp += 1
                if temp > MAX_NUM:
                    temp = ai + 1
                b.append(temp)
                record(temp)
                break  # Break after first replacement

        temp = 2
        while len(b) < len(a):
            while temp <= MAX_NUM and used[temp]:
                temp += 1
            if temp > MAX_NUM:
                break
            b.append(temp)
            record(temp)
            temp += 1

        return b
