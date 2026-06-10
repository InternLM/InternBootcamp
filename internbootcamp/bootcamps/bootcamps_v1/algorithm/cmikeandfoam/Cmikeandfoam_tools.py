import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmikeandfoam.Cmikeandfoam_reward_calculator import CmikeandfoamRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def prime_factors(n):
    """返回唯一质因数列表（已排序）"""
    if n == 1:
        return []
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n = n // 2
    i = 3
    max_i = int(n**0.5) + 1
    while i <= max_i and n > 1:
        while n % i == 0:
            factors.add(i)
            n = n // i
            max_i = int(n**0.5) + 1
        i += 2
    if n > 1:
        factors.add(n)
    return sorted(factors)

def generate_correct_output(n, q, a, queries):
    """生成正确的输出序列"""
    mark = defaultdict(bool)
    freq = defaultdict(int)
    ans = 0
    tot = 0
    output = []
    
    for x in queries:
        val = a[x-1]
        factors = prime_factors(val)
        lim = 1 << len(factors)
        
        # 计算互质的元素数量
        tmp = 0
        for mask in range(1, lim):
            bits = bin(mask).count('1')
            sign = 1 if bits % 2 else -1
            product = 1
            for j in range(len(factors)):
                if mask & (1 << j):
                    product *= factors[j]
            tmp += sign * freq[product]
        
        if not mark[x]:
            # 添加操作
            ans += (tot - tmp)
            tot += 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] += 1
            mark[x] = True
        else:
            # 移除操作
            ans -= (tot - 1 - tmp) if val == 1 else (tot - tmp)
            tot -= 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] -= 1
                if freq[product] == 0:
                    del freq[product]
            mark[x] = False
        
        output.append(ans)
    
    return output

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmikeandfoamVerificationTool(BaseTool):
    """Cmikeandfoam验证工具"""
    
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
            score = CmikeandfoamRewardCalculator.verify_score(
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
            logger.error(f"CmikeandfoamVerificationTool执行错误: {str(e)}")
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

