import sys


class Robot:
    """
    Robot class
    """
    # Available directions
    DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']

    # Constructor with default table length and width
    def __init__(self, length: int = 5, width: int = 5):
        self.x = None
        self.y = None
        self.direction = None
        self.length = length
        self.width = width
        self.step = 0
        self.placed = False

    # Place the robot on the table, x and y should be the available position
    def place(self, x: int, y: int, direction: str):
        if not self.is_valid_position(x, y) or direction not in self.DIRECTIONS:
            print('[WARNING]ignore "PLACE" command due to wrong position at step {}: {},{},{}'
                  .format(self.step, x, y, direction))
            return
        self.placed = True
        self.x = x
        self.y = y
        self.direction = direction

    # Move the robot to the next position
    def move(self):
        if self.direction == 'NORTH' and self.is_valid_position(self.x, self.y + 1):
            self.y += 1
        elif self.direction == 'EAST' and self.is_valid_position(self.x + 1, self.y):
            self.x += 1
        elif self.direction == 'SOUTH' and self.is_valid_position(self.x, self.y - 1):
            self.y -= 1
        elif self.direction == 'WEST' and self.is_valid_position(self.x - 1, self.y):
            self.x -= 1
        else:
            print('[WARNING]ignore "MOVE" command at step {}: {},{},{}'.format(
                self.step + 1, self.x, self.y, self.direction))

    # Rotate the robot to the left
    def left(self):
        if self.direction is not None:
            index = (self.DIRECTIONS.index(self.direction) - 1) % 4
            self.direction = self.DIRECTIONS[index]

    # Rotate the robot to the right
    def right(self):
        if self.direction is not None:
            index = (self.DIRECTIONS.index(self.direction) + 1) % 4
            self.direction = self.DIRECTIONS[index]

    # Report the current position and direction of the robot
    def report(self):
        if self.direction is not None:
            print(self.x, self.y, self.direction)

    # Check if the position is valid
    def is_valid_position(self, x, y):
        return 0 <= x < self.length and 0 <= y < self.width

    # Process the commands
    def process_commands(self, commands: [str]):
        for i, command in enumerate(commands):
            self.step = i
            if not self.placed and not command.startswith('PLACE '):
                print('[WARNING]ignore "{}" command at step {}: please provide available PLACE command at first.'
                      .format(command, i + 1))
                continue
            if command.startswith('PLACE '):
                x, y, direction = command[6:].split(',')
                self.place(int(x), int(y), direction)
            elif command == 'MOVE':
                self.move()
            elif command == 'LEFT':
                self.left()
            elif command == 'RIGHT':
                self.right()
            elif command == 'REPORT':
                self.report()


# Main function
def main():
    # Default table length and width
    robot = Robot(length=5, width=5)
    # Process the commands
    if len(sys.argv) > 1:
        if sys.argv[1] == '-f' and len(sys.argv) == 3:
            file = sys.argv[2]
            with open(file, 'r') as f:
                commands = f.read().splitlines()
        else:
            commands = sys.argv[1:]
        robot.process_commands(commands)
    else:
        print('[WARNING]No command provided. Call the script like this: "python robot.py -f a.txt"\n'
              'or this: "python robot.py \"PLACE 2,2,EAST\" RIGHT MOVE REPORT"')


if __name__ == '__main__':
    main()
