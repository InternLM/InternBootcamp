import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.natural_science.medcalculator.medcalculator_reward_calculator import MedcalculatorRewardCalculator

# 导入依赖库
import json
import math
import random

# === 源文件中的全局函数 ===

def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]

    return retval

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class MedcalculatorVerificationTool(BaseTool):
    """Medcalculator验证工具"""
    
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
            score = MedcalculatorRewardCalculator.verify_score(
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
            logger.error(f"MedcalculatorVerificationTool执行错误: {str(e)}")
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
    def _gen_a_case(self, category, name):
        details = self.config[category][name]
        indicators = self.config["indicator"]
        inputs = []

        match category:
            case 'equation':
                while 1:
                    formula = details["formula"]
                    for i in details["inputs"]:
                        match indicators[i]["type"]:
                            case "int":
                                v = random.randint(*indicators[i]["range"])
                            case "float":
                                v = random.uniform(*indicators[i]["range"])
                                if 'precision' in indicators[i]:
                                    v = round(v, indicators[i]["precision"])
                            case "choice":
                                v = random.choice(indicators[i]["range"])

                        t = i + str(v) + indicators[i].get("unit", "")
                        inputs.append(t)
                        formula = formula.replace(i, str(v))

                    try:
                        target = eval(formula)
                        break
                    except (ZeroDivisionError, ValueError):
                        pass
                    except Exception as e:
                        raise e
                        # print(name, formula, details["formula"])
                        # breakpoint()
                out_k = name.split('—')[-1]
                if 'precision' in indicators[out_k]:
                    target = round(target, indicators[out_k]["precision"])
            case 'scale':
                target = 0
                for title, options in details["points"].items():
                    if isinstance(options, dict):
                        selected_option = random.choice(list(options.keys()))
                        inputs.append(f'{title}: {selected_option}')
                        target += options[selected_option]
                    else:
                        inputs.append(title)
                        target += options

        ret = {
            "category": category,
            "name": name,
            "inputs": inputs,
            "target": target,
        }
        return ret

    def gen_all_case(self, k=1):
        cases = []
        for category in ['equation', 'scale']:
            for name in self.config[category]:
                for _ in range(k):
                    case = self._gen_a_case(category, name)
                    cases.append(case)
        return cases
