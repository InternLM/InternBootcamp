import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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




class CircuitInstructionGenerator(BaseInstructionGenerator):
    """Circuit Bootcamp指令生成器"""
    
    def __init__(self, min_nodes=3, max_nodes=6, seed=None):
        """
        初始化Circuit指令生成器
        
        Args:
            min_nodes: 参数描述
            max_nodes: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
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
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _parse_and_eval_equation(eq_str: str, true_branch_currents: List[Optional[float]], atol: float = 1e-2, rtol: float = 1e-3) -> bool:
        # # print(f"[DEBUG _parse_and_eval_equation] Evaluating equation: '{eq_str}' with currents: {true_branch_currents}")
        if "=" not in eq_str:
            # print("[DEBUG _parse_and_eval_equation] No '=' found in equation string.")
            return False

        lhs_str, rhs_str = eq_str.split('=', 1)
        # # print(f"[DEBUG _parse_and_eval_equation] LHS string: '{lhs_str}', RHS string: '{rhs_str}'")

        # Create a very limited scope for eval
        # Only allow math constants and functions that don't interact with system
        safe_globals = {"__builtins__": {}}
        # Whitelist specific math functions if necessary, e.g. abs, sqrt, etc.
        # For basic KCL/KVL, direct arithmetic should be fine.
        # safe_locals = {name: getattr(math, name) for name in dir(math) if callable(getattr(math, name))}
        # safe_locals.update({'abs': abs}) # Example
        safe_locals = {'abs': abs}


        def evaluate_side(side_str: str, true_branch_currents: List[Optional[float]]) -> Optional[float]:
            # # print(f"[DEBUG evaluate_side] Evaluating side: '{side_str}'")
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
            # # print(f"[DEBUG evaluate_side] Found current variables: {current_vars}")

            for idx_str in current_vars:
                current_idx = int(idx_str)
                # # print(f"[DEBUG evaluate_side] Attempting to substitute I_{current_idx}")
                if 0 < current_idx <= len(true_branch_currents):
                    val = true_branch_currents[current_idx - 1]
                    if val is None:
                        # print(f"[DEBUG evaluate_side] Current I_{current_idx} value is None. Cannot evaluate.")
                        return None  # Cannot evaluate if a current is None
                    # Ensure substitution is for the whole variable name, e.g. I_1 not I_10
                    original_substituted_side_str = substituted_side_str
                    substituted_side_str = re.sub(r'\bI_' + idx_str + r'\b', f"({str(val)})", substituted_side_str)
                    # # print(f"[DEBUG evaluate_side] Substituting I_{idx_str} with ({str(val)}). Before: '{original_substituted_side_str}', After: '{substituted_side_str}'")
                else:
                    # print(f"[DEBUG evaluate_side] Warning: Current index I_{idx_str} out of bounds for true_branch_currents (len {len(true_branch_currents)})")
                    return None  # Current index out of bounds

            # Check for any remaining alphabetic characters (potential unreplaced variables or forbidden functions)
            # Allows 'e' or 'E' for scientific notation.
            remaining_vars_match = re.search(r'[a-df-zA-DF-Z]', substituted_side_str) # Check for letters other than e/E
            if remaining_vars_match:
                # # print(f"[DEBUG evaluate_side] Warning: Expression '{substituted_side_str}' contains unhandled variables or functions (e.g., '{remaining_vars_match.group(0)}') after substitution.")
                return None
            else:
                # # print(f"[DEBUG evaluate_side] No unhandled variables found in '{substituted_side_str}'.")
                pass

            try:
                # # print(f"[DEBUG evaluate_side] Attempting to eval: '{substituted_side_str}'")
                # Evaluate the expression string.
                value = eval(substituted_side_str, safe_globals, safe_locals)
                # # print(f"[DEBUG evaluate_side] Eval result for '{substituted_side_str}': {value}")
                return float(value)
            except Exception as e:
                # print(f"[DEBUG evaluate_side] Error evaluating expression side '{substituted_side_str}': {e}")
                return None

        lhs_val = evaluate_side(lhs_str, true_branch_currents)
        rhs_val = evaluate_side(rhs_str, true_branch_currents)

        # # print(f"[DEBUG _parse_and_eval_equation] LHS evaluated value: {lhs_val}, RHS evaluated value: {rhs_val}")

        if lhs_val is not None and rhs_val is not None:
            is_close = np.isclose(lhs_val, rhs_val, atol=atol, rtol=rtol)
            # # print(f"[DEBUG _parse_and_eval_equation] Comparison np.isclose({lhs_val}, {rhs_val}) results in: {is_close}")
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
        # # print(f"[DEBUG _evaluate_expression_for_coeffs] Evaluating expr: '{expr_str}' with I_values: {current_values}")
        substituted_expr_str = expr_str

        # Apply implicit multiplication rules
        substituted_expr_str = Circuitbootcamp._apply_implicit_multiplication(substituted_expr_str)
        # # print(f"[DEBUG _evaluate_expression_for_coeffs] After implicit multiplication: '{substituted_expr_str}'")

        # Substitute I_k variables from highest index to lowest to avoid issues like I_10 vs I_1
        for i in range(num_total_currents, 0, -1):
            val_to_sub = current_values[i-1]
            # Wrap in parentheses for safety, especially for negative numbers
            substituted_expr_str = re.sub(r'\bI_' + str(i) + r'\b', f"({str(val_to_sub)})", substituted_expr_str)

        # # print(f"[DEBUG _evaluate_expression_for_coeffs] After substituting I_k: '{substituted_expr_str}'")

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
            # # print(f"[DEBUG _evaluate_expression_for_coeffs] Eval result for '{substituted_expr_str}': {value}")
            return float(value)
        except Exception as e:
            # print(f"[DEBUG _evaluate_expression_for_coeffs] Error evaluating expression '{substituted_expr_str}': {e}")
            return None

    @staticmethod
    def _get_equation_coefficients(eq_str: str, num_branch_currents: int) -> Optional[List[float]]:
        # # print(f"[DEBUG _get_equation_coefficients] Processing eq: '{eq_str}' for {num_branch_currents} current variables")
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
                # # print(f"[DEBUG _get_equation_coefficients] Eq with no currents: '{eq_str}', const_term = {lhs_val - rhs_val}")
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
        # # print(f"[DEBUG _get_equation_coefficients] Standardized expr: '{expression_str}'")

        coeffs = [0.0] * (num_branch_currents + 1) # +1 for the constant term

        # Calculate constant term (value of expression when all I_k = 0)
        all_currents_zero = [0.0] * num_branch_currents
        constant_term = Circuitbootcamp._evaluate_expression_for_coeffs(expression_str, all_currents_zero, num_branch_currents)
        if constant_term is None:
            # print(f"[DEBUG _get_equation_coefficients] Failed to evaluate constant term for: {expression_str}")
            return None
        coeffs[num_branch_currents] = constant_term
        # # print(f"[DEBUG _get_equation_coefficients] Constant term = {constant_term}")

        # Calculate coefficient for each I_k
        for k_idx in range(num_branch_currents): # k_idx from 0 to num_branch_currents-1
            current_values_Ik_one = [0.0] * num_branch_currents
            current_values_Ik_one[k_idx] = 1.0

            val_Ik_one = Circuitbootcamp._evaluate_expression_for_coeffs(expression_str, current_values_Ik_one, num_branch_currents)
            if val_Ik_one is None:
                # # print(f"[DEBUG _get_equation_coefficients] Failed to evaluate for I_{k_idx+1}=1 for: {expression_str}")
                return None

            # Coefficient of I_k is (Value of expr with I_k=1, others=0) - (Value of expr with all I_k=0, i.e. constant_term)
            coeffs[k_idx] = val_Ik_one - constant_term
            # # print(f"[DEBUG _get_equation_coefficients] Coeff for I_{k_idx+1} = {val_Ik_one} - {constant_term} = {coeffs[k_idx]}")

        # # print(f"[DEBUG _get_equation_coefficients] Successfully extracted coeffs for '{eq_str}': {coeffs}")
        return coeffs

    @staticmethod
    def _normalize_solution(solution):
        """
        The solution is expected to be a float or None after extract_output.
        No further normalization usually needed.
        """
        return solution

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
        # # print(f"\\n[DEBUG verify_score] --- Starting Verification ---")
        # # print(f"[DEBUG verify_score] model_output (first 300 chars):\n'''{model_output[:300]}...'''")
        # # print(f"[DEBUG verify_score] identity: {identity}") # Can be verbose

        if model_output is None or not model_output.strip():
            # print(f"[DEBUG verify_score] Model output is None or empty. Returning score_min: {score_min}")
            # print(f"[DEBUG verify_score] Model output is None or empty. Returning score_min: {score_min}")
            return score_min

        if not (0 <= equation_reward_weight <= 1.0):
            # print(f"[DEBUG verify_score] Invalid equation_reward_weight: {equation_reward_weight}. Using 1.0 as default.")
            # print(f"[DEBUG verify_score] Invalid equation_reward_weight: {equation_reward_weight}. Using 1.0 as default.")
            equation_reward_weight = 1.0 

        extracted_currents, extracted_potentials, extracted_equations = cls.extract_output(model_output)
        # # print(f"[DEBUG verify_score] Extracted Currents: {extracted_currents}")
        # # print(f"[DEBUG verify_score] Extracted Potentials: {extracted_potentials}")
        # # print(f"[DEBUG verify_score] Extracted Equations: {extracted_equations}")

        # --- Score for Currents and Potentials ---
        correct_vars_count = 0
        total_vars_count = 0

        expected_currents = identity.get('branch_currents')
        expected_potentials = identity.get('node_potentials')
        # # print(f"[DEBUG verify_score] Expected Currents: {expected_currents}")
        # # print(f"[DEBUG verify_score] Expected Potentials: {expected_potentials}")

        if expected_currents is not None:
            num_currents_to_compare = len(expected_currents)
            total_vars_count += num_currents_to_compare
            # # print(f"[DEBUG verify_score] Comparing {num_currents_to_compare} expected currents.")
            if extracted_currents is not None and len(extracted_currents) > 0 :
                for i in range(num_currents_to_compare):
                    is_correct = False
                    if i < len(extracted_currents) and extracted_currents[i] is not None and expected_currents[i] is not None:
                        if np.isclose(extracted_currents[i], expected_currents[i], atol=atol, rtol=rtol):
                            correct_vars_count += 1
                            is_correct = True
                    val_extracted = extracted_currents[i] if i < len(extracted_currents) else 'N/A'
                    # print(f"[DEBUG verify_score] Current I_{i+1}: Expected={expected_currents[i]}, Extracted={val_extracted}, Correct={is_correct}")
                    # print(f"[DEBUG verify_score] Current I_{i+1}: Expected={expected_currents[i]}, Extracted={val_extracted}, Correct={is_correct}")
            else:
                # # print(f"[DEBUG verify_score] Extracted currents are None or empty, all {num_currents_to_compare} expected currents count as incorrect.")
                pass

        if expected_potentials is not None:
            num_potentials_to_compare = len(expected_potentials)
            total_vars_count += num_potentials_to_compare
            # # print(f"[DEBUG verify_score] Comparing {num_potentials_to_compare} expected potentials.")
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
                    # print(f"[DEBUG verify_score] Potential V_{i}: Expected={expected_val}, Extracted={val_extracted}, Correct={is_correct}")
            else:
                # # print(f"[DEBUG verify_score] Extracted potentials are None or empty, all {num_potentials_to_compare} expected potentials count as incorrect.")
                pass
        current_potential_score_ratio = 0.0
        if total_vars_count > 0:
            current_potential_score_ratio = correct_vars_count / total_vars_count
        # # print(f"[DEBUG verify_score] Correct Vars: {correct_vars_count}, Total Vars: {total_vars_count}, Var Ratio: {current_potential_score_ratio:.4f}")

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
    def _save_kvl_equation_to_file(equation_str: str):
        """
        将提取到的 KVL 方程追加到指定文件中
        Args:
            equation_str: KVL 方程字符串
            kvl_file_path: 保存 KVL 方程的文件路径
        """
        # try:
        #     import datetime
        #     # 获取当前时间戳
        #     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #     # 确保目录存在
        #     os.makedirs(os.path.dirname(kvl_file_path), exist_ok=True)

        #     # 追加 KVL 方程到文件
        #     with open(kvl_file_path, 'a', encoding='utf-8') as f:
        #         f.write(f"[{timestamp}] KVL Equation: {equation_str}\n")

        #     # print(f"[DEBUG] KVL equation saved to {kvl_file_path}: {equation_str}")
        #     pass
        # except Exception as e:
        #     # print(f"[ERROR] Failed to save KVL equation to file: {e}")
        #     pass
        pass
