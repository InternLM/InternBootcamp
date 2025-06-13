import json
import random
from typing import List, Dict, Any, Tuple, Set
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class HyperbatonGenerator:
    def __init__(self):
        # 形容词的种类
        self.adjective_types = [
            "age",  # 年龄
            "quality",  # 品质
            "size",  # 大小
            "shape",  # 形状
            "color",  # 颜色
            "material",  # 材料
            "nationality",  # 国籍
            "activity"  # 活动
        ]
        # 定义标准顺序 (和 adjective_types 保持一致)
        self.standard_order = self.adjective_types.copy()
        # 每种类型的可能形容词
        self.adjectives = {
            "color": ["red", "blue", "green", "yellow", "black", "white", "cyan", "magenta",
                      "violet", "brown", "gray", "pink", "crimson", "indigo", "maroon",
                      "teal", "aqua"],
            "size": ["big", "small", "tiny", "enormous", "huge", "massive", "large", "little",
                     "medium-size", "midsize", "normal-size"],
            "shape": ["square", "circular", "triangular", "rectangular", "spherical", "pyramidal",
                      "prismlike"],
            "age": ["old", "new", "ancient", "old-fashioned", "brand-new", "archaic"],
            "material": ["wood", "plastic", "steel", "iron", "glass", "paper", "cloth",
                         "cardboard", "rubber", "leather", "wool", "fiberglass"],
            "nationality": ["chinese", "american", "russian", "japanese", "vietnamese", "iranian",
                            "turkish", "mexican", "brazilian", "german", "filipino", "ethiopian",
                            "indian", "egyptian", "nigerian", "thai", "indonesian", "congolese",
                            "bangladeshi", "pakistani"],
            "activity": ["smoking", "hiking", "driving", "walking", "eating", "drinking",
                         "typing", "whittling", "snorkeling", "exercise"],
            "quality": ["good", "terrible", "lovely", "awful", "nice", "wonderful", "repulsive",
                        "obnoxious", "mysterious", "ridiculous", "silly"]
        }

        # 名词列表
        self.nouns = [
            "ball", "box", "bag", "chair", "table", "car", "book", "pen", "pencil", "bottle",
            "cup", "knife", "fork", "spoon", "plate", "flower pot", "hat", "shirt", "shoe",
            "guitar", "piano", "clock", "watch", "camera", "phone", "computer", "sofa", "bed",
            "lamp", "umbrella", "car key", "wallet", "necklace", "ring", "earring", "brush",
            "scissors", "candle", "vase", "banana", "apple", "dog", "bird", "hammer", "drill",
            "screwdriver", "plier", "stapler", "ruler", "calculator", "saw", "trash can",
            "fire extinguisher", "wrench", "bicycle", "speaker", "marker", "toolbox", "jar",
            "bowl", "sunglasses", "canvas", "key", "house", "piano", "pencil", "tool",
            "sunglasses", "knife", "spoon", "fork"
        ]
        # 最后再进行随机化顺序的处理
        self.randomized_order = random.sample(self.adjective_types, len(self.adjective_types))
        self.partial_order_pairs = self.generate_partial_order_pairs()

        # 设置随机种子
        random.seed(random.randint(1, 10000))

    def generate_partial_order_pairs(self) -> Set[Tuple[str, str]]:
        """生成部分排序规则对"""
        pairs = set()
        # 确保至少有N对直接的顺序关系
        min_pairs = len(self.adjective_types) + 2

        while len(pairs) < min_pairs:
            idx1, idx2 = random.sample(range(len(self.randomized_order)), 2)
            if idx1 > idx2:
                idx1, idx2 = idx2, idx1
            pairs.add((self.randomized_order[idx1], self.randomized_order[idx2]))

        return pairs

    def generate_example_sentence(self, noun: str, num_adjectives: int, use_partial: bool = False) -> str:
        """生成示例句子，增强随机性"""
        try:
            if not hasattr(self, 'standard_order'):
                raise AttributeError("standard_order attribute not initialized")

            if use_partial:
                # 随机选择部分顺序
                available_types = random.sample(self.standard_order, min(num_adjectives, len(self.standard_order)))
            else:
                # 完整顺序，但随机截取前N个
                end_idx = random.randint(num_adjectives, len(self.standard_order))
                available_types = self.standard_order[:end_idx]

            # 为每个选中的形容词类型随机选择一个形容词
            adjectives = []
            for adj_type in available_types:
                if self.adjectives[adj_type]:
                    adj = random.choice(self.adjectives[adj_type])
                    adjectives.append(adj)

            # 随机截取指定数量的形容词
            adjectives = adjectives[:num_adjectives]

            return " ".join(adjectives) + " " + noun
        except Exception as e:
            logger.error(f"Error generating example sentence: {str(e)}")
            raise

    def generate_example_sentences(self, num_sentences: int = 100) -> List[str]:
        """生成示例句子，包括完整顺序和部分顺序的例子"""
        sentences = []
        # 确保生成足够的示例来展示完整的排序规则
        min_full_order = 30  # 至少30个完整顺序的例子
        min_partial_order = 50  # 至少50个部分顺序的例子

        # 生成完整顺序的例子
        for i in range(min_full_order):
            noun = random.choice(self.nouns)
            num_adjectives = random.randint(3, 5)  # 使用更多形容词
            sentence = self.generate_example_sentence(noun, num_adjectives, use_partial=False)
            sentences.append(f"({len(sentences) + 1}) {sentence}")

        # 生成部分顺序的例子
        for i in range(min_partial_order):
            noun = random.choice(self.nouns)
            num_adjectives = random.randint(2, 4)
            sentence = self.generate_example_sentence(noun, num_adjectives, use_partial=True)
            sentences.append(f"({len(sentences) + 1}) {sentence}")

        # 生成剩余的随机例子
        remaining = num_sentences - len(sentences)
        for i in range(remaining):
            noun = random.choice(self.nouns)
            num_adjectives = random.randint(1, 3)
            use_partial = random.choice([True, False])
            sentence = self.generate_example_sentence(noun, num_adjectives, use_partial)
            sentences.append(f"({len(sentences) + 1}) {sentence}")

        random.shuffle(sentences)
        return sentences

    def generate_test_sentence(self, correct: bool = True) -> str:
        """生成测试句子，增强随机性"""
        noun = random.choice(self.nouns)
        num_adjectives = random.randint(3, 7)

        if correct:
            # 正确句子保持标准顺序
            selected_types = self.standard_order[:num_adjectives]
        else:
            # 错误句子生成非标准顺序
            selected_types = random.sample(self.standard_order, num_adjectives)
            # 确保顺序与标准顺序不同
            while selected_types == self.standard_order[:num_adjectives]:
                random.shuffle(selected_types)

        # 为每个选中的形容词类型随机选择一个形容词
        adjectives = []
        for adj_type in selected_types:
            if self.adjectives[adj_type]:
                adj = random.choice(self.adjectives[adj_type])
                adjectives.append(adj)

        return " ".join(adjectives) + " " + noun

    def generate_options(self, num_options: int = 10, num_correct: int = None) -> Tuple[List[str], List[bool]]:
        if num_correct is None:
            num_correct = random.randint(3, 6)  # 修改正确选项的数量范围

        options = []
        is_correct = []

        # 生成正确选项
        correct_sentences = set()
        while len(correct_sentences) < num_correct:
            sentence = self.generate_test_sentence(correct=True)
            # 确保不会产生导致CEJ组合的选项
            if len(correct_sentences) >= 2:
                current_correct = ''.join(sorted([chr(65 + i) for i in range(len(options))
                                                  if is_correct[i]]))
                if "CEJ" in (current_correct + chr(65 + len(options))):
                    continue
            correct_sentences.add(sentence)

        options.extend(correct_sentences)
        is_correct.extend([True] * num_correct)

        # 生成错误选项
        incorrect_sentences = set()
        while len(incorrect_sentences) < (num_options - num_correct):
            sentence = self.generate_test_sentence(correct=False)
            incorrect_sentences.add(sentence)

        options.extend(incorrect_sentences)
        is_correct.extend([False] * (num_options - num_correct))

        # 打乱选项顺序
        combined = list(zip(options, is_correct))
        random.shuffle(combined)
        options, is_correct = zip(*combined)

        return list(options), list(is_correct)

    def format_options(self, options: List[str]) -> List[str]:
        """将选项格式化为(A), (B)等格式"""
        formatted_options = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, ...
            formatted_options.append(f"({letter}) {option}")
        return formatted_options

    def get_answer_string(self, is_correct: List[bool]) -> str:
        """将正确选项转换为答案字符串"""
        correct_letters = []
        for i, correct in enumerate(is_correct):
            if correct:
                letter = chr(65 + i)
                correct_letters.append(letter)

        return "K" if not correct_letters else "".join(correct_letters)

    def generate_task(self) -> Dict[str, Any]:
        while True:
            # 生成示例句子
            example_sentences = []
            while len(example_sentences) < random.randint(50, 180):
                sentence = self.generate_example_sentence(
                    random.choice(self.nouns),
                    random.randint(3, 5)
                )
                if sentence not in example_sentences:
                    example_sentences.append(sentence)

            # 生成测试选项
            options, is_correct = self.generate_options(10)
            formatted_options = self.format_options(options)

            # 确保选项和示例句子之间没有重复
            all_sentences = example_sentences + [opt.split(") ")[1] for opt in formatted_options]

            # 获取答案字符串
            answer = self.get_answer_string(is_correct)

            # 检查是否包含CEJ组合
            if "CEJ" in answer:
                continue  # 如果包含CEJ，重新生成

            if len(all_sentences) == len(set(all_sentences)):
                # 构建任务输入
                task_input = (
                    f"In a variant of English, we are given that the following sentences have correct adjective order:\n"
                    f"{' '.join(example_sentences)}\n\n"
                    f"In this variant of English, which of the following sentences (Options A-J) use the correct adjective order? "
                    f"If none of the sentences (Options A-J) use the correct adjective order, select option K. Select all that apply.\n"
                    f"{' '.join(formatted_options)}\n"
                    f"(K) None of the above\n\n"
                    f"Provide your final answer as a concatenation of all the correct choices. For example, if B and C have correct adjective order, "
                    f"then your final answer must be \"BC\"."
                )

                return {
                    "input": task_input,
                    "target": answer
                }

    def validate_sentence(self, sentence: str) -> bool:
        """验证生成的句子是否符合规则"""
        words = sentence.split()
        if len(words) < 2:  # 至少要有一个形容词和一个名词
            return False

        # 检查名词是否在允许的列表中
        if words[-1] not in self.nouns:
            return False

        # 检查形容词是否都是已知的
        adjectives = words[:-1]
        for adj in adjectives:
            found = False
            for adj_list in self.adjectives.values():
                if adj in adj_list:
                    found = True
                    break
            if not found:
                return False

        return True

    def generate_task_batch(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        """直接生成一批任务，不保存到文件"""
        tasks = []
        for _ in range(batch_size):
            task = self.generate_task()
            tasks.append(task)
        return tasks
if __name__ == "__main__":
    try:
        generator = HyperbatonGenerator()
        # 测试生成单个句子
        test_sentence = generator.generate_example_sentence("ball", 3, False)
        print(f"Test sentence: {test_sentence}")

        # 生成完整数据集
        generator.save_dataset("hyperbaton_dataset.json", 100)
        print("数据集已生成并保存到 hyperbaton_dataset.json")
    except Exception as e:
        print(f"Error: {str(e)}")

