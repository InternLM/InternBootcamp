import ast
from typing import Optional, Dict, Any

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.music_bootcamp.music_utils import (
    create_score_from_data, analyze_parallel_motion, get_chord_at_index,
    get_voice_leaps, check_voice_crossing, VOICES
)
from music21 import note, chord, stream, interval, voiceLeading, pitch, key, roman


class MusicRewardCalculator(BaseRewardCalculator):
    """四部和声纠错奖励计算器"""
    
    @staticmethod
    def extract_output(output_str: str):
        """
        从模型输出中提取和弦数据
        
        Args:
            output_str: 模型的原始输出
            
        Returns:
            Optional[list]: 提取的和弦数据列表，格式为 [{'Soprano': 'C5', ...}, {...}]
        """
        if not output_str:
            return None
        
        start_marker = "\\boxed{"
        start_index = output_str.find(start_marker)
        if start_index == -1:
            return None

        content_start = start_index + len(start_marker)
        balance = 1
        
        for i in range(content_start, len(output_str)):
            if output_str[i] == '{': 
                balance += 1
            elif output_str[i] == '}': 
                balance -= 1
            
            if balance == 0:
                try:
                    parsed = ast.literal_eval(output_str[content_start:i].strip())
                    return parsed if isinstance(parsed, list) else None
                except: 
                    return None
        
        return None
    
    @classmethod
    def _verify_correction(cls, extract_solution, identity: dict, **kwargs) -> float:
        """
        验证提取的解决方案并计算正确性分数
        
        Args:
            extract_solution: 从extract_output()提取的和弦数据
            identity: 任务标准答案信息
            kwargs: 额外关键字参数
            
        Returns:
            float: 正确性分数（0-1之间）
        """
        if not extract_solution or not isinstance(extract_solution, list) or len(extract_solution) != 2:
            return 0.0

        try:
            
            score = create_score_from_data(extract_solution)
            initial_data = identity["initial_score"]
            
            # 检查生成的 Score 是否完整
            for v in VOICES:
                part = score.parts[v]
                notes = list(part.getElementsByClass(note.Note))
                if len(notes) != 2: 
                    return 0.0

            # 1. 检查第一个和弦是否被篡改 (MIDI 级完全一致)
            for v in VOICES:
                n_sol = list(score.parts[v].getElementsByClass(note.Note))[0]
                n_init = note.Note(initial_data[0][v])
                if n_sol.pitch.midi != n_init.pitch.midi:
                    return 0.0

            # 2. 平行五八度检查 (一票否决)
            has_p5, has_p8, details = analyze_parallel_motion(score)
            if has_p5 or has_p8:
                return 0.0

            # 3. 检查第二个和弦的功能保留
            c2_sol = get_chord_at_index(score, 1)
            
            # 获取目标和弦的音级集合
            target_pcs = set()
            target_bass_pc = None
            for v in VOICES:
                if initial_data[1].get(v):
                    n = note.Note(initial_data[1][v])
                    target_pcs.add(n.pitch.pitchClass)
                    if v == 'Bass':
                        target_bass_pc = n.pitch.pitchClass
            
            sol_pcs = set(p.pitchClass for p in c2_sol.pitches)
            
            # A. 音级集合必须是子集 (允许省略五音，但不允许加外音)
            if not sol_pcs.issubset(target_pcs):
                return 0.0
            
            # B. 必须包含根音和三音 (简单起见，要求至少3个不同音级)
            if len(sol_pcs) < 3 and len(target_pcs) >= 3:
                return 0.5
            
            # C. 检查低音 Pitch Class 是否改变 (防止通过转位逃避问题)
            sol_bass_note = list(score.parts['Bass'].getElementsByClass(note.Note))[1]
            if sol_bass_note.pitch.pitchClass != target_bass_pc:
                return 0.0

            # 4. 声部导向 penalty
            penalty = 0.0
            leaps = get_voice_leaps(score)
            for v, intervals in leaps.items():
                limit = 12 if v == 'Bass' else 7  # 允许低音跳八度
                for val in intervals:
                    if val > limit: 
                        penalty += 0.25
            
            # 声部交叉在对位法习题中通常是禁止的，加重惩罚
            if check_voice_crossing(score):
                penalty += 0.5
            
            final_score = max(0.0, 1.0 - penalty)
            
            return final_score

        except Exception as e:
            print(f"  [验证错误] {e}")
            import traceback
            print(f"  [验证错误] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
