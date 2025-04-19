import random

class MazeBuilder:
    def __init__(self, width, height, seed=None):
        # logical cell dimensions
        self.width = width
        self.height = height
        # overall grid dimensions
        self.cols = 2 * width + 1
        self.rows = 2 * height + 1

        # allow reproducible randomness
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        # initialize tag grid
        self.maze = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

        # build outer walls and checkerboard walls
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    self.maze[r][c] = ['wall']
                elif r % 2 == 0 and c % 2 == 0:
                    self.maze[r][c] = ['wall']

        # place entrance (start) and exit (goal)
        top = self.pos_to_space(random.randint(1, self.width))
        bot = self.pos_to_space(random.randint(1, self.width))
        self.maze[self.rows - 1][bot] = ['door', 'entrance']
        self.maze[0][top]      = ['door', 'exit']

        # carve interior partitions
        self.partition(1, self.height - 1, 1, self.width - 1)

    def pos_to_space(self, x):
        return 2 * (x - 1) + 1

    def pos_to_wall(self, x):
        return 2 * x

    def partition(self, r1, r2, c1, c2):
        if r2 < r1 or c2 < c1:
            return

        # choose horizontal divider
        if r1 == r2:
            horiz = r1
        else:
            a, b = r1 + 1, r2 - 1
            start = a + (b - a) // 4
            end   = a + 3 * (b - a) // 4
            horiz = random.randint(start, end)

        # choose vertical divider
        if c1 == c2:
            vert = c1
        else:
            a, b = c1 + 1, c2 - 1
            start = a + (b - a) // 3
            end   = a + 2 * (b - a) // 3
            vert = random.randint(start, end)

        w_row = self.pos_to_wall(horiz)
        w_col = self.pos_to_wall(vert)

        # draw the partition walls
        for j in range(self.pos_to_wall(c1) - 1, self.pos_to_wall(c2) + 2):
            if 0 <= w_row < self.rows and 0 <= j < self.cols:
                self.maze[w_row][j] = ['wall']
        for i in range(self.pos_to_wall(r1) - 1, self.pos_to_wall(r2) + 2):
            if 0 <= i < self.rows and 0 <= w_col < self.cols:
                self.maze[i][w_col] = ['wall']

        # prepare four possible gap directions
        gaps = [0, 1, 2, 3]
        # Fisher–Yates shuffle for in-place randomness
        for i in range(len(gaps) - 1, 0, -1):
            j = random.randint(0, i)
            gaps[i], gaps[j] = gaps[j], gaps[i]

        # open exactly three gaps based on the first three shuffled indices
        for gap in gaps[:3]:
            if gap == 0:
                # gap on horizontal wall, left segment
                gp = random.randint(c1, vert)
                self.maze[w_row][self.pos_to_space(gp)] = []
            elif gap == 1:
                # gap on horizontal wall, right segment
                gp = random.randint(vert + 1, c2 + 1)
                self.maze[w_row][self.pos_to_space(gp)] = []
            elif gap == 2:
                # gap on vertical wall, top segment
                gp = random.randint(r1, horiz)
                self.maze[self.pos_to_space(gp)][w_col] = []
            elif gap == 3:
                # gap on vertical wall, bottom segment
                gp = random.randint(horiz + 1, r2 + 1)
                self.maze[self.pos_to_space(gp)][w_col] = []

        # recurse into sub-chambers
        self.partition(r1,     horiz - 1, c1,     vert - 1)
        self.partition(horiz + 1, r2,     c1,     vert - 1)
        self.partition(r1,     horiz - 1, vert + 1, c2)
        self.partition(horiz + 1, r2,     vert + 1, c2)

    def build(self):
        """
        Produces a 2D list grid and returns:
          grid  : 2D list of ints (1=wall, 0=open)
          start : (row, col) of entrance
          goal  : (row, col) of exit
        """
        grid = [[1 if 'wall' in self.maze[r][c] else 0
                 for c in range(self.cols)]
                for r in range(self.rows)]

        start = goal = None
        for r in range(self.rows):
            for c in range(self.cols):
                if 'entrance' in self.maze[r][c]:
                    start = (r, c)
                if 'exit' in self.maze[r][c]:
                    goal = (r, c)

        return grid, start, goal

# Example usage:
if __name__ == '__main__':
    seed = random.randint(0, 255)
    print('Seed:', seed)
    m = MazeBuilder(10, 10, seed=seed)
    grid1, start1, goal1 = m.build()
    # regenerating with same seed
    m2 = MazeBuilder(10, 10, seed=seed)
    grid2, start2, goal2 = m2.build()
    assert grid1 == grid2 and start1 == start2 and goal1 == goal2
    print('Start:', start1, 'Goal:', goal1)
    for row in grid1:
        print(''.join('██' if cell else '  ' for cell in row))