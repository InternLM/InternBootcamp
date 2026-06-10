## Description

Given a universal set U and a collection of subsets S, the Set Cover Problem aims to find the smallest possible sub-collection of S whose union equals U.  In other words, we want to select the fewest subsets from S such that every element in U is contained in at least one of the selected subsets.

## Submission Format

The answer should be a list of subset IDs representing the selected sub-collection. The order of the IDs does not matter.  If no solution exists (i.e., the union of all subsets in S does not cover U), return "Impossible".


## Example Input
```
U = {0, 1, 2, 3, 4, 5}
S = {
0: {0, 1, 2},
1: {2, 3},
2: {0, 4},
3: {3, 4, 5},
4: {1, 2, 5}
}
```

## Example Output
```
Answer: [0, 3, 4]
```
