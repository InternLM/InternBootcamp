import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.domnomandnecklace.Domnomandnecklace_reward_calculator import DomnomandnecklaceRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DomnomandnecklaceVerificationTool(BaseTool):
    """Domnomandnecklace验证工具"""
    
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
            score = DomnomandnecklaceRewardCalculator.verify_score(
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
            logger.error(f"DomnomandnecklaceVerificationTool执行错误: {str(e)}")
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
    def compute_z(s):
        # 保持与C++完全一致的Z算法实现
        n = len(s)
        z = [0] * n
        z[0] = n  # 空字符匹配整个字符串
        l, r = 0, 0
        for i in range(1, n):
            if i > r:
                l = r = i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
            else:
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    l = i
                    while r < n and s[r - l] == s[r]:
                        r += 1
                    z[i] = r - l
                    r -= 1
        return z

    def solve(self, n, k, s):
        # 移除k=0处理分支
        if k == 0:
            return '0' * n
        z = self.compute_z(s)
        ans = [0] * (n + 2)  # 增加缓冲空间

        for lenAB in range(1, n + 1):
            # 检查前k个B是否满足条件
            valid = True
            current_pos = lenAB
            for _ in range(k - 1):
                if current_pos >= n:
                    valid = False
                    break
                required = lenAB
                if current_pos + required > n:
                    if z[current_pos] < n - current_pos:
                        valid = False
                        break
                else:
                    if z[current_pos] < required:
                        valid = False
                        break
                current_pos += lenAB

            if not valid:
                continue

            # 计算可选A的长度范围
            l = lenAB * k - 1
            if l >= n:
                continue

            a_start = lenAB * k
            if a_start >= n:
                max_a = 0
            else:
                max_a = z[a_start]

            possible_a = min(lenAB, max_a)
            r = l + possible_a

            # 修正差分数组标记
            end = min(r, n)
            ans[l] += 1
            if end < n:
                ans[end + 1] -= 1
            else:
                ans[n] -= 1

        # 重建结果数组
        res = []
        current = 0
        for i in range(n):
            current += ans[i]
            res.append('1' if current > 0 else '0')
        return ''.join(res)
