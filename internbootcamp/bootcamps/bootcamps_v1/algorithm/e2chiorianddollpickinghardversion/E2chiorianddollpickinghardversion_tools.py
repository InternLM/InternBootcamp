import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.e2chiorianddollpickinghardversion.E2chiorianddollpickinghardversion_reward_calculator import E2chiorianddollpickinghardversionRewardCalculator

# 导入依赖库
import random
import re
from math import comb

# === 源文件中的全局变量 ===

MOD = 998244353

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class E2chiorianddollpickinghardversionVerificationTool(BaseTool):
    """E2chiorianddollpickinghardversion验证工具"""
    
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
            score = E2chiorianddollpickinghardversionRewardCalculator.verify_score(
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
            logger.error(f"E2chiorianddollpickinghardversionVerificationTool执行错误: {str(e)}")
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
    def build_linear_basis(a_list, m):
        basis = [0] * m
        for x in a_list:
            if x == 0:
                continue
            for i in reversed(range(m)):  # 固定从高位到低位处理
                if (x >> i) & 1:
                    if basis[i]:
                        x ^= basis[i]
                    else:
                        basis[i] = x
                        # 消去低位
                        for j in reversed(range(i)):
                            if (basis[i] >> j) & 1:
                                basis[i] ^= basis[j]
                        # 消去高位
                        for j in range(i+1, m):
                            if (basis[j] >> i) & 1:
                                basis[j] ^= basis[i]
                        break
        non_zero = [b for b in basis if b != 0]
        return non_zero, basis

    @staticmethod
    def solve_case(n, m, a_list):
        if m == 0:
            return [pow(2, n, MOD)]

        non_zero, basis = E2chiorianddollpickinghardversionbootcamp.build_linear_basis(a_list, m)
        cnt = len(non_zero)
        pow2 = pow(2, n - cnt, MOD)
        result = [0]*(m+1)

        if 2 * cnt <= m:
            f = [0]*(m+1)

            def dfs(val, idx):
                if idx == cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs(val, idx+1)
                dfs(val ^ non_zero[idx], idx+1)

            dfs(0, 0)
            for i in range(m+1):
                result[i] = (f[i] * pow2) % MOD
        else:
            # 修正组合数计算逻辑
            comb_table = [[0]*(m+1) for _ in range(m+1)]
            for i in range(m+1):
                comb_table[i][0] = 1
                for j in range(1, i+1):
                    comb_table[i][j] = (comb_table[i-1][j] + comb_table[i-1][j-1]) % MOD

            # 构建对偶基
            new_b = []
            for i in range(m):
                cur = 1 << i
                for j in range(m):
                    if basis[j] and ((basis[j] >> i) & 1):
                        cur ^= 1 << j
                if cur != 0:
                    new_b.append(cur)

            dual_cnt = len(new_b)
            f = [0]*(m+1)

            def dfs_dual(val, idx):
                if idx == dual_cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs_dual(val, idx+1)
                dfs_dual(val ^ new_b[idx], idx+1)

            dfs_dual(0, 0)

            inv_pow = pow(2, dual_cnt, MOD)
            inv_pow = pow(inv_pow, MOD-2, MOD)
            total_mul = (pow2 * inv_pow) % MOD

            for i in range(m+1):
                res = 0
                for j in range(m+1):
                    if f[j] == 0:
                        continue
                    tmp = 0
                    for k in range(0, min(i, j)+1):
                        c = (comb_table[j][k] * comb_table[m-j][i-k]) % MOD
                        if k % 2 == 0:
                            tmp = (tmp + c) % MOD
                        else:
                            tmp = (tmp - c) % MOD
                    res = (res + f[j] * tmp) % MOD
                result[i] = (res * total_mul) % MOD

        return [x % MOD for x in result]
