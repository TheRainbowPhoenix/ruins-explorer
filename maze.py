import random

class MazeBuilder:
    def __init__(self, width, height, seed=None, items_count=5):
        # logical cell dimensions
        self.width = width
        self.height = height
        # overall grid dimensions
        self.cols = 2 * width + 1
        self.rows = 2 * height + 1

        # reproducible randomness
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        # how many random items to place
        self.items_count = items_count

        # initialize tag grid for walls, doors, etc.
        self.maze = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

        # build outer and cell-grid walls
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    self.maze[r][c] = ['wall']
                elif r % 2 == 0 and c % 2 == 0:
                    self.maze[r][c] = ['wall']

        # place entrance (start) and exit (goal) doors
        top = self.pos_to_space(random.randint(1, self.width))
        bot = self.pos_to_space(random.randint(1, self.width))
        self.maze[self.rows - 1][bot] = ['door', 'entrance']
        self.maze[0][top]      = ['door', 'exit']

        # carve interior partitions recursively
        self.partition(1, self.height - 1, 1, self.width - 1)

    def pos_to_space(self, x):
        return 2 * (x - 1) + 1

    def pos_to_wall(self, x):
        return 2 * x

    def partition(self, r1, r2, c1, c2):
        if r2 < r1 or c2 < c1:
            return

        # select horizontal divider
        if r1 == r2:
            horiz = r1
        else:
            a, b = r1 + 1, r2 - 1
            start = a + (b - a) // 4
            end   = a + 3 * (b - a) // 4
            horiz = random.randint(start, end)

        # select vertical divider
        if c1 == c2:
            vert = c1
        else:
            a, b = c1 + 1, c2 - 1
            start = a + (b - a) // 3
            end   = a + 2 * (b - a) // 3
            vert = random.randint(start, end)

        w_row = self.pos_to_wall(horiz)
        w_col = self.pos_to_wall(vert)

        # draw walls
        for j in range(self.pos_to_wall(c1) - 1, self.pos_to_wall(c2) + 2):
            if 0 <= w_row < self.rows and 0 <= j < self.cols:
                self.maze[w_row][j] = ['wall']
        for i in range(self.pos_to_wall(r1) - 1, self.pos_to_wall(r2) + 2):
            if 0 <= i < self.rows and 0 <= w_col < self.cols:
                self.maze[i][w_col] = ['wall']

        # Fisher–Yates shuffle four gap indices
        gaps = [0, 1, 2, 3]
        for i in range(len(gaps) - 1, 0, -1):
            j = random.randint(0, i)
            gaps[i], gaps[j] = gaps[j], gaps[i]

        # open exactly three gaps
        for gap in gaps[:3]:
            if gap == 0:
                gp = random.randint(c1, vert)
                self.maze[w_row][self.pos_to_space(gp)] = []
            elif gap == 1:
                gp = random.randint(vert + 1, c2 + 1)
                self.maze[w_row][self.pos_to_space(gp)] = []
            elif gap == 2:
                gp = random.randint(r1, horiz)
                self.maze[self.pos_to_space(gp)][w_col] = []
            elif gap == 3:
                gp = random.randint(horiz + 1, r2 + 1)
                self.maze[self.pos_to_space(gp)][w_col] = []

        # recurse into four subareas
        self.partition(r1,     horiz - 1, c1,     vert - 1)
        self.partition(horiz + 1, r2,     c1,     vert - 1)
        self.partition(r1,     horiz - 1, vert + 1, c2)
        self.partition(horiz + 1, r2,     vert + 1, c2)

    def build(self):
        """
        Generate the maze and place key + random items.

        Returns:
          grid       : 2D list of ints (1=wall, 0=open)
          start      : (row, col) of entrance
          goal       : (row, col) of exit
          key_pos    : (row, col) of key
          item_pos   : list of (row, col) for each random item
        """
        # convert to binary grid
        grid = [[1 if 'wall' in self.maze[r][c] else 0
                 for c in range(self.cols)]
                for r in range(self.rows)]

        # identify start and goal
        start = goal = None
        for r in range(self.rows):
            for c in range(self.cols):
                if 'entrance' in self.maze[r][c]:
                    start = (r, c)
                if 'exit' in self.maze[r][c]:
                    goal = (r, c)

        # collect all open cells except start/goal
        open_cells = [ (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if grid[r][c] == 0 and (r,c) not in (start, goal) ]

        # shuffle and pick key + items
        random.shuffle(open_cells)
        key_pos  = open_cells.pop()  # last of shuffled
        item_pos = [ open_cells[i] for i in range(min(self.items_count, len(open_cells))) ]

        return grid, start, goal, key_pos, item_pos

# Demo
if __name__ == '__main__':
    seed = 42
    m = MazeBuilder(10, 6, seed=seed, items_count=5)
    grid, start, goal, key, items = m.build()
    print('Start:', start, 'Goal:', goal)
    print('Key:', key)
    print('Items:', items)
    for r, row in enumerate(grid):
        line = ''
        for c, v in enumerate(row):
            if (r, c) == start:
                line += 'S '
            elif (r, c) == goal:
                line += 'G '
            elif (r, c) == key:
                line += 'K '
            elif (r, c) in items:
                line += 'I '
            else:
                line += '██' if v else '  '
        print(line)
