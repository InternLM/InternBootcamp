from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cbeautifullyrics.Cbeautifullyrics_reward_calculator import CbeautifullyricsRewardCalculator

# 导入依赖库
import json
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def count_vowels_and_last_vowel(word):
    vowels = {'a', 'e', 'i', 'o', 'u'}
    count = 0
    last_v = None
    for c in word:
        if c in vowels:
            count += 1
            last_v = c
    return count, last_v

def extract_all_vowels(word):
    vowels = {'a', 'e', 'i', 'o', 'u'}
    return [c for c in word if c in vowels]


class CbeautifullyricsInteraction(BaseInteraction):
    """Cbeautifullyrics交互管理器"""
    
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
        score = CbeautifullyricsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cbeautifullyrics问题！"""
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
    def _generate_solvable_case(self):
        # Generate at least one valid lyric
        words = []
        # Generate one valid lyric with 4 unique words
        a = self._generate_word_with_vowel_count(2)
        c = self._generate_word_with_vowel_count(2)
        b = self._generate_word_with_vowel_count_and_last(1, 'a')
        d = self._generate_word_with_vowel_count_and_last(1, 'a')
        words.extend([a, b, c, d])
        # Ensure expected_m is 1 for this simple case
        expected_m = 1
        return words, expected_m

    def _generate_unsolvable_case(self):
        # Generate words that cannot form any lyric
        words = [
            self._generate_word_with_vowel_count_and_last(1, 'a'),
            self._generate_word_with_vowel_count_and_last(2, 'e'),
            self._generate_word_with_vowel_count_and_last(3, 'i'),
            self._generate_word_with_vowel_count_and_last(4, 'o')
        ]
        return words, 0

    def _generate_word_with_vowel_count(self, count):
        vowels = ['a', 'e', 'i', 'o', 'u']
        other = [chr(c) for c in range(ord('a'), ord('z')+1) if chr(c) not in vowels]
        parts = []
        for _ in range(count):
            parts.append(random.choice(vowels))
            if random.random() < 0.5 and len(parts) < count * 2:
                parts.append(random.choice(other))
        # Add trailing consonants
        for _ in range(random.randint(0, 3)):
            parts.append(random.choice(other))
        return ''.join(parts)

    def _generate_word_with_vowel_count_and_last(self, count, last_vowel):
        vowels = ['a', 'e', 'i', 'o', 'u']
        other = [chr(c) for c in range(ord('a'), ord('z')+1) if chr(c) not in vowels]
        parts = []
        # Generate count-1 vowels
        for _ in range(count-1):
            parts.append(random.choice(vowels))
            if random.random() < 0.5:
                parts.append(random.choice(other))
        # Add the last vowel
        parts.append(last_vowel)
        # Add trailing consonants
        for _ in range(random.randint(0, 3)):
            parts.append(random.choice(other))
        return ''.join(parts)
