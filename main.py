import pprint

from caltrain import CaltrainModel
from maps_client import maps_client_network_stats
from util import create_bike_connections
from util import Node, store_all_nodes_db

DEBUG = False
# DEBUG = True

NUMBER_OF_SOLUTIONS = 5


def setup_DB(all_nodes):
    # Create global lookup
    all_nodes_db = {}
    for n in all_nodes:
        all_nodes_db[n.id] = n
    store_all_nodes_db(all_nodes_db)


if __name__ == '__main__':
    service_id = 'CT-17OCT-Combo-Weekday-01'
    print "Loading..."

    # Models
    caltrain = CaltrainModel()

    # Create basic nodes
    departure_node = Node(modes=["bike"], id="departure", name="Office              ", direction="", lat=37.425822, lon=-122.100192)  # lat=37.414933, lon=-122.103811
    arrival_node = Node(modes=["bike"], id="arrival", name="Embarc              ", direction="", lat=37.792740, lon=-122.397068)
    setup_DB(caltrain.nodes + [departure_node] + [arrival_node])
    # setup_DB(caltrain.nodes)  # TODO: For testing

    #
    # Graph search
    #

    # Set initial node
    first_node = Node.find_node_by_id("departure")
    first_node.arrival_time = 17 * 60 + 0
    first_node.cost = 0
    final_node_id = "arrival"

    # first_node = Node.find_node_by_id("A")  # TODO: For testing
    # first_node.arrival_time = 1 * 60 + 1  # TODO: For testing
    # first_node.cost = 0  # TODO: For testing
    # final_node_id = "C"  # TODO: For testing

    # Remove connections that are in the past, or too far off in the future
    caltrain.keep_connections_bw(first_node.arrival_time - 1, first_node.arrival_time + 4 * 60)

    open_set = []
    open_set.append(first_node)

    closed_set = []
    solution_number = 0

    print "Calculating...\n-----"
    while len(open_set) > 0:
        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)

        # Get next node to explore
        current_node = Node.cheapest_node(open_set)
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
            while solution_node is not None:
                print solution_node
                if solution_node.from_mode == "bike":
                    print "\t", solution_node.from_mode
                # print "\twaiting:", solution_node.time_waiting, "moving:", solution_node.time_moving, ""
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
            bike_connections = create_bike_connections(current_node)

            # Prune bike connections
            pruned_connections = []
            for connection in bike_connections:
                conn_destination_node = Node.find_node_by_id(connection.end_node_id)
                conn_departure_node = Node.find_node_by_id(connection.start_node_id)

                # 1. Ignore biking b/w NB and SB stations
                if conn_departure_node.name == conn_destination_node.name:
                    continue

                # 2. Don't not bike between stations of the same provider
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

                pruned_connections.append(connection)

            current_node.connections += pruned_connections

        if DEBUG:
            print "\nNew connections:"

        # Iterate over connections and add nodes
        for connection in current_node.connections:
            if DEBUG:
                print connection

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
            bike_penalty = 1.2 if connection.mode == "bike" else 1.0
            waiting_penalty = 0.001 if current_node.first_dest_node else 2.0
            new_node.cost = current_node.cost + time_moving * bike_penalty + time_waiting * waiting_penalty

            if DEBUG:
                print "time_waiting", time_waiting, "time_moving", time_moving, "cost", new_node.cost

            new_node.time_waiting = time_waiting
            new_node.time_moving = time_moving

            # Add new node to open set
            open_set.append(new_node)

        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)
            print "\n-----"
            raw_input()
