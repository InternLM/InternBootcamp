## Description
Given an undirected graph, the Maximum Clique Problem aims to find a subset of vertices (a clique) where every two distinct vertices in the clique are adjacent (i.e., connected by an edge), and the clique is as large as possible.

## Submission Format
The answer should specify the vertices in the maximum clique. The answer should be in the following format: `[0, 1, 2, 3]`. Note that:
1. All vertices in the set must be distinct
2. Every pair of vertices in the set must be connected by an edge in the original graph
3. The set should be as large as possible

## Example Input
```
{
"0": {"1": 1, "2": 1, "3": 1},
"1": {"0": 1, "2": 1, "3": 1},
"2": {"0": 1, "1": 1, "3": 1},
"3": {"0": 1, "1": 1, "2": 1, "4": 1},
"4": {"3": 1}
}
```

## Example Output
```
Answer: [0, 1, 2, 3]
```
