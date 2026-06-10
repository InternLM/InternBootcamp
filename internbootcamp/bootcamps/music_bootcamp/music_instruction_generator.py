from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.music_bootcamp.music_utils import fast_check_parallel_math
from typing import Dict, Any
from music21 import note, chord, stream, interval, voiceLeading, pitch, key, roman
import random


class MusicInstructionGenerator(BaseInstructionGenerator):
    """
    四部和声纠错指令生成器 (配置驱动版)
    """
    
    def __init__(self, 
                 ranges: Dict[str, list] = {
                     'Soprano': [60, 81], 
                     'Alto': [55, 74], 
                     'Tenor': [48, 67], 
                     'Bass': [40, 60]
                 },
                 roots: list = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'F', 'B-', 'E-', 'A-'],
                 progression_types: list = [
                     ['V', 'I'], ['IV', 'I'], ['V', 'vi'], ['i', 'V']
                 ],
                 progression_weights: list = [0.5, 0.2, 0.1, 0.2],
                 max_v1_candidates: int = 30,
                 max_v2_candidates: int = 100,
                 **kwargs):
        """
        初始化生成器
        
        Args:
            ranges: 声部音域设置，格式 {'Soprano': [min, max], ...}
            roots: 调性根音列表
            progression_types: 和声进行类型列表
            progression_weights: 和声进行权重列表
            max_v1_candidates: 第一个和弦的候选数量上限
            max_v2_candidates: 第二个和弦的候选数量上限
            **kwargs: 其他参数
        """
        super().__init__()
        
        # 设置参数
        self.ranges = ranges
        self.roots = roots
        self.progression_types = progression_types
        self.progression_weights = progression_weights
        self.max_v1_candidates = max_v1_candidates
        self.max_v2_candidates = max_v2_candidates


    def _get_chord_tones(self, key_obj, degree):
        """获取和弦的音级集合和根音"""
        rn = roman.RomanNumeral(degree, key_obj)
        return set(p.pitchClass for p in rn.pitches), rn.root().pitchClass

    def _get_all_valid_voicings(self, chord_pcs, root_pc):
        """
        获取所有符合音域和声部进行规则的排列法
        
        Args:
            chord_pcs: 和弦的音级集合
            root_pc: 根音的音级
        
        Returns:
            List: 有效的配音列表 [Bass, Tenor, Alto, Soprano]
        """
        valid_voicings = []
        
        # Bass 必须是根音
        bass_candidates = [
            m for m in range(self.ranges['Bass'][0], self.ranges['Bass'][1]+1) 
            if m % 12 == root_pc
        ]
        
        for b in bass_candidates:
            for t in range(self.ranges['Tenor'][0], self.ranges['Tenor'][1]+1):
                if t < b: 
                    continue 
                if t % 12 not in chord_pcs: 
                    continue
                if t - b > 19:  # Bass-Tenor 不超过十九度
                    continue 
                
                for a in range(self.ranges['Alto'][0], self.ranges['Alto'][1]+1):
                    if a < t: 
                        continue
                    if a % 12 not in chord_pcs: 
                        continue
                    if a - t > 12:  # Tenor-Alto 不超过八度
                        continue 
                    
                    for s in range(self.ranges['Soprano'][0], self.ranges['Soprano'][1]+1):
                        if s < a: 
                            continue 
                        if s % 12 not in chord_pcs: 
                            continue
                        if s - a > 12:  # Alto-Soprano 不超过八度
                            continue 
                        
                        # 检查是否包含所有和弦音
                        current_pcs = {b%12, t%12, a%12, s%12}
                        if chord_pcs.issubset(current_pcs):
                            valid_voicings.append([b, t, a, s])
        
        return valid_voicings

    def _is_smooth_connection(self, v1_midis, v2_midis):
        """
        检查两个和弦之间是否为平滑连接
        
        Args:
            v1_midis: 第一个和弦的 MIDI 值
            v2_midis: 第二个和弦的 MIDI 值
        
        Returns:
            bool: 是否平滑
        """
        # Bass <= 12 semitones, S/A/T <= 7 semitones
        if abs(v1_midis[0] - v2_midis[0]) > 12: 
            return False
        for i in [1, 2, 3]:
            if abs(v1_midis[i] - v2_midis[i]) > 7: 
                return False
        
        # Crossing check
        if not (v2_midis[0] <= v2_midis[1] <= v2_midis[2] <= v2_midis[3]):
            return False
        
        return True

    def case_generator(self) -> Dict[str, Any]:
        """
        生成四部和声纠错任务案例
        
        Returns:
            Dict[str, Any]: 任务信息字典
        """

        while True:
            # 随机选择调性和和声进行
            root = random.choice(self.roots)
            mode = random.choice(['major', 'minor'])
            k = key.Key(root, mode)
            
            prog_type = random.choices(
                self.progression_types, 
                weights=self.progression_weights, 
                k=1
            )[0]
            deg1, deg2 = prog_type
            
            try:
                pcs1, root1 = self._get_chord_tones(k, deg1)
                pcs2, root2 = self._get_chord_tones(k, deg2)
            except: 
                continue
            
            # 获取所有有效的配音
            voicings1 = self._get_all_valid_voicings(pcs1, root1)
            voicings2 = self._get_all_valid_voicings(pcs2, root2)
            
            if not voicings1 or not voicings2: 
                continue
            
            random.shuffle(voicings1)
            random.shuffle(voicings2)
            
            # 限制搜索空间，防止卡死
            v1_candidates = voicings1[:self.max_v1_candidates]
            v2_candidates = voicings2[:self.max_v2_candidates]

            for v1 in v1_candidates:
                has_error_connection = False
                has_clean_connection = False
                error_details = None
                target_bad_v2 = None

                for v2 in v2_candidates:
                    # 直接传入 MIDI 列表进行数学计算，不创建 Score 对象
                    is_err, err_type, err_voices = fast_check_parallel_math(v1, v2)
                    is_smooth = self._is_smooth_connection(v1, v2)

                    if is_err:
                        if not has_error_connection and is_smooth:
                            has_error_connection = True
                            error_details = (err_type, f"{err_voices[0]} and {err_voices[1]}")
                            target_bad_v2 = v2
                    else:
                        if is_smooth:
                            has_clean_connection = True
                    
                    if has_error_connection and has_clean_connection:
                        break
                
                if has_error_connection and has_clean_connection:
                    error_type, voice_pair = error_details
                    
                    # 辅助函数：MIDI 转音名
                    def get_n(midi_val): 
                        from music21 import note, pitch
                        return note.Note(pitch.Pitch(midi=midi_val)).nameWithOctave

                    # v1/v2 格式: [Bass, Tenor, Alto, Soprano]
                    c1_dict = {
                        'Bass': get_n(v1[0]), 
                        'Tenor': get_n(v1[1]), 
                        'Alto': get_n(v1[2]), 
                        'Soprano': get_n(v1[3])
                    }
                    c2_dict = {
                        'Bass': get_n(target_bad_v2[0]), 
                        'Tenor': get_n(target_bad_v2[1]), 
                        'Alto': get_n(target_bad_v2[2]), 
                        'Soprano': get_n(target_bad_v2[3])
                    }
                    
                    return {
                        "initial_score": [c1_dict, c2_dict],
                        "error_type": error_type,
                        "error_description": f"Detected {error_type} between {voice_pair}",
                        "key_name": k.name,
                        "progression": f"{deg1} -> {deg2}"
                    }


    def prompt_func(self, identity: Dict[str, Any]) -> str:
        """
        生成四部和声Prompt
        """
        
        # 1. 准备乐谱字符串
        score_str = ""
        for i, ch in enumerate(identity["initial_score"]):
            score_str += f"Chord {i+1}: [S: {ch['Soprano']}, A: {ch['Alto']}, T: {ch['Tenor']}, B: {ch['Bass']}]\n"

        # 2. 提取常用参数 (确保 safe get)
        key_name = identity['key_name']
        progression = identity.get('progression', 'Unknown')

        # 3. 定义 10 个中文 Prompt 变种
        templates = [
        # --- 变种 1: 严厉教授 (学术规范) ---
        f"""
**致作曲学徒：**
我是皇家礼拜堂的乐长。我刚刚审阅了你呈交的四部和声草稿，遗憾地发现其中触犯了对位法中最不可饶恕的禁忌——平行五度或平行八度。

**你的草稿 (Key: {key_name} | Progression: {progression}):**
{score_str}

**修正指令：**
为了挽救这段音乐，你必须重写 **第二个和弦**。
1. **工具辅助**：我允许你使用 `detect_parallel_intervals` 来找出那个刺耳的错误。
2. **和声约束**：低音（Bass）必须保持不变，以维持和声根基；和弦性质不可改变。
3. **声部导向**：各声部应平稳进行，避免像受惊的野兽一样大跳。
4. **结构完整**：除非特殊情况，不可省略三音或五音。

请将修正后的完整乐谱以标准格式呈交：
\\boxed{{[{{'Soprano': 'C5', 'Alto': 'E4', 'Tenor': 'G3', 'Bass': 'C3'}}, {{'Soprano': 'D5', 'Alto': 'F4', 'Tenor': 'A3', 'Bass': 'D3'}}]}}
""",

        # --- 变种 2: 乐理助教 (亲切引导) ---
        f"""
>>> SYSTEM_ALERT: 检测到和声逻辑异常
>>> ERROR_TYPE: Parallel_Intervals (5th/8th)
>>> CONTEXT: Four-part harmony object

**当前数据状态:**
Key: {key_name}
Progression: {progression}
Data Stream:
{score_str}

**DEBUG 任务:**
调用 `detect_parallel_intervals` 定位异常索引。重构列表中的 **Index 1 (第二个元素)** 以修复 Bug。

**重构约束:**
1. [Immutable] Index 1 的 'Bass' 字段值必须保持原样（维持转位与功能）。
2. [Optimization] 最小化各声部（S/A/T）的移动距离（Voice Leading Distance）。
3. [Validation] 确保 Index 1 的和弦构成音完整。
4. [Immutable] Index 0 保持不变。

**输出期望 (Python List[Dict]):**
\\boxed{{[{{'Soprano': 'E5', 'Alto': 'C5', 'Tenor': 'G4', 'Bass': 'C4'}}, {{'Soprano': 'F5', 'Alto': 'C5', 'Tenor': 'A4', 'Bass': 'F4'}}]}}
""",

        # --- 变种 3: 分析挑战 (逻辑分析) ---
        f"""
**科目：高级和声学与对位法**
**题目 3：不良进行修正**

**题目描述：**
下方的和声片段（调性：{key_name}，和声进行：{progression}）中包含一处严禁的平行进行（五度或八度）。请分析并修正它。
乐谱内容：
{score_str}

**答题要求：**
1. 使用 `detect_parallel_intervals` 确认错误位置。
2. 修改 **第二个和弦** 的上方三个声部（Soprano, Alto, Tenor）。
3. **低音锁定**：第二个和弦的 Bass 音高不得更改。
4. **平稳原则**：声部连接必须符合平滑导向原则。
5. **完整性**：修正后的和弦必须包含根音、三音和五音。

**最终答案格式：**
请输出完整的 Python 列表格式。
示例：\\boxed{{[{{'Soprano': 'G4', 'Alto': 'E4', 'Tenor': 'C4', 'Bass': 'C3'}}, {{'Soprano': 'F4', 'Alto': 'D4', 'Tenor': 'B3', 'Bass': 'G2'}}]}}
""",

        # --- 变种 4: 古典乐长 (风格化/巴洛克) ---
        f"""
**Hey，这轨编曲有点问题。**
我是制作人。刚才回放的时候，我听到这两小节（{key_name}调，和声：{progression}）里有个很明显的平行五八度问题，听起来太空了，像初学者写的。

**目前的MIDI信息:**
{score_str}

**你需要做的：**
1. 跑一下 `detect_parallel_intervals` 插件，看看具体是哪两个声部打架了。
2. 调整 **第二个和弦** 的 Voicing（排列）。
   - **注意**：别动 Bass 线，那是贝斯手定好的 Groovy。
   - 其他声部（S/A/T）这就近解决，别跳来跳去的，要顺滑。
   - 和弦里的音要齐，别漏了三音。

搞定后把新的 Note Event 列表发给我：
\\boxed{{[{{'Soprano': 'C5', 'Alto': 'G4', 'Tenor': 'E4', 'Bass': 'C3'}}, {{'Soprano': 'A4', 'Alto': 'F4', 'Tenor': 'C4', 'Bass': 'F2'}}]}}
""",

        # --- 变种 5: 负向约束 (强调禁止项) ---
        f"""
你好！我看你在编写一段 {key_name} 调的和声 ({progression})，不过我注意到这里似乎有一个常见的声部导向错误（平行五度或八度）。

**当前片段：**
{score_str}

**我可以帮你修复它：**
为了保持你原本的音乐构思，我建议只修改 **第二个和弦** 的上方声部。
1. 我们可以先用 `detect_parallel_intervals` 确认一下问题出在哪。
2. 保持低音（Bass）不变，这样和弦功能就不变了。
3. 调整 Soprano、Alto 和 Tenor，让它们“就近”移动到下一个音。

请确认修复方案，并按以下格式输出结果：
\\boxed{{[{{'Soprano': 'F5', 'Alto': 'C5', 'Tenor': 'A4', 'Bass': 'F3'}}, {{'Soprano': 'E5', 'Alto': 'C5', 'Tenor': 'G4', 'Bass': 'C3'}}]}}
""",

        # --- 变种 6: 算法程序风 (步骤化) ---
        f"""
**输入**：
- Key: {key_name}
- Progression: {progression}
- Score:
{score_str}

**操作步骤**：
1. 调用 `detect_parallel_intervals`。
2. 修改和弦列表中的第 2 个元素。
   - 约束 A：保留 Bass 音高。
   - 约束 B：保留第一个和弦不变。
   - 约束 C：声部连接必须平稳。
   - 约束 D：和弦音完整。

**输出**：
严格的 Python List[Dict] 格式，包裹在 Box 中。
示例：
\\boxed{{[{{'Soprano': 'D5', 'Alto': 'A4', 'Tenor': 'F4', 'Bass': 'D3'}}, {{'Soprano': 'C5', 'Alto': 'G4', 'Tenor': 'E4', 'Bass': 'C3'}}]}}
""",

        # --- 变种 7: 期末考试 (高压场景) ---
        f"""
**Problem 1024: Fix Forbidden Parallels**

**Description:**
给定一个包含两个和弦的数组 `score`，代表 {key_name} 调 ({progression}) 的四部和声。当前输入存在平行五度或平行八度错误。
Input:
{score_str}

**Requirements:**
返回一个新的数组，其中第二个和弦已被修改以消除错误。
- `Fixed_Chord.Bass` 必须等于 `Input_Chord.Bass`。
- 必须遵循最近距离声部导向 (Voice Leading) 原则。
- 可以使用 helper function `detect_parallel_intervals()`。

**Output Format:**
Return the result as a strict Python List.
\\boxed{{[{{'Soprano': 'A4', 'Alto': 'E4', 'Tenor': 'C4', 'Bass': 'A2'}}, {{'Soprano': 'G4', 'Alto': 'D4', 'Tenor': 'B3', 'Bass': 'G2'}}]}}
""",

        # --- 变种 8: 极简主义 (纯指令) ---
        f"""
**校对单：乐理错误修正**
**状态**：待处理
**调号**：{key_name}
**和声标记**：{progression}

**问题描述**：
在以下小节中发现平行进行，不符合出版标准。
{score_str}

**处理意见**：
请立即重排 **第二个和弦**。
1. **强制保留**：低音部的音高（Bass Note）。
2. **修改建议**：调整高音声部位置，打破平行关系，尽量采用反向或斜向进行。
3. **工具验证**：修正前后请务必使用 `detect_parallel_intervals` 核查。

请在下方方框内填入修正后的完整和弦序列代码：
\\boxed{{[{{'Soprano': 'E5', 'Alto': 'C5', 'Tenor': 'G4', 'Bass': 'C4'}}, {{'Soprano': 'D5', 'Alto': 'B4', 'Tenor': 'G4', 'Bass': 'G3'}}]}}
""",

        # --- 变种 9: 声部纯粹主义 (关注旋律线) ---
        f"""
**案件编号：No. {progression}**
**地点（调性）**：{key_name} 街区
**现场记录**：
听着，新人。我们在乐谱里发现了一起严重的违规事件——平行五度或八度。这是对位法警局绝不容忍的勾当。

**相关证物 (当前乐谱):**
{score_str}

**你的任务：**
要把这个烂摊子收拾干净，你需要重写 **第二个和弦**。
1. **取证**：先用 `detect_parallel_intervals` 找出是谁在搞鬼。
2. **底线**：别碰低音（Bass）。那是地基，动了它楼就塌了。
3. **行动方针**：让高音部的那些家伙（S/A/T）老实点，动静越小越好（就近解决）。
4. **结案标准**：必须保证是个完整的三和弦，别缺胳膊少腿。

把修正后的报告放在档案盒里交给我：
\\boxed{{[{{'Soprano': 'G4', 'Alto': 'E4', 'Tenor': 'C4', 'Bass': 'C3'}}, {{'Soprano': 'F4', 'Alto': 'D4', 'Tenor': 'B3', 'Bass': 'G2'}}]}}
""",

        # --- 变种 10: 数据脚本场景 (代码语境) ---
        f"""
**::: 警告：检测到谐振异常 :::**
**系统状态**：不稳定
**主频调制**：{key_name}
**和声模式**：{progression}
**异常描述**：核心与护盾发生相位锁定（平行五度/八度干涉），结构完整性下降。

**遥测数据 (Telemetry Data):**
{score_str}

**紧急校准协议：**
请立即重新计算 **时间点 T2 (第二个和弦)** 的频率分布。
1. **启用诊断**：调用 `detect_parallel_intervals` 模组定位干涉源。
2. **基频锁定**：Bass 频段必须保持不变，以维持引擎推力。
3. **平滑过渡**：S/A/T 频段应执行最小化位移操作，避免能量激增。
4. **完整性检查**：确保三项式波形（根三五音）完整。

输入修正后的波形序列以重启系统：
\\boxed{{[{{'Soprano': 'C5', 'Alto': 'G4', 'Tenor': 'E4', 'Bass': 'C3'}}, {{'Soprano': 'A4', 'Alto': 'F4', 'Tenor': 'C4', 'Bass': 'F3'}}]}}
"""
    ]

    # 4. 随机选择一个模板返回
        return random.choice(templates)