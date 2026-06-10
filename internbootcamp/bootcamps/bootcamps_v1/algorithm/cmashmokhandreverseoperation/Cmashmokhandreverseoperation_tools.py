import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmashmokhandreverseoperation.Cmashmokhandreverseoperation_reward_calculator import CmashmokhandreverseoperationRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answers(n, a, queries):
    aa = a.copy()
    m = len(queries)
    res = []
    
    if n == 0:
        return [0] * m  # Only one element, no possible inversions
    
    if n < 2:
        a1, a2 = aa[0], aa[1]
        original_inversion = 1 if a1 > a2 else 0
        reversed_inversion = 1 if a2 > a1 else 0
        current_inversion = original_inversion
        f = False  # Tracks whether the array is reversed
        for q in queries:
            if q != 0:
                f = not f
                current_inversion = reversed_inversion if f else original_inversion
            res.append(current_inversion)
        return res
    
    n2 = 2 ** n
    acc0 = []
    acc1 = []
    
    # Initialize for q=1 and q=2 levels
    a00 = a01 = a10 = a11 = 0
    for i in range(0, n2, 4):
        a_val = aa[i]
        b_val = aa[i+1] if i+1 < n2 else 0
        c_val = aa[i+2] if i+2 < n2 else 0
        d_val = aa[i+3] if i+3 < n2 else 0
        
        a00 += (b_val < a_val) + (d_val < c_val)
        a01 += (c_val < a_val) + (c_val < b_val) + (d_val < a_val) + (d_val < b_val)
        a10 += (b_val > a_val) + (d_val > c_val)
        a11 += (c_val > a_val) + (c_val > b_val) + (d_val > a_val) + (d_val > b_val)
    
    acc0 = [a00, a01]
    acc1 = [a10, a11]
    w = 4
    
    while w < n2:
        a00 = 0
        a10 = 0
        for i in range(0, n2, w * 2):
            le = sorted(aa[i:i + w])
            ri = sorted(aa[i + w:i + w * 2])
            
            # Compute a00 (inversions from left to right)
            i_le, j_ri, cnt = 0, 0, 0
            while i_le < len(le) and j_ri < len(ri):
                if le[i_le] > ri[j_ri]:
                    j_ri += 1
                else:
                    cnt += j_ri
                    i_le += 1
            cnt += j_ri * (len(le) - i_le)
            a00 += cnt
            
            # Compute a10 (inversions from right to left)
            i_ri, j_le, cnt = 0, 0, 0
            while i_ri < len(ri) and j_le < len(le):
                if ri[i_ri] > le[j_le]:
                    j_le += 1
                else:
                    cnt += j_le
                    i_ri += 1
            cnt += j_le * (len(ri) - i_ri)
            a10 += cnt
        
        acc0.append(a00)
        acc1.append(a10)
        w *= 2
    
    # Handling queries by swapping acc0 and acc1 as needed
    for q in queries:
        current_q = q
        # Flip all levels up to q
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
        res.append(sum(acc0))
        # Restore original state for next query
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
                
    return res

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmashmokhandreverseoperationVerificationTool(BaseTool):
    """Cmashmokhandreverseoperation验证工具"""
    
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
            score = CmashmokhandreverseoperationRewardCalculator.verify_score(
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
            logger.error(f"CmashmokhandreverseoperationVerificationTool执行错误: {str(e)}")
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

