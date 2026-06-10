# Introduction to NP Tasks
The folder structure you provided contains ten classic **NP (Nondeterministic Polynomial-time)** tasks, each representing a fundamental challenge in the field of **computational complexity theory** — a branch of **theoretical computer science** that studies the inherent difficulty of computational problems. NP problems are central to understanding what computers can efficiently solve and form the foundation of algorithmic science, optimization, and artificial intelligence.

<div align="center">
 <img src="./images/data.png" width="800"/>
</div>

## 🧠 What Are NP Tasks?

An **NP problem** is one whose proposed solution can be *verified* in polynomial time, even if finding the solution itself may require exponential time. These problems often arise in real-world applications such as logistics, cryptography, network design, scheduling, and data mining.

The study of NP problems is a cornerstone of **computational science**, **operations research**, and **algorithmic complexity theory**, blending mathematics, computer science, and applied optimization.

---

## 🔬 The Ten NP Tasks in This Repository

| Task | Description | Scientific Domain |
|------|--------------|------------------|
| **Hamiltonian Cycle** | Determine whether a path exists that visits each node exactly once and returns to the start. | Graph theory, combinatorial optimization |
| **Knapsack Problem** | Choose items with maximum total value without exceeding a weight limit. | Optimization, economics, logistics |
| **Maximum Clique Problem** | Find the largest subset of vertices such that every two are connected. | Network science, graph theory |
| **Maximum Set Problem** | Select the largest subset that satisfies given constraints. | Discrete mathematics, set theory |
| **Meeting Schedule** | Allocate time slots and participants to minimize conflicts and maximize efficiency. | Scheduling theory, operations research |
| **Minimum Cut** | Partition a graph into two disjoint subsets minimizing the number of crossing edges. | Network flow theory, computer networks |
| **Set Cover Problem** | Choose the fewest subsets that together cover all elements of a universal set. | Combinatorial optimization, data science |
| **Subset Sum** | Determine whether a subset of numbers sums to a target value. | Number theory, cryptography |
| **Traveling Salesman Problem (TSP)** | Find the shortest route visiting all cities once and returning to the start. | Operations research, route optimization |
| **Graph Coloring (GCP_D)** | Assign colors to nodes so that adjacent nodes have different colors. | Graph theory, scheduling, compiler optimization |

---

## 🧩 Why NP Problems Matter

These NP problems are more than academic exercises — they form a **unified scientific framework** for studying complexity, optimization, and decision-making under constraints. Research in this area explores:
- How to approximate NP-hard problems efficiently.
- When exact solutions are computationally feasible.
- Theoretical limits of computation (e.g., the famous *P vs NP* question).

Thus, NP tasks lie at the intersection of **computer science**, **mathematics**, and **applied systems engineering**, forming a core component of the **science of computation and optimization**.

---

