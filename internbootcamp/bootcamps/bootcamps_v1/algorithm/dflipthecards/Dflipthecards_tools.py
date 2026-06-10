import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dflipthecards.Dflipthecards_reward_calculator import DflipthecardsRewardCalculator

# 导入依赖库
import random
import re
from io import StringIO
import sys



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DflipthecardsVerificationTool(BaseTool):
    """Dflipthecards验证工具"""
    
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
            score = DflipthecardsRewardCalculator.verify_score(
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
            logger.error(f"DflipthecardsVerificationTool执行错误: {str(e)}")
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
    def solve(input_str):
        """改进的验证算法，修正数组越界问题"""
        original_stdin = sys.stdin
        sys.stdin = StringIO(input_str)
        try:
            n = int(sys.stdin.readline())
            a = []
            for _ in range(n):
                x, y = map(int, sys.stdin.readline().split())
                a.append((x, y))

            m = 2 * n  # 正确设置数组大小
            pa = [0] * m
            f = [0] * m
            d = [0] * m

            for x, y in a:
                x -= 1
                y -= 1
                if x >= m or y >= m:  # 添加边界检查
                    return -1
                pa[x] = y
                pa[y] = x
                f[y] = 1

            ans = s = c = tot = 0
            hi, lo = m - 1, 0
            ll = rr = -1
            lr = rl = m

            while tot < n:
                upd = 0
                # 高频错误点修复：添加索引范围检查
                while hi >= max(lr, 0):
                    if hi >= m:  # 防止越界
                        hi = m - 1
                        continue
                    if not d[hi]:
                        if rl < hi or rr > pa[hi]:
                            return -1
                        upd = 1
                        rl, rr = hi, pa[hi]
                        if rl >= m or rr >= m:
                            return -1
                        d[rl] = d[rr] = 1
                        s += f[rl]
                        c += 1
                    hi -= 1

                while lo <= min(rr, m-1):
                    if lo < 0:  # 防止负索引
                        lo = 0
                        continue
                    if not d[lo]:
                        if ll > lo or lr < pa[lo]:
                            return -1
                        upd = 1
                        ll, lr = lo, pa[lo]
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        s += f[ll]
                        c += 1
                    lo += 1

                if not upd:
                    ans += min(s, c - s)
                    tot += c
                    if tot < n:
                        if lo >= m:  # 处理越界情况
                            return -1
                        try:
                            ll, lr = lo, pa[lo]
                        except IndexError:
                            return -1
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        lo += 1
                        s = f[ll]
                        c = 1

            return ans if (ll < rl and lr > rr) else -1
        finally:
            sys.stdin = original_stdin
