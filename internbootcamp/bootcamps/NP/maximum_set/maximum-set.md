## Description
Given an undirected graph, the Maximum Independent Set Problem aims to find the largest set of vertices where no two vertices are adjacent (i.e., no two vertices in the set share an edge).

## Submission Format
The answer should specify the vertices in the maximum independent set. The answer should be in the following format: `[0, 3, 5, 7]`. Note that:
1. All vertices in the set must be distinct
2. No two vertices in the set can be adjacent in the original graph
3. The set should be as large as possible

## Example Input
```
{
"0": {"1": 1, "2": 1},
"1": {"0": 1, "2": 1, "3": 1},
"2": {"0": 1, "1": 1, "3": 1},
"3": {"1": 1, "2": 1}
}
```

## Example Output
```
Answer: [0, 3]
```
