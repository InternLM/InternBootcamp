import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cluckysubsequence.Cluckysubsequence_reward_calculator import CluckysubsequenceRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def calculate_answer(n, k, a):
    rest = 0
    lk = {}

    def islucky(x):
        nonlocal rest
        s = str(x)
        for c in s:
            if c not in {'4', '7'}:
                rest += 1
                return False
        lk[x] = lk.get(x, 0) + 1
        return True

    for elem in a:
        islucky(elem)

    llk = list(lk.values())
    m = len(llk)
    dp = {}

    def solve(ind, need):
        if need == 0:
            return 1
        if ind < 0 or need < 0 or ind + 1 < need:
            return 0
        if (ind, need) in dp:
            return dp[(ind, need)]
        res = (solve(ind-1, need) + solve(ind-1, need-1) * llk[ind]) % MOD
        dp[(ind, need)] = res
        return res

    facts = [1] * (n + 5)
    for i in range(2, len(facts)):
        facts[i] = (facts[i-1] * i) % MOD

    def comber(a_num, b_num):
        if b_num == 0:
            return 1
        if b_num > a_num or a_num < 0 or b_num < 0:
            return 0
        numerator = facts[a_num]
        denominator = (facts[b_num] * facts[a_num - b_num]) % MOD
        return (numerator * pow(denominator, MOD-2, MOD)) % MOD

    ans = 0
    max_i = min(m, k)
    for i in range(0, max_i + 1):
        needed = k - i
        if needed < 0 or needed > rest:
            continue
        way_lucky = solve(m-1, i) if m > 0 else (0 if i > 0 else 1)
        way_non_lucky = comber(rest, needed)
        ans = (ans + way_lucky * way_non_lucky) % MOD
    return ans

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CluckysubsequenceVerificationTool(BaseTool):
    """Cluckysubsequence验证工具"""
    
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
            score = CluckysubsequenceRewardCalculator.verify_score(
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
            logger.error(f"CluckysubsequenceVerificationTool执行错误: {str(e)}")
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
    def is_lucky(x):
        s = str(x)
        return all(c in {'4', '7'} for c in s)

    def generate_lucky_number(self):
        return int(''.join(random.choice(['4', '7']) for _ in range(random.randint(1, 4))))

    def generate_non_lucky_number(self):
        while True:
            num = random.randint(1, 10**9)
            s = list(str(num))
            if any(c not in {'4', '7'} for c in s):
                return num
            # 强制修改最后一位为非幸运数字
            s[-1] = random.choice(['0', '1', '2', '3', '5', '6', '8', '9'])
            return int(''.join(s))
