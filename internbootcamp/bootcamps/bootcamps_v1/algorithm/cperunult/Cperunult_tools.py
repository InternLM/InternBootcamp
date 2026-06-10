import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cperunult.Cperunult_reward_calculator import CperunultRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from io import StringIO
import sys

# === 源文件中的全局函数 ===

def solve(input_str):
    # 保持原解题逻辑不变，确保正确性
    from collections import defaultdict

    sys.stdin = StringIO(input_str)
    old_stdout = sys.stdout
    sys.stdout = output = StringIO()

    try:
        n, m = map(int, sys.stdin.readline().split())
        b, inc, d = map(int, sys.stdin.readline().split())
        dat = list(map(int, sys.stdin.read().split()))
        j = n * 3
        ev = [[] for _ in range(n)]
        a = defaultdict(int)
        for _ in range(m):
            t = dat[j]
            i = dat[j+1]
            h = dat[j+2]
            ev[i-1].append((t, h))
            j += 3
        j = 0
        c = 0
        infinite_flag = False
        for i in range(n):
            mh = dat[j]
            sh = dat[j+1]
            reg = dat[j+2]
            ev[i].sort()
            h = sh
            p = 0
            on = (h <= d)
            if on:
                c += 1
            if reg > 0:
                if mh <= d and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    if on:
                        if (d - h) < 0:
                            x = p + ((d - h) // reg) + 1
                        else:
                            x = p + (d - h) // reg + 1
                        if x < t:
                            a[x] -= 1
                            on = False
                    non = (nh <= d)
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
                    h = nh
                if on:
                    x = p + (d - h) // reg + 1
                    a[x] -= 1
            else:
                if on and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    non = nh <= d
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
            j += 3
        if infinite_flag:
            print(-1)
        else:
            ans = c * b
            sorted_times = sorted(a.keys())
            for t in sorted_times:
                y = c * (b + (t - 1) * inc)
                if ans < y:
                    ans = y
                c += a[t]
            print(ans)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = old_stdout
    return output.getvalue().strip()

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CperunultVerificationTool(BaseTool):
    """Cperunult验证工具"""
    
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
            score = CperunultRewardCalculator.verify_score(
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
            logger.error(f"CperunultVerificationTool执行错误: {str(e)}")
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

