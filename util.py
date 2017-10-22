import csv
import copy


def create_csv_reader(filename):
    file = open(filename, 'r')
    reader = csv.DictReader(file)
    return reader, file


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


class Node:
    def __init__(self, modes, id, name, lat=0., lon=0.):
        self.modes = modes
        self.id = id
        self.name = name.replace(" Caltrain", "")
        self.lat = lat
        self.lon = lon
        self.connections = []

        # for A* search
        self.cost = float("inf")

    def __repr__(self):
        # return "{} ({})".format(self.name, self.id)
        return "{} ({}) #conn: {} [{}]".format(
            self.name,
            time_int_to_str(self.cost),
            len(self.connections),
            hex(id(self))
        )

    @classmethod
    def find_node(cls, id, all_nodes):
        for n in all_nodes:
            if n.id == id:
                return n
        return None

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
    def __init__(self, start_node, start_time_str, end_node, end_time_str):
        self.start_node = start_node
        self.start_time = time_str_to_int(start_time_str)
        self.end_node = end_node
        self.end_time = time_str_to_int(end_time_str)

    def __repr__(self):
        # return "{} {} --> {} {}".format(
        #     self.start_node, time_int_to_str(self.start_time),
        #     self.end_node, time_int_to_str(self.end_time))
        return "Start: {} \t@{} \n End:   {} \t@{}\n".format(
            self.start_node, time_int_to_str(self.start_time),
            self.end_node, time_int_to_str(self.end_time))
