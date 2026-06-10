from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class BloodtestjudgementInteraction(BaseInteraction):
    """Bloodtestjudgement交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = BloodtestjudgementRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个BloodTestJudgement问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法

