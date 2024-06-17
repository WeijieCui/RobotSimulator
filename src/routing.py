import math
from ortools.constraint_solver import routing_enums_pb2, pywrapcp


class Router:
    def __init__(self):
        self.manager = None
        self.distance_matrix = None
        self.routes = None
        self.start = None

    def solve(self, grid) -> [str]:
        """Solve the routing problem."""
        # Create the data
        data = self.create_data_model(grid)
        # Create the routing index manager
        self.manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
        # Create Routing Model
        routing = pywrapcp.RoutingModel(self.manager)
        # Calculate the distance between two points
        self.distance_matrix = self.compute_euclidean_distance_matrix(data['locations'])
        # Register the distance callback
        transit_callback_index = routing.RegisterTransitCallback(self.distance_callback)
        # Define cost of each arc
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Define strategy
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.time_limit.seconds = 15

        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        routes = self.get_routes(solution, routing, self.manager)
        return self.wrap_result(data, routes)

    def distance_callback(self, from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.distance_matrix[from_node][to_node]

    @staticmethod
    def create_data_model(grid):
        def search_start():
            """Search the start point."""
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    if grid[i][j] > 0:
                        return i, j
            return 0, 0

        start = search_start()
        # Create the data
        data = {
            'locations': [],
            'depot': 0,
            'num_vehicles': 1,
        }
        count = 0
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] >= 0:
                    data['locations'].append((j, i))
                    if i == start[0] and j == start[1]:
                        data['depot'] = count
                    count += 1
        return data

    def get_routes(self, solution, routing, manager):
        routes = []
        for route_nbr in range(routing.vehicles()):
            index = routing.Start(route_nbr)
            route = [manager.IndexToNode(index)]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
            routes.append(route)
        return routes

    @staticmethod
    def wrap_result(data, routes):
        """Wrap the result into a list of commands."""
        DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        x = [data['locations'][i][0] for i in routes[0]]
        y = [data['locations'][i][1] for i in routes[0]]
        commands = ['PLACE {},{},EAST'.format(x[0], y[0])]
        xp, yp = x[0], y[0]
        direction = 'EAST'
        for i in range(1, len(x)):
            if direction == 'NORTH':
                # Turn right and move to the next point
                if x[i] - xp == 1 and y[i] - yp == 0:
                    commands.append('RIGHT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[(DIRECTIONS.index(direction) + 1) % 4]
                # Turn left and move to the next point
                elif x[i] - xp == -1 and y[i] - yp == 0:
                    commands.append('LEFT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 1]
                # Move to the next point
                elif y[i] - yp == 1 and x[i] - xp == 0:
                    commands.append('MOVE')
                # Turn around and move to the next point
                elif y[i] - yp == -1 and x[i] - xp == 0:
                    commands.append('LEFT')
                    commands.append('LEFT')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 2]
                else:
                    print('[ERROR] Invalid movement:{} ({}, {}) -> ({}, {})'.format(direction, xp, yp, x[i], y[i]))
            elif direction == 'EAST':
                # Move to the next point
                if x[i] - xp == 1:
                    commands.append('MOVE')
                # Turn left and move to the next point
                elif y[i] - yp == 1:
                    commands.append('LEFT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 1]
                # Turn right and move to the next point
                elif y[i] - yp == -1:
                    commands.append('RIGHT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[(DIRECTIONS.index(direction) + 1) % 4]
                # Turn around and move to the next point
                elif x[i] - xp == -1:
                    commands.append('LEFT')
                    commands.append('LEFT')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 2]
                else:
                    print('[ERROR] Invalid movement:{} ({}, {}) -> ({}, {})'.format(direction, xp, yp, x[i], y[i]))
            elif direction == 'SOUTH':
                # Turn left and move to the next point
                if x[i] - xp == 1:
                    commands.append('LEFT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 1]
                # Turn right and move to the next point
                elif x[i] - xp == -1:
                    commands.append('RIGHT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[(DIRECTIONS.index(direction) + 1) % 4]
                # Move to the next point
                elif y[i] - yp == -1:
                    commands.append('MOVE')
                # Turn around and move to the next point
                elif y[i] - yp == 1:
                    commands.append('LEFT')
                    commands.append('LEFT')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 2]
                else:
                    print('[ERROR] Invalid movement:{} ({}, {}) -> ({}, {})'.format(direction, xp, yp, x[i], y[i]))
            else:
                # Move to the next point
                if x[i] - xp == -1:
                    commands.append('MOVE')
                # Turn right and move to the next point
                elif y[i] - yp == 1:
                    commands.append('RIGHT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[(DIRECTIONS.index(direction) + 1) % 4]
                # Turn left and move to the next point
                elif y[i] - yp == -1:
                    commands.append('LEFT')
                    commands.append('MOVE')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 1]
                # Turn around and move to the next point
                elif x[i] - xp == 1:
                    commands.append('LEFT')
                    commands.append('LEFT')
                    direction = DIRECTIONS[DIRECTIONS.index(direction) - 2]
                else:
                    print('[ERROR] Invalid movement:{} ({}, {}) -> ({}, {})'.format(direction, xp, yp, x[i], y[i]))
            xp, yp = x[i], y[i]
        return commands

    @staticmethod
    def compute_euclidean_distance_matrix(locations):
        """Creates callback to return distance between points."""
        distances = {}
        length = int(math.sqrt(len(locations)))
        for from_counter, from_node in enumerate(locations):
            distances[from_counter] = {}
            for to_counter, to_node in enumerate(locations):
                if from_counter == to_counter:
                    distances[from_counter][to_counter] = 0
                elif abs(from_counter - to_counter) == length or \
                        (from_counter - to_counter == 1 and from_counter % length != 0) or \
                        (from_counter - to_counter == -1 and to_counter % length != 0):
                    distances[from_counter][to_counter] = 1
                else:
                    # Euclidean distance
                    distances[from_counter][to_counter] = 10000
        return distances


if __name__ == '__main__':
    router = Router()
    movements = router.solve([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])
    with open('../data/output.txt', 'w') as f:
        for movement in movements:
            f.write(movement + '\n')
