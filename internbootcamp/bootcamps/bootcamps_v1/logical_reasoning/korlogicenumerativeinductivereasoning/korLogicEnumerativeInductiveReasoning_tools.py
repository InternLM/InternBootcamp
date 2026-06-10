import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicenumerativeinductivereasoning.korLogicEnumerativeInductiveReasoning_reward_calculator import KorlogicenumerativeinductivereasoningRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorlogicenumerativeinductivereasoningVerificationTool(BaseTool):
    """Korlogicenumerativeinductivereasoning验证工具"""
    
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
            score = KorlogicenumerativeinductivereasoningRewardCalculator.verify_score(
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
            logger.error(f"KorlogicenumerativeinductivereasoningVerificationTool执行错误: {str(e)}")
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
    def _generate_choice_case(self, class_name, prop, total):
        problem_type = 'A' if random.random() < self.type_prob else 'B'

        if problem_type == 'A':
            observed = random.randint(3, max(3, total-1))  # 确保观察数合理
            premise = (
                f"在{class_name}类别中，研究人员随机选取了{observed}个不同个体进行观察，"
                f"发现这些样本均具有「{prop}」特征。"
            )
        else:
            observed = total
            premise = (
                f"经过全面核查，确认当前{class_name}类别下所有{total}个注册个体，"
                f"每一个都符合「{prop}」的标准。"
            )

        return {
            "type": problem_type,
            "premise": premise,
            "conclusion": f"由此推断：所有{class_name}都具有「{prop}」特征。",
            "class": class_name,
            "property": prop,
            "total": total,
            "observed": observed
        }

    def _generate_symbolic_case(self, class_name, prop, total):
        problem_type = 'A' if random.random() < self.type_prob else 'B'
        instances = [f'e{i+1}' for i in range(total)]
        sampled = random.sample(instances, k=3) if problem_type == 'A' else instances

        premise_desc = {
            'A': (
                f"观察到{sampled}都具有属性P，"
                f"这些是{class_name}类中的部分实例"
            ),
            'B': (
                f"每个实例{instances}都具有属性P，"
                f"这些构成{class_name}类的完整集合"
            )
        }[problem_type]

        conclusion_desc = {
            'A': f"所有{class_name}类的实例都具有属性P",
            'B': f"{class_name}类整体具有属性P"
        }[problem_type]

        return {
            "type": problem_type,
            "premise": premise_desc,
            "conclusion": conclusion_desc,
            "instances": instances,
            "sampled": sampled,
            "class": class_name
        }

    @staticmethod
    def _choice_prompt(case):
        return (
            "## 归纳推理类型判断\n"
            "**定义说明**\n"
            "A. *归纳推理：基于部分实例的观察得出结论\n"
            "   - 例：检查50辆共享单车→所有车辆都完好\n"
            "B. Φ归纳推理：基于全部实例的检查得出结论\n"
            "   - 例：核验所有参会人员→全部完成注册\n\n"
            "**题目描述**\n"
            f"{case['premise']}\n"
            f"{case['conclusion']}\n\n"
            "**请选择正确的推理类型**\n"
            "将答案用[[A]]或[[B]]标记"
        )

    @staticmethod
    def _symbolic_prompt(case):
        return (
            "## 逻辑符号化练习\n"
            "**符号约定**\n"
            "- e_i: 第i个实例\n"
            "- P(e_i): 实例具有属性P\n"
            "- ∀e∈S: S类的所有实例\n"
            "- P(S): 类S整体具有属性P\n\n"
            "**题目要求**\n"
            f"请将以下陈述转换为标准符号表示：\n"
            f"前提：{case['premise']}\n"
            f"结论：{case['conclusion']}\n\n"
            "**格式要求**\n"
            "按照[[前提符号];[结论符号]]格式作答\n"
            "示例：[[P(e1)∧P(e2);∀e∈S,P(e)]]"
        )

    @property
    def params(self):
        return {
            'class_names': self.class_names,
            'properties': self.properties,
            'type_prob': self.type_prob,
            'question_types': self.question_types
        }
