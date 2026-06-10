import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.celections.Celections_reward_calculator import CelectionsRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CelectionsVerificationTool(BaseTool):
    """Celections验证工具"""
    
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
            score = CelectionsRewardCalculator.verify_score(
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
            logger.error(f"CelectionsVerificationTool执行错误: {str(e)}")
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
    def calculate_min_cost(voters):
        c0 = sum(1 for ai, _ in voters if ai == 0)
        candidate_bribes = defaultdict(list)

        # 收集贿赂成本并按候选人分组
        for ai, bi in voters:
            if ai != 0:
                candidate_bribes[ai].append(bi)

        # 对每个候选人的贿赂成本排序（降序，便于后续处理）
        for k in candidate_bribes:
            candidate_bribes[k].sort(reverse=True)

        # 预处理所有可能的贿赂方案
        all_costs = []
        total_available = 0
        for cand in candidate_bribes.values():
            all_costs.extend(cand)
            total_available += len(cand)

        # 处理无需贿赂的情况
        if not candidate_bribes:
            return 0

        # 预处理每个候选人的前缀和
        prefix_sums = {}
        for cand, costs in candidate_bribes.items():
            prefix = [0]
            s = 0
            for cost in costs:
                s += cost
                prefix.append(s)
            prefix_sums[cand] = prefix

        min_cost = float('inf')
        max_possible = c0 + total_available

        # 确定s的范围优化：s只需要到达最大候选人的当前票数+1
        max_current_votes = max(len(v) for v in candidate_bribes.values())
        s_candidates = range(max(1, max_current_votes - c0 + 1), max_possible + 1)
        if not s_candidates:
            return float('inf')

        # 计算所有可能的s值
        for s in s_candidates:
            required = s - c0
            if required <= 0:
                current_cost = 0
                if all(len(v) < s for v in candidate_bribes.values()):
                    current_cost = 0
                else:
                    continue
            else:
                total_bribes = 0
                total_obtained = 0
                remaining_costs = []

                # 第一部分：必须贿赂的选票
                for cand, costs in candidate_bribes.items():
                    needed = max(len(costs) - (s - 1), 0)
                    if needed > len(costs):
                        break
                    total_bribes += prefix_sums[cand][needed]
                    total_obtained += needed
                    remaining_costs.extend(costs[needed:])
                else:  # 正常完成循环时才执行后续逻辑
                    # 第二部分：补充需要的额外选票
                    if total_obtained >= required:
                        current_cost = total_bribes
                    else:
                        additional_needed = required - total_obtained
                        if len(remaining_costs) < additional_needed:
                            continue
                        remaining_sorted = sorted(remaining_costs)
                        current_cost = total_bribes + sum(remaining_sorted[:additional_needed])

                    if current_cost < min_cost:
                        min_cost = current_cost

        return min_cost if min_cost != float('inf') else None
