import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esashaandapatientfriend.Esashaandapatientfriend_reward_calculator import EsashaandapatientfriendRewardCalculator

# 导入依赖库
import random
import re
import bisect
from bisect import bisect_left
from bisect import bisect_right



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EsashaandapatientfriendVerificationTool(BaseTool):
    """Esashaandapatientfriend验证工具"""
    
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
            score = EsashaandapatientfriendRewardCalculator.verify_score(
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
            logger.error(f"EsashaandapatientfriendVerificationTool执行错误: {str(e)}")
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
    def _gen_lr(self, event_times):
        """生成合理的l和r范围"""
        if event_times:
            min_t = event_times[0]
            max_t = event_times[-1]
            l = random.randint(max(1, min_t-10), max_t+10)
            r = random.randint(l, min(self.max_time, max_t+1000))
        else:
            l = random.randint(1, 100)
            r = random.randint(l, min(self.max_time, l+1000))
        return l, r

    @staticmethod
    def _simulate(events, l, r, v_initial):
        if v_initial == 0:
            return l  # 初始值为0立即破裂

        current_time = l
        current_speed = 0  # 初始速度
        v = v_initial
        sorted_events = sorted(events, key=lambda x: x["t"])

        for event in sorted_events:
            t_event = event["t"]
            s_new = event["s"]

            # 处理当前时间段 [current_time, t_event)
            if t_event > current_time:
                dt = t_event - current_time
                if current_speed < 0:
                    # 计算在当前速度下是否会耗尽
                    if v <= 0:
                        return current_time
                    time_to_empty = v / (-current_speed)
                    if time_to_empty <= dt:
                        return current_time + time_to_empty
                    # 不会耗尽，更新v和时间
                    v += current_speed * dt
                    current_time = t_event
                else:
                    v += current_speed * dt
                    current_time = t_event
                if v <= 0:
                    return current_time  # 刚好在时间点耗尽

            # 更新速度
            current_speed = s_new

        # 处理最后的时间段 [current_time, r)
        dt = r - current_time
        if dt > 0:
            if current_speed < 0:
                if v <= 0:
                    return current_time
                time_to_empty = v / (-current_speed)
                if time_to_empty <= dt:
                    return current_time + time_to_empty
                v += current_speed * dt
            else:
                v += current_speed * dt
            if v <= 0:
                return r  # 在结束时间点耗尽

        return -1 if v > 0 else r
