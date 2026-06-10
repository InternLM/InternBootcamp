import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cproblemfornazar.Cproblemfornazar_reward_calculator import CproblemfornazarRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CproblemfornazarVerificationTool(BaseTool):
    """Cproblemfornazar验证工具"""
    
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
            score = CproblemfornazarRewardCalculator.verify_score(
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
            logger.error(f"CproblemfornazarVerificationTool执行错误: {str(e)}")
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
    def _find_max_stage(self):
        """动态计算最大可能的阶段数"""
        total, stage = 0, 0
        while True:
            add = 1 << stage
            if total + add > self.max_lr:
                return stage
            total += add
            stage += 1

    def _build_case_around(self, pos):
        """生成围绕特定位置的测试案例"""
        if random.choice([True, False]):
            l = max(1, pos - random.randint(0, 100))
            r = min(self.max_lr, pos + random.randint(0, 100))
        else:
            r = min(self.max_lr, pos + random.randint(0, 1000))
            l = max(1, r - random.randint(0, 1000))
        return {'l': l, 'r': r}

    def _generate_normal_case(self):
        """生成覆盖不同范围的普通案例"""
        range_type = random.choice([
            'tiny', 'small', 'medium', 'large', 'huge'
        ])

        ranges = {
            'tiny': (1, 100),
            'small': (100, 10**6),
            'medium': (10**6, 10**12),
            'large': (10**12, 10**15),
            'huge': (10**15, self.max_lr)
        }
        min_r, max_r = ranges[range_type]
        r = self._get_random_in_range(min_r, max_r)
        l = random.randint(1, r)
        return {'l': l, 'r': r}

    def _get_random_in_range(self, min_val, max_val):
        """高效生成指定范围的随机数"""
        span = max_val - min_val
        if span < 0:
            return min_val
        return min_val + random.randint(0, span)

    @staticmethod
    def _calculate_sum(x):
        sum_total = 0
        stage_size = 1  # 当前阶段元素个数
        is_odd = True    # 当前阶段奇偶性
        next_odd = 1     # 下一个奇数起始值
        next_even = 2    # 下一个偶数起始值
        remaining = x

        while remaining > 0:
            take = min(stage_size, remaining)

            if is_odd:
                start = next_odd
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_odd = end + 2
            else:
                start = next_even
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_even = end + 2

            sum_total = (sum_total + segment_sum) % MOD
            remaining -= take
            stage_size *= 2
            is_odd = not is_odd

        return sum_total