## 👀 Our Results
If you are interested in applying NP tasks to LLM RLVR training, please refer to the
[📃[Paper](http://arxiv.org/abs/2506.10764)]
[🌐[Project Page](https://github.com/OliverLeeXZ/NP-Engine)] for more details.


### Performance on NP Bench.  
| **Model**              | **Graph SR** | **Graph AR** | **Schedule SR** | **Schedule AR** | **Partition SR** | **Partition AR** | **Selection SR** | **Selection AR** | **Planning SR** | **Planning AR** | **Overall SR** | **Overall AR** |
|------------------------|--------------|--------------|-----------------|-----------------|------------------|------------------|------------------|------------------|-----------------|-----------------|----------------|----------------|
| **Proprietary LLMs**    |              |              |                 |                 |                  |                  |                  |                  |                 |                 |                |                |
| DS-V3.1-Thinking        | 86.0         | 78.2         | **99.0**        | 91.4            | 98.0             | **77.1**         | **99.3**         | **98.5**         | 61.9            | 54.3            | 88.8           | **79.9**       |
| gpt-o3                  | **97.0**     | **86.4**     | **99.0**        | **94.5**        | **100.0**        | 51.4             | 87.4             | 87.3             | 74.0            | **65.1**        | 91.5           | 76.9           |
| Qwen3-235B-Thinking     | 66.7         | 62.9         | 95.0            | 93.0            | **100.0**        | 55.8             | 98.0             | 97.1             | 52.0            | 44.8            | 82.3           | 70.7           |
| gpt-4o-2024-08-06      | 64.7         | 29.3         | 79.0            | 59.8            | **100.0**        | 53.0             | 14.7             | 9.3              | 52.0            | 29.6            | 62.1           | 36.2           |
| **Open-Source LLMs**    |              |              |                 |                 |                  |                  |                  |                  |                 |                 |                |                |
| Qwen3-32B               | 44.7         | 39.3         | 94.0            | 93.9            | 99.0             | 52.6             | 94.1             | 91.4             | 21.6            | 11.2            | 70.7           | 57.6           |
| Qwen3-8B                | 22.7         | 16.8         | 78.0            | 75.3            | 98.0             | 51.0             | 86.0             | 82.6             | 3.0             | 1.2             | 57.5           | 45.4           |
| DS-R1-Qwen-32B          | 23.3         | 18.1         | 49.0            | 45.1            | 96.0             | 48.6             | 85.7             | 79.7             | 15.4            | 7.9             | 53.9           | 39.9           |
| DS-R1-Qwen-14B          | 18.0         | 13.4         | 52.0            | 51.7            | 32.0             | 16.2             | 67.3             | 63.4             | 4.5             | 1.4             | 34.8           | 29.2           |
| Qwen2.5-72B             | 34.7         | 15.2         | 59.0            | 58.5            | 90.0             | 39.5             | 27.0             | 17.4             | 6.5             | 2.1             | 43.4           | 26.5           |
| Qwen2.5-32B             | 35.3         | 15.2         | 15.0            | 12.8            | **100.0**        | 51.7             | 32.0             | 22.4             | 23.5            | 6.7             | 41.2           | 21.8           |
| Qwen2.5-14B             | 30.0         | 11.5         | 21.0            | 15.8            | 89.0             | 44.3             | 23.3             | 12.7             | 17.5            | 4.9             | 36.2           | 17.8           |
| InternLM3-8b            | 15.0         | 3.6          | 20.0            | 9.5             | 86.0             | 43.3             | 41.3             | 23.7             | 16.0            | 4.1             | 35.7           | 16.8           |
| LLama3.1-8B             | 23.0         | 8.0          | 9.0             | 7.8             | 0.0              | 0.0              | 28.7             | 11.4             | 15.0            | 1.8             | 15.1           | 5.8            |
| Qwen2.5-3B              | 7.7          | 2.9          | 17.0            | 5.0             | 6.0              | 2.2              | 23.0             | 10.7             | 15.5            | 3.7             | 13.8           | 4.9            |
| DS-R1-Qwen-7B           | 6.3          | 1.9          | 1.0             | 0.9             | 2.0              | 1.0              | 13.7             | 8.9              | 0.5             | 0.1             | 4.7            | 2.5            |
| Qwen2.5-7B              | 11.0         | 3.1          | 40.0            | 19.8            | 67.0             | 34.0             | 26.7             | 15.2             | 3.5             | 1.0             | 29.6           | 14.6           |
| **Qwen2.5-7B-NP**               | **89.7**     | **27.8**     | **85.0**        | 43.5            | **99.0**          | **53.8**         | **93.7**         | **79.1**         | **98.2**         | **28.9**         | **93.1**        | **46.6**        |
| **Delta**               | +78.7        | +24.7        | +45.0           | +23.7           | +32.0            | +19.8            | +67.0            | +63.9            | +94.7            | +27.9            | +63.5           | +32.0           |


### Performance on LLM's General Ability.  

This table shows the performance of various models on out-of-domain benchmarks, spanning both **reasoning** and **non-reasoning** tasks. The results demonstrate that **RLVR training on `NP tasks`** generalizes effectively across multiple categories.

| **Model**          | **Logic**<br>KORBench | **Math**<br>Math500 | **Math**<br>OlpBench | **Knowledge**<br>GPQA_diamond | **Instruction**<br>IFEval | **Average** |
|--------------------|-----------------------|----------------------|----------------------|-------------------------------|----------------------------|-------------|
| LLama3.1-8b        | 44.5                  | 48.6                 | 17.7                 | 22.7                          | 69.3                       | 40.6        |
| Qwen2.5-3B         | 36.6                  | 67.2                 | 29.7                 | 30.3                          | 59.1                       | 44.6        |
| InternLM3-8B       | 40.7                  | 78.2                 | 25.1                 | 36.9                          | 72.5                       | 50.7        |
| Qwen2.5-14B        | 50.6                  | 80.0                 | 45.1                 | 41.9                          | 81.6                       | 59.8        |
| Qwen2.5-32B        | **56.2**              | 82.8                 | 48.8                 | 43.9                          | 79.5                       | 62.3        |
| Qwen2.5-72B        | 53.0                  | **84.2**             | **49.1**             | **46.0**                      | **84.3**                   | **63.3**    |
|                    |                       |                      |                      |                               |                            |             |
| Qwen2.5-7B         | 42.9                  | 72.4                 | 30.0                 | 33.3                          | 73.5                       | 50.4        |
| `\model` (Ours)    | _44.1 (+1.2)_         | _74.6 (+2.2)_        | 32.1 (+2.1)          | _37.4 (+4.1)_                 | _79.6 (+6.1)_              | _53.6 (+3.2)_ |
