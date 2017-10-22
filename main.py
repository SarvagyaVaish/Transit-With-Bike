import pprint
import copy

from caltrain import CaltrainModel

from util import create_csv_reader, create_bike_connections
from util import Node, Connection

DEBUG = False


# stop_times_reader, f = create_csv_reader('stop_times.txt')
# realtime_trips_reader, f = create_csv_reader('realtime_trips.txt')
# calendar_reader, f = create_csv_reader('calendar.txt')
# trips_reader, f = create_csv_reader('trips.txt')
# stops_reader, f = create_csv_reader('stops.txt')


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


if __name__ == '__main__':
    service_id = 'CT-17OCT-Combo-Weekday-01'

    # Models
    caltrain = CaltrainModel()
    # pprint.pprint(caltrain.nodes)
    # pprint.pprint(caltrain.connections)

    # Create basic nodes
    departure_node = Node(modes=["bike"], id="departure", name="departure", lat=37.425822, lon=-122.100192)
    arrival_node = Node(modes=["bike"], id="arrival", name="arrival", lat=37.785399, lon=-122.398752)
    all_nodes = caltrain.nodes + [departure_node] + [arrival_node]  # TODO: bart.nodes

    #
    # Graph search
    #

    # Set initial node
    first_node = copy.deepcopy(Node.find_node("70201", all_nodes))
    first_node.cost = 18 * 60 + 9  # Start time
    # first_node = copy.deepcopy(Node.find_node("A", all_nodes))
    # first_node.cost = 1 * 60 + 1  # Start time

    open_set = []
    open_set.append(first_node)

    closed_set = []

    while len(open_set) > 0:
        if DEBUG:
            print "\n-----"
            raw_input()

        # Condense open set
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
        if current_node.id == "70011":
            print "Found one"
            continue

        # Add connections for caltrain
        if "caltrain" in current_node.modes:
            all_connections = caltrain.connections

            # Find connections from current node
            relevant_connections = []
            for connection in all_connections:
                if connection.start_node.id == current_node.id:
                    relevant_connections.append(connection)

            # Find connections that are still possible
            possible_connections = []
            for connection in relevant_connections:
                if connection.start_time >= current_node.cost:
                    possible_connections.append(connection)

            # Set connections
            current_node.connections += possible_connections

        # Add connections for bikes
        # if "bike" in current_node.modes:
        #     bike_connections = create_bike_connections(current_node, all_nodes)
        #     current_node.connections += bike_connections

        if DEBUG:
            print "\nNew connections:"
            pprint.pprint(current_node.connections)

        # Iterate over connections and add nodes
        for connection in current_node.connections:
            new_node = copy.deepcopy(connection.end_node)
            new_node.cost = connection.end_time

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
