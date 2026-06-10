import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cfencepainting.Cfencepainting_reward_calculator import CfencepaintingRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CfencepaintingVerificationTool(BaseTool):
    """Cfencepainting验证工具"""
    
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
            score = CfencepaintingRewardCalculator.verify_score(
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
            logger.error(f"CfencepaintingVerificationTool执行错误: {str(e)}")
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
    def solve_case(case):
        a, b, c = case['a'], case['b'], case['c']
        n, m = case['n'], case['m']

        # 构建需要修改的位置
        required = defaultdict(list)
        for i in range(n):
            if a[i] != b[i]:
                required[b[i]].append(i)

        # 检查最后一个颜色是否有效
        last_valid = False
        if c:
            last_color = c[-1]
            if last_color in required:
                last_valid = True
            else:
                for i in range(n):
                    if b[i] == last_color:
                        last_valid = True
                        break

        if not last_valid:
            return ('NO', None)

        # 逆向构建解决方案
        solution = []
        temp_required = {k: v.copy() for k, v in required.items()}
        required_list = [(b[i], i) for i in range(n) if a[i] != b[i]]

        for color in reversed(c):
            found = False
            # 优先使用必须修改的位置
            if color in temp_required and temp_required[color]:
                plank = temp_required[color].pop()
                solution.append(plank)
                found = True
                if not temp_required[color]:
                    del temp_required[color]
            # 使用任意有效位置
            if not found:
                for i in range(n):
                    if b[i] == color:
                        solution.append(i)
                        found = True
                        break
            # 使用最后保留的位置
            if not found:
                solution.append(solution[-1] if solution else 0)

        # 检查是否所有需求都被满足
        if any(len(v) > 0 for v in temp_required.values()):
            return ('NO', None)

        # 反转并转换为1-based索引
        final_solution = [x+1 for x in reversed(solution)]
        return ('YES', final_solution)
