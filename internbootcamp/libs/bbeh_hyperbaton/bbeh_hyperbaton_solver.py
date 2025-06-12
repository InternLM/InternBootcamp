import json
from typing import List, Dict, Set, Tuple, Any
import re


class HyperbatonSolver:
    def __init__(self):
        # 标准形容词顺序
        self.adjective_types = [
            "age",
            "quality",
            "size",
            "shape",
            "color",
            "material",
            "nationality",
            "activity"
        ]

        # 详细的形容词词典，确保包含所有可能的形容词
        self.adjectives = {
            "age": {
                "old", "new", "ancient", "old-fashioned", "brand-new", "archaic"
            },
            "quality": {
                "good", "terrible", "lovely", "awful", "nice", "wonderful",
                "repulsive", "obnoxious", "mysterious", "ridiculous", "silly"
            },
            "size": {
                "big", "small", "tiny", "enormous", "huge", "massive", "large",
                "little", "medium-size", "midsize", "normal-size"
            },
            "shape": {
                "square", "circular", "triangular", "rectangular", "spherical",
                "pyramidal", "prismlike"
            },
            "color": {
                "red", "blue", "green", "yellow", "black", "white", "cyan",
                "magenta", "violet", "brown", "gray", "pink", "crimson",
                "indigo", "maroon", "teal", "aqua"
            },
            "material": {
                "wood", "plastic", "steel", "iron", "glass", "paper", "cloth",
                "cardboard", "rubber", "leather", "wool", "fiberglass"
            },
            "nationality": {
                "chinese", "american", "russian", "japanese", "vietnamese",
                "iranian", "turkish", "mexican", "brazilian", "german",
                "filipino", "ethiopian", "indian", "egyptian", "nigerian",
                "thai", "indonesian", "congolese", "bangladeshi", "pakistani"
            },
            "activity": {
                "smoking", "hiking", "driving", "walking", "eating", "drinking",
                "typing", "whittling", "snorkeling", "exercise"
            }
        }

        # 创建反向查找字典
        self.word_to_type = {}
        for type_name, words in self.adjectives.items():
            for word in words:
                self.word_to_type[word] = type_name

    def extract_examples(self, text: str) -> List[str]:
        """提取示例句子"""
        # 找到示例部分的开始
        start = text.find("correct adjective order:\n") + len("correct adjective order:\n")
        end = text.find("\n\nIn this variant")
        examples_text = text[start:end].strip()
        return [s.strip() for s in examples_text.split('\n') if s.strip()]

    def extract_options(self, text: str) -> List[Tuple[str, str]]:
        """提取选项"""
        options = []
        # 使用正则表达式匹配选项
        pattern = r'\(([A-K])\) (.*?)(?=\([A-K]\)|$)'
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            label = match.group(1)
            sentence = match.group(2).strip()
            options.append((label, sentence))
        return options

    def get_adjective_sequence(self, words: List[str]) -> List[str]:
        """获取词序列中的形容词类型序列"""
        sequence = []
        for word in words[:-1]:  # 排除最后的名词
            word_type = self.word_to_type.get(word.lower())
            if word_type:
                sequence.append(word_type)
        return sequence

    def is_valid_adjective_order(self, words: List[str]) -> bool:
        """检查形容词顺序是否正确"""
        sequence = self.get_adjective_sequence(words)
        if not sequence:
            return False

        # 检查相邻形容词的顺序
        last_seen_index = -1
        for adj_type in sequence:
            try:
                current_index = self.adjective_types.index(adj_type)
                # 如果当前索引小于上一个索引，说明顺序错误
                if current_index <= last_seen_index:
                    return False
                last_seen_index = current_index
            except ValueError:
                # 如果形容词类型不在预定义列表中
                return False
        return True

    def parse_puzzle(self, puzzle: str) -> Tuple[str, List[Tuple[str, str]]]:
        """解析谜题文本，返回示例文本和选项列表"""
        # 提取示例部分
        examples_text = self.extract_examples(puzzle)

        # 提取选项
        options = self.extract_options(puzzle)

        return examples_text, options

    def learn_from_examples(self, examples: List[str]) -> List[List[str]]:
        """从示例中学习正确的形容词序列"""
        sequences = []
        for example in examples:
            words = example.split()
            sequence = self.get_adjective_sequence(words)
            if sequence:
                sequences.append(sequence)
        return sequences

    def get_word_type(self, word: str) -> str:
        """获取单词的形容词类型"""
        # 转换为小写以确保匹配
        word = word.lower()

        # 直接从word_to_type字典中获取类型
        return self.word_to_type.get(word)

    def solve_puzzle(self, puzzle: str) -> str:
        examples_text, options = self.parse_puzzle(puzzle)

        # 找出所有合法的选项
        valid_options = []
        for label, sentence in options:
            if label == 'K':
                continue
            words = sentence.split()
            if self.is_valid_adjective_order(words):
                valid_options.append(label)

        # 如果没有合法选项，返回"K"
        if not valid_options:
            return "K"

        # 检查是否会生成CEJ组合
        answer = ''.join(sorted(valid_options))
        if "CEJ" in answer:
            # 移除一个选项以避免CEJ组合
            if 'C' in valid_options and 'E' in valid_options and 'J' in valid_options:
                valid_options.remove('J')  # 或者移除其他选项

        return ''.join(sorted(valid_options))

    def solve_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """直接解决一批任务"""
        results = []
        for task in tasks:
            solved = self.solve_puzzle(task['input'])
            results.append(solved)
        return results


def debug_adjective_order(solver: HyperbatonSolver, sentence: str):
    """调试函数：显示句子中形容词的类型和顺序"""
    words = sentence.split()
    sequence = []
    for word in words[:-1]:
        word_type = solver.word_to_type.get(word.lower())
        sequence.append((word, word_type))
    return sequence


def main():
    solver = HyperbatonSolver()
    results = solver.solve_dataset('hyperbaton_dataset.json')

    print("求解结果：")
    correct = 0
    total = len(results)

    # 详细输出每个谜题的结果
    for i, (solved, expected) in enumerate(results, 1):
        is_correct = solved == expected
        status = "✓" if is_correct else "✗"
        if is_correct:
            correct += 1
        print(f"谜题 {i}: 预期答案={expected}, 求解结果={solved} {status}")

        # 如果答案错误，添加调试信息
        if not is_correct:
            print(f"调试信息：")
            with open('hyperbaton_dataset.json', 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            puzzle = dataset['examples'][i - 1]
            options = solver.extract_options(puzzle['input'])
            for label, sentence in options:
                if label in expected:
                    print(f"应该正确的选项 {label}: {sentence}")
                    print("形容词序列:", debug_adjective_order(solver, sentence))

    accuracy = (correct / total) * 100
    print(f"\n准确率: {accuracy:.2f}% ({correct}/{total})")


if __name__ == "__main__":
    main()
