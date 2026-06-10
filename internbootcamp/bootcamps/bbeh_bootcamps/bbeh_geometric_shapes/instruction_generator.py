import math
import random
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


Point = Tuple[float, float]
Edge = Tuple[Point, Point]


class GeometricShapeCaseBuilder:
    """用于生成几何图形识别任务的题目与答案。"""

    def __init__(
        self,
        distract_density: float = 0.5,
        max_distractors: int = 3,
        seed: int | None = None,
    ) -> None:
        self.distract_density = max(0.0, min(1.0, float(distract_density)))
        self.max_distractors = max(0, int(max_distractors))
        self.rng = random.Random(seed)

    def _uniform(self, low: float, high: float) -> float:
        return self.rng.uniform(low, high)

    def _randint(self, low: int, high: int) -> int:
        return self.rng.randint(low, high)

    def _choice(self, seq: Sequence[Any]) -> Any:
        return self.rng.choice(seq)

    def _random_sign(self) -> int:
        return self._choice([1, -1])

    def generate_rectangle(self) -> List[Point]:
        x = self._uniform(0, 50)
        y = self._uniform(0, 50)
        width = self._uniform(10, 30)
        height = self._uniform(10, 30)
        while abs(width - height) < 5:
            height = self._uniform(10, 30)
        return [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y),
        ]

    def generate_square(self) -> List[Point]:
        x = self._uniform(0, 50)
        y = self._uniform(0, 50)
        size = self._uniform(10, 30)
        return [
            (x, y),
            (x + size, y),
            (x + size, y + size),
            (x, y + size),
            (x, y),
        ]

    def generate_parallelogram(self) -> List[Point]:
        x = self._uniform(0, 50)
        y = self._uniform(0, 50)
        width = self._uniform(10, 30)
        height = self._uniform(10, 30)
        skew = self._uniform(5, 15) * self._random_sign()
        if self.rng.random() < 0.5:
            return [
                (x, y),
                (x + width + skew, y),
                (x + width, y + height),
                (x - skew, y + height),
                (x, y),
            ]
        return [
            (x, y),
            (x, y + width + skew),
            (x + height, y + width),
            (x + height, y - skew),
            (x, y),
        ]

    def generate_triangle(self, non_right: bool = True) -> List[Point]:
        if non_right:
            a = (self._uniform(0, 50), self._uniform(0, 50))
            b = (a[0] + self._uniform(10, 30), a[1])
            c = (a[0] + self._uniform(5, 15), a[1] + self._uniform(10, 30))
            v1 = (b[0] - a[0], b[1] - a[1])
            v2 = (c[0] - a[0], c[1] - a[1])
            if abs(v1[0] * v2[0] + v1[1] * v2[1]) < 1e-6:
                c = (c[0] + 5.0, c[1])
            return [a, b, c, a]

        right_angle_at = self._choice(["a", "b", "c"])
        if right_angle_at == "a":
            a = (self._uniform(-20, 70), self._uniform(-20, 70))
            dx = self._uniform(10, 30) * self._random_sign()
            dy = self._uniform(10, 30) * self._random_sign()
            b = (a[0] + dx, a[1])
            c = (a[0], a[1] + dy)
        elif right_angle_at == "b":
            b = (self._uniform(-20, 70), self._uniform(-20, 70))
            dx = self._uniform(10, 30) * self._random_sign()
            dy = self._uniform(10, 30) * self._random_sign()
            a = (b[0] - dx, b[1])
            c = (b[0], b[1] + dy)
        else:
            c = (self._uniform(-20, 70), self._uniform(-20, 70))
            dx = self._uniform(10, 30) * self._random_sign()
            dy = self._uniform(10, 30) * self._random_sign()
            a = (c[0] - dx, c[1])
            b = (c[0], c[1] - dy)
        return [a, b, c, a]

    def generate_trapezoid(self) -> List[Point]:
        x = self._uniform(0, 50)
        y = self._uniform(0, 50)
        base1 = self._uniform(20, 40)
        base2 = base1 * self._uniform(0.3, 0.7)
        height = self._uniform(15, 30)
        offset = (base1 - base2) * self._uniform(0.4, 0.6)
        if self.rng.random() < 0.5:
            x, y = y, x
        if self.rng.random() < 0.5:
            return [
                (x, y),
                (x + base1, y),
                (x + base1 - offset, y + height),
                (x + offset, y + height),
                (x, y),
            ]
        return [
            (x, y),
            (x, y + base1),
            (x + height, y + base1 - offset),
            (x + height, y + offset),
            (x, y),
        ]

    def generate_regular_polygon(self, sides: int, size: float = 30.0) -> List[Point]:
        radius = size * self._uniform(0.8, 1.2)
        start_angle = self._uniform(0, 2 * math.pi)
        center_x = self._uniform(20, 80)
        center_y = self._uniform(20, 80)
        points: List[Point] = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides + start_angle
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        points.append(points[0])
        return points

    def generate_irregular_convex_pentagon(self) -> List[Point]:
        angles = [i * 72 + self._uniform(-15, 15) for i in range(5)]
        points: List[Point] = []
        for angle in angles:
            r = self._uniform(20, 35)
            x = 50 + r * math.cos(math.radians(angle))
            y = 50 + r * math.sin(math.radians(angle))
            points.append((x, y))
        points.append(points[0])
        return points

    def generate_irregular_concave_pentagon(self) -> List[Point]:
        convex = self.generate_irregular_convex_pentagon()[:-1]
        idx = self._randint(0, 4)
        centroid_x = sum(p[0] for p in convex) / 5
        centroid_y = sum(p[1] for p in convex) / 5
        new_x = convex[idx][0] + 1.5 * (centroid_x - convex[idx][0])
        new_y = convex[idx][1] + 1.5 * (centroid_y - convex[idx][1])
        convex[idx] = (new_x, new_y)
        convex.append(convex[0])
        return convex

    def split_segment(self, a: Point, b: Point, num_splits: int = 1) -> List[Point]:
        points = [a]
        for _ in range(num_splits):
            t = self._uniform(0.2, 0.8)
            x = a[0] + t * (b[0] - a[0])
            y = a[1] + t * (b[1] - a[1])
            points.append((x, y))
        points.append(b)
        return points

    def select_shape(self, target: int) -> List[Point]:
        if target == 1:
            return self.generate_rectangle()
        if target == 2:
            return self.generate_square()
        if target in (3, 4):
            return self.generate_triangle(non_right=(target == 3))
        if target == 5:
            return self.generate_parallelogram()
        if target == 6:
            return self.generate_trapezoid()
        if target == 7:
            return self.generate_irregular_convex_pentagon()
        if target == 8:
            return self.generate_irregular_concave_pentagon()
        if target == 9:
            return self.generate_regular_polygon(5)
        if target == 10:
            return self.generate_regular_polygon(6)
        raise ValueError(f"Unsupported target index: {target}")

    def _build_edges(self, points: Iterable[Point]) -> List[Edge]:
        points_list = list(points)
        edges: List[Edge] = []
        for idx in range(len(points_list) - 1):
            a, b = points_list[idx], points_list[idx + 1]
            splits = self._randint(0, 2)
            split_pts = self.split_segment(a, b, splits)
            for j in range(len(split_pts) - 1):
                edges.append((split_pts[j], split_pts[j + 1]))
        return edges

    def _add_distractors(self, edges: List[Edge]) -> None:
        if self.max_distractors <= 0:
            return
        if self.rng.random() >= self.distract_density:
            return
        num_distractors = self._randint(1, self.max_distractors)
        for _ in range(num_distractors):
            x1 = self._uniform(-10, 60)
            y1 = self._uniform(-10, 60)
            x2 = self._uniform(-10, 60)
            y2 = self._uniform(-10, 60)
            edges.append(((x1, y1), (x2, y2)))

    def _edges_to_svg_path(self, edges: Sequence[Edge]) -> str:
        commands: List[str] = []
        for start, end in edges:
            commands.append(f"M {start[0]:.5f},{start[1]:.5f} L {end[0]:.5f},{end[1]:.5f}")
        return " ".join(commands)

    def generate_case(self) -> Dict[str, Any]:
        target = self._randint(1, 10)
        shape_points = self.select_shape(target)
        edges = self._build_edges(shape_points)
        self._add_distractors(edges)
        svg_path = self._edges_to_svg_path(edges)
        return {
            "Paths": svg_path,
            "ans": str(target),
        }

    @staticmethod
    def construct_prompt(identity: Dict[str, Any]) -> str:
        svg_path = identity.get("Paths", "")
        intro = f"Suppose we draw this SVG path element:{svg_path} ."
        options = (
            "Out of the following shapes:\n"
            "1. rectangle that is not a square and with no diagonals drawn\n"
            "2. square with no diagonals drawn\n"
            "3. triangle that is not a right triangle\n"
            "4. right triangle\n"
            "5. parallelogram that is not a rectangle and with no diagonals drawn\n"
            "6. trapezoid with exactly one pair of parallel sides and with no diagonals drawn\n"
            "7. irregular convex pentagon with no diagonals drawn\n"
            "8. irregular concave pentagon with no diagonals drawn\n"
            "9. regular pentagon with no diagonals drawn\n"
            "10. regular hexagon with no diagonals drawn\n"
            "which one can be viewed when the lines in the SVG are visualized? "
            "Note that a shape with n sides should not necessarily be drawn by n lines; "
            "e.g., a triangle might be drawn by 4 lines, two of which collinear. \n"
            "Coordinates have been rounded to 5 decimal places so ignore slight differences. "
            "Solve this problem step by step and provide the final answer within \\boxed{}. "
            'For example: "Final Answer: \\boxed{3}." '
        )
        return intro + options


class BbehGeometricShapesInstructionGenerator(BaseInstructionGenerator):
    """BBEH 几何图形识别任务的指令生成器。"""

    def __init__(
        self,
        distract_density: float = 0.5,
        max_distractors: int = 3,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.case_builder = GeometricShapeCaseBuilder(
            distract_density=distract_density,
            max_distractors=max_distractors,
            seed=seed,
        )

    def case_generator(self) -> Dict[str, Any]:
        return self.case_builder.generate_case()

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        return self.case_builder.construct_prompt(identity)


