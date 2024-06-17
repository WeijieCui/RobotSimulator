import tkinter as tk
from tkinter.filedialog import askopenfilename

from routing import Router


class Robot:
    """Robot class with basic movement functions."""
    DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']

    def __init__(self):
        """initialize robot with default position and direction."""
        self.x = 0
        self.y = 0
        self.step = 0
        self.direction = 'EAST'

    def place(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def left(self):
        d = self.direction
        index = (self.DIRECTIONS.index(self.direction) - 1) % 4
        self.direction = self.DIRECTIONS[index]
        print('{}->left->{}'.format(d, self.direction))

    def right(self):
        d = self.direction
        index = (self.DIRECTIONS.index(self.direction) + 1) % 4
        self.direction = self.DIRECTIONS[index]
        print('{}->right->{}'.format(d, self.direction))

    def move(self):
        x, y = self.x, self.y
        if self.direction == 'NORTH':
            self.y += 1
        elif self.direction == 'EAST':
            self.x += 1
        elif self.direction == 'SOUTH':
            self.y -= 1
        elif self.direction == 'WEST':
            self.x -= 1
        print('({},{})->({},{})'.format(x, y, self.x, self.y))


class RobotGUI(Robot):
    def __init__(self, width=5, height=5):
        """initialize robot with grid size and canvas size"""
        super().__init__()
        self.cw = 600
        self.ch = 600
        self.delay = 30
        self.s = int(self.cw / max(width, height))
        self.pad = 5
        self.width = width
        self.height = height
        self.root = tk.Tk()
        self.canvas = None
        self.robot = None
        self.canvas_lines = []
        self.log_trace = False
        self.trace = []
        self.init_canvas()
        self.create_buttons()
        # bind keyboard event
        self.root.bind('<Left>', self.left)
        self.root.bind('<Right>', self.right)
        self.root.bind('<Up>', self.move)

    def draw_robot(self):
        """draw robot on canvas"""
        h = self.height * self.s + self.pad
        w = self.width * self.s + self.pad
        if self.direction == 'NORTH':
            return self.canvas.create_polygon(int((self.x + .5) * self.s + self.pad), h - (self.y + 1) * self.s,
                                              self.x * self.s + self.pad, h - self.y * self.s,
                                              (self.x + 1) * self.s + self.pad, h - self.y * self.s,
                                              fill="blue")
        elif self.direction == 'EAST':
            return self.canvas.create_polygon((self.x + 1) * self.s + self.pad, h - int((self.y + .5) * self.s),
                                              self.x * self.s + self.pad, h - self.y * self.s,
                                              self.x * self.s + self.pad, h - (self.y + 1) * self.s,
                                              fill="blue")
        elif self.direction == 'SOUTH':
            return self.canvas.create_polygon(self.x * self.s + int(self.s / 2) + self.pad, h - self.y * self.s,
                                              self.x * self.s + self.pad, h - (self.y + 1) * self.s,
                                              (self.x + 1) * self.s + self.pad, h - (self.y + 1) * self.s,
                                              fill="blue")
        elif self.direction == 'WEST':
            return self.canvas.create_polygon(self.x * self.s + self.pad, h - self.y * self.s - int(self.s / 2),
                                              (self.x + 1) * self.s + self.pad, h - self.y * self.s,
                                              (self.x + 1) * self.s + self.pad, h - (self.y + 1) * self.s,
                                              fill="blue")

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_valid_movement(self):
        """check if the movement is valid"""
        if ((((self.direction == 'NORTH' and self.is_valid_position(self.x, self.y + 1))
              or (self.direction == 'EAST' and self.is_valid_position(self.x + 1, self.y)))
             or (self.direction == 'SOUTH' and self.is_valid_position(self.x, self.y - 1)))
                or (self.direction == 'WEST' and self.is_valid_position(self.x - 1, self.y))):
            return True
        else:
            print('[WARNING]ignore "MOVE" command at step {}: {},{},{}'.format(
                self.step + 1, self.x, self.y, self.direction))

    def init_canvas(self):
        """initialize canvas"""
        self.canvas = tk.Canvas(self.root, width=self.cw + 2 * self.pad, height=self.ch + 2 * self.pad)
        self.refresh_canvas()
        self.canvas.pack()

    def clear_trace(self):
        """clear trace on canvas"""
        if self.canvas:
            for step in self.trace:
                self.canvas.delete(step)
            self.trace = []

    def refresh_canvas(self):
        """refresh canvas with grid lines and robot"""
        if self.canvas:
            if self.robot:
                self.canvas.delete(self.robot)
            for line in self.canvas_lines:
                self.canvas.delete(line)
            self.clear_trace()
        # grid size
        h = self.height * self.s + self.pad
        w = self.width * self.s + self.pad
        for i in range(0, self.width + 1):
            self.canvas_lines.append(
                self.canvas.create_line(i * self.s + self.pad, self.pad, i * self.s + self.pad, h,
                                        fill='green'))
        for i in range(0, self.height + 1):
            self.canvas_lines.append(
                self.canvas.create_line(self.pad, i * self.s + self.pad, w, i * self.s + self.pad,
                                        fill='green'))
        self.robot = self.draw_robot()
        self.canvas.update()

    def place(self, x, y, direction):
        if not self.log_trace:
            self.clear_trace()
        super().place(x, y, direction)
        self.canvas.delete(self.robot)
        self.robot = self.draw_robot()

    def move(self, *args):
        if not self.log_trace:
            self.clear_trace()
        self.step += 1
        if not self.is_valid_movement():
            return
        super().move()
        if self.log_trace:
            self.canvas.itemconfig(self.robot, fill="gray")
            self.trace.append(self.robot)
        else:
            self.clear_trace()
            self.canvas.delete(self.robot)
        self.robot = self.draw_robot()
        self.canvas.after(self.delay)
        self.canvas.update()

    def left(self, *args):
        if not self.log_trace:
            self.clear_trace()
        super().left()
        self.canvas.delete(self.robot)
        self.robot = self.draw_robot()
        self.canvas.after(self.delay)
        self.canvas.update()

    def right(self, *args):
        if not self.log_trace:
            self.clear_trace()
        super().right()
        self.canvas.delete(self.robot)
        self.robot = self.draw_robot()
        self.canvas.after(self.delay)
        self.canvas.update()

    def report(self):
        if self.direction is not None:
            print(self.x, self.y, self.direction)

    def process_file_commands(self):
        filepath = askopenfilename()
        if not filepath:
            return
        with open(filepath, 'r') as f:
            commands = f.read().splitlines()
            self.process_commands(commands)

    def process_commands(self, commands):
        self.log_trace = True
        self.clear_trace()
        placed = False
        for i, command in enumerate(commands):
            self.step = i
            if not placed and not command.startswith('PLACE '):
                print('[WARNING]ignore "{}" command at step {}: please provide available PLACE command at first.'
                      .format(command, i + 1))
                continue
            if command.startswith('PLACE '):
                x, y, direction = command[6:].split(',')
                x, y = int(x), int(y)
                if self.is_valid_position(x, y) and direction in self.DIRECTIONS:
                    placed = True
                    self.place(int(x), int(y), direction)
            elif command == 'MOVE':
                self.move()
            elif command == 'LEFT':
                self.left()
            elif command == 'RIGHT':
                self.right()
            elif command == 'REPORT':
                self.report()
        self.log_trace = False

    def explore(self):
        data = [[0] * self.width for _ in range(self.height)]
        data[self.y][self.x] = 1
        router = Router()
        commands = router.solve(data)
        self.process_commands(commands)

    def resize(self):
        self.width = int(self.width_entry.get())
        self.height = int(self.height_entry.get())
        self.s = int(self.cw / max(self.width, self.height))
        self.refresh_canvas()

    def create_buttons(self):
        self.width_entry = tk.Entry(self.root, width=10)
        self.width_entry.insert(0, '5')
        self.height_entry = tk.Entry(self.root, width=10)
        self.height_entry.insert(0, '5')
        size_button = tk.Button(self.root, text="resize", command=self.resize)

        left_button = tk.Button(self.root, text="LEFT", command=self.left)
        right_button = tk.Button(self.root, text="RIGHT", command=self.right)
        move_button = tk.Button(self.root, text="MOVE", command=self.move)
        place_button = tk.Button(self.root, text="PLACE", command=self.place_dialog)
        self.place_entry = tk.Entry(self.root, width=10)
        self.place_entry.insert(0, '0,0,EAST')
        button = tk.Button(self.root, text="Open File", command=self.process_file_commands)
        explore = tk.Button(self.root, text="Explore", command=self.explore)
        self.width_entry.pack(side=tk.LEFT)
        self.height_entry.pack(side=tk.LEFT)
        size_button.pack(side=tk.LEFT)
        explore.pack(side=tk.RIGHT)
        button.pack(side=tk.RIGHT)
        place_button.pack(side=tk.RIGHT)
        self.place_entry.pack(side=tk.RIGHT)
        move_button.pack(side=tk.RIGHT)
        right_button.pack(side=tk.RIGHT)
        left_button.pack(side=tk.RIGHT)

    def place_dialog(self):
        place_str = self.place_entry.get()
        sp = place_str.split(',')
        if len(sp) < 3:
            print('[WARNING]ignore "PLACE" command: {}, correct format: x,y,direction'.format(place_str))
            return
        x, y, direction = sp
        x, y = int(x), int(y)
        if self.is_valid_position(x, y) and direction in self.DIRECTIONS:
            self.place(int(x), int(y), direction)
        else:
            print('[WARNING]ignore "PLACE" command: {}, correct format: x,y,direction'.format(place_str))

    def start(self):
        self.root.mainloop()


def main():
    robot = RobotGUI()
    robot.start()


if __name__ == '__main__':
    main()
