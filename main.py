import pprint

from caltrain import CaltrainModel

from util import create_csv_reader, create_bike_connections
from util import Node, Connection, store_all_nodes_db, dist_bw_nodes

DEBUG = False
# DEBUG = True

All_SOLUTIONS = False
# All_SOLUTIONS = True


def get_trips(service_id):
    result_trips = []

    trips_reader, f = create_csv_reader('trips.txt')
    for trip in trips_reader:
        if trip["service_id"] == service_id:
            result_trips.append(trip)
    f.close()

    return result_trips


def get_stops(trip_ids):
    result_stops = []

    stop_times_reader, f = create_csv_reader('stop_times.txt')
    for stop in stop_times_reader:
        if stop["trip_id"] in trip_ids:
            result_stops.append(stop)
    f.close()

    return result_stops


def add_stop_info(stop):
    stops_reader, f = create_csv_reader('stops.txt')
    for stop_row in stops_reader:
        if stop_row["stop_id"] == stop["stop_id"]:
            # Add info
            stop["stop_name"] = stop_row["stop_name"]
            stop["stop_lat"] = stop_row["stop_lat"]
            stop["stop_lon"] = stop_row["stop_lon"]
            stop["zone_id"] = stop_row["zone_id"]
            break
    f.close()

    return stop


def setup_DB(all_nodes):
    # Create global lookup
    all_nodes_db = {}
    for n in all_nodes:
        all_nodes_db[n.id] = n
    store_all_nodes_db(all_nodes_db)


if __name__ == '__main__':
    service_id = 'CT-17OCT-Combo-Weekday-01'

    # Models
    caltrain = CaltrainModel()

    # Create basic nodes
    departure_node = Node(modes=["bike"], id="departure", name="departure", lat=37.425822, lon=-122.100192)
    arrival_node = Node(modes=["bike"], id="arrival", name="arrival", lat=37.785399, lon=-122.398752)
    setup_DB(caltrain.nodes + [departure_node] + [arrival_node])
    # setup_DB(caltrain.nodes)  # TODO: For testing

    #
    # Graph search
    #

    # Set initial node
    # first_node = Node.find_node_by_id("70201")
    # first_node.time = 18 * 60 + 9
    # first_node.cost = 0
    # final_node_id = "70011"

    first_node = Node.find_node_by_id("departure")
    first_node.time = 17 * 60
    first_node.cost = 0
    final_node_id = "70011"

    # first_node = Node.find_node_by_id("A")  # TODO: For testing
    # first_node.time = 1 * 60 + 1  # TODO: For testing
    # first_node.cost = 0  # TODO: For testing
    # final_node_id = "C"  # TODO: For testing

    open_set = []
    open_set.append(first_node)

    closed_set = []

    while len(open_set) > 0:
        if DEBUG:
            print "\n-----"
            raw_input()

        # Condense open set: keep only the first lowest cost node for each node id.
        new_set = {}
        for node in open_set:
            if not node.id in new_set.keys() or new_set[node.id].cost > node.cost:
                new_set[node.id] = node
                continue
        open_set = new_set.values()

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

        # Check for goal
        if current_node.id == final_node_id:
            print "Solution: "

            solution_node = current_node
            while solution_node is not None:
                print solution_node
                print "\t", solution_node.from_mode
                solution_node = solution_node.from_node
            print "--"

            if All_SOLUTIONS:
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
                if connection.start_time >= current_node.time:
                    possible_connections.append(connection)

            # Set connections
            current_node.connections += possible_connections

        # Add connections for bikes
        if "bike" in current_node.modes:
            bike_connections = create_bike_connections(current_node)
            current_node.connections += bike_connections

        if DEBUG:
            print "\nNew connections:"
            pprint.pprint(current_node.connections)

        # Iterate over connections and add nodes
        for connection in current_node.connections:
            new_node_id = connection.end_node_id
            new_node = Node.find_node_by_id(new_node_id)
            new_node.time = connection.end_time
            new_node.from_node = current_node
            new_node.from_mode = connection.mode

            # Cost
            duration = connection.end_time - current_node.time
            bike_penalty = 1.5 if connection.mode == "bike" else 1.0
            new_node.cost = current_node.cost + duration * bike_penalty

            # Add new node to open set
            open_set.append(new_node)

        if DEBUG:
            print "\nOpen set:"
            pprint.pprint(open_set)


    # Print answer
    # pprint.pprint(closed_set)



    # # Get all trips on service
    # trips = get_trips(service_id)
    #
    # # Collect Trip IDs
    # trip_ids = []
    # for trip in trips:
    #     trip_ids.append(trip["trip_id"])
    #
    # # Collect stops
    # stops = get_stops(trip_ids)#(["6512465-CT-17OCT-Combo-Weekday-01"])
    #
    # # Add information about stops
    # for i, stop in enumerate(stops):
    #     stops[i] = add_stop_info(stop)

    # trip_id = '6512465-CT-17OCT-Combo-Weekday-01'
    # caltrain_connections = get_connections_for_trip(trip_id, caltrain_nodes)
    # pprint.pprint(caltrain_connections)

    # for c in caltrain_connections:
    #     print c.start_node.lat, c.start_node.lon, c.end_node.lat, c.end_node.lon
    #     dist_bw_nodes(c.start_node, c.end_node)
