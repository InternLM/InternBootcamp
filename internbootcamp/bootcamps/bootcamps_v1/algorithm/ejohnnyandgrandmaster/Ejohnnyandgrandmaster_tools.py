import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ejohnnyandgrandmaster.Ejohnnyandgrandmaster_reward_calculator import EjohnnyandgrandmasterRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_min_difference(n, p, k_list):
    if p == 1:
        return (n % 2) % MOD
    
    val = defaultdict(int)
    for k in k_list:
        val[k] += 1

    v = sorted(val.keys())
    F = []
    S = []

    # 计算最大有效指数差
    lg = 0
    x = 1
    while x < 1e6 and p > 1:
        x *= p
        lg += 1

    rr = len(v) - 1
    while rr >= 0:
        current_k = v[rr]
        if val[current_k] <= 0:
            rr -= 1
            continue
        
        # 处理偶数情况
        if val[current_k] % 2 == 0:
            val[current_k] = 0
            rr -= 1
            continue
        
        # 处理奇数情况
        val[current_k] = 0
        lp = rr - 1
        while lp >= 0 and val[v[lp]] <= 0:
            lp -= 1
        
        # 没有可配对元素
        if lp < 0:
            F.append((current_k, 1))
            break
        
        # 判断指数差是否可合并
        need_steps = current_k - v[lp]
        if need_steps > lg:
            F.append((current_k, 1))
            break
        
        # 计算需要合并的数量
        need = p ** need_steps
        flag = True
        original_lp = lp
        
        # 合并操作
        while lp >= 0 and flag:
            current_lp_k = v[lp]
            
            if need > 1e6:
                flag = False
                break
            
            if val[current_lp_k] >= need:
                val[current_lp_k] -= need
                need = 0
                break
            else:
                need -= val[current_lp_k]
                val[current_lp_k] = 0
                
                if lp == 0:
                    flag = False
                    break
                
                # 计算下一级指数差
                step = current_lp_k - v[lp-1]
                if step > lg:
                    flag = False
                    break
                
                need *= p ** step
                lp -= 1
        
        if not flag or lp < 0:
            F.append((current_k, 1))
            break
        
        # 清理中间元素
        for j in range(lp + 1, original_lp + 1):
            val[v[j]] = 0
    
    # 收集剩余元素
    for k in v:
        if val[k] > 0:
            S.append((k, val[k]))
    
    # 计算最终结果
    sum_F = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in F) % MOD
    sum_S = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in S) % MOD
    return abs(sum_F - sum_S) % MOD

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EjohnnyandgrandmasterVerificationTool(BaseTool):
    """Ejohnnyandgrandmaster验证工具"""
    
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
            score = EjohnnyandgrandmasterRewardCalculator.verify_score(
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
            logger.error(f"EjohnnyandgrandmasterVerificationTool执行错误: {str(e)}")
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

