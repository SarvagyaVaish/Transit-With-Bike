import util
from util import Node, Connection


def read_nodes():
    """
    Read caltrain stops and create create Node objects.
    :return: list of Nodes
    """
    nodes = []
    stops_reader, f = util.create_csv_reader('stops.txt')
    for stop_row in stops_reader:
        node = Node(
            modes=["caltrain", "bike"],
            id=stop_row['stop_id'],
            name=stop_row['stop_name'],
            lat=float(stop_row['stop_lat']),
            lon=float(stop_row['stop_lon'])
        )
        nodes.append(node)
    f.close()

    return nodes


def read_connections(nodes):
    # TODO: expand to include all trips.
    """
    Read caltrain trip data and create connections between nodes.
    :return: list of Connections
    """
    trip_ids = ['6512465-CT-17OCT-Combo-Weekday-01', '6512464-CT-17OCT-Combo-Weekday-01', '6512553-CT-17OCT-Combo-Weekday-01']
    # trip_ids = ['trip1', 'trip2', 'trip3']
    connections = []

    for trip_id in trip_ids:
        stop_times_reader, f = util.create_csv_reader('stop_times.txt')
        trip_sequence = {}
        for row in stop_times_reader:
            if row['trip_id'] == trip_id:
                trip_sequence[int(row['stop_sequence'])] = \
                    {
                        'time':    row['arrival_time'],
                        'stop_id': row['stop_id']
                    }
        f.close()

        number_of_stops = len(trip_sequence.keys())
        for i in range(1, number_of_stops):
            # start node
            start_node = filter(lambda n: n.id == trip_sequence[i]['stop_id'], nodes)[0]
            start_time = trip_sequence[i]['time']

            # end node
            end_node = filter(lambda n: n.id == trip_sequence[i+1]['stop_id'], nodes)[0]
            end_time = trip_sequence[i+1]['time']

            # append
            connection = Connection(start_node, start_time, end_node, end_time)
            connections.append(connection)

    return connections


class CaltrainModel:
    def __init__(self):
        self.nodes = read_nodes()
        self.connections = read_connections(self.nodes)