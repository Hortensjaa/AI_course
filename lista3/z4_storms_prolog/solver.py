import heapq
from collections import deque
from typing import List, Tuple, FrozenSet


class CommandoSolver:

    def __init__(self, maze: List[str]):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])

        # wyliczam najpierw dostępne komórki
        self.valid = [[False] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                self.valid[r][c] = self.maze[r][c] != '#'

        self.start_points = self._find_start_points()
        self.goal_points = self._find_goal_points()
        self.goal_dist = self._compute_goal_distances()

    def _find_start_points(self) -> List[Tuple[int, int]]:
        result = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] in ("S", "B"):
                    result.append((r, c))
        return result

    def _find_goal_points(self) -> List[Tuple[int, int]]:
        result = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] in ("G", "B"):
                    result.append((r, c))
        return result

    # dla każdego pola zliczam liczbę kroków do najbliższego celu z użyciem bfs
    def _compute_goal_distances(self) -> List[List[int]]:
        dist = [[float('inf')] * self.cols for _ in range(self.rows)]
        q = deque()
        for r, c in self.goal_points:
            dist[r][c] = 0
            q.append((r, c))

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while q:
            r, c = q.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.valid[nr][nc] and dist[nr][nc] == float('inf'):
                        dist[nr][nc] = dist[r][c] + 1
                        q.append((nr, nc))
        return dist

    def solve(self) -> str:
        initial_positions = frozenset(self.start_points)
        # jeśli wszyscy komandosi są na mecie, to wychodzimy
        if all(self.goal_dist[r][c] == 0 for (r, c) in initial_positions):
            return ""
        path = self._find_path(initial_positions)
        return "".join(path)

    def _find_path(self, start: FrozenSet[Tuple[float, float]]) -> List[str]:
        visited = set()
        directions = [("U", -1, 0), ("D", 1, 0), ("L", 0, -1), ("R", 0, 1)]
        counter = 0

        # heurystyka: minimalizujemy odległość najdalszego komandosa do swojego najbliższego punktu
        # najdalszego w sensie długości trasy którą już pokonał + odległości do najbliższego celu z aktualnej pozycji
        # w sensie no ta długość pokonanej jest taka sama dla każdego komandosa w danym stanie XD
        initial_heuristic = max(self.goal_dist[r][c] for (r, c) in start)
        heap = [(initial_heuristic, counter, start, [])]
        heapq.heapify(heap)

        while heap:
            priority, _, current, path = heapq.heappop(heap)

            # warunek końca - wszyscy na mecie
            if all(self.goal_dist[r][c] == 0 for (r, c) in current):
                return path

            # "odwiedzone" stany komandosów
            if current in visited:
                continue
            visited.add(current)

            # kolejne stany w każdym kierunku
            for dir_name, dr, dc in directions:
                new_pos = set()
                for r, c in current:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.valid[nr][nc]:
                        new_pos.add((nr, nc))
                    else:
                        new_pos.add((r, c))
                new_state = frozenset(new_pos)

                if new_state in visited:
                    continue

                # wyliczanie priorytetu
                h = max(self.goal_dist[r][c] for (r, c) in new_state)
                new_cost = len(path) + 1
                new_priority = new_cost + h * 1.1

                counter += 1
                heapq.heappush(heap, (new_priority, counter, new_state, path + [dir_name]))

        return []  # nie ma trasy