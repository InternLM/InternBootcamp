import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import numpy as np
import random
import math
import re
import os
from typing import Optional
from typing import Dict
from typing import List
from typing import Tuple
from typing import Any
from internbootcamp.bootcamps.bootcamps_v1.natural_science.circuit.lib.libcircuit import CoreCircuit




class CircuitRewardCalculator(BaseRewardCalculator):
    """Circuit奖励计算器"""
    
    @staticmethod
    def extract_output(output_str: str) -> Tuple[Optional[List[Optional[float]]], Optional[List[Optional[float]]], List[Dict[str, str]]]:
        """
        从模型的输出字符串中提取所有边的电流值、所有节点的电势值以及方程。
        优先从 markdown 代码块（```...```）中提取 Equations 区块。
        电流和电势也优先从最后一个 markdown 代码块中的相应区块提取。
        """
        # # print(f"\\n[DEBUG extract_output] --- Starting Extraction ---")
        temp_output_preview = output_str[:100] if output_str else 'None'
        # # print(f"[DEBUG extract_output] Input output_str (first 100 chars): '{temp_output_preview}'...")

        if output_str is None:
            # print("[DEBUG extract_output] output_str is None, returning None, None, []")
            return None, None, []
        
        output_str = output_str.strip()
        # # print(f"[DEBUG extract_output] Stripped output_str (first 100 chars): '{output_str[:100]}'...") # Redundant with above
        
        branch_currents: List[Optional[float]] = []
        node_potentials: List[Optional[float]] = []
        extracted_equations: List[Dict[str, str]] = []

        # --- Step 1: Attempt to find the last markdown code block ---
        last_code_block_content = None

        # ADDED: Primitive checks for "```"
        literal_backtick_count = output_str.count("```")
        # # print(f"[DEBUG extract_output] output_str.count('```'): {literal_backtick_count}")
        literal_backtick_matches = list(re.finditer(r"```", output_str))
        # # print(f"[DEBUG extract_output] Positions of literal '```' found by re.finditer(r'```', output_str): {[m.start() for m in literal_backtick_matches]}")

        # MODIFIED REGEX for code block matching
        code_block_matches = list(re.finditer(r'```((?:.|\n)*?)```', output_str)) 
        # # print(f"[DEBUG extract_output] Number of code blocks found (using new regex): {len(code_block_matches)}") 

        if code_block_matches:
            # ADDED DEBUG to see all captured blocks if there are few
            if len(code_block_matches) < 5: # # print all if not too many
                for i, match in enumerate(code_block_matches):
                    # # print(f"[DEBUG extract_output] Code block {i} content (first 200 chars):\n'''{match.group(1).strip()[:200]}...'''")
                    pass
            
            last_code_block_content = code_block_matches[-1].group(1).strip()
            # # print(f"[DEBUG extract_output] LAST code block content (first 500 chars):\n'''{last_code_block_content[:500]}...'''") # MODIFIED DEBUG
        else: # ADDED DEBUG
            # print("[DEBUG extract_output] No markdown code blocks found by re.finditer.")
            pass

        # --- Step 2: Extract Equations ---
        # Prefer equations from the last code block if available, otherwise search globally.
        text_to_search_equations = last_code_block_content if last_code_block_content else output_str
        
        # If searching in last_code_block_content, ensure we don't re-match the full output_str if no section found in block
        # This means the "else" for global search should only trigger if last_code_block_content is None.
        
        # MODIFIED REGEX for capturing group
        equations_section_match_target = re.search(r'Equations?:?\s*((?:.|\n)*?)(?=Currents?:?|Potentials?:?|$)', text_to_search_equations, re.IGNORECASE)
        if not equations_section_match_target and last_code_block_content is not None: # Searched in block, not found, try global
             # MODIFIED REGEX for capturing group
             equations_section_match_target = re.search(r'Equations?:?\s*((?:.|\n)*?)(?=Currents?:?|Potentials?:?|$)', output_str, re.IGNORECASE)


        if equations_section_match_target:
            equations_text = equations_section_match_target.group(1).strip()
            # # print(f"[DEBUG extract_output] Equations section found. Text:\n'''{equations_text}'''")
            # MODIFIED: Use splitlines() for robust line splitting
            raw_eq_lines = equations_text.splitlines() 
            # # print(f"[DEBUG extract_output] Number of raw equation lines found: {len(raw_eq_lines)}") # ADDED DEBUG
            for i, line in enumerate(raw_eq_lines):
                line = line.strip()
                # # print(f"[DEBUG extract_output] Processing equation line {i+1}/{len(raw_eq_lines)}: '{line}'") # MODIFIED DEBUG
                if not line or line == "...": 
                    # # print(f"[DEBUG extract_output] Skipping empty or '...' line.") # ADDED DEBUG
                    continue
                
                # KCL Match Attempt
                kcl_regex = r'KCL\s+at\s+Node\s+\w+:\s*(.*)'
                kcl_match = re.match(kcl_regex, line, re.IGNORECASE)
                # # print(f"[DEBUG extract_output] KCL match for '{line}' using regex '{kcl_regex}': {bool(kcl_match)}") # ADDED DEBUG
                if kcl_match:
                    eq_s = kcl_match.group(1).strip()
                    eq_s_cleaned = eq_s.split('//')[0].strip()
                    if eq_s_cleaned and not eq_s_cleaned.startswith("<equation_node_"):
                        extracted_equations.append({"type": "kcl", "equation_str": eq_s_cleaned})
                        # # print(f"[DEBUG extract_output] Appended KCL equation: {eq_s_cleaned}")
                    else: 
                        # # print(f"[DEBUG extract_output] KCL equation '{eq_s_cleaned}' not appended (empty or placeholder).") # ADDED DEBUG
                        continue
                
                # KVL Match Attempt
                kvl_regex = r'KVL\s+for\s+(.+?):\s*(.*)'
                kvl_match = re.match(kvl_regex, line, re.IGNORECASE)
                # # print(f"[DEBUG extract_output] KVL match for '{line}' using regex '{kvl_regex}': {bool(kvl_match)}") # ADDED DEBUG
                if kvl_match:
                    eq_s = kvl_match.group(2).strip()
                    eq_s_cleaned = eq_s.split('//')[0].strip()
                    if eq_s_cleaned and not eq_s_cleaned.startswith("<equation_loop_"):
                        extracted_equations.append({"type": "kvl", "equation_str": eq_s_cleaned})
                        # 保存 KVL 方程到文件
                        Circuitbootcamp._save_kvl_equation_to_file(eq_s_cleaned)
                        # # print(f"[DEBUG extract_output] Appended KVL equation: {eq_s_cleaned}")
                    else: 
                        # # print(f"[DEBUG extract_output] KVL equation '{eq_s_cleaned}' not appended (empty or placeholder).") # ADDED DEBUG
                        continue
                
                # # print(f"[DEBUG extract_output] Line did not match KCL or KVL pattern.") # ADDED DEBUG
        else:
            # print("[DEBUG extract_output] Equations section not found in preferred or global search.")
            pass

        # --- Step 3: Extract Currents and Potentials ---
        # Priority: Last code block -> Global text
        
        parsed_currents_from_block = False
        parsed_potentials_from_block = False

        if last_code_block_content:
            # # print("[DEBUG extract_output] Attempting to extract Currents and Potentials from LAST CODE BLOCK.")
            current_section_text_block = None
            potential_section_text_block = None
            
            # MODIFIED REGEX for capturing group
            current_match_block = re.search(r'Currents?:?\s*((?:.|\n)*?)(?=Potentials?:?|$)', last_code_block_content, re.IGNORECASE)
            if current_match_block:
                current_section_text_block = current_match_block.group(1).strip()
                # # print(f"[DEBUG extract_output] [BLOCK] Currents section found. Text:\n'''{current_section_text_block}'''")
                
                temp_currents_map: Dict[int, float] = {}
                # MODIFIED: Process line by line
                current_lines = current_section_text_block.splitlines()
                # # print(f"[DEBUG extract_output] [BLOCK] Number of current lines: {len(current_lines)}")
                for line_idx, current_line in enumerate(current_lines):
                    current_line = current_line.strip()
                    # # print(f"[DEBUG extract_output] [BLOCK] Processing current line {line_idx+1}: '{current_line}'")
                    # Try primary pattern: I_X = VAL A
                    match_primary = re.match(r'I_(\d+)\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*A', current_line, re.IGNORECASE)
                    if match_primary:
                        edge_idx_str, current_str = match_primary.groups()
                        # # print(f"[DEBUG extract_output] [BLOCK] Primary match: idx='{edge_idx_str}', val='{current_str}'")
                        try:
                            edge_idx = int(edge_idx_str) - 1  
                            if edge_idx >= 0: 
                                temp_currents_map[edge_idx] = float(current_str)
                                # # print(f"[DEBUG extract_output] [BLOCK] Parsed current I_{edge_idx+1} = {current_str}")
                                parsed_currents_from_block = True # Mark success if at least one parsed
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing current: idx='{edge_idx_str}', val='{current_str}'")
                            pass
                        continue # Process next line after try/except for current match_primary
            
                    # Try alternative pattern: Edge X : VAL A or Current X : VAL A
                    match_alt = re.match(r'(?:Edge|Current)\s+(\d+)\s*:?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*A', current_line, re.IGNORECASE)
                    if match_alt:
                        edge_idx_str, current_str = match_alt.groups()
                        # # print(f"[DEBUG extract_output] [BLOCK] Alt match: idx='{edge_idx_str}', val='{current_str}'")
                        try:
                            edge_idx = int(edge_idx_str) - 1  
                            if edge_idx >= 0: 
                                temp_currents_map[edge_idx] = float(current_str)
                                # # print(f"[DEBUG extract_output] [BLOCK] Parsed current (alt) I_{edge_idx+1} = {current_str}")
                                parsed_currents_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing current (alt): idx='{edge_idx_str}', val='{current_str}'")
                            pass
                        continue # Process next line after try/except for current match_alt
                    if current_line: # If line is not empty and didn't match
                         # print(f"[DEBUG extract_output] [BLOCK] No current pattern matched for line: '{current_line}'")
                         pass
                
                # Removed old re.findall logic for block currents
                # # print(f"[DEBUG extract_output] [BLOCK] Currents: Primary indexed matches={len(current_matches_primary_block)}, Alt indexed matches={len(current_matches_alt_block)}")

                # for edge_idx_str, current_str in all_current_matches_block:
                # ... (old loop removed)
                if temp_currents_map:
                    max_idx = max(temp_currents_map.keys())
                    branch_currents = [temp_currents_map.get(i) for i in range(max_idx + 1)]
                    # parsed_currents_from_block = True # This is now set inside the loop on first success
                # else:
                #    # print("[DEBUG extract_output] [BLOCK] No indexed currents found in Currents section of the code block.")
            else:
                # print("[DEBUG extract_output] [BLOCK] Currents section not found in the code block.")
                pass

            # MODIFIED REGEX for capturing group
            potential_match_block = re.search(r'Potentials?:?\s*((?:.|\n)*?)(?=$)', last_code_block_content, re.IGNORECASE)
            if potential_match_block:
                potential_section_text_block = potential_match_block.group(1).strip()
                # # print(f"[DEBUG extract_output] [BLOCK] Potentials section found. Text:\n'''{potential_section_text_block}'''")

                temp_potentials_map: Dict[int, float] = {}
                # MODIFIED: Process line by line
                potential_lines = potential_section_text_block.splitlines()
                # # print(f"[DEBUG extract_output] [BLOCK] Number of potential lines: {len(potential_lines)}")
                for line_idx, p_line in enumerate(potential_lines):
                    p_line = p_line.strip()
                    # # print(f"[DEBUG extract_output] [BLOCK] Processing potential line {line_idx+1}: '{p_line}'")
                    # Try primary pattern: V_X = VAL V
                    match_primary_pot = re.match(r'V_(\d+)\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*V', p_line, re.IGNORECASE)
                    if match_primary_pot:
                        node_idx_str, potential_str = match_primary_pot.groups()
                        # # print(f"[DEBUG extract_output] [BLOCK] Primary potential match: idx='{node_idx_str}', val='{potential_str}'")
                        try:
                            node_idx = int(node_idx_str)
                            if node_idx >= 0: 
                                temp_potentials_map[node_idx] = float(potential_str)
                                # # print(f"[DEBUG extract_output] [BLOCK] Parsed potential V_{node_idx} = {potential_str}")
                                parsed_potentials_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing potential: idx='{node_idx_str}', val='{potential_str}'")
                            continue

                    # Try alternative pattern: Node X : VAL V or Potential X : VAL V
                    match_alt_pot = re.match(r'(?:Node|Potential)\s+(\d+)\s*:?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*V', p_line, re.IGNORECASE)
                    if match_alt_pot:
                        node_idx_str, potential_str = match_alt_pot.groups()
                        # # print(f"[DEBUG extract_output] [BLOCK] Alt potential match: idx='{node_idx_str}', val='{potential_str}'")
                        try:
                            node_idx = int(node_idx_str)
                            if node_idx >= 0: 
                                temp_potentials_map[node_idx] = float(potential_str)
                                # # print(f"[DEBUG extract_output] [BLOCK] Parsed potential (alt) V_{node_idx} = {potential_str}")
                                parsed_potentials_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing potential (alt): idx='{node_idx_str}', val='{potential_str}'")
                            pass
                        continue
                    if p_line: # If line is not empty and didn't match
                        # # print(f"[DEBUG extract_output] [BLOCK] No potential pattern matched for line: '{p_line}'")
                        pass
                
                # Removed old re.findall logic for block potentials
                # # print(f"[DEBUG extract_output] [BLOCK] Potentials: Primary indexed matches={len(potential_matches_primary_block)}, Alt indexed matches={len(potential_matches_alt_block)}")

                # for node_idx_str, potential_str in all_potential_matches_block:
                # ... (old loop removed)

                if temp_potentials_map:
                    max_idx = max(temp_potentials_map.keys())
                    node_potentials = [temp_potentials_map.get(i) for i in range(max_idx + 1)]
                    # NO FALLBACK TO ALL FLOATS FOR GLOBAL SEARCH EITHER
                    # Ensure V0 is 0.0 if present (similar logic to block parsing)
                    if node_potentials and len(node_potentials) > 0:
                        if 0 in temp_potentials_map and temp_potentials_map[0] == 0.0:
                            node_potentials[0] = 0.0
                        elif 0 not in temp_potentials_map and node_potentials[0] is not None: # If V0 is not 0 and it's the first value
                            node_potentials[0] = 0.0
                        # else if V0 is missing, it's fine, it will be None in the list unless filled by V0=0 from prompt.
                else:
                    # print("[DEBUG extract_output] [GLOBAL] No indexed potentials, trying to extract any floats for potentials.") # Old fallback
                    values_only = re.findall(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(?:V|Volts?)?', potential_section_text_global)
                    if values_only: node_potentials = [float(val) for val in values_only]
            else:
                # print("[DEBUG extract_output] [BLOCK] Potentials section not found in the code block.")
                pass

        # --- Step 4: Global search if not found or incomplete from code block ---
        if not parsed_currents_from_block:
            # # print("[DEBUG extract_output] Currents not found in code block or parsing failed, trying GLOBAL search.")
            current_section_text_global = None
            # MODIFIED REGEX for capturing group
            current_match_global = re.search(r'Currents?:?\s*((?:.|\n)*?)(?=Potentials?:?|$)', output_str, re.IGNORECASE)
            if current_match_global:
                current_section_text_global = current_match_global.group(1).strip()
                # # print(f"[DEBUG extract_output] [GLOBAL] Currents section found. Text (first 100 chars):\n'''{current_section_text_global[:100]}...'''")
                
                temp_currents_map: Dict[int, float] = {}
                current_matches_primary_global = re.findall(r'I_(\\d+)\\s*=\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*A', current_section_text_global, re.IGNORECASE)
                current_matches_alt_global = re.findall(r'(?:Edge|Current)\\s+(\\d+)\\s*:?\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*A', current_section_text_global, re.IGNORECASE)
                all_current_matches_global = current_matches_primary_global + current_matches_alt_global
                # # print(f"[DEBUG extract_output] [GLOBAL] Currents: Primary indexed matches={len(current_matches_primary_global)}, Alt indexed matches={len(current_matches_alt_global)}")

                for edge_idx_str, current_str in all_current_matches_global:
                    try:
                        edge_idx = int(edge_idx_str) - 1  
                        if edge_idx >= 0: temp_currents_map[edge_idx] = float(current_str)
                    except ValueError: continue
                if temp_currents_map:
                    max_idx = max(temp_currents_map.keys())
                    branch_currents = [temp_currents_map.get(i) for i in range(max_idx + 1)]
                # NO FALLBACK TO ALL FLOATS FOR GLOBAL SEARCH EITHER - keep it strict
                # else:
                #    # print("[DEBUG extract_output] [GLOBAL] No indexed currents, trying to extract any floats for currents.") # Old fallback
                #    values_only = re.findall(r'([-+]\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*(?:A|Amperes?)?', current_section_text_global)
                #    if values_only: branch_currents = [float(val) for val in values_only]
            else:
                # print("[DEBUG extract_output] [GLOBAL] Currents section not found.")
                pass
        
        if not parsed_potentials_from_block:
            # # print("[DEBUG extract_output] Potentials not found in code block or parsing failed, trying GLOBAL search.")
            potential_section_text_global = None
            # MODIFIED REGEX for capturing group
            potential_match_global = re.search(r'Potentials?:?\s*((?:.|\n)*?)(?=$)', output_str, re.IGNORECASE)
            if potential_match_global:
                potential_section_text_global = potential_match_global.group(1).strip()
                # print(f"[DEBUG extract_output] [GLOBAL] Potentials section found. Text (first 100 chars):\n'''{potential_section_text_global[:100]}...'''")

                temp_potentials_map: Dict[int, float] = {}
                potential_matches_primary_global = re.findall(r'V_(\\d+)\\s*=\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*V', potential_section_text_global, re.IGNORECASE)
                potential_matches_alt_global = re.findall(r'(?:Node|Potential)\\s+(\\d+)\\s*:?\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*V', potential_section_text_global, re.IGNORECASE)
                all_potential_matches_global = potential_matches_primary_global + potential_matches_alt_global
                # print(f"[DEBUG extract_output] [GLOBAL] Potentials: Primary indexed matches={len(potential_matches_primary_global)}, Alt indexed matches={len(potential_matches_alt_global)}")
                
                for node_idx_str, potential_str in all_potential_matches_global:
                    try:
                        node_idx = int(node_idx_str)
                        if node_idx >= 0: temp_potentials_map[node_idx] = float(potential_str)
                    except ValueError: continue
                if temp_potentials_map:
                    max_idx = max(temp_potentials_map.keys())
                    node_potentials = [temp_potentials_map.get(i) for i in range(max_idx + 1)]
                    # NO FALLBACK TO ALL FLOATS FOR GLOBAL SEARCH EITHER
                    # Ensure V0 is 0.0 if present (similar logic to block parsing)
                    if node_potentials and len(node_potentials) > 0:
                        if 0 in temp_potentials_map and temp_potentials_map[0] == 0.0:
                            node_potentials[0] = 0.0
                        elif 0 not in temp_potentials_map and node_potentials[0] is not None: # If V0 is not 0 and it's the first value
                            node_potentials[0] = 0.0
                        # else if V0 is missing, it's fine, it will be None in the list unless filled by V0=0 from prompt.
                else:
                    # print("[DEBUG extract_output] [GLOBAL] No indexed potentials, trying to extract any floats for potentials.") # Old fallback
                    values_only = re.findall(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(?:V|Volts?)?', potential_section_text_global)
                    if values_only: node_potentials = [float(val) for val in values_only]
            else:
                # print("[DEBUG extract_output] [GLOBAL] Potentials section not found.")
                pass
        
        # Fallback if sections are not clearly marked and no values extracted yet (original fallback, more constrained now)
        if not branch_currents and not node_potentials and not extracted_equations: 
            # print("[DEBUG extract_output] Entering fallback for currents/potentials as NO sections found AND no equations extracted.")
            pass
            # This fallback should be very conservative, only matching strict I_X = VAL A or V_X = VAL V patterns globally
            current_pattern_fallback = r'I_(\\d+)\\s*=\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*A'
            potential_pattern_fallback = r'V_(\\d+)\\s*=\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*V'
            
            temp_currents_map_fb: Dict[int, float] = {}
            matches_curr_fb = list(re.finditer(current_pattern_fallback, output_str, re.IGNORECASE))
            if matches_curr_fb: 
                # print(f"[DEBUG extract_output] Fallback current indexed matches found: {len(matches_curr_fb)}")
                pass
            for match in matches_curr_fb:
                try:
                    idx = int(match.group(1)) -1 
                    val = float(match.group(2))
                    if idx >=0: temp_currents_map_fb[idx] = val
                except ValueError: continue
            if temp_currents_map_fb:
                max_idx = max(temp_currents_map_fb.keys())
                branch_currents = [temp_currents_map_fb.get(i) for i in range(max_idx + 1)]

            temp_potentials_map_fb: Dict[int, float] = {}
            matches_pot_fb = list(re.finditer(potential_pattern_fallback, output_str, re.IGNORECASE))
            if matches_pot_fb: 
                # print(f"[DEBUG extract_output] Fallback potential indexed matches found: {len(matches_pot_fb)}")
                pass
            for match in matches_pot_fb:
                try:
                    idx = int(match.group(1)) 
                    val = float(match.group(2))
                    if idx >= 0: temp_potentials_map_fb[idx] = val
                except ValueError: continue
            if temp_potentials_map_fb:
                max_idx = max(temp_potentials_map_fb.keys())
                node_potentials = [temp_potentials_map_fb.get(i) for i in range(max_idx + 1)]
            
            if branch_currents or node_potentials:
                 # print("[DEBUG extract_output] Returning from fallback with some strictly indexed currents/potentials.")
                 pass
            else:
                # print("[DEBUG extract_output] Fallback did not find any strictly indexed currents/potentials.")
                pass


        # Final V0=0.0 assurance if potentials were found by any means.
        if node_potentials and len(node_potentials) > 0:
            # Check if V0 (index 0) exists and is 0. If it exists and not 0, force to 0.
            # If it doesn't exist (list is shorter or starts with None at index 0),
            # and other potentials exist, we might need to be careful.
            # The prompt asks for V0=0V.
            # If node_potentials[0] is None or not 0.0, but the list is not empty.
            # For now, if node_potentials list exists and has at least one element, ensure node_potentials[0] = 0.0
            # This assumes that if any potentials are given, V_0 is either explicitly given as 0 or implied.
            # A more robust way is to check if 0 was in temp_potentials_map and was 0.
            # Let's refine: if 0 key exists in any temp_potentials_map and is not 0, set it to 0.
            # If 0 key doesn't exist but list is populated, this is ambiguous.
            # For now: if potentials are extracted, and node_potentials[0] is present, it MUST be 0.
            # If it's not present as first element, it means V_0 was not given or list is malformed.
            # The safest is to rely on an explicit V_0 = 0V being parsed, or ensuring the list starts with 0.
            # if it starts at all.
            # The current logic for setting V0=0 during block/global parsing handles if it's found.
            # This final check ensures if a list was somehow formed without V0=0 as the first element, we try to fix it.
            if node_potentials[0] is None: # If V0 is explicitly None in a list e.g. [None, 10.0, 5.0]
                node_potentials[0] = 0.0
            elif node_potentials[0] != 0.0: # If V0 is some other number
                node_potentials[0] = 0.0
        # Removed the problematic elif block that referenced an undefined variable 'expected_potentials_exist'


        final_branch_currents = branch_currents if branch_currents else None
        final_node_potentials = node_potentials if node_potentials else None
        
        # # print(f"[DEBUG extract_output] Final extracted currents: {final_branch_currents}")
        # # print(f"[DEBUG extract_output] Final extracted potentials: {final_node_potentials}")
        # # print(f"[DEBUG extract_output] Final extracted equations: {extracted_equations}")
        # # print(f"[DEBUG extract_output] --- Ending Extraction ---")
        return final_branch_currents, final_node_potentials, extracted_equations
    
    @classmethod
    def _verify_correction(cls, solution, identity: dict) -> bool:
        """
        Verifies if the extracted solution (current) matches the pre-calculated expected current.
        (This method seems specific to a single value, not directly used by verify_score for lists)
        """
        expected_current = identity.get('expected_current') # Assuming 'expected_current' is a single float

        if solution is None and expected_current is None:
            return True 
        if solution is None or expected_current is None:
            return False

        return np.isclose(solution, expected_current, atol=1e-2, rtol=1e-3)
    
    # 其他额外方法

