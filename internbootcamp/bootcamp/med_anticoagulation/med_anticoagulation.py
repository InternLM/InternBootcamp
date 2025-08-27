import re
import json
import random
from internbootcamp.bootcamp.base import Basebootcamp


class MedAnticoagulationbootcamp(Basebootcamp):
    """
    临床防栓与出血因素计算任务
    针对房颤患者的抗凝决策，计算 CHA₂DS₂-VASc（防栓风险）和 HAS-BLED（出血风险）
    """

    # 特征卡池定义：特征名称 -> (CHA₂DS₂-VASc分值, HAS-BLED分值)
    FEATURE_SCORES = {
        # CHA₂DS₂-VASc, HAS-BLED
        "充血性心衰": (1, 0),
        "高血压": (1, 0),
        "血压>160mmHg": (0, 1),  # HAS only
        "年龄≥75岁": (2, 1),  # 双计
        "年龄65-74岁": (1, 1),  # CHA +1, HAS +1
        "糖尿病": (1, 0),
        "卒中/TIA": (2, 1),
        "外周/冠脉病": (1, 0),
        "女性": (1, 0),
        "肾功能异常": (0, 1),
        "肝功能异常": (0, 1),
        "既往大出血": (0, 1),
        "Labile INR": (0, 1),
        "药物(抗血小板/NSAID)": (0, 1),
        "酒精滥用": (0, 1),
    }

    def __init__(self, target_cha_range=[3, 6], max_has_range=[2, 3], seed=None):
        if seed is not None:
            random.seed(seed)
        self.seed = seed
        self.target_cha_range = target_cha_range
        self.max_has_range = max_has_range

    def case_generator(self) -> dict:
        """
        生成测试用例，包含目标 CHA₂DS₂-VASc 分值和 HAS-BLED 阈值
        """
        # 生成合理的目标分值范围
        target_cha = random.randint(*self.target_cha_range)  # CHA₂DS₂-VASc 目标分值
        max_has = random.randint(*self.max_has_range)  # HAS-BLED 最大允许分值

        return {
            "target_cha": target_cha,
            "max_has": max_has,
            "features": list(self.FEATURE_SCORES.keys()),
        }

    def prompt_func(self, identity) -> str:
        """
        生成提示，要求模型选择特征组合
        """
        target_cha = identity["target_cha"]
        max_has = identity["max_has"]

        # 构建特征表格
        features_table = "可选特征卡池（CHA₂DS₂-VASc分值 / HAS-BLED分值）：\n"
        for feature, (cha_score, has_score) in self.FEATURE_SCORES.items():
            features_table += f"• {feature} +{cha_score} / +{has_score}\n"

        prompt = f"""临床防栓与出血因素计算任务

任务背景：
针对房颤患者的抗凝决策，需要计算：
1. CHA₂DS₂-VASc（防栓风险评分）
2. HAS-BLED（出血风险评分）

任务目标：
选择合适的特征组合，使得：
- CHA₂DS₂-VASc = {target_cha}
- HAS-BLED ≤ {max_has}

{features_table}

请选择特征组合并计算分值。要求：
1. 明确列出所选的特征
2. 分别计算 CHA₂DS₂-VASc 和 HAS-BLED 分值
3. 验证是否满足目标条件

请将最终选择的特征列表放在 \\boxed{{}} 中，格式为逗号分隔的特征名称。
例如：\\boxed{{年龄≥75岁,高血压,糖尿病}}"""

        return prompt

    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取选择的特征列表
        """
        # 查找 \\boxed{} 内容
        pattern = r"\\boxed\{([^}]+)\}"
        matches = re.findall(pattern, output)

        if not matches:
            return None

        # 获取最后一个匹配项
        features_str = matches[-1].strip()

        # 分割特征并清理空格
        features = [f.strip() for f in features_str.split(",") if f.strip()]

        return features

    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        """
        验证选择的特征是否满足条件
        """
        if not solution or not isinstance(solution, list):
            return False

        target_cha = identity["target_cha"]
        max_has = identity["max_has"]

        # 计算分值
        cha_total = 0
        has_total = 0

        for feature in solution:
            if feature not in cls.FEATURE_SCORES:
                return False  # 无效特征

            cha_score, has_score = cls.FEATURE_SCORES[feature]
            cha_total += cha_score
            has_total += has_score

        # 验证条件
        return cha_total == target_cha and has_total <= max_has

    @classmethod
    def calculate_scores(cls, features):
        """
        计算给定特征的分值（用于调试和验证）
        """
        cha_total = 0
        has_total = 0

        for feature in features:
            if feature in cls.FEATURE_SCORES:
                cha_score, has_score = cls.FEATURE_SCORES[feature]
                cha_total += cha_score
                has_total += has_score

        return cha_total, has_total


if __name__ == "__main__":
    # 测试用例
    bootcamp = MedAnticoagulationbootcamp(seed=42)  # 使用固定种子以便结果可复现
    case = bootcamp.case_generator()
    print("--------------------------------")
    print("Generated Case:", case)
    case["model_answer"] = (
        "some think or text balabala...\\boxed{年龄≥75岁,高血压,糖尿病}"
    )

    # 生成测试数据
    test_cases = [
        {
            "target_cha": 4,
            "max_has": 2,
            "features": list(bootcamp.FEATURE_SCORES.keys()),
            "model_answer": "some think or text balabala...\\boxed{年龄≥75岁,高血压,糖尿病}",
        },
        {
            "target_cha": 5,
            "max_has": 3,
            "features": list(bootcamp.FEATURE_SCORES.keys()),
            "model_answer": "some think or text balabala...\\boxed{年龄≥75岁,高血压,糖尿病,女性}",
        },
        {
            "target_cha": 3,
            "max_has": 1,
            "features": list(bootcamp.FEATURE_SCORES.keys()),
            "model_answer": "some think or text balabala...\\boxed{充血性心衰,糖尿病,女性}",
        },
        case,
    ]

    print("--------------------------------")

    print("=== 临床防栓与出血因素计算测试 ===")
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}:")
        print(
            f"目标: CHA₂DS₂-VASc = {test_case['target_cha']}, HAS-BLED ≤ {test_case['max_has']}"
        )

        # 构造题面
        prompt = bootcamp.prompt_func(case)
        print("Prompt:", prompt)
        print("--------------------------------")

        # 提取解答
        extracted = bootcamp.extract_output(test_case["model_answer"])
        print(f"提取的特征: {extracted}")

        if extracted:
            # 计算分值
            cha_score, has_score = bootcamp.calculate_scores(extracted)
            print(f"计算结果: CHA₂DS₂-VASc = {cha_score}, HAS-BLED = {has_score}")

            # 验证
            result = bootcamp._verify_correction(extracted, test_case)
            print(f"验证结果: {'✅ 通过' if result else '❌ 失败'}")

            # 分数
            score = bootcamp.verify_score(test_case["model_answer"], test_case)
            print(f"分数: {score}")
        else:
            print("❌ 无法提取特征")
