"""
Music Harmony Utilities - 音乐和声工具函数
提供四部和声分析所需的辅助函数
"""
from typing import List, Dict, Any, Tuple

from music21 import note, chord, stream, interval, voiceLeading, pitch, key, roman


# 常量定义
VOICES = ["Soprano", "Alto", "Tenor", "Bass"]
VOICE_INDICES = {"Bass": 0, "Tenor": 1, "Alto": 2, "Soprano": 3}
INDEX_TO_VOICE = {0: "Bass", 1: "Tenor", 2: "Alto", 3: "Soprano"}


def create_score_from_data(chord_data: List[Dict[str, str]]):
    """
    将字典数据转换为 music21 Score 对象
    
    Args:
        chord_data: 和弦数据列表，每个元素为 {'Soprano': 'C5', 'Alto': 'G4', ...}
    
    Returns:
        music21.stream.Score: Score 对象
    """
    
    s = stream.Score()
    parts = {v: stream.Part() for v in VOICES}
    for v in VOICES:
        parts[v].id = v
    
    for c_info in chord_data:
        for v in VOICES:
            n_str = c_info.get(v)
            if n_str:
                try:
                    n = note.Note(n_str)
                    n.quarterLength = 1.0
                    parts[v].append(n)
                except:
                    pass
    
    # 按照 SATB 顺序插入
    for v in VOICES:
        s.insert(0, parts[v])
    return s


def create_score_from_midis(v1_midis: List[int], v2_midis: List[int]):
    """
    专为生成器设计的快速构建 Score 函数
    输入为 MIDI 整数列表，顺序对应 [Bass, Tenor, Alto, Soprano]
    
    Args:
        v1_midis: 第一个和弦的 MIDI 值列表
        v2_midis: 第二个和弦的 MIDI 值列表
    
    Returns:
        music21.stream.Score: Score 对象
    """
    
    s = stream.Score()
    voice_names_in_order = ["Bass", "Tenor", "Alto", "Soprano"]
    
    for i, name in enumerate(voice_names_in_order):
        p = stream.Part()
        p.id = name
        n1 = note.Note(pitch.Pitch(midi=v1_midis[i]))
        n2 = note.Note(pitch.Pitch(midi=v2_midis[i]))
        n1.quarterLength = 1.0
        n2.quarterLength = 1.0
        p.append([n1, n2])
        s.insert(0, p)
    return s


def fast_check_parallel_math(v1_midis: List[int], v2_midis: List[int]) -> Tuple[bool, str, Tuple]:
    """
    纯数学方法检测平行五八度，不依赖 music21 对象，避免 Segfault
    
    Args:
        v1_midis: 第一个和弦的 MIDI 值 [Bass, Tenor, Alto, Soprano]
        v2_midis: 第二个和弦的 MIDI 值 [Bass, Tenor, Alto, Soprano]
    
    Returns:
        Tuple[bool, str, Tuple]: (是否有错误, 错误类型, 声部对)
    """
    # 所有的声部组合对 (索引)
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    
    for i, j in pairs:
        # i 是低声部索引，j 是高声部索引
        n1_start, n1_end = v1_midis[i], v2_midis[i]
        n2_start, n2_end = v1_midis[j], v2_midis[j]
        
        # 计算移动向量
        m1 = n1_end - n1_start
        m2 = n2_end - n2_start
        
        # 排除：保持不动(Oblique) 或 反向进行(Contrary)
        if m1 == 0 or m2 == 0 or (m1 * m2) < 0:
            continue
            
        # 计算结束时的音程 (绝对值)
        interval_end = abs(n2_end - n1_end)
        
        # 7半音=P5, 19半音=P12(视为P5); 0,12,24=P1,P8
        if interval_end % 12 == 7:
            return True, "Parallel 5th", (INDEX_TO_VOICE[i], INDEX_TO_VOICE[j])
        if interval_end % 12 == 0:
            return True, "Parallel 8th", (INDEX_TO_VOICE[i], INDEX_TO_VOICE[j])
            
    return False, None, None


def analyze_parallel_motion(score):
    """
    修改后的分析函数：优先提取 MIDI 进行数学检测，防止 music21 内部错误
    
    Args:
        score: music21.stream.Score 对象
    
    Returns:
        Tuple[bool, bool, List]: (有平行五度, 有平行八度, 错误详情列表)
    """
    
    try:
        parts = {p.id: p for p in score.parts}
        v1_midis = [0]*4
        v2_midis = [0]*4
        valid_data = True
        
        # 提取 MIDI
        for i, v_name in enumerate(["Bass", "Tenor", "Alto", "Soprano"]):
            if v_name not in parts: 
                valid_data = False
                break
            notes = list(parts[v_name].getElementsByClass(note.Note))
            if len(notes) < 2: 
                valid_data = False
                break
            v1_midis[i] = notes[0].pitch.midi
            v2_midis[i] = notes[1].pitch.midi
            
        if valid_data:
            # 使用数学方法作为主要检测手段
            is_err, err_type, voices = fast_check_parallel_math(v1_midis, v2_midis)
            if is_err:
                return True, True, [{"type": err_type, "voices": f"{voices[0]} and {voices[1]}"}]

        # 兜底：如果数学方法没测出来，再尝试 music21 原生
        vlq = voiceLeading.VoiceLeadingQuartet(
            parts['Soprano'], parts['Alto'], parts['Tenor'], parts['Bass']
        )
        p5_errors = vlq.parallelFifth()
        p8_errors = vlq.parallelOctave()
        
        details = []
        if p5_errors: details.append({"type": "Parallel 5th", "voices": "two voices"})
        if p8_errors: details.append({"type": "Parallel 8th", "voices": "two voices"})
        
        return bool(p5_errors), bool(p8_errors), details

    except Exception:
        return False, False, []


def get_chord_at_index(score, index: int):
    """
    获取指定索引处的垂直和弦
    
    Args:
        score: music21.stream.Score 对象
        index: 和弦索引
    
    Returns:
        music21.chord.Chord: 和弦对象
    """
    
    notes = []
    for p in score.parts:
        element_list = list(p.getElementsByClass(note.Note))
        if index < len(element_list):
            notes.append(element_list[index])
    return chord.Chord(notes)


def get_voice_leaps(score) -> Dict[str, List[int]]:
    """
    计算每个声部的跳进幅度（半音数）
    
    Args:
        score: music21.stream.Score 对象
    
    Returns:
        Dict[str, List[int]]: 每个声部的跳进列表
    """
    
    leaps = {v: [] for v in VOICES}
    for v in VOICES:
        part = score.parts[v]
        notes = list(part.getElementsByClass(note.Note))
        for i in range(len(notes) - 1):
            n1, n2 = notes[i], notes[i+1]
            leaps[v].append(abs(interval.Interval(n1, n2).semitones))
    return leaps


def check_voice_crossing(score) -> bool:
    """
    检查是否存在声部交叉
    
    Args:
        score: music21.stream.Score 对象
    
    Returns:
        bool: 是否存在声部交叉
    """
    
    num_chords = len(list(score.parts['Soprano'].getElementsByClass(note.Note)))
    for i in range(num_chords):
        midis = {}
        for v in VOICES:
            el = list(score.parts[v].getElementsByClass(note.Note))
            if i < len(el):
                midis[v] = el[i].pitch.midi
        if not (midis['Soprano'] >= midis['Alto'] >= midis['Tenor'] >= midis['Bass']):
            return True
    return False
