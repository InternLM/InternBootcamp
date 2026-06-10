import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bonlinemeeting.Bonlinemeeting_reward_calculator import BonlinemeetingRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BonlinemeetingVerificationTool(BaseTool):
    """Bonlinemeeting验证工具"""
    
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
            score = BonlinemeetingRewardCalculator.verify_score(
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
            logger.error(f"BonlinemeetingVerificationTool执行错误: {str(e)}")
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
    def solve_leader(n, messages):
        m = len(messages)
        a = [0]*(m+1)  # 操作数组（1-based）
        b = [0]*(m+1)  # 用户数组（1-based）

        # 解析操作
        for i in range(1, m+1):
            op, id_str = messages[i-1].split()
            a[i] = 1 if op == '+' else -1
            b[i] = int(id_str)

        # 第一遍处理：初始化s数组
        l = defaultdict(int)  # 记录用户最后一次操作位置
        s = [0]*(m+2)  # 前缀和数组

        for i in range(1, m+1):
            user = b[i]
            # 处理首次登出但之前未登录的情况
            if a[i] == -1 and l[user] == 0:
                s[0] += 1  # 初始未在线但收到登出
            s[i] = a[i]
            l[user] = i

        # 计算在线人数前缀和
        for i in range(1, m+1):
            s[i] += s[i-1]

        # 转换为在线状态标记（1在线，0离线）
        for i in range(m+1):
            s[i] = 1 if s[i] > 0 else 0

        # 转换为累计在线时间
        for i in range(1, m+1):
            s[i] += s[i-1]

        # 第二遍处理：验证候选者
        l = defaultdict(int)  # 重置记录
        v = [0]*(n+1)  # 违规标记

        for i in range(1, m+1):
            user = b[i]
            if a[i] == 1:  # 登录事件
                violation = False
                if l[user] == 0:  # 首次登录
                    if s[i-1] > 0:  # 登录前已有在线
                        violation = True
                else:  # 非首次登录
                    prev = l[user]
                    if (s[i-1] - s[prev-1]) > 0:  # 两次登录之间有其他人
                        violation = True

                if violation:
                    v[user] = 1
            l[user] = i  # 更新最后操作位置

        # 检查最后一次登出后的状态
        for user in range(1, n+1):
            last_op_idx = l[user]
            if last_op_idx != 0 and a[last_op_idx] == -1:  # 最后操作是登出
                if (s[m] - s[last_op_idx-1]) > 0:  # 登出后仍有其他人
                    v[user] = 1

        # 收集未违规的候选人
        leaders = [user for user in range(1, n+1) if v[user] == 0]
        return sorted(leaders)
