import csv
import copy
from math import sin, cos, sqrt, atan2, radians
from contextlib import contextmanager

BIKE_SPEED_M_PER_MIN = 250.
ALL_NODES_DB = {}


@contextmanager
def create_csv_reader(filename):
    file = open(filename, 'r')
    reader = csv.DictReader(file)
    yield reader
    file.close()


def time_str_to_int(time_str):
    elms = time_str.split(":")
    return 60 * int(elms[0]) + int(elms[1])


def time_int_to_str(time_int):
    elms = []
    elms.append(time_int % 60)
    time_int /= 60
    elms.append(time_int % 60)
    elms.reverse()

    s = ""
    for e in elms:
        s += str(e).zfill(2) + ":"
    s = s[0:-1]
    return s


def dist_bw_nodes(node1, node2):
    """
    Calculate distance between two nodes.
    :param node1:
    :param node2:
    :return: Distance in meters.
    """
    lat1 = radians(abs(node1.lat))
    lon1 = radians(abs(node1.lon))
    lat2 = radians(abs(node2.lat))
    lon2 = radians(abs(node2.lon))

    R = 6373.
    dlon = abs(lon2 - lon1)
    dlat = abs(lat2 - lat1)

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance * 1000


def get_close_nodes(node, all_nodes, dist_th=5000):
    """
    :param node: the node in question
    :param all_nodes: list of all nodes to check against
    :param dist_th: return all nodes closer than this threshold
    :return: list of nodes
    """
    result_nodes = []
    for n in all_nodes:
        if n.id == node.id:  # ignore self
            continue
        if dist_bw_nodes(node, n) < dist_th:
            result_nodes.append(n)

    return result_nodes


def create_bike_connections(from_node):
    all_nodes = Node.get_all_nodes()
    close_nodes = get_close_nodes(from_node, all_nodes)

    bike_connections = []
    for node in close_nodes:
        start_time = from_node.arrival_time
        bike_dist = dist_bw_nodes(from_node, node)
        end_time = start_time + max(5, int(bike_dist / BIKE_SPEED_M_PER_MIN))
        connection = Connection(from_node.id, start_time, node.id, end_time, "bike")
        bike_connections.append(connection)

    return bike_connections


def store_all_nodes_db(all_nodes_db):
    global ALL_NODES_DB
    ALL_NODES_DB = all_nodes_db


class Node:
    def __init__(self, modes, id, name, direction, lat=0., lon=0.):
        self.modes = modes
        self.id = id
        self.name = name
        self.direction = direction
        self.lat = lat
        self.lon = lon
        self.connections = []
        self.arrival_time = 0

        # for A* search
        self.cost = float("inf")
        self.from_node = None
        self.from_mode = None
        self.time_waiting = None
        self.time_moving = None
        self.first_dest_node = False

    def __repr__(self):
        # return "{} ({})".format(self.name, self.id)
        return "{} {} ({}) {} {}".format(
            self.name,
            self.direction,
            time_int_to_str(self.arrival_time),
            self.cost,
            self.from_mode,
        )

    @classmethod
    def find_node_by_id(cls, id, make_copy=True):
        if make_copy:
            return copy.deepcopy(ALL_NODES_DB[id])
        else:
            return ALL_NODES_DB[id]

    @classmethod
    def get_all_nodes(cls, make_copy=True):
        if make_copy:
            return copy.deepcopy(ALL_NODES_DB.values())
        else:
            return ALL_NODES_DB.values()

    @classmethod
    def cheapest_node(cls, nodes):
        best_cost = float('inf')
        best_node = None
        for node in nodes:
            if node.cost < best_cost:
                best_cost = node.cost
                best_node = node

        return best_node


class Connection:
    def __init__(self, start_node_id, start_time_str, end_node_id, end_time_str, mode):
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        if isinstance(start_time_str, basestring):
            self.start_time = time_str_to_int(start_time_str)
        else:
            self.start_time = start_time_str
        if isinstance(end_time_str, basestring):
            self.end_time = time_str_to_int(end_time_str)
        else:
            self.end_time = end_time_str
        self.mode = mode

    def __repr__(self):
        # return "{} {} --> {} {}".format(
        #     self.start_node, time_int_to_str(self.start_time),
        #     self.end_node, time_int_to_str(self.end_time))
        return "Start: {} \t@{} \t\t\t{}\n  End: {} \t@{}".format(
            Node.find_node_by_id(self.start_node_id), time_int_to_str(self.start_time),
            self.mode,
            Node.find_node_by_id(self.end_node_id), time_int_to_str(self.end_time),
        )
