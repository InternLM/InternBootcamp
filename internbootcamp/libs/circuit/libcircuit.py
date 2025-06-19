import numpy as np
import random
import math

class CoreCircuit:
    """
    Encapsulates the core logic for circuit generation and solving.
    """

    @staticmethod
    def generate_random_graph_edges(n_nodes: int, seed: int | None = None) -> list:
        """
        Generates a list of edges for a random graph with n_nodes.
        Each edge is (R, E, u, v).
        Ensures the graph is connected if n_nodes > 1.
        Seedable for reproducibility.
        """
        # print(f"[DEBUG libcircuit] generate_random_graph_edges called with n_nodes={n_nodes}, seed={seed}")
        if seed is not None:
            np.random.seed(seed)
            # print(f"[DEBUG libcircuit] NumPy random seed set to {seed}")

        if n_nodes == 0:
            # print("[DEBUG libcircuit] n_nodes is 0, returning []")
            return []
        if n_nodes == 1:
            # print("[DEBUG libcircuit] n_nodes is 1, returning []")
            return [] # No edges for a single node typically in circuit problems unless specified

        edges = []
        min_r_int, max_r_int = 1, 10 # Changed to int
        min_e_int, max_e_int = -10, 10 # Changed to int

        # Ensure connectivity for n_nodes > 1 using a spanning tree (line graph)
        nodes = list(range(n_nodes))
        np.random.shuffle(nodes) # Shuffle to make the spanning tree random
        for i in range(n_nodes - 1):
            u, v = nodes[i], nodes[i+1]
            R = np.random.randint(min_r_int, max_r_int + 1) # Generate integer R
            E = np.random.randint(min_e_int, max_e_int + 1) # Generate integer E
            edges.append((R, E, u, v))
        
        # print(f"[DEBUG libcircuit] Edges after spanning tree: {len(edges)}")

        max_possible_edges = n_nodes * (n_nodes -1) // 2
        # print(f"[DEBUG libcircuit] max_possible_edges: {max_possible_edges}")

        if n_nodes > 2:
            num_additional_edges_max = max(0, min(int(n_nodes * 0.5), max_possible_edges - (n_nodes - 1)))
            # print(f"[DEBUG libcircuit] num_additional_edges_max: {num_additional_edges_max}")
            
            num_target_additional_edges = 0
            if num_additional_edges_max > 0:
                num_target_additional_edges = np.random.randint(2, num_additional_edges_max + 1)
            # print(f"[DEBUG libcircuit] num_target_additional_edges: {num_target_additional_edges}")

            existing_pairs = set()
            for _, _, u, v in edges:
                existing_pairs.add(tuple(sorted((u,v))))

            successfully_added_edges = 0
            max_attempts_per_edge = n_nodes * n_nodes # A relatively loose attempt limit

            if num_target_additional_edges > 0:
                # print(f"[DEBUG libcircuit] Attempting to add {num_target_additional_edges} additional edges.")
                for i in range(num_target_additional_edges):
                    if len(existing_pairs) >= max_possible_edges:
                        # print("[DEBUG libcircuit] Graph is full, cannot add more edges.")
                        break # Graph is full

                    current_attempts = 0
                    added_this_iteration = False
                    while current_attempts < max_attempts_per_edge:
                        u, v = np.random.choice(range(n_nodes), 2, replace=False)
                        if tuple(sorted((u, v))) not in existing_pairs:
                            R = np.random.randint(min_r_int, max_r_int + 1) # Generate integer R
                            E = np.random.randint(min_e_int, max_e_int + 1) # Generate integer E
                            edges.append((R, E, u, v))
                            existing_pairs.add(tuple(sorted((u, v))))
                            successfully_added_edges += 1
                            added_this_iteration = True
                            # print(f"[DEBUG libcircuit] Successfully added additional edge #{successfully_added_edges} (target {i+1}/{num_target_additional_edges}). Total edges: {len(edges)}")
                            break # Successfully added, break from while
                        current_attempts += 1
                    
                    if not added_this_iteration:
                        # print(f"[DEBUG libcircuit] Failed to add additional edge target {i+1}/{num_target_additional_edges} after {max_attempts_per_edge} attempts.")
                        # Optional: log a warning if an edge couldn't be added despite many attempts
                        # print(f"Warning: Could not add target additional edge after {max_attempts_per_edge} attempts.")
                        # break # Stop trying to add more additional edges if one attempt fails badly
                        pass
            else:
                # print("[DEBUG libcircuit] num_target_additional_edges is 0, no additional edges will be attempted.")
                pass
            
            # print(f"[DEBUG libcircuit] Total successfully_added_edges: {successfully_added_edges}")
        else:
            # print("[DEBUG libcircuit] n_nodes is not > 2, skipping additional edge logic.")
            pass
        
        # print(f"[DEBUG libcircuit] Returning {len(edges)} edges.")
        return edges

    @staticmethod
    def solve_circuit_potentials_and_currents(n_nodes: int, edges: list, seed: int | None = None):
        """
        Solves a circuit using MNA to find all node potentials (node 0 as reference)
        and all branch currents.
        Args:
            n_nodes (int): Number of nodes in the circuit.
            edges (list): List of edges, where each edge is a tuple (R, E, u, v).
                          R: resistance, E: EMF (+ terminal at v), u: start node, v: end node.
            seed (int, optional): Not used in this deterministic calculation, but kept for API consistency.
        Returns:
            tuple: (branch_currents, node_potentials)
                   branch_currents (list[float] | None): List of currents for each edge in the input 'edges' list.
                                                       Positive current flows from u to v as defined by the edge tuple.
                   node_potentials (list[float] | None): List of potentials for each node (0 to n_nodes-1).
                                                       node_potentials[0] is always 0.0.
                   Returns (None, None) if the circuit is unsolvable or invalid.
        """
        if seed is not None:
            # np.random.seed(seed) # Not strictly needed for np.linalg.solve
            pass # Seed is not used in this deterministic MNA solver

        if n_nodes < 1:
            return None, None

        # Validate edges: R > 0 and valid node indices
        for R_val, _, u_node, v_node in edges:
            if R_val <= 0: # Resistances must be positive for this MNA formulation
                return None, None
            if not (0 <= u_node < n_nodes and 0 <= v_node < n_nodes):
                return None, None # Invalid node indices

        if n_nodes == 1:
            # Only node 0 exists, its potential is 0.
            node_potentials = [0.0]
            branch_currents = []
            for R_k, E_k, u_k, v_k in edges:
                # For n_nodes=1, valid edges must be (0,0) due to above validation
                if u_k == 0 and v_k == 0: # Edge from node 0 to node 0
                    # Current I = (V0 - V0 + E_k) / R_k = E_k / R_k
                    branch_currents.append(E_k / R_k)
                # else: This path should not be reachable if validation is correct
            return branch_currents, node_potentials

        ref_node = 0
        num_voltage_vars = n_nodes - 1 # We solve for V_1, ..., V_{n_nodes-1}

        # If there are no unknown potentials (e.g. n_nodes=1 already handled, but for safety if num_voltage_vars becomes 0)
        if num_voltage_vars == 0: # Should be covered by n_nodes == 1 case
            all_node_potentials_trivial = [0.0] * n_nodes # all_node_potentials[0] = 0
            branch_currents_trivial = []
            for R_k, E_k, u_k, v_k in edges:
                V_u_k = all_node_potentials_trivial[u_k]
                V_v_k = all_node_potentials_trivial[v_k]
                current_k = (V_u_k - V_v_k + E_k) / R_k
                branch_currents_trivial.append(current_k)
            return branch_currents_trivial, all_node_potentials_trivial

        M = np.zeros((num_voltage_vars, num_voltage_vars))
        Z = np.zeros(num_voltage_vars)

        # Populate MNA matrices based on KCL
        # For an edge (u,v) with R_uv, E_uv (+ at v):
        # Current I_uv = (V_u - V_v + E_uv) / R_uv
        # This can be seen as (V_u - V_v)/R_uv + E_uv/R_uv
        # The term E_uv/R_uv is an equivalent current source from u to v.
        for R, E_uv, u, v in edges: 
            g = 1.0 / R
            J_eq = E_uv * g # Equivalent current source from u to v due to E_uv

            # Matrix indices map from node numbers (1 to n_nodes-1) to (0 to n_nodes-2)
            if u != ref_node:
                u_idx = u - 1 # Node u (if not ref) corresponds to (u-1)-th unknown potential V_u
                M[u_idx, u_idx] += g
                Z[u_idx] -= J_eq # J_eq flows out of node u, hence negative on RHS of KCL sum_Ig = sum_Is
            
            if v != ref_node:
                v_idx = v - 1 # Node v (if not ref) corresponds to (v-1)-th unknown potential V_v
                M[v_idx, v_idx] += g
                Z[v_idx] += J_eq # J_eq flows into node v, hence positive on RHS

            if u != ref_node and v != ref_node:
                u_idx = u - 1
                v_idx = v - 1
                M[u_idx, v_idx] -= g
                M[v_idx, u_idx] -= g
        
        # Solve for unknown node potentials (V_1 to V_{n_nodes-1})
        solved_potentials_unknowns = np.zeros(num_voltage_vars)
        try:
            solved_potentials_unknowns = np.linalg.solve(M, Z)
            if np.any(np.isnan(solved_potentials_unknowns)) or np.any(np.isinf(solved_potentials_unknowns)):
                return None, None # Unstable solution
        except np.linalg.LinAlgError: # e.g. singular matrix if circuit is ill-defined
            return None, None
        
        # Construct full list of node potentials (V_0 to V_{n_nodes-1})
        all_node_potentials = [0.0] * n_nodes # V_0 (all_node_potentials[0]) is 0.0 by definition
        for i in range(num_voltage_vars):
            all_node_potentials[i + 1] = solved_potentials_unknowns[i] # V_1, V_2 ...

        # Calculate branch currents using solved potentials
        branch_currents = []
        for R_k, E_k, u_k, v_k in edges: # E_k is EMF, positive if + terminal at v_k
            V_u_k = all_node_potentials[u_k]
            V_v_k = all_node_potentials[v_k]
            # Current I_k from u_k to v_k is (V_u_k - V_v_k + E_k) / R_k
            current_k = (V_u_k - V_v_k + E_k) / R_k
            branch_currents.append(current_k)
            
        return branch_currents, all_node_potentials
