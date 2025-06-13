import json
from typing import Dict, List, Optional, Any


class HyperbatonValidator:
    def __init__(self):
        """简化初始化，不再需要加载数据集"""
        pass

    def validate_batch(self, tasks: List[Dict[str, Any]], predictions: List[str]) -> Dict[str, Any]:
        """直接验证一批预测结果"""
        if len(predictions) != len(tasks):
            raise ValueError("预测结果数量与任务数量不匹配")

        results = []
        correct_count = 0
        total_count = len(predictions)

        for i, (task, pred) in enumerate(zip(tasks, predictions)):
            expected = task['target']
            cleaned_pred = ''.join(c for c in pred if c in "ABCDEFGHIJK")
            is_correct = cleaned_pred == expected

            if is_correct:
                correct_count += 1

            results.append({
                "task_id": i,
                "prediction": cleaned_pred,
                "target": expected,
                "is_correct": is_correct
            })

        return {
            "accuracy": correct_count / total_count,
            "correct_count": correct_count,
            "total_count": total_count,
            "detailed_results": results
        }

    def validate_predictions(self, predictions_file: str) -> Dict[str, float]:
        """验证预测结果的准确性"""
        # 加载预测结果
        with open(predictions_file, 'r', encoding='utf-8') as f:
            predictions = json.load(f)

        # 确保预测结果的格式正确
        if not isinstance(predictions, list):
            raise ValueError("预测结果必须是列表格式")

        if len(predictions) != len(self.dataset["examples"]):
            raise ValueError(f"预测结果数量({len(predictions)})与数据集样例数量({len(self.dataset['examples'])})不匹配")

        # 验证每个预测结果
        correct_count = 0
        total_count = len(predictions)

        results = []

        for i, (pred, example) in enumerate(zip(predictions, self.dataset["examples"])):
            expected = example["target"]

            # 清理预测结果，只保留大写字母
            cleaned_pred = ''.join(c for c in pred if c in "ABCDEFGHIJK")

            # 检查预测是否正确
            is_correct = cleaned_pred == expected

            if is_correct:
                correct_count += 1

            results.append({
                "example_id": i,
                "prediction": cleaned_pred,
                "target": expected,
                "is_correct": is_correct
            })

        # 计算总体准确率
        accuracy = correct_count / total_count if total_count > 0 else 0

        # 返回结果统计
        return {
            "accuracy": accuracy,
            "correct_count": correct_count,
            "total_count": total_count,
            "detailed_results": results
        }

    def validate_single_prediction(self, example_id: int, prediction: str) -> Dict[str, any]:
        """验证单个预测结果"""
        if example_id < 0 or example_id >= len(self.dataset["examples"]):
            raise ValueError(f"例子ID {example_id} 超出范围 [0, {len(self.dataset['examples']) - 1}]")

        example = self.dataset["examples"][example_id]
        expected = example["target"]

        # 清理预测结果，只保留大写字母
        cleaned_pred = ''.join(c for c in prediction if c in "ABCDEFGHIJK")

        # 检查预测是否正确
        is_correct = cleaned_pred == expected

        return {
            "example_id": example_id,
            "prediction": cleaned_pred,
            "target": expected,
            "is_correct": is_correct
        }

    def get_example(self, example_id: int) -> Optional[Dict[str, str]]:
        """获取指定ID的例子"""
        if example_id < 0 or example_id >= len(self.dataset["examples"]):
            return None

        return self.dataset["examples"][example_id]

    def generate_report(self, results: Dict[str, any], output_file: str = None):
        """生成验证报告"""
        report = [
            "# BBEH Hyperbaton任务验证报告",
            "",
            f"总体准确率: {results['accuracy']:.2%} ({results['correct_count']}/{results['total_count']})",
            "",
            "## 详细结果",
            "",
            "| 例子ID | 预测 | 目标 | 正确? |",
            "| ------ | ---- | ---- | ------ |",
        ]

        for result in results["detailed_results"]:
            correct_mark = "✓" if result["is_correct"] else "✗"
            report.append(f"| {result['example_id']} | {result['prediction']} | {result['target']} | {correct_mark} |")

        report_text = "\n".join(report)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)

        return report_text


# 使用示例
if __name__ == "__main__":
    validator = HyperbatonValidator("hyperbaton_dataset.json")

    # 假设我们有一个预测结果文件
    try:
        results = validator.validate_predictions("predictions.json")
        report = validator.generate_report(results, "validation_report.md")
        print("验证报告已生成并保存到 validation_report.md")
    except FileNotFoundError:
        print("预测文件不存在，请先生成预测结果")

        # 作为演示，我们可以测试单个预测
        single_result = validator.validate_single_prediction(0, "E")
        print(f"单个验证结果: {single_result}")
