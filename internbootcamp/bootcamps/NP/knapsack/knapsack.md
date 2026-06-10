## Description
The knapsack problem's goal is to choose a subset of items to pack into a limited-capacity bag in a way that maximizes total value without exceeding the weight limit.

Given a set of items—each with a weight **w**<sub>*i*</sub> and a value **v**<sub>*i*</sub>—and a knapsack that can carry at most **W** total weight, choose a subset of items whose total weight is **≤ W** and whose total value is as large as possible.

## Submission Format
Return an ordered list of **item IDs** in square brackets (no duplicates):

```
[0, 3, 5]
```

The listed items must exist, and their combined weight must be **≤ W**.

---

## Example Input
```
{
  "capacity": 20,
  "items": {
    "0": {"weight": 3, "value": 4},
    "1": {"weight": 4, "value": 5},
    "2": {"weight": 7, "value": 10},
    "3": {"weight": 8, "value": 11}
  }
}
```

## Example Output
```
Answer: [0, 2, 3]
```
Item 2 alone weighs 7 ≤ 10 and yields the maximum value, 10.
