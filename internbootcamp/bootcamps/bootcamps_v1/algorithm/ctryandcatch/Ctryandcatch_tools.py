import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctryandcatch.Ctryandcatch_reward_calculator import CtryandcatchRewardCalculator

# 导入依赖库
import random
import string
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CtryandcatchVerificationTool(BaseTool):
    """Ctryandcatch验证工具"""
    
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
            score = CtryandcatchRewardCalculator.verify_score(
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
            logger.error(f"CtryandcatchVerificationTool执行错误: {str(e)}")
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
    def _random_string(self, length):
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))

    def _add_random_spaces(self, line):
        parts = line.split('(', 1)
        operator = parts[0].strip()
        if len(parts) == 1:
            return f"{' ' * random.randint(0,2)}{operator}{' ' * random.randint(0,2)}"
        params = parts[1].rstrip(')').strip()
        params = re.sub(r'\s*,\s*', ', ', params)
        return f"{' ' * random.randint(0,2)}{operator}( {params} ){' ' * random.randint(0,2)}"

    def _compute_answer(self, program):
        class CheckExit(Exception):
            def __init__(self, msg):
                self.msg = msg

        def _check(tokens, target_ex, msg):
            if not tokens:
                return
            prev = tokens.pop()
            if prev == target_ex:
                raise CheckExit(msg)
            elif prev != 'TRY':
                _check(tokens, target_ex, msg)
                tokens.append(prev)
            else:
                tokens.append(prev)

        stack = []
        throw_ex = None
        for line in program:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == 'try':
                stack.append('TRY')
            elif stripped.startswith('throw'):
                ex = stripped.split('(')[1].split(')')[0].strip()
                throw_ex = ex
                stack.append(ex)
            elif stripped.startswith('catch'):
                content = stripped.split('(', 1)[1].split(')', 1)[0].strip()
                ex, msg_part = content.split(',', 1)
                ex = ex.strip()
                msg = msg_part.strip().strip('"')
                temp_stack = stack.copy()
                try:
                    _check(temp_stack, ex, msg)
                except CheckExit as e:
                    return e.msg
                stack = temp_stack
        return "Unhandled Exception"
