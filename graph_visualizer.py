import matplotlib.pyplot as plt
from util import Node
import time


nodes_handle = None
nodes_data = {'x':[], 'y':[]}

def init_plot():
    plt.ion()  # interactive mode
    plt.axis('equal')
    # plt.gca().invert_xaxis()
    # plt.gca().invert_yaxis()
    plot_corners()


def plot_corners():
    plt.plot(-122.616066, 37.914449, ".", color='1')  # invisible
    plt.plot(-121.965846, 37.364846, ".", color='1')


#
# All nodes
#
all_nodes_handle = None
all_nodes_data = None
def set_all_nodes(all_nodes):
    global all_nodes_data
    all_nodes_data = {'x': [], 'y': []}
    for node in all_nodes:
        all_nodes_data['x'].append(node.lon)
        all_nodes_data['y'].append(node.lat)

def plot_all_nodes():
    global all_nodes_handle, all_nodes_data
    if all_nodes_handle is None:
        all_nodes_handle, = plt.plot(0, 0, ".", color='0.8')
    all_nodes_handle.set_xdata(all_nodes_data['x'])
    all_nodes_handle.set_ydata(all_nodes_data['y'])


#
# Current node
#
curr_node_handle = None
curr_node_data = None
def set_current_node(node):
    global curr_node_handle, curr_node_data
    curr_node_data = {'x': [], 'y': []}
    curr_node_data['x'].append(node.lon)
    curr_node_data['y'].append(node.lat)

def plot_curr_node():
    global curr_node_handle, curr_node_data
    if curr_node_handle is None:
        curr_node_handle, = plt.plot(0, 0, "ro")
    curr_node_handle.set_xdata(curr_node_data['x'])
    curr_node_handle.set_ydata(curr_node_data['y'])


#
# Home and Destination node
#
HnD_nodes_handle = None
HnD_nodes_data = None
def set_HnD_node(H_node, D_node):
    global HnD_nodes_handle, HnD_nodes_data
    HnD_nodes_data = {'x': [], 'y': []}

    HnD_nodes_data['x'].append(H_node.lon)
    HnD_nodes_data['y'].append(H_node.lat)

    HnD_nodes_data['x'].append(D_node.lon)
    HnD_nodes_data['y'].append(D_node.lat)

def plot_HnD_nodes():
    global HnD_nodes_handle, HnD_nodes_data
    if HnD_nodes_handle is None:
        HnD_nodes_handle, = plt.plot(0, 0, "b*")
    HnD_nodes_handle.set_xdata(HnD_nodes_data['x'])
    HnD_nodes_handle.set_ydata(HnD_nodes_data['y'])


#
# Neighboring node
#
nbr_nodes_handle = None
nbr_nodes_data = None
def set_nbr_node(nbr_nodes):
    global nbr_nodes_handle, nbr_nodes_data
    nbr_nodes_data = {'x': [], 'y': []}
    for node in nbr_nodes:
        nbr_nodes_data['x'].append(node.lon)
        nbr_nodes_data['y'].append(node.lat)

def plot_nbr_nodes():
    global nbr_nodes_handle, nbr_nodes_data
    if nbr_nodes_handle is None:
        nbr_nodes_handle, = plt.plot(0, 0, "go")
    nbr_nodes_handle.set_xdata(nbr_nodes_data['x'])
    nbr_nodes_handle.set_ydata(nbr_nodes_data['y'])


#
# Helpers
#
def show_plot():
    plot_all_nodes()
    plot_nbr_nodes()
    plot_HnD_nodes()
    plot_curr_node()

    plt.gca().relim()
    plt.gca().autoscale_view(True,True,True)
    plt.draw()
    plt.pause(.0001)


def keep_open():
    plt.ioff()
    plt.show()
