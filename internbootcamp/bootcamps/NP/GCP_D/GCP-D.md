## Description
Given an undirected graph G = （V, E）, where V is a set of vertices and E is a set of edges, the Graph Coloring Problem (GCP) asks whether it is possible to assign colors to the vertices such that no two adjacent vertices share the same color. The goal is to use the minimum number of colors necessary to achieve a valid coloring. 

To solve this problem, start with a feasible solution and then optimize it by gradually reducing the number of colors, ensuring the solution remains valid at each step. Continue this process until the smallest valid coloring is achieved.

## Submission Format
The answer should be a list of integers, where each integer represents the color assigned to the corresponding vertex in the graph. The list should be indexed starting from vertex 0. The number assigned to each vertex indicates the color assigned to that vertex, and the colors should be represented by integer values. The output should be in the following format (as an example): [1, 2, 1, 2]. The example output list means that Vertex 0 is assigned color 1. Vertex 1 is assigned color 2. Vertex 2 is assigned color 1. Vertex 3 is assigned color 2. The colors are represented by integers (bigger than 0), where each vertex receives a distinct integer color, ensuring no adjacent vertices share the same color.

## Example Input

```
0: [1, 2]
1: [0, 3]
2: [0, 3]
3: [1, 2]
```
## Example Output
```
Answer: [1, 2, 1, 2]
```
