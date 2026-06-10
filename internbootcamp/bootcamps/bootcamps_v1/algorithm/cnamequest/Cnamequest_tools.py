import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnamequest.Cnamequest_reward_calculator import CnamequestRewardCalculator

# 导入依赖库
import re
import random
import string



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnamequestVerificationTool(BaseTool):
    """Cnamequest验证工具"""
    
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
            score = CnamequestRewardCalculator.verify_score(
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
            logger.error(f"CnamequestVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_t(self, s):
        """生成有效t字符串（保证s是t的子序列且存在分割点）"""
        # 生成左右部分各包含s的构造
        left = []
        ptr = 0
        for c in s:
            # 在字符前添加随机前缀
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            left.append(c)
            ptr += 1
        left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))

        right = []
        ptr = 0
        for c in s:
            # 在字符后添加随机后缀
            right.append(c)
            right.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            ptr += 1

        return (''.join(left) + ''.join(right)).replace('\x00', '')  # 防止空字符

    def _generate_invalid_t(self, s):
        """生成无效t字符串（保证至少有一半不满足条件）"""
        # 首先生成有效左半部分
        left = []
        ptr = 0
        for c in s:
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 2))))
            left.append(c)
        left = ''.join(left)

        # 生成无效右半部分（不包含s）
        right = ''.join(random.choices(string.ascii_lowercase, 
                      k=random.randint(len(s)+1, len(s)*2)))
        while self._is_subsequence(s, right):
            right = ''.join(random.choices(string.ascii_lowercase, 
                          k=random.randint(len(s)+1, len(s)*2)))

        return left + right

    def _is_subsequence(self, s, t):
        """正确实现子序列判断"""
        it = iter(t)
        return all(c in it for c in s)

    def _adjust_length(self, t):
        """确保t长度在合理范围内"""
        t = t[:self.t_max_len]
        while len(t) < self.t_min_len:
            t += random.choice(string.ascii_lowercase)
        return t
