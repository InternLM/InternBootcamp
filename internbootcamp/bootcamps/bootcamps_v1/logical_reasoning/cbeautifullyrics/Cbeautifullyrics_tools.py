import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CbeautifullyricsVerificationTool(BaseTool):
    """Cbeautifullyrics验证工具"""
    
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
            score = CbeautifullyricsRewardCalculator.verify_score(
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
            logger.error(f"CbeautifullyricsVerificationTool执行错误: {str(e)}")
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
