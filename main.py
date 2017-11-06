import pprint

from caltrain import CaltrainModel
from maps_client import maps_client_network_stats
from util import create_bike_connections, time_str_to_int, time_int_to_str
from util import Node, setup_DB, biking_duration_bw_nodes, heuristic_time_to_destination
import graph_visualizer as viz

DEBUG = False
# DEBUG = True
VIZ = False
# VIZ = True

NUMBER_OF_SOLUTIONS = 4


def find_directions(departure_coordinate, arrival_coordinate, departure_time):
    """
    :param departure_coordinate:  tuple of (lat, long)
    :param arrival_coordinate: tuple of (lat, long)
    :param departure_time: Departure time string
    :return: Json with directions
    """

    # Load transit models
    caltrain = CaltrainModel()

    # Create basic nodes
    departure_node = Node(modes=["bike"], id="departure", name="Departure", direction="",
                          lat=departure_coordinate[0],
                          lon=departure_coordinate[1]
                          )

    arrival_node = Node(modes=["bike"], id="arrival", name="Arrival", direction="",
                        lat=arrival_coordinate[0],
                        lon=arrival_coordinate[1]
                        )

    setup_DB(caltrain.nodes + [departure_node] + [arrival_node])

    if VIZ:
        viz.init_plot()
        viz.set_all_nodes(Node.get_all_nodes())
        viz.set_HnD_node(Node.find_node_by_id("departure"), Node.find_node_by_id("arrival"))

    #
    # Graph search
    #

    # Set initial node
    first_node = Node.find_node_by_id("departure")
    first_node.arrival_time = time_str_to_int(departure_time)
    first_node.cost = 0
    final_node_id = "arrival"

    # Remove connections that are in the past, or too far off in the future
    caltrain.keep_connections_bw(first_node.arrival_time - 1, first_node.arrival_time + 3 * 60)

    open_set = [first_node]

    closed_set = []
    solution_number = 0

    while len(open_set) > 0:
        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)

        # Get next node to explore
        current_node = Node.cheapest_node(
            open_set,
            h_func=heuristic_time_to_destination(Node.find_node_by_id("arrival"))
        )

        if VIZ:
            viz.set_current_node(current_node)

        if DEBUG:
            print "\nCurrent node:"
            print current_node

        open_set.remove(current_node)
        closed_set.append(current_node)

        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)

        # Check for goal
        if current_node.id == final_node_id:
            solution_number += 1
            print "\nSolution #:", solution_number

            solution_node = current_node
            wait_at_previous_node = 0
            while solution_node is not None:
                wait_at_current_node = wait_at_previous_node
                wait_at_previous_node = solution_node.time_waiting
                print "{} {} : {} {}".format(
                    solution_node.name,
                    time_int_to_str(solution_node.arrival_time),
                    time_int_to_str(solution_node.arrival_time + wait_at_current_node),
                    solution_node.from_mode
                )
                # print solution_node
                if solution_node.from_mode == "bike":
                    print "\t", solution_node.from_mode, "for {} mins".format(solution_node.time_moving)
                solution_node = solution_node.from_node

            if DEBUG:
                print "\nNetwork stats:"
                maps_client_network_stats()

            print "\n\n--\n\n"

            if solution_number < NUMBER_OF_SOLUTIONS:
                continue
            else:
                break

        # Add connections for caltrain
        if "caltrain" in current_node.modes:
            all_connections = caltrain.connections

            # Find connections from current node
            relevant_connections = []
            for connection in all_connections:
                if connection.start_node_id == current_node.id:
                    relevant_connections.append(connection)

            # Find connections that are still possible
            possible_connections = []
            for connection in relevant_connections:
                if connection.start_time >= current_node.arrival_time:
                    possible_connections.append(connection)

            # Set connections
            current_node.connections += possible_connections

        # Add connections for bikes
        if "bike" in current_node.modes:
            bike_connections = create_bike_connections(current_node, compute_end_time=False)

            # Prune bike connections
            pruned_connections = []
            for connection in bike_connections:
                conn_destination_node = Node.find_node_by_id(connection.end_node_id)
                conn_departure_node = Node.find_node_by_id(connection.start_node_id)

                # 1. Ignore biking b/w NB and SB stations
                if conn_departure_node.name == conn_destination_node.name:
                    continue

                # 2. Don't bike between stations of the same provider
                if "caltrain" in conn_departure_node.modes and "caltrain" in conn_destination_node.modes:
                    continue

                # 3. Do not create loops
                keep_connection = True
                prev_node = current_node.from_node
                while prev_node is not None:
                    if prev_node.id == conn_destination_node.id:
                        keep_connection = False
                        break
                    prev_node = prev_node.from_node
                if not keep_connection:
                    continue

                # We want to keep this connection. Calculate end_time.
                connection.end_time = connection.start_time + biking_duration_bw_nodes(conn_departure_node, conn_destination_node)
                pruned_connections.append(connection)

            current_node.connections += pruned_connections

        if DEBUG:
            print "\nNew connections:"

        # Iterate over connections and add nodes
        new_nodes = []
        for connection in current_node.connections:
            new_node_id = connection.end_node_id
            new_node = Node.find_node_by_id(new_node_id)
            new_node.arrival_time = connection.end_time
            new_node.from_node = current_node
            new_node.from_mode = connection.mode

            if current_node.id == "departure":  # Mark new node as first "real" node, aka first destination node to.
                new_node.first_dest_node = True

            # Cost
            time_waiting = connection.start_time - current_node.arrival_time
            time_moving = connection.end_time - connection.start_time
            bike_penalty = 1.0 if connection.mode == "bike" else 1.0
            waiting_penalty = 1.0 if current_node.first_dest_node else 1.0
            new_node.cost = current_node.cost + time_moving * bike_penalty + time_waiting * waiting_penalty

            if DEBUG:
                print connection
                print "time_waiting", time_waiting, "time_moving", time_moving, "cost", new_node.cost

            new_node.time_waiting = time_waiting
            new_node.time_moving = time_moving

            new_nodes.append(new_node)

        # Add new node to open set
        open_set += new_nodes

        # Prune open set for duplicates
        open_set.sort(key=lambda x: x.cost)
        unique_open_set = []
        i = 0
        prev_node = None
        for i in range(len(open_set)):
            curr_node = open_set[i]
            accept = False
            if prev_node is None:
                accept = True
            elif prev_node.name != curr_node.name or prev_node.arrival_time != curr_node.arrival_time:
                accept = True

            if accept:
                unique_open_set.append(curr_node)
                prev_node = curr_node
        open_set = unique_open_set

        if VIZ:
            viz.set_nbr_node(open_set)
            viz.show_plot()

        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)
            print "\n-----"
            raw_input()

    print "opened nodes:", len(open_set)
    if VIZ:
        viz.keep_open()