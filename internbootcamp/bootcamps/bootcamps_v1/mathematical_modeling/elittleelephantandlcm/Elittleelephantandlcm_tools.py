import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.elittleelephantandlcm.Elittleelephantandlcm_reward_calculator import ElittleelephantandlcmRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ElittleelephantandlcmVerificationTool(BaseTool):
    """Elittleelephantandlcm验证工具"""
    
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
            score = ElittleelephantandlcmRewardCalculator.verify_score(
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
            logger.error(f"ElittleelephantandlcmVerificationTool执行错误: {str(e)}")
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
    def _solve(a):
        # 优化后的高效解法实现
        if not a:
            return 0

        # 预处理频率统计
        freq = defaultdict(int)
        max_val = max(a) if a else 0
        for num in a:
            freq[num] += 1

        # 构建dist数组
        dist = {}
        current = 0
        for x in range(max_val, 0, -1):
            current += freq.get(x, 0)
            dist[x] = current

        # 预计算所有数的约数
        divisors = defaultdict(list)
        for d in range(1, max_val + 1):
            for multiple in range(d, max_val + 1, d):
                divisors[multiple].append(d)

        ans = 1  # 初始值对应X=1的情况

        # 主计算逻辑
        for X in range(2, max_val + 1):
            divs = divisors.get(X, [])
            sz = len(divs)
            if sz < 1:
                continue

            # 计算big乘积项
            big = 1
            for j in range(sz - 1):
                d_current = divs[j]
                d_next = divs[j+1]
                cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                big = (big * pow(j+1, cnt, MOD)) % MOD

            # 处理最后一个约数项
            last_d = divs[-1]
            big = (big * pow(sz, dist.get(last_d, 0), MOD)) % MOD

            # 计算small乘积项
            small = 1
            if sz >= 2:
                for j in range(sz - 2):
                    d_current = divs[j]
                    d_next = divs[j+1]
                    cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                    small = (small * pow(j+1, cnt, MOD)) % MOD

                second_last_d = divs[-2]
                small = (small * pow(sz-1, dist.get(second_last_d, 0), MOD)) % MOD
            else:
                small = 0

            # 累加有效贡献
            contribution = (big - small) % MOD
            ans = (ans + contribution) % MOD

        return ans % MOD
