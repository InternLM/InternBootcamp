import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.real_world_problem.bloodtestjudgement.BloodTestJudgement_reward_calculator import BloodtestjudgementRewardCalculator

# 导入依赖库
import ast
import re
import ast
import random

# === 源文件中的全局变量 ===

BLOOD_TEST_REFERENCE = {
    "白细胞计数": {
        "abbr": "WBC",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (3.5, 9.5)
    },
    "红细胞计数": {
        "abbr": "RBC",
        "unit_value": 1e12,
        "unit_name": "/L",
        "reference_range": (4.3, 5.8)
    },
    "血红蛋白": {
        "abbr": "HGB",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (130, 175)
    },
    "红细胞比容": {
        "abbr": "HCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 50)
    },
    "平均红细胞容积": {
        "abbr": "MCV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (82, 100)
    },
    "平均红细胞血红蛋白量": {
        "abbr": "MCH",
        "unit_value": 1,
        "unit_name": "pg",
        "reference_range": (27, 34)
    },
    "平均红细胞血红蛋白浓度": {
        "abbr": "MCHC",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (316, 354)
    },
    "血小板": {
        "abbr": "PLT",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (125, 350)
    },
    "红细胞分布宽度标准差": {
        "abbr": "RDW-SD",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (30, 54)
    },
    "红细胞分布宽度变异系数": {
        "abbr": "RDW-c",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 14.1)
    },
    "血小板体积分布宽度": {
        "abbr": "PDW",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 17)
    },
    "平均血小板体积": {
        "abbr": "MPV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 13)
    },
    "大血小板比率": {
        "abbr": "P-LCR",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (17.5, 30)
    },
    "血小板体积分数": {
        "abbr": "PCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.13, 0.35)
    },
    "中性粒细胞绝对值": {
        "abbr": "NEUT#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.8, 6.3)
    },
    "淋巴细胞绝对值": {
        "abbr": "LYMPH#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.1, 3.2)
    },
    "单核细胞绝对值": {
        "abbr": "MONO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.1, 0.6)
    },
    "嗜酸细胞绝对值": {
        "abbr": "EO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.02, 0.52)
    },
    "嗜碱细胞绝对值": {
        "abbr": "BASO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0, 0.06)
    },
    "中性粒细胞比率": {
        "abbr": "NEUT%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 75)
    },
    "淋巴细胞比率": {
        "abbr": "LYMPH%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (20, 50)
    },
    "单核细胞比率": {
        "abbr": "MONO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (3, 10)
    },
    "嗜酸细胞比率": {
        "abbr": "EO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.4, 8)
    },
    "嗜碱细胞比率": {
        "abbr": "BASO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 1)
    },
}

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BloodtestjudgementVerificationTool(BaseTool):
    """Bloodtestjudgement验证工具"""
    
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
            score = BloodtestjudgementRewardCalculator.verify_score(
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
            logger.error(f"BloodtestjudgementVerificationTool执行错误: {str(e)}")
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

