import numpy as np
import random
import math
import re
import os
from typing import Optional, Dict, List, Tuple, Any
# Attempt to import Basebootcamp, assuming the path is accessible
try:
    from internbootcamp.bootcamp.base import Basebootcamp
except ImportError:
    # Fallback if the specific path is not found, e.g. for local testing
    # This might need adjustment based on the actual execution environment
    class Basebootcamp:
        def __init__(self, *args, **kwargs):
            pass
        def case_generator(self):
            raise NotImplementedError
        def prompt_func(self, identity):
            raise NotImplementedError
        @staticmethod
        def extract_output(output_str):
            raise NotImplementedError
        @classmethod
        def _verify_correction(cls, solution, identity):
            raise NotImplementedError

# Import the new core logic class
# Assuming the path is relative to the workspace root or correctly configured in PYTHONPATH
from internbootcamp.libs.circuit.libcircuit import CoreCircuit

class Circuitbootcamp(Basebootcamp):
    def __init__(self, min_nodes=3, max_nodes=6, seed=None):
        """
        Initializes the circuit bootcamp.
        Args:
            min_nodes (int): Minimum number of nodes for generated circuits.
            max_nodes (int): Maximum number of nodes for generated circuits.
            seed (int, optional): Seed for random number generation.
        """
        super().__init__()
        self.min_nodes = max(2, min_nodes) # Ensure at least 2 nodes
        self.max_nodes = max(self.min_nodes, max_nodes)
        self.seed = seed # Store the seed
        if self.seed is not None:
            random.seed(self.seed) # Seed for random operations within Circuitbootcamp itself
            # np.random.seed(self.seed) # Not strictly needed here as CoreCircuit handles its numpy seeding

    def case_generator(self) -> dict:
        """
        生成一个电路问题：n_nodes, edges, branch_currents 和 node_potentials。
        branch_currents：原始电路每条边上的电流列表
        node_potentials：每个节点的电势列表（节点0的电势为参考0V）
        """
        # n_nodes is already a Python int due to random.randint
        n_nodes = random.randint(self.min_nodes, self.max_nodes) 
        
        # 使用 CoreCircuit 生成图，传递种子
        # edges from CoreCircuit will have u,v as numpy integers
        original_edges = CoreCircuit.generate_random_graph_edges(n_nodes, seed=self.seed)
        # print(f"[DEBUG circuit] Generated original_edges: {original_edges}")
        
        # 转换 edges 中的 u, v 为 Python int 类型
        processed_edges = []
        if original_edges:
            for edge in original_edges:
                R, E, u, v = edge
                processed_edges.append((R, E, int(u), int(v)))
        
        # 使用 CoreCircuit 求解电路，获取每条支路的电流和每个节点的电势
        # 注意：solve_circuit_potentials_and_currents 需要原始的 edges (如果它内部依赖特定类型，尽管通常数值计算库可以处理)
        # 但为了安全和一致性，传递处理过的或者确保 solve_circuit_potentials_and_currents 也能处理 Python int 节点
        # 从 libcircuit.py 的实现看，它在MNA矩阵构建时使用 u,v 作为索引，Python int 也可以。
        branch_currents, node_potentials = CoreCircuit.solve_circuit_potentials_and_currents(n_nodes, processed_edges, seed=self.seed)

        # 确保 branch_currents 和 node_potentials 中的浮点数是标准 Python float (numpy floats 也能序列化，但为了彻底)
        safe_branch_currents = None
        if branch_currents is not None:
            safe_branch_currents = [float(bc) if bc is not None else None for bc in branch_currents]
            
        safe_node_potentials = None
        if node_potentials is not None:
            safe_node_potentials = [float(np) if np is not None else None for np in node_potentials]

        return {
            'n_nodes': int(n_nodes), # 确保是 Python int
            'edges': processed_edges, 
            'branch_currents': safe_branch_currents,
            'node_potentials': safe_node_potentials
        }

    def prompt_func(self, identity: dict) -> str:
        """
        根据电路问题生成提示语，要求计算每条边上的电流和每个节点的电势。
        """
        n_nodes = identity['n_nodes']
        edges_str_list = []
        for i, edge_data in enumerate(identity['edges']):
            R, E, u, v = edge_data
            edges_str_list.append(f"  Edge {i+1}: R={R:.2f} Ohm, E={E:.2f} V, in branch {u}-{v} (E is the Electromotive Force in branch {u}-{v}; positive if the source's positive terminal is at node {v} and negative terminal at node {u}.)")
        edges_presentation = "\n".join(edges_str_list) if edges_str_list else "  No existing edges."

        instruction = (
            f"Consider an electrical circuit with {n_nodes} nodes, labeled 0 to {n_nodes-1}.  "
            f"The circuit has the following edges:\\n{edges_presentation}\\n"
            f"For this circuit, your task is to formulate the set of equations based on Kirchhoff's Laws that can be used to solve for all branch currents.\\n"
            f"You are NOT required to solve these equations or provide the numerical values for currents.\\n"
        )
        
        instruction_following = (
            "Let's think step by step. Follow these instructions to formulate the equations:\n\n"
            "1. **Analyze the Circuit Structure:** Identify all nodes and branches in the circuit. Determine how many independent loops exist.\n"
            "2. **Formulate Equations using Kirchhoff's Laws with Branch Currents as Unknowns:**\n"
            "   - Assign a branch current variable to each edge. I_1 represents the current through Edge 1, I_2 represents the current through Edge 2, and so on. The assumed direction of each current aligns with the u -> v direction of the edge definition as provided: 'positive current is defined to flow from the first node towards the second node listed in the edge description'.\n"
            "   - Apply Kirchhoff's Current Law (KCL) at n-1 independent nodes (where n is the total number of nodes) to get a set of equations.\n"
            "   - Apply Kirchhoff's Voltage Law (KVL) around each independent loop to get another set of equations. Ensure you correctly account for the voltage drops across resistors (V=IR) and the EMFs of voltage sources (E), paying attention to their polarities relative to the loop traversal direction.\n"
            "3. **Output the Equations:** Use the following format for your answer, listing all formulated KCL and KVL equations clearly:\n\n"
            "```\n"
            "Equations:\n"
            "KCL at Node 1: <equation_node_1>\n"
            "KCL at Node 2: <equation_node_2>\n"
            "...\n"
            "KVL for Loop 1: <equation_loop_1>\n"
            "KVL for Loop 2: <equation_loop_2>\n"
            "...\n"
            "```\n\n"
            "Focus solely on providing the correct set of equations based on the circuit description."
        )
        prompt = instruction + '\n' + instruction_following
        return prompt

    @staticmethod
    def _parse_and_eval_equation(eq_str: str, true_branch_currents: List[Optional[float]], atol: float = 1e-2, rtol: float = 1e-3) -> bool:
        # print(f"[DEBUG _parse_and_eval_equation] Evaluating equation: '{eq_str}' with currents: {true_branch_currents}")
        if "=" not in eq_str:
            # print("[DEBUG _parse_and_eval_equation] No '=' found in equation string.")
            return False

        lhs_str, rhs_str = eq_str.split('=', 1)
        # print(f"[DEBUG _parse_and_eval_equation] LHS string: '{lhs_str}', RHS string: '{rhs_str}'")

        # Create a very limited scope for eval
        # Only allow math constants and functions that don't interact with system
        safe_globals = {"__builtins__": {}}
        # Whitelist specific math functions if necessary, e.g. abs, sqrt, etc.
        # For basic KCL/KVL, direct arithmetic should be fine.
        # safe_locals = {name: getattr(math, name) for name in dir(math) if callable(getattr(math, name))}
        # safe_locals.update({'abs': abs}) # Example
        safe_locals = {'abs': abs}


        def evaluate_side(side_str: str, true_branch_currents: List[Optional[float]]) -> Optional[float]:
            # print(f"[DEBUG evaluate_side] Evaluating side: '{side_str}'")
            substituted_side_str = side_str.strip()

            # 自动补全省略的乘号，例如 10 I_2 -> 10*I_2，I_1 I_2 -> I_1*I_2
            # 1. 数字和变量之间
            substituted_side_str = re.sub(r'(\d)\s*([A-Za-z_][A-Za-z0-9_]*)', r'\1*\2', substituted_side_str)
            # 2. 变量和变量之间
            substituted_side_str = re.sub(r'(I_\d+)\s+(I_\d+)', r'\1*\2', substituted_side_str)
            # 3. 括号和变量之间 (如 )I_2)
            substituted_side_str = re.sub(r'(\))\s*([A-Za-z_][A-Za-z0-9_]*)', r'\1*\2', substituted_side_str)
            # 4. 变量和括号之间 (如 I_2(3+4))
            substituted_side_str = re.sub(r'([A-Za-z_][A-Za-z0-9_]*)\s*(\()', r'\1*\2', substituted_side_str)

            # Find all I_(\d+) tokens, sort by index (desc) to replace I_10 before I_1
            current_vars = sorted(list(set(re.findall(r'I_(\d+)', substituted_side_str))), key=lambda x: int(x), reverse=True)
            # print(f"[DEBUG evaluate_side] Found current variables: {current_vars}")

            for idx_str in current_vars:
                current_idx = int(idx_str)
                # print(f"[DEBUG evaluate_side] Attempting to substitute I_{current_idx}")
                if 0 < current_idx <= len(true_branch_currents):
                    val = true_branch_currents[current_idx - 1]
                    if val is None:
                        # print(f"[DEBUG evaluate_side] Current I_{current_idx} value is None. Cannot evaluate.")
                        return None  # Cannot evaluate if a current is None
                    # Ensure substitution is for the whole variable name, e.g. I_1 not I_10
                    original_substituted_side_str = substituted_side_str
                    substituted_side_str = re.sub(r'\bI_' + idx_str + r'\b', f"({str(val)})", substituted_side_str)
                    # print(f"[DEBUG evaluate_side] Substituting I_{idx_str} with ({str(val)}). Before: '{original_substituted_side_str}', After: '{substituted_side_str}'")
                else:
                    # print(f"[DEBUG evaluate_side] Warning: Current index I_{idx_str} out of bounds for true_branch_currents (len {len(true_branch_currents)})")
                    return None  # Current index out of bounds

            # Check for any remaining alphabetic characters (potential unreplaced variables or forbidden functions)
            # Allows 'e' or 'E' for scientific notation.
            remaining_vars_match = re.search(r'[a-df-zA-DF-Z]', substituted_side_str) # Check for letters other than e/E
            if remaining_vars_match:
                # print(f"[DEBUG evaluate_side] Warning: Expression '{substituted_side_str}' contains unhandled variables or functions (e.g., '{remaining_vars_match.group(0)}') after substitution.")
                return None
            else:
                # print(f"[DEBUG evaluate_side] No unhandled variables found in '{substituted_side_str}'.")
                pass
            
            try:
                # print(f"[DEBUG evaluate_side] Attempting to eval: '{substituted_side_str}'")
                # Evaluate the expression string.
                value = eval(substituted_side_str, safe_globals, safe_locals)
                # print(f"[DEBUG evaluate_side] Eval result for '{substituted_side_str}': {value}")
                return float(value)
            except Exception as e:
                # print(f"[DEBUG evaluate_side] Error evaluating expression side '{substituted_side_str}': {e}")
                return None

        lhs_val = evaluate_side(lhs_str, true_branch_currents)
        rhs_val = evaluate_side(rhs_str, true_branch_currents)

        # print(f"[DEBUG _parse_and_eval_equation] LHS evaluated value: {lhs_val}, RHS evaluated value: {rhs_val}")

        if lhs_val is not None and rhs_val is not None:
            is_close = np.isclose(lhs_val, rhs_val, atol=atol, rtol=rtol)
            # print(f"[DEBUG _parse_and_eval_equation] Comparison np.isclose({lhs_val}, {rhs_val}) results in: {is_close}")
            return is_close
        
        # print("[DEBUG _parse_and_eval_equation] LHS or RHS evaluation resulted in None. Returning False.")
        return False

    @staticmethod
    def _apply_implicit_multiplication(expr_str: str) -> str:
        """Applies regex for implicit multiplications."""
        # 1. 数字和变量之间
        expr_str = re.sub(r'(\d(?:\.\d*)?(?:[eE][-+]?\d+)?)\s*([A-Za-z_][A-Za-z0-9_]*)', r'\1*\2', expr_str)
        # 2. 变量和变量之间
        expr_str = re.sub(r'(I_\d+)\s+(I_\d+)', r'\1*\2', expr_str) # I_1 I_2 -> I_1*I_2
        expr_str = re.sub(r'([A-Za-z_][A-Za-z0-9_]*)\s+(I_\d+)', r'\1*\2', expr_str) # Potentially other vars like V_1 I_2 -> V_1*I_2
        expr_str = re.sub(r'(I_\d+)\s+([A-Za-z_][A-Za-z0-9_]*)', r'\1*\2', expr_str) # I_1 V_2 -> I_1*V_2
        # 3. 括号和变量之间 (如 )I_2 or (expr) I_2 )
        expr_str = re.sub(r'\)\s*([A-Za-z_][A-Za-z0-9_]*)', r')*\1', expr_str)
        # 4. 变量和括号之间 (如 I_2(3+4) or I_2 (3+4) )
        expr_str = re.sub(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', r'\1*(', expr_str)
        # 5. 数字和开括号之间 (e.g. 2(I_1+I_2))
        expr_str = re.sub(r'(\d(?:\.\d*)?(?:[eE][-+]?\d+)?)\s*\(', r'\1*(', expr_str)
        # 6. 闭括号和数字之间 (e.g. (I_1+I_2)2)
        expr_str = re.sub(r'\)\s*(\d(?:\.\d*)?(?:[eE][-+]?\d+)?)', r')*\1', expr_str)
        return expr_str

    @staticmethod
    def _evaluate_expression_for_coeffs(expr_str: str, current_values: List[float], num_total_currents: int) -> Optional[float]:
        # print(f"[DEBUG _evaluate_expression_for_coeffs] Evaluating expr: '{expr_str}' with I_values: {current_values}")
        substituted_expr_str = expr_str

        # Apply implicit multiplication rules
        substituted_expr_str = Circuitbootcamp._apply_implicit_multiplication(substituted_expr_str)
        # print(f"[DEBUG _evaluate_expression_for_coeffs] After implicit multiplication: '{substituted_expr_str}'")

        # Substitute I_k variables from highest index to lowest to avoid issues like I_10 vs I_1
        for i in range(num_total_currents, 0, -1):
            val_to_sub = current_values[i-1]
            # Wrap in parentheses for safety, especially for negative numbers
            substituted_expr_str = re.sub(r'\bI_' + str(i) + r'\b', f"({str(val_to_sub)})", substituted_expr_str)
        
        # print(f"[DEBUG _evaluate_expression_for_coeffs] After substituting I_k: '{substituted_expr_str}'")

        # Check for any remaining I_k variables (should not happen if all substituted) or other letters
        # Allows 'e' or 'E' for scientific notation in numbers.
        remaining_vars_match = re.search(r'\bI_\d+\b|[a-df-zA-DF-Z]', substituted_expr_str)
        if remaining_vars_match:
            # print(f"[DEBUG _evaluate_expression_for_coeffs] Warning: Expression '{substituted_expr_str}' contains unhandled variables (e.g., '{remaining_vars_match.group(0)}') after substitution.")
            return None
        
        safe_globals = {"__builtins__": {}}
        safe_locals = {'abs': abs} # Add other math functions if needed by equations

        try:
            # Evaluate the expression string.
            value = eval(substituted_expr_str, safe_globals, safe_locals)
            # print(f"[DEBUG _evaluate_expression_for_coeffs] Eval result for '{substituted_expr_str}': {value}")
            return float(value)
        except Exception as e:
            # print(f"[DEBUG _evaluate_expression_for_coeffs] Error evaluating expression '{substituted_expr_str}': {e}")
            return None

    @staticmethod
    def _get_equation_coefficients(eq_str: str, num_branch_currents: int) -> Optional[List[float]]:
        # print(f"[DEBUG _get_equation_coefficients] Processing eq: '{eq_str}' for {num_branch_currents} current variables")
        if num_branch_currents == 0: # No currents, no variable coefficients
            # Try to evaluate the expression directly if it's like "const1 = const2"
            if "=" not in eq_str:
                # print(f"[DEBUG _get_equation_coefficients] No '=' in equation '{eq_str}' with no currents, cannot form const vector.")
                return None 
            lhs_s, rhs_s = eq_str.split("=", 1)
            try:
                # Apply implicit multiplication for safety, e.g. "2 pi = 6.28"
                lhs_s = Circuitbootcamp._apply_implicit_multiplication(lhs_s)
                rhs_s = Circuitbootcamp._apply_implicit_multiplication(rhs_s)
                
                safe_globals = {"__builtins__": {}}
                safe_locals = {'abs': abs} # Add other math functions if needed
                
                lhs_val = float(eval(lhs_s, safe_globals, safe_locals))
                rhs_val = float(eval(rhs_s, safe_globals, safe_locals))
                # constant term for "expr = 0" is "lhs_val - rhs_val"
                # print(f"[DEBUG _get_equation_coefficients] Eq with no currents: '{eq_str}', const_term = {lhs_val - rhs_val}")
                return [lhs_val - rhs_val] # Just the constant term
            except Exception as e:
                # print(f"[DEBUG _get_equation_coefficients] Could not eval '{eq_str}' as const=const: {e}")
                return None

        if "=" not in eq_str:
            # print(f"[DEBUG _get_equation_coefficients] No '=' found in equation string: '{eq_str}'")
            return None
        
        lhs_str, rhs_str = eq_str.split('=', 1)
        # Form the expression string "LHS - (RHS)" which should evaluate to 0
        expression_str = f"({lhs_str.strip()}) - ({rhs_str.strip()})"
        # print(f"[DEBUG _get_equation_coefficients] Standardized expr: '{expression_str}'")

        coeffs = [0.0] * (num_branch_currents + 1) # +1 for the constant term

        # Calculate constant term (value of expression when all I_k = 0)
        all_currents_zero = [0.0] * num_branch_currents
        constant_term = Circuitbootcamp._evaluate_expression_for_coeffs(expression_str, all_currents_zero, num_branch_currents)
        if constant_term is None:
            # print(f"[DEBUG _get_equation_coefficients] Failed to evaluate constant term for: {expression_str}")
            return None
        coeffs[num_branch_currents] = constant_term
        # print(f"[DEBUG _get_equation_coefficients] Constant term = {constant_term}")

        # Calculate coefficient for each I_k
        for k_idx in range(num_branch_currents): # k_idx from 0 to num_branch_currents-1
            current_values_Ik_one = [0.0] * num_branch_currents
            current_values_Ik_one[k_idx] = 1.0
            
            val_Ik_one = Circuitbootcamp._evaluate_expression_for_coeffs(expression_str, current_values_Ik_one, num_branch_currents)
            if val_Ik_one is None:
                # print(f"[DEBUG _get_equation_coefficients] Failed to evaluate for I_{k_idx+1}=1 for: {expression_str}")
                return None
            
            # Coefficient of I_k is (Value of expr with I_k=1, others=0) - (Value of expr with all I_k=0, i.e. constant_term)
            coeffs[k_idx] = val_Ik_one - constant_term
            # print(f"[DEBUG _get_equation_coefficients] Coeff for I_{k_idx+1} = {val_Ik_one} - {constant_term} = {coeffs[k_idx]}")

        # print(f"[DEBUG _get_equation_coefficients] Successfully extracted coeffs for '{eq_str}': {coeffs}")
        return coeffs

    @staticmethod
    def extract_output(output_str: str) -> Tuple[Optional[List[Optional[float]]], Optional[List[Optional[float]]], List[Dict[str, str]]]:
        """
        从模型的输出字符串中提取所有边的电流值、所有节点的电势值以及方程。
        优先从 markdown 代码块（```...```）中提取 Equations 区块。
        电流和电势也优先从最后一个 markdown 代码块中的相应区块提取。
        """
        # print(f"\\n[DEBUG extract_output] --- Starting Extraction ---")
        temp_output_preview = output_str[:100] if output_str else 'None'
        # print(f"[DEBUG extract_output] Input output_str (first 100 chars): '{temp_output_preview}'...")

        if output_str is None:
            # print("[DEBUG extract_output] output_str is None, returning None, None, []")
            return None, None, []
        
        output_str = output_str.strip()
        # print(f"[DEBUG extract_output] Stripped output_str (first 100 chars): '{output_str[:100]}'...") # Redundant with above
        
        branch_currents: List[Optional[float]] = []
        node_potentials: List[Optional[float]] = []
        extracted_equations: List[Dict[str, str]] = []

        # --- Step 1: Attempt to find the last markdown code block ---
        last_code_block_content = None

        # ADDED: Primitive checks for "```"
        literal_backtick_count = output_str.count("```")
        # print(f"[DEBUG extract_output] output_str.count('```'): {literal_backtick_count}")
        literal_backtick_matches = list(re.finditer(r"```", output_str))
        # print(f"[DEBUG extract_output] Positions of literal '```' found by re.finditer(r'```', output_str): {[m.start() for m in literal_backtick_matches]}")

        # MODIFIED REGEX for code block matching
        code_block_matches = list(re.finditer(r'```((?:.|\n)*?)```', output_str)) 
        # print(f"[DEBUG extract_output] Number of code blocks found (using new regex): {len(code_block_matches)}") 

        if code_block_matches:
            # ADDED DEBUG to see all captured blocks if there are few
            if len(code_block_matches) < 5: # Print all if not too many
                for i, match in enumerate(code_block_matches):
                    # print(f"[DEBUG extract_output] Code block {i} content (first 200 chars):\n'''{match.group(1).strip()[:200]}...'''")
                    pass
            
            last_code_block_content = code_block_matches[-1].group(1).strip()
            # print(f"[DEBUG extract_output] LAST code block content (first 500 chars):\n'''{last_code_block_content[:500]}...'''") # MODIFIED DEBUG
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
            # print(f"[DEBUG extract_output] Equations section found. Text:\n'''{equations_text}'''")
            # MODIFIED: Use splitlines() for robust line splitting
            raw_eq_lines = equations_text.splitlines() 
            # print(f"[DEBUG extract_output] Number of raw equation lines found: {len(raw_eq_lines)}") # ADDED DEBUG
            for i, line in enumerate(raw_eq_lines):
                line = line.strip()
                # print(f"[DEBUG extract_output] Processing equation line {i+1}/{len(raw_eq_lines)}: '{line}'") # MODIFIED DEBUG
                if not line or line == "...": 
                    # print(f"[DEBUG extract_output] Skipping empty or '...' line.") # ADDED DEBUG
                    continue
                
                # KCL Match Attempt
                kcl_regex = r'KCL\s+at\s+Node\s+\w+:\s*(.*)'
                kcl_match = re.match(kcl_regex, line, re.IGNORECASE)
                # print(f"[DEBUG extract_output] KCL match for '{line}' using regex '{kcl_regex}': {bool(kcl_match)}") # ADDED DEBUG
                if kcl_match:
                    eq_s = kcl_match.group(1).strip()
                    eq_s_cleaned = eq_s.split('//')[0].strip()
                    if eq_s_cleaned and not eq_s_cleaned.startswith("<equation_node_"):
                        extracted_equations.append({"type": "kcl", "equation_str": eq_s_cleaned})
                        # print(f"[DEBUG extract_output] Appended KCL equation: {eq_s_cleaned}")
                    else: 
                        # print(f"[DEBUG extract_output] KCL equation '{eq_s_cleaned}' not appended (empty or placeholder).") # ADDED DEBUG
                        continue
                
                # KVL Match Attempt
                kvl_regex = r'KVL\s+for\s+(.+?):\s*(.*)'
                kvl_match = re.match(kvl_regex, line, re.IGNORECASE)
                # print(f"[DEBUG extract_output] KVL match for '{line}' using regex '{kvl_regex}': {bool(kvl_match)}") # ADDED DEBUG
                if kvl_match:
                    eq_s = kvl_match.group(2).strip()
                    eq_s_cleaned = eq_s.split('//')[0].strip()
                    if eq_s_cleaned and not eq_s_cleaned.startswith("<equation_loop_"):
                        extracted_equations.append({"type": "kvl", "equation_str": eq_s_cleaned})
                        # 保存 KVL 方程到文件
                        Circuitbootcamp._save_kvl_equation_to_file(eq_s_cleaned)
                        # print(f"[DEBUG extract_output] Appended KVL equation: {eq_s_cleaned}")
                    else: 
                        # print(f"[DEBUG extract_output] KVL equation '{eq_s_cleaned}' not appended (empty or placeholder).") # ADDED DEBUG
                        continue
                
                # print(f"[DEBUG extract_output] Line did not match KCL or KVL pattern.") # ADDED DEBUG
        else:
            # print("[DEBUG extract_output] Equations section not found in preferred or global search.")
            pass

        # --- Step 3: Extract Currents and Potentials ---
        # Priority: Last code block -> Global text
        
        parsed_currents_from_block = False
        parsed_potentials_from_block = False

        if last_code_block_content:
            # print("[DEBUG extract_output] Attempting to extract Currents and Potentials from LAST CODE BLOCK.")
            current_section_text_block = None
            potential_section_text_block = None
            
            # MODIFIED REGEX for capturing group
            current_match_block = re.search(r'Currents?:?\s*((?:.|\n)*?)(?=Potentials?:?|$)', last_code_block_content, re.IGNORECASE)
            if current_match_block:
                current_section_text_block = current_match_block.group(1).strip()
                # print(f"[DEBUG extract_output] [BLOCK] Currents section found. Text:\n'''{current_section_text_block}'''")
                
                temp_currents_map: Dict[int, float] = {}
                # MODIFIED: Process line by line
                current_lines = current_section_text_block.splitlines()
                # print(f"[DEBUG extract_output] [BLOCK] Number of current lines: {len(current_lines)}")
                for line_idx, current_line in enumerate(current_lines):
                    current_line = current_line.strip()
                    # print(f"[DEBUG extract_output] [BLOCK] Processing current line {line_idx+1}: '{current_line}'")
                    # Try primary pattern: I_X = VAL A
                    match_primary = re.match(r'I_(\d+)\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*A', current_line, re.IGNORECASE)
                    if match_primary:
                        edge_idx_str, current_str = match_primary.groups()
                        # print(f"[DEBUG extract_output] [BLOCK] Primary match: idx='{edge_idx_str}', val='{current_str}'")
                        try:
                            edge_idx = int(edge_idx_str) - 1  
                            if edge_idx >= 0: 
                                temp_currents_map[edge_idx] = float(current_str)
                                # print(f"[DEBUG extract_output] [BLOCK] Parsed current I_{edge_idx+1} = {current_str}")
                                parsed_currents_from_block = True # Mark success if at least one parsed
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing current: idx='{edge_idx_str}', val='{current_str}'")
                            pass
                        continue # Process next line after try/except for current match_primary
            
                    # Try alternative pattern: Edge X : VAL A or Current X : VAL A
                    match_alt = re.match(r'(?:Edge|Current)\s+(\d+)\s*:?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*A', current_line, re.IGNORECASE)
                    if match_alt:
                        edge_idx_str, current_str = match_alt.groups()
                        # print(f"[DEBUG extract_output] [BLOCK] Alt match: idx='{edge_idx_str}', val='{current_str}'")
                        try:
                            edge_idx = int(edge_idx_str) - 1  
                            if edge_idx >= 0: 
                                temp_currents_map[edge_idx] = float(current_str)
                                # print(f"[DEBUG extract_output] [BLOCK] Parsed current (alt) I_{edge_idx+1} = {current_str}")
                                parsed_currents_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing current (alt): idx='{edge_idx_str}', val='{current_str}'")
                            pass
                        continue # Process next line after try/except for current match_alt
                    if current_line: # If line is not empty and didn't match
                         # print(f"[DEBUG extract_output] [BLOCK] No current pattern matched for line: '{current_line}'")
                         pass
                
                # Removed old re.findall logic for block currents
                # print(f"[DEBUG extract_output] [BLOCK] Currents: Primary indexed matches={len(current_matches_primary_block)}, Alt indexed matches={len(current_matches_alt_block)}")

                # for edge_idx_str, current_str in all_current_matches_block:
                # ... (old loop removed)
                if temp_currents_map:
                    max_idx = max(temp_currents_map.keys())
                    branch_currents = [temp_currents_map.get(i) for i in range(max_idx + 1)]
                    # parsed_currents_from_block = True # This is now set inside the loop on first success
                # else:
                #    print("[DEBUG extract_output] [BLOCK] No indexed currents found in Currents section of the code block.")
            else:
                # print("[DEBUG extract_output] [BLOCK] Currents section not found in the code block.")
                pass

            # MODIFIED REGEX for capturing group
            potential_match_block = re.search(r'Potentials?:?\s*((?:.|\n)*?)(?=$)', last_code_block_content, re.IGNORECASE)
            if potential_match_block:
                potential_section_text_block = potential_match_block.group(1).strip()
                # print(f"[DEBUG extract_output] [BLOCK] Potentials section found. Text:\n'''{potential_section_text_block}'''")

                temp_potentials_map: Dict[int, float] = {}
                # MODIFIED: Process line by line
                potential_lines = potential_section_text_block.splitlines()
                # print(f"[DEBUG extract_output] [BLOCK] Number of potential lines: {len(potential_lines)}")
                for line_idx, p_line in enumerate(potential_lines):
                    p_line = p_line.strip()
                    # print(f"[DEBUG extract_output] [BLOCK] Processing potential line {line_idx+1}: '{p_line}'")
                    # Try primary pattern: V_X = VAL V
                    match_primary_pot = re.match(r'V_(\d+)\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*V', p_line, re.IGNORECASE)
                    if match_primary_pot:
                        node_idx_str, potential_str = match_primary_pot.groups()
                        # print(f"[DEBUG extract_output] [BLOCK] Primary potential match: idx='{node_idx_str}', val='{potential_str}'")
                        try:
                            node_idx = int(node_idx_str)
                            if node_idx >= 0: 
                                temp_potentials_map[node_idx] = float(potential_str)
                                # print(f"[DEBUG extract_output] [BLOCK] Parsed potential V_{node_idx} = {potential_str}")
                                parsed_potentials_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing potential: idx='{node_idx_str}', val='{potential_str}'")
                            continue

                    # Try alternative pattern: Node X : VAL V or Potential X : VAL V
                    match_alt_pot = re.match(r'(?:Node|Potential)\s+(\d+)\s*:?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*V', p_line, re.IGNORECASE)
                    if match_alt_pot:
                        node_idx_str, potential_str = match_alt_pot.groups()
                        # print(f"[DEBUG extract_output] [BLOCK] Alt potential match: idx='{node_idx_str}', val='{potential_str}'")
                        try:
                            node_idx = int(node_idx_str)
                            if node_idx >= 0: 
                                temp_potentials_map[node_idx] = float(potential_str)
                                # print(f"[DEBUG extract_output] [BLOCK] Parsed potential (alt) V_{node_idx} = {potential_str}")
                                parsed_potentials_from_block = True # Mark success
                        except ValueError:
                            # print(f"[DEBUG extract_output] [BLOCK] ValueError parsing potential (alt): idx='{node_idx_str}', val='{potential_str}'")
                            pass
                        continue
                    if p_line: # If line is not empty and didn't match
                        # print(f"[DEBUG extract_output] [BLOCK] No potential pattern matched for line: '{p_line}'")
                        pass
                
                # Removed old re.findall logic for block potentials
                # print(f"[DEBUG extract_output] [BLOCK] Potentials: Primary indexed matches={len(potential_matches_primary_block)}, Alt indexed matches={len(potential_matches_alt_block)}")

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
            # print("[DEBUG extract_output] Currents not found in code block or parsing failed, trying GLOBAL search.")
            current_section_text_global = None
            # MODIFIED REGEX for capturing group
            current_match_global = re.search(r'Currents?:?\s*((?:.|\n)*?)(?=Potentials?:?|$)', output_str, re.IGNORECASE)
            if current_match_global:
                current_section_text_global = current_match_global.group(1).strip()
                # print(f"[DEBUG extract_output] [GLOBAL] Currents section found. Text (first 100 chars):\n'''{current_section_text_global[:100]}...'''")
                
                temp_currents_map: Dict[int, float] = {}
                current_matches_primary_global = re.findall(r'I_(\\d+)\\s*=\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*A', current_section_text_global, re.IGNORECASE)
                current_matches_alt_global = re.findall(r'(?:Edge|Current)\\s+(\\d+)\\s*:?\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*A', current_section_text_global, re.IGNORECASE)
                all_current_matches_global = current_matches_primary_global + current_matches_alt_global
                # print(f"[DEBUG extract_output] [GLOBAL] Currents: Primary indexed matches={len(current_matches_primary_global)}, Alt indexed matches={len(current_matches_alt_global)}")

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
                #    print("[DEBUG extract_output] [GLOBAL] No indexed currents, trying to extract any floats for currents.") # Old fallback
                #    values_only = re.findall(r'([-+]\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*(?:A|Amperes?)?', current_section_text_global)
                #    if values_only: branch_currents = [float(val) for val in values_only]
            else:
                # print("[DEBUG extract_output] [GLOBAL] Currents section not found.")
                pass
        
        if not parsed_potentials_from_block:
            # print("[DEBUG extract_output] Potentials not found in code block or parsing failed, trying GLOBAL search.")
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
        
        # print(f"[DEBUG extract_output] Final extracted currents: {final_branch_currents}")
        # print(f"[DEBUG extract_output] Final extracted potentials: {final_node_potentials}")
        # print(f"[DEBUG extract_output] Final extracted equations: {extracted_equations}")
        # print(f"[DEBUG extract_output] --- Ending Extraction ---")
        return final_branch_currents, final_node_potentials, extracted_equations

    @staticmethod
    def _normalize_solution(solution):
        """
        The solution is expected to be a float or None after extract_output.
        No further normalization usually needed.
        """
        return solution

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

    @classmethod
    def verify_score(cls, model_output: str, identity: dict,
                     score_max: float = 1.0,
                     score_min: float = 0.0,
                     atol: float = 1e-3,
                     rtol: float = 1e-3,
                     equation_reward_weight: float = 1.0,  # Changed default to 1.0
                     format_score: Optional[float] = None, # Compatibility, unused
                     w_num: float = 0.2, # Weight for equation number score (将被新逻辑忽略)
                     w_combined: float = 0.8,  # Weight for combined equation correctness and independence score (将被新逻辑忽略)
                     short_penalty: bool = False,  # Added for compatibility
                     format_penalty: bool = False,  # Added for compatibility
                     **kwargs  # Accept any additional keyword arguments
                    ) -> float:
        """
        Verifies model output for currents, potentials, and equations, calculating a comprehensive score.
        新的分数计算逻辑：
        0.5 * (正确的KCL方程数/理应有的KCL方程数[节点数-1]) 
        + 0.5 * (正确的KVL方程数/理应有的KVL方程数[边数-节点数+1])
        - (不独立的方程数[方程数-系数矩阵的秩] / (理应有的KCL方程数+理应有的KVL方程数))
        """
        # print(f"\\n[DEBUG verify_score] --- Starting Verification ---")
        # print(f"[DEBUG verify_score] model_output (first 300 chars):\n'''{model_output[:300]}...'''")
        # print(f"[DEBUG verify_score] identity: {identity}") # Can be verbose

        if model_output is None or not model_output.strip():
            # print(f"[DEBUG verify_score] Model output is None or empty. Returning score_min: {score_min}")
            return score_min
        
        if not (0 <= equation_reward_weight <= 1.0):
            # print(f"[DEBUG verify_score] Invalid equation_reward_weight: {equation_reward_weight}. Using 1.0 as default.")
            equation_reward_weight = 1.0 

        extracted_currents, extracted_potentials, extracted_equations = cls.extract_output(model_output)
        # print(f"[DEBUG verify_score] Extracted Currents: {extracted_currents}")
        # print(f"[DEBUG verify_score] Extracted Potentials: {extracted_potentials}")
        # print(f"[DEBUG verify_score] Extracted Equations: {extracted_equations}")
        
        # --- Score for Currents and Potentials ---
        correct_vars_count = 0
        total_vars_count = 0
        
        expected_currents = identity.get('branch_currents')
        expected_potentials = identity.get('node_potentials')
        # print(f"[DEBUG verify_score] Expected Currents: {expected_currents}")
        # print(f"[DEBUG verify_score] Expected Potentials: {expected_potentials}")

        if expected_currents is not None:
            num_currents_to_compare = len(expected_currents)
            total_vars_count += num_currents_to_compare
            # print(f"[DEBUG verify_score] Comparing {num_currents_to_compare} expected currents.")
            if extracted_currents is not None and len(extracted_currents) > 0 :
                for i in range(num_currents_to_compare):
                    is_correct = False
                    if i < len(extracted_currents) and extracted_currents[i] is not None and expected_currents[i] is not None:
                        if np.isclose(extracted_currents[i], expected_currents[i], atol=atol, rtol=rtol):
                            correct_vars_count += 1
                            is_correct = True
                    val_extracted = extracted_currents[i] if i < len(extracted_currents) else 'N/A'
                    # print(f"[DEBUG verify_score] Current I_{i+1}: Expected={expected_currents[i]}, Extracted={val_extracted}, Correct={is_correct}")
            else:
                # print(f"[DEBUG verify_score] Extracted currents are None or empty, all {num_currents_to_compare} expected currents count as incorrect.")
                pass

        if expected_potentials is not None:
            num_potentials_to_compare = len(expected_potentials)
            total_vars_count += num_potentials_to_compare
            # print(f"[DEBUG verify_score] Comparing {num_potentials_to_compare} expected potentials.")
            if extracted_potentials is not None and len(extracted_potentials) > 0:
                for i in range(num_potentials_to_compare):
                    is_correct = False
                    # Node 0 potential should be 0 if present
                    expected_val = 0.0 if i == 0 and expected_potentials[i] is not None else expected_potentials[i]

                    if i < len(extracted_potentials) and extracted_potentials[i] is not None and expected_val is not None:
                        if np.isclose(extracted_potentials[i], expected_val, atol=atol, rtol=rtol):
                            correct_vars_count += 1
                            is_correct = True
                    val_extracted = extracted_potentials[i] if i < len(extracted_potentials) else 'N/A'
                    # print(f"[DEBUG verify_score] Potential V_{i}: Expected={expected_val}, Extracted={val_extracted}, Correct={is_correct}")
            else:
                # print(f"[DEBUG verify_score] Extracted potentials are None or empty, all {num_potentials_to_compare} expected potentials count as incorrect.")
                pass
        current_potential_score_ratio = 0.0
        if total_vars_count > 0:
            current_potential_score_ratio = correct_vars_count / total_vars_count
        # print(f"[DEBUG verify_score] Correct Vars: {correct_vars_count}, Total Vars: {total_vars_count}, Var Ratio: {current_potential_score_ratio:.4f}")
        
        # --- 新的方程分数计算逻辑 ---
        equation_accuracy_ratio = 0.0

        n_nodes = identity.get('n_nodes', 0)
        n_edges = len(identity.get('edges', [])) # Number of branches/edges
        
        # num_branch_currents is essentially n_edges for coefficient vector size
        num_branch_currents_for_coeffs = n_edges

        exp_kcl_count = max(0, n_nodes - 1)
        exp_kvl_count = max(0, n_edges - n_nodes + 1) if n_nodes > 0 else (1 if n_edges > 0 else 0) # KVL for a single edge is V=E
        if n_nodes == 1 and n_edges == 0: exp_kvl_count = 0 # Special case: single isolated node

        exp_total_eq = exp_kcl_count + exp_kvl_count
        # print(f"[DEBUG verify_score] Expected KCLs: {exp_kcl_count}, Expected KVLs: {exp_kvl_count}, Expected Total Eqs: {exp_total_eq}")

        total_submitted_equations = len(extracted_equations)
        # print(f"[DEBUG verify_score] Total Submitted Equations: {total_submitted_equations}")

        if equation_reward_weight > 0: # Only calculate equation scores if they contribute
            # 分别计算正确的KCL和KVL方程数量
            correct_kcl_count = 0
            correct_kvl_count = 0
            matrix_rank = 0
            coefficient_vectors = []

            # 计算正确的方程数量，分KCL和KVL类型
            if total_submitted_equations > 0 and expected_currents is not None:
                for eq_info in extracted_equations:
                    eq_str = eq_info.get("equation_str")
                    eq_type = eq_info.get("type")
                    if eq_str:
                        is_eq_correct = cls._parse_and_eval_equation(eq_str, expected_currents, atol=atol, rtol=rtol)
                        if is_eq_correct:
                            if eq_type == 'kcl':
                                correct_kcl_count += 1
                            elif eq_type == 'kvl':
                                correct_kvl_count += 1
                        # print(f"[DEBUG verify_score] Equation Eval '{eq_str}' (Type: {eq_type}): Correct={is_eq_correct}")

            # 计算回路识别分数
            correct_loop_count = 0
            edges = identity.get('edges', [])
            
            if total_submitted_equations > 0:
                for eq_info in extracted_equations:
                    eq_str = eq_info.get("equation_str")
                    eq_type = eq_info.get("type")
                    if eq_str and eq_type == 'kvl':
                        # 从KVL方程中提取电流变量对应的边索引
                        edge_indices = cls._extract_current_variables_from_equation(eq_str)
                        # 检查这些边是否构成有效回路
                        if cls._check_if_edges_form_loop(edge_indices, edges):
                            correct_loop_count += 1
                            # print(f"[DEBUG verify_score] KVL equation '{eq_str}' forms valid loop with edges {edge_indices}")
                        else:
                            # print(f"[DEBUG verify_score] KVL equation '{eq_str}' does NOT form valid loop with edges {edge_indices}")
                            pass

            # 计算矩阵的秩来确定独立方程数量
            if total_submitted_equations > 0 and num_branch_currents_for_coeffs > 0:
                for eq_info in extracted_equations:
                    eq_str = eq_info.get("equation_str")
                    if eq_str:
                        coeffs = cls._get_equation_coefficients(eq_str, num_branch_currents_for_coeffs)
                        if coeffs and len(coeffs) == num_branch_currents_for_coeffs + 1:
                            coefficient_vectors.append(coeffs)
                        else:
                            # print(f"[DEBUG verify_score] Failed to get valid coefficients for eq: '{eq_str}'")
                            pass
                
                if coefficient_vectors:
                    # We are interested in the rank of the variable coefficients part of the matrix
                    # Each vector in coefficient_vectors is [c1, c2, ..., cN, const_term]
                    var_coeffs_matrix = np.array([vec[:-1] for vec in coefficient_vectors])
                    
                    if var_coeffs_matrix.size > 0: # Ensure matrix is not empty
                        # Suppress RankWarning if matrix is ill-conditioned but rank can still be computed
                        with np.testing.suppress_warnings() as sup:
                            sup.filter(UserWarning, "Near rank deficient matrix detected.") # For scipy.linalg.rank
                            # Using numpy.linalg.matrix_rank directly
                            try:
                                matrix_rank = np.linalg.matrix_rank(var_coeffs_matrix, tol=1e-6) # Add tolerance
                                # print(f"[DEBUG verify_score] Coefficient Matrix (vars only) for rank check (shape {var_coeffs_matrix.shape}):\n{var_coeffs_matrix}")
                                # print(f"[DEBUG verify_score] Rank of coefficient matrix: {matrix_rank}")
                            except Exception as e_rank:
                                # print(f"[DEBUG verify_score] Error calculating matrix rank: {e_rank}")
                                matrix_rank = 0 # Error in rank calculation

            # 计算KCL分数
            kcl_score = 0.0
            if exp_kcl_count > 0:
                kcl_score = min(1.0, correct_kcl_count / exp_kcl_count)
            else:
                # 如果不需要KCL方程，那么这部分得满分
                kcl_score = 1.0

            # 计算基础KVL分数（方程正确性）
            base_kvl_score = 0.0
            if exp_kvl_count > 0:
                base_kvl_score = min(1.0, correct_kvl_count / exp_kvl_count)
            else:
                # 如果不需要KVL方程，那么这部分得满分
                base_kvl_score = 1.0

            # 计算回路识别分数
            loop_score = 0.0
            if exp_kvl_count > 0:
                loop_score = min(1.0, correct_loop_count / exp_kvl_count)
            else:
                # 如果不需要KVL方程，回路分数也是满分
                loop_score = 1.0

            # 新的KVL分数：0.3 * 回路分 + 0.7 * 原来的kvl_score
            kvl_score = 0.3 * loop_score + 0.7 * base_kvl_score

            # 计算不独立的方程数
            non_independent_equations = total_submitted_equations - matrix_rank
            independence_penalty = 0.0
            if exp_total_eq > 0:
                independence_penalty = non_independent_equations / exp_total_eq

            # 最终方程分数
            equation_accuracy_ratio = 0.4 * kcl_score + 0.6 * kvl_score - independence_penalty
            # 确保分数不小于0
            equation_accuracy_ratio = max(0.0, equation_accuracy_ratio)

            # print(f"[DEBUG verify_score] Correct KCL Equations: {correct_kcl_count} / {exp_kcl_count} = {kcl_score:.4f}")
            # print(f"[DEBUG verify_score] Correct KVL Equations: {correct_kvl_count} / {exp_kvl_count} = {base_kvl_score:.4f}")
            # print(f"[DEBUG verify_score] Correct Loop Identification: {correct_loop_count} / {exp_kvl_count} = {loop_score:.4f}")
            # print(f"[DEBUG verify_score] Final KVL Score (0.3*loop + 0.7*base): {kvl_score:.4f}")
            # print(f"[DEBUG verify_score] Matrix Rank: {matrix_rank}")
            # print(f"[DEBUG verify_score] Non-independent Equations: {non_independent_equations}")
            # print(f"[DEBUG verify_score] Independence Penalty: {independence_penalty:.4f}")
            # print(f"[DEBUG verify_score] Final Equation Accuracy Ratio: {equation_accuracy_ratio:.4f}")
        
        # --- Combine Overall Scores ---
        variables_weight = 1.0 - equation_reward_weight
        
        combined_correct_ratio = (variables_weight * current_potential_score_ratio +
                                  equation_reward_weight * equation_accuracy_ratio)
        # print(f"[DEBUG verify_score] Variables Weight: {variables_weight:.2f}, Overall Equation Reward Weight: {equation_reward_weight:.2f}")
        # print(f"[DEBUG verify_score] Combined Correct Ratio (vars + eq_weighted): {combined_correct_ratio:.4f}")

        # Handle case where nothing was expected and nothing was provided for vars
        if total_vars_count == 0 and not (extracted_currents or extracted_potentials): # No vars expected, none given
            # If equations were also not expected and not given, this is perfect.
            if exp_total_eq == 0 and total_submitted_equations == 0:
                # print(f"[DEBUG verify_score] No vars or equations expected, none provided. Perfect score contribution from this part.")
                pass # current logic for combined_correct_ratio should handle this.
        elif total_vars_count == 0 and (extracted_currents or extracted_potentials): # No vars expected, but some given
             # print(f"[DEBUG verify_score] No vars expected, but some extracted. current_potential_score_ratio is 0/0=nan, setting to 0.")
             current_potential_score_ratio = 0.0 # Avoid NaN if total_vars_count is 0 but extracted exist.
             # Recalculate combined_correct_ratio
             combined_correct_ratio = (variables_weight * current_potential_score_ratio +
                                  equation_reward_weight * equation_accuracy_ratio)

        if total_vars_count == 0 and total_submitted_equations == 0 and not (extracted_currents or extracted_potentials or extracted_equations) :
            # This condition implies nothing was extracted.
            # If nothing was expected either (total_vars_count ==0 already handled, and exp_total_eq == 0):
            if exp_total_eq == 0: # total_vars_count is already 0
                 # print(f"[DEBUG verify_score] Nothing extracted, nothing expected. Score should be max.")
                 return score_max # Perfect score if nothing expected and nothing given.
            else: # Nothing extracted, but something was expected
                 # print(f"[DEBUG verify_score] Nothing extracted, but something was expected. Returning score_min: {score_min}")
                 return score_min

        final_score = score_min + combined_correct_ratio * (score_max - score_min)
        # Clamp score to [score_min, score_max]
        final_score = max(score_min, min(final_score, score_max))

        # print(f"[DEBUG verify_score] Final Score: {final_score:.4f}")
        # print(f"[DEBUG verify_score] --- Ending Verification ---")
        return final_score

    @staticmethod
    def _extract_current_variables_from_equation(eq_str: str) -> List[int]:
        """
        从KVL方程中提取电流变量的索引
        例如：从 "7*I_1 - 2 + 8*I_2 + 10 = 0" 中提取 [0, 1] (对应边0和边1)
        注意：I_1对应边0，I_2对应边1，等等。I_0被认为是无效的
        返回的是边的索引列表
        """
        import re
        # 匹配 I_数字 的模式
        pattern = r'I_(\d+)'
        matches = re.findall(pattern, eq_str)
        # 转换为整数并减1（因为I_1对应边0），过滤掉I_0
        edge_indices = []
        for match in matches:
            current_index = int(match)
            if current_index > 0:  # 只接受I_1, I_2, I_3... 不接受I_0
                edge_indices.append(current_index - 1)  # I_1对应边0，I_2对应边1
        return list(set(edge_indices))  # 去重
    
    @staticmethod
    def _check_if_edges_form_loop(edge_indices: List[int], edges: List[List]) -> bool:
        """
        检查给定的边索引是否形成一个回路
        使用图论方法：如果边集合形成连通图且边数等于节点数，则形成回路
        edges格式: [(R, E, u, v), ...]
        """
        if len(edge_indices) < 3:  # 至少需要3条边才能形成回路
            return False
        
        # 收集所有涉及的节点
        nodes_in_edges = set()
        edge_connections = []
        
        for edge_idx in edge_indices:
            if edge_idx < len(edges):
                edge = edges[edge_idx]
                if len(edge) >= 4:  # (R, E, u, v)格式
                    node1, node2 = edge[2], edge[3]  # u, v
                    nodes_in_edges.add(node1)
                    nodes_in_edges.add(node2)
                    edge_connections.append((node1, node2))
        
        if len(nodes_in_edges) == 0:
            return False
        
        # 对于回路：边数应该等于节点数
        if len(edge_connections) != len(nodes_in_edges):
            return False
        
        # 检查连通性：使用并查集或DFS
        # 这里使用简单的连通性检查
        if len(nodes_in_edges) < 3:  # 至少需要3个节点
            return False
        
        # 构建邻接表
        adj = {node: [] for node in nodes_in_edges}
        for node1, node2 in edge_connections:
            adj[node1].append(node2)
            adj[node2].append(node1)
        
        # 检查每个节点的度数是否为2（回路的特征）
        for node in nodes_in_edges:
            if len(adj[node]) != 2:
                return False
        
        # 检查连通性：从任意节点开始DFS，应该能访问所有节点
        start_node = next(iter(nodes_in_edges))
        visited = set()
        stack = [start_node]
        
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                for neighbor in adj[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        # 如果访问的节点数等于总节点数，则连通
        return len(visited) == len(nodes_in_edges)

    @staticmethod
    def _save_kvl_equation_to_file(equation_str: str, kvl_file_path: str = "/cpfs01/shared/llm_ddd/yuzijie/new/kvlstore.txt"):
        """
        将提取到的 KVL 方程追加到指定文件中
        Args:
            equation_str: KVL 方程字符串
            kvl_file_path: 保存 KVL 方程的文件路径
        """
        try:
            import datetime
            # 获取当前时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(kvl_file_path), exist_ok=True)
            
            # 追加 KVL 方程到文件
            with open(kvl_file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] KVL Equation: {equation_str}\n")
            
            # print(f"[DEBUG] KVL equation saved to {kvl_file_path}: {equation_str}")
            pass
        except Exception as e:
            # print(f"[ERROR] Failed to save KVL equation to file: {e}")
            pass

# Example usage in __main__ would need to be updated to test equations:
# 1. Sample outputs in __main__ should include an "Equations:" section.
# 2. test_identity might need to be augmented if ground truth equations were to be directly compared (not needed for substitution method).
# 3. Calls to verify_score could pass different equation_reward_weight.

if __name__ == '__main__':
    bootcamp = Circuitbootcamp(min_nodes=3, max_nodes=4, seed=42) # Use a fixed seed for consistent tests
    
    # print("--- Test Case Generation and Prompt ---")
    # test_case_identity = bootcamp.case_generator()
    # print("Generated Case:")
    # print(f"  Nodes: {test_case_identity['n_nodes']}")
    # print(f"  Edges: {test_case_identity['edges']}")
    # print(f"  Branch Currents (True): {test_case_identity['branch_currents']}")
    # print(f"  Node Potentials (True): {test_case_identity['node_potentials']}")
    
    # prompt = bootcamp.prompt_func(test_case_identity)
    # # print("\\nGenerated Prompt:\\n", prompt) # Can be very long
    # print("-" * 30)

    # print("\\n--- Test Output Extraction and Scoring ---")

    # Mock model output - Perfect Match including equations
    # For seed 42, n_nodes=3, edges=[(R,E,u,v),...], true_currents, true_potentials
    # Example based on a hypothetical run with seed 42:
    # Nodes: 3
    # Edges: [(7.0, 2.0, 0, 1), (8.0, -10.0, 1, 2)]
    # Branch Currents (True): [-0.5333333333333333, -0.5333333333333333]
    # Node Potentials (True): [0.0, -5.733333333333333, -1.4666666666666661]
    # KCL at Node 1: I_1 - I_2 = 0 (True: -0.533 - (-0.533) = 0)
    # KVL for Loop (0-1-2-0, assuming V_2 -> V_0 is through some implicit path or a more complex KVL):
    # Let's simplify KVL: 7*I_1 - 2 + 8*I_2 - (-10) = V_0 - V_2 = 0 - (-1.466) = 1.466 (This is a path voltage, not a loop)
    # KVL for Loop 0-1-2 and back to 0 (if node 2 is connected to 0):
    # For a simple series: 7*I_1 - 2 + 8*I_2 - (-10) = 0 (if I_1 is current 0->1, I_2 1->2 and ends)
    # True KVL for loop 0-1-2-ref (assuming V2 is grounded directly for simple test):
    # V0 - V1 + V1 - V2 + V2 - V0 = 0
    # (E1 - R1*I1) + (E2 - R2*I2) + V2 = 0 ... this is getting complex for a simple test string.
    # Let's use the model output format:
    
    # Example: I_1 = -0.533, I_2 = -0.533
    # KCL at Node 1: I_1 - I_2 = 0  => -0.533 - (-0.533) = 0. Correct.
    # KVL for Loop 1: 7*I_1 - 2 + 8*I_2 + 10 = 0 => 7*(-0.533) - 2 + 8*(-0.533) + 10 = -3.731 - 2 - 4.264 + 10 = 0.005. Approx Correct.
    
#     perfect_output_str = """
# Equations:
# KCL at Node 1: I_1 - I_2 = 0
# KVL for Loop 1: 7*I_1 - 2 + 8*I_2 + 10 = 0

# Currents:
# I_1 = -0.5333 A
# I_2 = -0.5333 A

# Potentials:
# V_0 = 0.0 V
# V_1 = -5.7333 V
# V_2 = -1.4667 V 
# """
    # Note: The above KVL string is based on the true currents for seed 42 and edges above.
    # test_case_identity for seed=42 as run locally:
    # Nodes: 3
    # Edges: [(7.0, 2.0, 0, 1), (8.0, -10.0, 1, 2)]
    # Branch Currents (True): [-0.5333333333333333, -0.5333333333333333]
    # Node Potentials (True): [0.0, 5.733333333333333, 1.4666666666666661] -- My local run got positive V with current direction.
    # Let's re-verify the true values.
    # If I1 flows 0->1, I2 flows 1->2.
    # KCL at 1: I1 - I2 = 0 => I1 = I2.
    # Loop 0-1-2-ground(implicit from V0=0): (V0-V1) + (V1-V2) + (V2-V0_ref) = 0
    # R1*I1 - E1 + R2*I2 - E2 = 0 (if current defined other way, signs flip)
    # From prompt: "positive current is defined to flow from the first node towards the second node"
    # Edge 1 (0-1): R1=7, E1=2 (E is positive if source's positive terminal is at node 1) => voltage rise from E1 is from 0 to 1.
    # So, for KVL loop 0-1-2-ref-0:
    # -V_R1 + E1 -V_R2 + E2 = 0 => -(7*I1) + 2 -(8*I2) + (-10) = 0
    # -7*I1 - 8*I2 - 8 = 0. Since I1=I2: -15*I1 = 8 => I1 = -8/15 = -0.5333
    # V1 = V0 - (-E1 + R1*I1) = 0 - (-2 + 7*(-8/15)) = 0 - (-2 - 56/15) = 2 + 56/15 = (30+56)/15 = 86/15 = 5.7333
    # V2 = V1 - (-E2 + R2*I2) = 86/15 - (-(-10) + 8*(-8/15)) = 86/15 - (10 - 64/15) = 86/15 - ( (150-64)/15 ) = 86/15 - 86/15 = 0.
    # Ah, if node 2 is the end and V0 is ref, V2 is not necessarily 0 unless specified.
    # The libcircuit.py calculates potentials. Let's use its output directly.
    # For seed=42 (min_nodes=3, max_nodes=3 for consistency):
    # Nodes: 3, Edges: [(R=approx 7, E=approx 2, 0, 1), (R=approx 8, E=approx -10, 1, 2)]
    # True Branch Currents: [-0.5333333333333333, -0.5333333333333333]
    # True Node Potentials: [0.0, 5.733333333333333, 1.4666666666666661]
    # So, perfect_output_str should reflect these:
    # KCL at Node 1: I_1 - I_2 = 0 (Still true: -0.533 - (-0.533) = 0)
    # KVL for Loop (path 0-1-2, voltage relative to V0=0):  -7*I_1 + 2 -8*I_2 -10 - V_2 = 0  (if V2 is end of path) No, this is not a loop equation.
    # A loop equation from libcircuit is usually derived from MNA.
    # Let's make the KVL equation simpler for the test:
    # For edge 1 (0-1): V1 - V0 = -R1*I1 + E1 => V1 = -7*(-0.5333) + 2 = 3.7331 + 2 = 5.7331. This matches.
    # For edge 2 (1-2): V2 - V1 = -R2*I2 + E2 => V2 = V1 -8*(-0.5333) -10 = 5.7333 + 4.2664 - 10 = -0.0003. This should be 1.466. Calculation diff.
    # The E direction: "positive if the source's positive terminal is at node v". So for u-v, it's a rise of E from u to v.
    # So, V_v - V_u = R*I + E (if I is u->v and R is resistance drop). Or V_v - V_u = -R*I + E (if R*I is voltage drop).
    # Let's use V_drop = R*I. Then V_u - R*I + E = V_v.
    # For edge 0-1 (R1,E1,I1): V0 - R1*I1 + E1 = V1 => 0 - 7*(-0.5333) + 2 = V1 => 3.7331 + 2 = 5.7331. This matches.
    # For edge 1-2 (R2,E2,I2): V1 - R2*I2 + E2 = V2 => 5.7333 - 8*(-0.5333) + (-10) = V2 => 5.7333 + 4.2664 - 10 = -0.0003. This still doesn't match 1.466.
    # The internal solver is correct. The equations written by hand for testing are tricky.
    # Let's assume the model provides an equation that SHOULD be true with the true currents.

    # Updated perfect_output_str based on seed 42's true values from a local libcircuit run:
    # True Branch Currents: [-0.5333333333333333, -0.5333333333333333]
    # True Node Potentials: [0.0, 5.733333333333333, 1.4666666666666661]
    # KCL @ Node 1: I_1 - I_2 = 0
    # KVL Example (0-1-2-gnd and then use potentials): V0-R1*I1+E1-R2*I2+E2-V2_true = 0 (if V2_true refers to potential at node 2 relative to gnd)
    # (0) - 7*(-0.53333) + (2) - 8*(-0.53333) + (-10) - (1.46666) = 3.73331 + 2 + 4.26664 - 10 - 1.46666 = 10 - 10 - 1.46666 = -1.46666 != 0
    # This is hard. Let's use simpler placeholder equations for testing the eval logic itself.
    
#     test_identity_main = {
#         'branch_currents': [0.0, 1.7763568394002506e-16, 1.9737298215558337e-16, -3.9474596431116675e-16],
#         'node_potentials': [0.0, 5.0, 18.999999999999996, 14.999999999999998, 17.0],
#         'n_nodes': 5,
#         'edges': [[1, 5, 0, 1], [10, 10, 1, 3], [9, 4, 3, 2], [9, -2, 2, 4]] # Not strictly needed for equation eval if coeffs are in string
#     }

#     perfect_output_str_eq_test = """
# Let's solve the circuit step by step.\n\n### Step 1: Analyze the Circuit Structure\nThe circuit has 5 nodes (0, 1, 2, 3, 4) and 4 edges with resistors and voltage sources. We need to identify the independent loops and nodes.\n\n### Step 2: Formulate Equations using Kirchhoff's Laws\n\n#### Assign Branch Currents\nLet's assign the following branch currents:\n- \\( I_1 \\) for Edge 1 (0-1)\n- \\( I_2 \\) for Edge 2 (1-3)\n- \\( I_3 \\) for Edge 3 (3-2)\n- \\( I_4 \\) for Edge 4 (2-4)\n\n#### Kirchhoff's Current Law (KCL)\nWe need to apply KCL at nodes 1, 2, and 3 (since node 0 is the reference node and has no current flowing into or out of it).\n\n**KCL at Node 1:**\n\\[ I_1 = I_2 + I_5 \\]\nwhere \\( I_5 \\) is the current through the path from node 1 to node 4 (which we need to find).\n\n**KCL at Node 2:**\n\\[ I_5 = I_3 + I_4 \\]\n\n**KCL at Node 3:**\n\\[ I_2 = I_3 \\]\n\n#### Kirchhoff's Voltage Law (KVL)\nWe need to apply KVL around the independent loops. Let's define two loops:\n- Loop 1: 0-1-3-2-4\n- Loop 2: 0-1-3-2\n\n**KVL for Loop 1:**\n\\[ E_1 - R_1 I_1 + E_2 - R_2 I_2 + R_3 I_3 + R_4 I_4 = 0 \\]\n\\[ 5 - 1 I_1 + 10 - 10 I_2 + 9 I_3 + 9 I_4 = 0 \\]\n\\[ 15 - I_1 - 10 I_2 + 9 I_3 + 9 I_4 = 0 \\]\n\n**KVL for Loop 2:**\n\\[ E_1 - R_1 I_1 + E_2 - R_2 I_2 + R_3 I_3 = 0 \\]\n\\[ 5 - 1 I_1 + 10 - 10 I_2 + 9 I_3 = 0 \\]\n\\[ 15 - I_1 - 10 I_2 + 9 I_3 = 0 \\]\n\n### Step 3: Solve the System of Equations\n\nWe have the following system of equations:\n1. \\( I_1 = I_2 + I_5 \\)\n2. \\( I_5 = I_3 + I_4 \\)\n3. \\( I_2 = I_3 \\)\n4. \\( 15 - I_1 - 10 I_2 + 9 I_3 + 9 I_4 = 0 \\)\n5. \\( 15 - I_1 - 10 I_2 + 9 I_3 = 0 \\)\n\nFrom equations 2 and 3:\n\\[ I_5 = I_3 + I_4 \\]\n\\[ I_2 = I_3 \\]\n\nSubstitute \\( I_2 = I_3 \\) into the other equations:\n1. \\( I_1 = I_3 + I_5 \\)\n2. \\( I_5 = I_3 + I_4 \\)\n3. \\( 15 - I_1 - I_3 + 9 I_4 = 0 \\)\n4. \\( 15 - I_1 - I_3 = 0 \\)\n\nSimplify the equations:\n1. \\( I_1 = I_3 + I_5 \\)\n2. \\( I_5 = I_3 + I_4 \\)\n3. \\( 15 - I_1 - I_3 + 9 I_4 = 0 \\)\n4. \\( 15 - I_1 - I_3 = 0 \\)\n\nFrom equation 4:\n\\[ I_1 = 15 - I_3 \\]\n\nSubstitute \\( I_1 = 15 - I_3 \\) into equation 3:\n\\[ 15 - (15 - I_3) - I_3 + 9 I_4 = 0 \\]\n\\[ 0 + 9 I_4 = 0 \\]\n\\[ I_4 = 0 \\]\n\nNow substitute \\( I_4 = 0 \\) into equation 2:\n\\[ I_5 = I_3 + 0 \\]\n\\[ I_5 = I_3 \\]\n\nSubstitute \\( I_5 = I_3 \\) into equation 1:\n\\[ I_1 = I_3 + I_3 \\]\n\\[ I_1 = 2 I_3 \\]\n\nFrom equation 4:\n\\[ I_1 = 15 - I_3 \\]\n\\[ 2 I_3 = 15 - I_3 \\]\n\\[ 3 I_3 = 15 \\]\n\\[ I_3 = 5 \\]\n\nNow we can find the other currents:\n\\[ I_1 = 2 I_3 = 2 \\times 5 = 10 \\]\n\\[ I_2 = I_3 = 5 \\]\n\\[ I_5 = I_3 = 5 \\]\n\n### Step 4: Calculate Node Potentials\n\nUsing the reference node 0 (V_0 = 0 V):\n- Node 1: \\( V_1 = E_1 - R_1 I_1 = 5 - 1 \\times 10 = -5 \\) V\n- Node 2: \\( V_2 = V_1 - R_3 I_3 = -5 - 9 \\times 5 = -50 \\) V\n- Node 3: \\( V_3 = V_2 + E_2 - R_2 I_2 = -50 + 10 - 10 \\times 5 = -100 \\) V\n- Node 4: \\( V_4 = V_2 + R_4 I_4 = -50 + 9 \\times 0 = -50 \\) V\n\n### Final Answers\n\n```\nEquations:\nKCL at Node 1: I_1 = I_2 + I_5\nKCL at Node 2: I_5 = I_3 + I_4\nKCL at Node 3: I_2 = I_3\nKVL for Loop 1: 15 - I_1 - 10 I_2 + 9 I_3 + 9 I_4 = 0\nKVL for Loop 2: 15 - I_1 - 10 I_2 + 9 I_3 = 0\n\nCurrents:\nI_1 = 10 A\nI_2 = 5 A\nI_3 = 5 A\nI_4 = 0 A\n\nPotentials:\nV_0 = 0 V\nV_1 = -5 V\nV_2 = -50 V\nV_3 = -100 V\nV_4 = -50 V\n```\n\nThese are the currents and potentials for the given circuit.
# """


    # test_identity_main = {"n_nodes": 6, "edges": [[4, -7, 5, 0], [8, -3, 0, 2], [6, 6, 2, 4], [5, 3, 4, 1], [1, 8, 1, 3], [1, -2, 4, 5], [9, 8, 5, 2]], "branch_currents": [-0.7058823529411766, -0.7058823529411764, 0.35294117647058826, -1.0658141036401502e-15, 0.0, 0.35294117647058876, 1.0588235294117647], "node_potentials": [0.0, 9.529411764705888, 2.6470588235294117, 17.529411764705888, 6.529411764705882, 4.1764705882352935]}
    test_identity_main = {"n_nodes": 6, "edges": [[5, -10, 4, 2], [1, 8, 2, 3], [1, 10, 3, 5], [7, 7, 5, 0], [7, 1, 0, 1], [1, 8, 5, 1], [6, 0, 0, 4]], "branch_currents": [0.8964143426294833, 0.8964143426294786, 0.8964143426294804, 0.4780876494023896, -0.4183266932270909, 0.41832669322709126, 0.8964143426294827], "node_potentials": [0.0, 3.928286852589636, -19.860557768924313, -12.756972111553791, -5.3784860557768965, -3.6533864541832726]}

#     perfect_output_str_eq_test = """
# Let's solve the circuit step by step.\n\n### Step 1: Analyze the Circuit Structure\nThe circuit has 6 nodes (0 to 5) and 7 edges. We need to identify the independent loops and nodes.\n\n### Step 2: Formulate Equations using Kirchhoff's Laws with Branch Currents as Unknowns\n\n#### Assign Branch Currents\nLet's assign branch currents as follows:\n- \\( I_1 \\) for Edge 1 (5-0)\n- \\( I_2 \\) for Edge 2 (0-2)\n- \\( I_3 \\) for Edge 3 (2-4)\n- \\( I_4 \\) for Edge 4 (4-1)\n- \\( I_5 \\) for Edge 5 (1-3)\n- \\( I_6 \\) for Edge 6 (4-5)\n- \\( I_7 \\) for Edge 7 (5-2)\n\n#### Kirchhoff's Current Law (KCL)\nWe need to write KCL equations at nodes 1, 2, 3, 4, and 5 (since node 0 is the reference node with \\( V_0 = 0 \\) V).\n\n**KCL at Node 1:**\n\\[ I_2 + I_4 - I_5 = 0 \\]\n\n**KCL at Node 2:**\n\\[ I_1 + I_7 - I_3 = 0 \\]\n\n**KCL at Node 3:**\n\\[ I_5 - I_7 = 0 \\]\n\n**KCL at Node 4:**\n\\[ I_3 + I_6 - I_4 = 0 \\]\n\n**KCL at Node 5:**\n\\[ I_1 - I_6 - I_7 = 0 \\]\n\n#### Kirchhoff's Voltage Law (KVL)\nWe need to write KVL equations for the independent loops. We can choose loops 1, 2, and 3 as independent loops.\n\n**KVL for Loop 1 (5-0-2-4-5):**\n\\[ -7.00 + 4.00I_1 + 6.00I_3 + 1.00I_6 + 8.00I_7 = 0 \\]\n\n**KVL for Loop 2 (0-2-4-1-0):**\n\\[ 3.00 - 8.00I_2 + 6.00I_3 + 5.00I_4 - 1.00I_5 = 0 \\]\n\n**KVL for Loop 3 (1-3-5-2-1):**\n\\[ 8.00 - 1.00I_5 + 8.00I_7 - 9.00I_2 + 1.00I_6 = 0 \\]\n\n### Step 3: Solve the System of Equations\n\nWe have the following system of linear equations:\n\n1. \\( I_2 + I_4 - I_5 = 0 \\)\n2. \\( I_1 + I_7 - I_3 = 0 \\)\n3. \\( I_5 - I_7 = 0 \\)\n4. \\( I_3 + I_6 - I_4 = 0 \\)\n5. \\( I_1 - I_6 - I_7 = 0 \\)\n6. \\( -7.00 + 4.00I_1 + 6.00I_3 + 1.00I_6 + 8.00I_7 = 0 \\)\n7. \\( 3.00 - 8.00I_2 + 6.00I_3 + 5.00I_4 - 1.00I_5 = 0 \\)\n8. \\( 8.00 - 1.00I_5 + 8.00I_7 - 9.00I_2 + 1.00I_6 = 0 \\)\n\nFrom equations 3 and 5, we can express \\( I_5 \\) and \\( I_7 \\) in terms of \\( I_1 \\) and \\( I_2 \\):\n\n\\[ I_5 = I_7 \\]\n\\[ I_1 = I_6 + I_7 \\]\n\nSubstitute \\( I_5 = I_7 \\) and \\( I_1 = I_6 + I_7 \\) into the other equations:\n\n1. \\( I_2 + I_4 - I_7 = 0 \\)\n2. \\( (I_6 + I_7) + I_7 - I_3 = 0 \\)\n3. \\( I_3 + I_6 - I_4 = 0 \\)\n4. \\( (I_6 + I_7) - I_6 - I_7 = 0 \\) (This simplifies to 0 = 0, which is always true and doesn't provide new information)\n5. \\( -7.00 + 5.00I_6 + 14.00I_7 + 6.00I_3 = 0 \\)\n6. \\( 3.00 - 8.00I_2 + 6.00I_3 + 5.00I_4 - I_7 = 0 \\)\n7. \\( 8.00 - I_7 + 8.00I_7 - 9.00I_2 + I_6 = 0 \\)\n\nSimplify and solve the system:\n\n1. \\( I_2 + I_4 - I_7 = 0 \\)\n2. \\( I_6 + 2I_7 - I_3 = 0 \\)\n3. \\( I_3 + I_6 - I_4 = 0 \\)\n4. \\( -7.00 + 5.00I_6 + 14.00I_7 + 6.00I_3 = 0 \\)\n5. \\( 3.00 - 8.00I_2 + 6.00I_3 + 5.00I_4 - I_7 = 0 \\)\n6. \\( 8.00 - I_7 + 8.00I_7 - 9.00I_2 + I_6 = 0 \\)\n\nSolving these equations, we get:\n\n\\[ I_1 = 1.00 \\, \\text{A} \\]\n\\[ I_2 = 0.50 \\, \\text{A} \\]\n\\[ I_3 = 1.50 \\, \\text{A} \\]\n\\[ I_4 = 0.50 \\, \\text{A} \\]\n\\[ I_5 = 1.50 \\, \\text{A} \\]\n\\[ I_6 = 0.50 \\, \\text{A} \\]\n\\[ I_7 = 1.50 \\, \\text{A} \\]\n\n### Step 4: Calculate Node Potentials\n\nUsing the branch currents, we can calculate the node potentials:\n\n**Node 1:**\n\\[ V_1 = V_0 + I_2 \\cdot R_2 + I_5 \\cdot R_5 = 0 + 0.50 \\cdot 8.00 + 1.50 \\cdot 1.00 = 4.50 \\, \\text{V} \\]\n\n**Node 2:**\n\\[ V_2 = V_0 + I_1 \\cdot R_1 + I_7 \\cdot R_7 = 0 + 1.00 \\cdot 4.00 + 1.50 \\cdot 9.00 = 19.50 \\, \\text{V} \\]\n\n**Node 3:**\n\\[ V_3 = V_0 + I_5 \\cdot R_5 + I_7 \\cdot R_7 = 0 + 1.50 \\cdot 1.00 + 1.50 \\cdot 8.00 = 13.50 \\, \\text{V} \\]\n\n**Node 4:**\n\\[ V_4 = V_0 + I_3 \\cdot R_3 + I_6 \\cdot R_6 = 0 + 1.50 \\cdot 6.00 + 0.50 \\cdot 5.00 = 10.50 \\, \\text{V} \\]\n\n**Node 5:**\n\\[ V_5 = V_0 + I_1 \\cdot R_1 + I_6 \\cdot R_6 + I_7 \\cdot R_7 = 0 + 1.00 \\cdot 4.00 + 0.50 \\cdot 1.00 + 1.50 \\cdot 8.00 = 19.50 \\, \\text{V} \\]\n\n### Step 5: Output the Final Answers\n\n```\nEquations:\nKCL at Node 0: I_2 + I_4 - I_5 = 0\nKCL at Node 1: I_2 + I_4 - I_5 = 0\nKCL at Node 2: I_1 + I_7 - I_3 = 0\nKCL at Node 3: I_5 - I_7 = 0\nKCL at Node 4: I_3 + I_6 - I_4 = 0\nKCL at Node 5: I_1 - I_6 - I_7 = 0\nKVL for Loop 1: -7.00 + 4.00I_1 + 6.00I_3 + 1.00I_6 + 8.00I_7 = 0\nKVL for Loop 2: 3.00 - 8.00I_2 + 6.00I_3 + 5.00I_4 - 1.00I_5 = 0\nKVL for Loop 3: 8.00 - 1.00I_5 + 8.00I_7 - 9.00I_2 + 1.00I_6 = 0\n\nCurrents:\nI_1 = 1.00 A\nI_2 = 0.50 A\nI_3 = 1.50 A\nI_4 = 0.50 A\nI_5 = 1.50 A\nI_6 = 0.50 A\nI_7 = 1.50 A\n\nPotentials:\nV_0 = 0 V\nV_1 = 4.50 V\nV_2 = 19.50 V\nV_3 = 13.50 V\nV_4 = 10.50 V\nV_5 = 19.50 V\n```\n\nThis completes the solution for the given circuit.
# """
#     perfect_output_str_eq_test = """
# Let's start by analyzing the circuit structure and formulating the equations using Kirchhoff's laws.

# ### Circuit Structure
# The circuit has 6 nodes (0 to 5) and 7 edges. We need to identify the independent loops and apply Kirchhoff's laws.

# ### Kirchhoff's Current Law (KCL)
# We will apply KCL at nodes 1, 2, 3, 4, and 5 (since node 0 is the reference node).

# #### KCL at Node 0:
# \[ I_1 + I_2 = I_7 \]

# #### KCL at Node 1:
# \[ I_4 = I_5 \]

# #### KCL at Node 2:
# \[ I_7 - I_2 = I_3 \]

# #### KCL at Node 3:
# \[ I_5 = 0 \]

# #### KCL at Node 4:
# \[ I_3 = I_4 + I_6 \]

# #### KCL at Node 5:
# \[ I_7 + I_6 = I_1 \]

# ### Kirchhoff's Voltage Law (KVL)
# We will identify the independent loops and apply KVL.

# #### Loop 1 (5-0-2-5):
# \[ -7 + 4I_1 + 8I_2 - 8I_7 = 0 \]

# #### Loop 2 (0-2-4-0):
# \[ -3 + 8I_2 - 6I_3 + 3I_4 = 0 \]

# #### Loop 3 (2-4-5-2):
# \[ 6I_3 + 3I_4 - 1I_6 + 8I_7 - 2 = 0 \]

# #### Loop 4 (4-1-3-4):
# \[ 3I_4 - 1I_5 + 8 - 2 = 0 \]

# ### Simplify the Equations
# From KCL at Node 3:
# \[ I_5 = 0 \]

# This simplifies Loop 4:
# \[ 3I_4 - 2 = 0 \implies I_4 = \frac{2}{3} \text{ A} \]

# Using \( I_4 = \frac{2}{3} \) in KCL at Node 1:
# \[ I_5 = I_4 = \frac{2}{3} \text{ A} \]

# Using \( I_4 = \frac{2}{3} \) in KCL at Node 4:
# \[ I_3 = I_4 + I_6 \implies I_3 = \frac{2}{3} + I_6 \]

# Using \( I_4 = \frac{2}{3} \) in Loop 2:
# \[ -3 + 8I_2 - 6\left(\frac{2}{3} + I_6\right) + 3\left(\frac{2}{3}\right) = 0 \implies -3 + 8I_2 - 4 - 6I_6 + 2 = 0 \implies 8I_2 - 6I_6 = 5 \]

# Using \( I_4 = \frac{2}{3} \) in Loop 3:
# \[ 6\left(\frac{2}{3} + I_6\right) + 3\left(\frac{2}{3}\right) - I_6 + 8I_7 - 2 = 0 \implies 4 + 6I_6 + 2 - I_6 + 8I_7 - 2 = 0 \implies 4 + 5I_6 + 8I_7 = 0 \implies 5I_6 + 8I_7 = -4 \]

# From KCL at Node 0:
# \[ I_1 + I_2 = I_7 \implies I_7 = I_1 + I_2 \]

# From Loop 1:
# \[ -7 + 4I_1 + 8I_2 - 8(I_1 + I_2) = 0 \implies -7 + 4I_1 + 8I_2 - 8I_1 - 8I_2 = 0 \implies -7 - 4I_1 = 0 \implies I_1 = -\frac{7}{4} \text{ A} \]

# Using \( I_1 = -\frac{7}{4} \) in KCL at Node 0:
# \[ I_7 = -\frac{7}{4} + I_2 \]

# Using \( I_7 = -\frac{7}{4} + I_2 \) in Loop 3:
# \[ 5I_6 + 8\left(-\frac{7}{4} + I_2\right) = -4 \implies 5I_6 - 14 + 8I_2 = -4 \implies 5I_6 + 8I_2 = 10 \]

# Solving the system of equations:
# \[ 8I_2 - 6I_6 = 5 \]
# \[ 5I_6 + 8I_2 = 10 \]

# From these, we get:
# \[ I_6 = -\frac{5}{14} \text{ A}, \quad I_2 = \frac{10}{14} = \frac{5}{7} \text{ A} \]

# Finally, we can find all currents and voltages.

# ### Final Answer
# ```
# Equations:
# KCL at Node 0: I_1 + I_2 = I_7
# KCL at Node 1: I_4 = I_5
# KCL at Node 2: I_7 - I_2 = I_3
# KCL at Node 3: I_5 = 0
# KCL at Node 4: I_3 = I_4 + I_6
# KCL at Node 5: I_7 + I_6 = I_1

# KVL Loop 1: -I_6*6 + I_5*4 + I_3*3 + I_5*4 + I_4*4 = 0
# KVL for Loop 2: -3 + 8I_2 - 6I_3 + 3I_4 = 0
# KVL for Loop 3: 6I_3 + 3I_4 - I_6 + 8I_7 - 2 = 0
# KVL for Loop 4: 3I_4 - I_5 + 8 - 2 = 0

# ```
# """

#     perfect_output_str_eq_test = """
# To solve the given problem, we need to apply Kirchhoff's Current Law (KCL) and Kirchhoff's Voltage Law (KVL) to formulate the necessary equations. Let's follow the step-by-step instructions.

# ### Step 1: Analyze the Circuit Structure
# The circuit has 4 nodes labeled 0 to 3. The edges and their properties are as follows:
# - Edge 1: R=1.00 Ω, E=-7.00 V, in branch 0-1 (from node 0 to node 1)
# - Edge 2: R=7.00 Ω, E=-2.00 V, in branch 1-2 (from node 1 to node 2)
# - Edge 3: R=4.00 Ω, E=-4.00 V, in branch 2-3 (from node 2 to node 3)
# - Edge 4: R=5.00 Ω, E=-5.00 V, in branch 3-1 (from node 3 to node 1)

# ### Step 2: Formulate Equations using Kirchhoff's Laws

# #### KCL Equations:
# - Node 1 (Currents entering and leaving node 1):
#   \[
#   I_1 - I_2 - I_4 = 0
#   \]

# - Node 2 (Currents entering and leaving node 2):
#   \[
#   I_2 - I_3 = 0
#   \]

# #### KVL Equations:
# - Loop 1: Traversing around the loop 0-1-2-3-1 (clockwise):
#   \[
#   -E_1 + R_1 \cdot I_1 + E_2 - R_2 \cdot I_2 + E_4 - R_4 \cdot I_4 = 0
#   \]
#   Substituting the values:
#   \[
#   7 + 1 \cdot I_1 + 2 - 7 \cdot I_2 - 5 - 5 \cdot I_4 = 0
#   \]
#   Simplifying:
#   \[
#   4 + I_1 - 7I_2 - 5I_4 = 0
#   \]

# - Loop 2: Traversing around the loop 2-3-1-2 (clockwise):
#   \[
#   -E_2 + R_2 \cdot I_2 + E_3 - R_3 \cdot I_3 + E_4 - R_4 \cdot I_4 = 0
#   \]
#   Substituting the values:
#   \[
#   2 - 7 \cdot I_2 + 4 - 4 \cdot I_3 - 5 - 5 \cdot I_4 = 0
#   \]
#   Simplifying:
#   \[
#   1 - 7I_2 - 4I_3 - 5I_4 = 0
#   \]

# ### Step 3: Output the Equations

# ```
# Equations:
# KCL at Node 1: I_1 - I_2 - I_4 = 0
# KCL at Node 2: I_2 - I_3 = 0
# KVL for Loop 1: 4 + I_1 - 7I_2 - 5I_4 = 0
# KVL for Loop 2: 1 - 7I_2 - 4I_3 - 5I_4 = 0
# ```




# These are the equations formulated based on Kirchhoff's Laws for the given circuit.
# """

# 偷懒没说kvl 的版本如下

    perfect_output_str_eq_test = """
Let's analyze the circuit and then apply Kirchhoff's Laws to formulate the equations.

### Step 1: Analyze the Circuit Structure

The circuit has 6 nodes (0, 1, 2, 3, 4, 5) and the following edges:

- Edge 1: R=5.00 Ohm, E=-10.00 V, from node 4 to node 2
- Edge 2: R=1.00 Ohm, E=8.00 V, from node 2 to node 3
- Edge 3: R=1.00 Ohm, E=10.00 V, from node 3 to node 5
- Edge 4: R=7.00 Ohm, E=7.00 V, from node 5 to node 0
- Edge 5: R=7.00 Ohm, E=1.00 V, from node 0 to node 1
- Edge 6: R=1.00 Ohm, E=8.00 V, from node 5 to node 1
- Edge 7: R=6.00 Ohm, E=0.00 V, from node 0 to node 4

### Step 2: Formulate Equations using Kirchhoff's Laws

#### Assigning Branch Current Variables

Let:
- \( I_1 \) be the current through Edge 1 (from node 4 to node 2)
- \( I_2 \) be the current through Edge 2 (from node 2 to node 3)
- \( I_3 \) be the current through Edge 3 (from node 3 to node 5)
- \( I_4 \) be the current through Edge 4 (from node 5 to node 0)
- \( I_5 \) be the current through Edge 5 (from node 0 to node 1)
- \( I_6 \) be the current through Edge 6 (from node 5 to node 1)
- \( I_7 \) be the current through Edge 7 (from node 0 to node 4)

#### Applying Kirchhoff's Current Law (KCL) at each node

- **Node 0:**
  \[
  I_4 - I_5 - I_7 = 0
  \]

- **Node 1:**
  \[
  I_5 + I_6 = 0
  \]

- **Node 2:**
  \[
  I_1 - I_2 = 0
  \]

- **Node 3:**
  \[
  I_2 - I_3 = 0
  \]

- **Node 4:**
  \[
  I_7 - I_1 = 0
  \]

### Step 3: Output the Equations

```
Equations:
KCL at Node 0: I_4 - I_5 - I_7 = 0
KCL at Node 1: I_5 + I_6 = 0
KCL at Node 2: I_1 - I_2 = 0
KCL at Node 3: I_2 - I_3 = 0
KCL at Node 4: I_7 - I_1 = 0
KVL for Loop 1: I_5 + I_6 + I_4 = 0
KVL for Loop 2: I_5 + I_6  = 0
```

These are the equations based on the given circuit and Kirchhoff's Laws.
"""
    print(f"Testing with perfect output:")
    score = bootcamp.verify_score(perfect_output_str_eq_test, test_identity_main, equation_reward_weight=1)
    print(f"  Score: {score}") # Expect 1.0

#     partial_output_str_eq_test = """
# Equations:
# KCL at Node 1: I_1 + I_2 = 0          // False: 1 + (-2) = -1 != 0
# KVL for LoopX: 2*I_1 - I_3 + 1.0001 = 0 // Approx True: 2-3+1.0001 = 0.0001
# Currents:
# I_1 = 1.0 A
# I_2 = -1.999 A # Almost correct for I_2
# // I_3 missing
# Potentials:
# V_0 = 0.0 V
# V_1 = 5.01 V # Almost correct for V_1
# // V_2, V_3 missing
# """
#     # Variables: I1 (correct), I2 (correct), I3 (missing, count as 1 var) -> 2/3 correct for currents with values
#     # V0 (correct), V1 (correct), V2 (missing), V3 (missing) -> 2/4 correct for potentials
#     # Total vars correct: 2+2=4. Total vars expected: 3+4=7. Var_ratio = 4/7
#     # Equations: Eq1 (False), Eq2 (True) -> 1/2 correct. Eq_ratio = 0.5
#     # Score = 0.7 * (4/7) + 0.3 * (0.5) = 0.7 * 0.5714 + 0.3 * 0.5 = 0.4 + 0.15 = 0.55
#     print(f"Testing with partial output (eq_weight=0.3):")
#     score = bootcamp.verify_score(partial_output_str_eq_test, test_identity_main, equation_reward_weight=0.3)
#     print(f"  Score: {score}") # Expect approx 0.55

#     only_equations_correct_str = """
# Equations:
# KCL at Node 1: I_1 + I_2 + 1 = 0
# KVL for LoopX: 2*I_1 - I_3 + 1 = 0
# Currents:
# I_1 = 100 A
# Potentials:
# V_0 = 0 V
# """
#     # Variables: I1(F), I2(M), I3(M) -> 0/3. V0(T), V1(M), V2(M), V3(M) -> 1/4. Var_ratio = 1/7
#     # Equations: Eq1(T), Eq2(T) -> 2/2 = 1.0. Eq_ratio = 1.0
#     # Score = 0.7 * (1/7) + 0.3 * (1.0) = 0.7 * 0.1428 + 0.3 = 0.09996 + 0.3 = ~0.40
#     print(f"Testing with only equations mostly correct (eq_weight=0.3):")
#     score = bootcamp.verify_score(only_equations_correct_str, test_identity_main, equation_reward_weight=0.3)
#     print(f"  Score: {score}") # Expect approx 0.40
    
#     bad_format_output_str = "This is not parseable."
#     print(f"Testing with bad format (eq_weight=0.3):")
#     score = bootcamp.verify_score(bad_format_output_str, test_identity_main, equation_reward_weight=0.3)
#     print(f"  Score: {score}") # Expect 0.0 (score_min)

    print("\\nCircuit bootcamp tests with equation scoring complete.")