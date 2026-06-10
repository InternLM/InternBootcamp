import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccleverfatrat.Ccleverfatrat_reward_calculator import CcleverfatratRewardCalculator

# 导入依赖库
import re
import random
from functools import reduce

# === 源文件中的全局变量 ===

max_oats = 10**6 + 1



# === 源文件中的全局函数 ===

def create_goals(ws):
    wrapped_ws = []
    for row in ws:
        new_row = [max_oats] + row + [max_oats]
        wrapped_ws.append(new_row)
    goal_oats = []
    pre_goal_oat = [0, 0]
    for idx in range(len(wrapped_ws)-1, -1, -1):
        goal_oat = []
        for jdx in range(1, len(wrapped_ws[idx])-1):
            current_ws = wrapped_ws[idx][jdx]
            left_parent = pre_goal_oat[jdx-1]
            right_parent = pre_goal_oat[jdx]
            goal_value = max(current_ws, min(left_parent, right_parent))
            goal_oat.append(goal_value)
        goal_oats.append(goal_oat)
        pre_goal_oat = [max_oats] + goal_oat + [max_oats]
    goal_oats.reverse()
    return goal_oats

def possible_oats(oats_list, current_ws):
    new_oats = []
    for idx in range(len(current_ws)):
        current_threshold = current_ws[idx]
        available_mass = sum([m for (m, _) in oats_list[idx]])
        if available_mass >= current_threshold:
            left = oats_list[idx-1] if idx > 0 else None
            right = oats_list[idx] if idx < len(oats_list)-1 else None
            new_mass = available_mass
            if left is not None:
                new_left = left + [(new_mass, (idx-1, idx))]
                new_oats.append(new_left)
            if right is not None:
                new_right = right + [(new_mass, (idx, idx+1))]
                new_oats.append(new_right)
    return new_oats

def is_break_all(goal_layer, oats_list):
    for idx, threshold in enumerate(goal_layer):
        if idx >= len(oats_list):
            continue
        total_mass = sum([m for (m, _) in oats_list[idx]])
        if total_mass >= threshold:
            return True
    return False

def fatrat(state):
    try:
        a, ws = state['a'], state['ws']
        goals = create_goals(ws)
        current_layer = [[(m, (0, i))] for i, m in enumerate(a)]
        
        for level in range(len(ws)):
            current_goal = goals[level]
            if is_break_all(current_goal, current_layer):
                return "Cerealguy"
            if level == len(ws)-1:
                break
            current_layer = possible_oats(current_layer, ws[level])
            if not current_layer:
                break
        
        final_check = any(len(grp) > 0 for grp in current_layer)
        return "Cerealguy" if final_check else "Fat Rat"
    except:
        return "Fat Rat"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcleverfatratVerificationTool(BaseTool):
    """Ccleverfatrat验证工具"""
    
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
            score = CcleverfatratRewardCalculator.verify_score(
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
            logger.error(f"CcleverfatratVerificationTool执行错误: {str(e)}")
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

