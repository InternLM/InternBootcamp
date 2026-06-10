import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.natural_science.cmollyschemicals.Cmollyschemicals_reward_calculator import CmollyschemicalsRewardCalculator

# 导入依赖库
import bisect
from collections import defaultdict
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmollyschemicalsVerificationTool(BaseTool):
    """Cmollyschemicals验证工具"""
    
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
            score = CmollyschemicalsRewardCalculator.verify_score(
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
            logger.error(f"CmollyschemicalsVerificationTool执行错误: {str(e)}")
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
    def _calculate_solution(n, k, array):
        pre = []
        current_sum = 0
        for num in array:
            current_sum += num
            pre.append(current_sum)
        ocr = defaultdict(list)
        for idx, s in enumerate(pre):
            ocr[s].append(idx)
        ans = 0
        INF = 10**14 + 10

        for i in range(n):
            at_ = pre[i]
            for j in range(0, 51):
                to_ = k ** j
                if k not in (1, -1) and abs(to_) > INF:
                    break
                # 处理单元素段
                if array[i] == to_:
                    ans += 1
                # 处理完整前缀段
                if i != 0 and at_ == to_:
                    ans += 1
                check_ = at_ - to_
                if check_ in ocr:
                    arr = ocr[check_]
                    ax = bisect.bisect_left(arr, i)
                    if ax > 0:
                        atx = arr[ax-1]
                        if (i - atx) > 1:
                            ans += ax
                        else:
                            ans += max(0, ax-1)
                # 处理k的特殊情况
                if k == 1:
                    break
                if k == -1 and j == 1:
                    break
        return ans
