## Description
Given a weighted undirected graph, the **Balanced Minimum Bisection Problem** aims to partition the graph into two disjoint subsets of **equal size** (or differing by at most one node if the number of nodes is odd), such that the sum of the weights of the edges between the two subsets is minimized.  

This problem differs from the classic Minimum Cut Problem because of the **balance constraint**: both subsets must contain the same number of nodes (or differ by at most one). To solve this problem, start with a feasible solution and then iteratively optimize it by reducing the size of the cut, ensuring that the solution remains valid at each step. Continue this process until the smallest valid cut is obtained.

## Submission Format
The answer should specify the two balanced subsets of nodes separated by the minimum cut. The answer should be in the following format: [[0, 1, 2], [3, 4, 5]].  Note that:  
1. The two subsets must be disjoint and together contain all nodes in the graph  
2. The number of nodes in each subset must be equal (or differ by at most one)  
3. The order of the subsets and the order of nodes within each subset does not matter  

## Example Input
```
0: {1: 3, 2: 1}
1: {0: 3, 2: 2, 3: 2}
2: {0: 1, 1: 2, 3: 3}
3: {1: 2, 2: 3}
```
## Example Output
```
Answer: [[0, 1], [2, 3]]
```
