import matplotlib.pyplot as plt
from util import Node
import time


nodes_handle = None
nodes_data = {'x':[], 'y':[]}


def init_plot():
    plt.ion()  # interactive mode
    plt.axis('equal')
    plot_corners()


def plot_corners():
    plt.plot(37.914449, abs(-122.616066), "k.")
    plt.plot(37.364846, abs(-121.965846), "k.")
    show_plot()


def plot_node(node):
    global nodes_data
    nodes_data['x'].append(node.lat)
    nodes_data['y'].append(abs(node.lon))

    global nodes_handle
    if nodes_handle is None:
        nodes_handle, = plt.plot(0, 0, "ro")

    nodes_handle.set_xdata(nodes_data['x'])
    nodes_handle.set_ydata(nodes_data['y'])


def show_plot():
    plt.gca().relim()
    plt.gca().autoscale_view(True,True,True)
    plt.draw()
    plt.pause(0.00001)


def keep_open():
    plt.ioff()
    plt.show()


if __name__ == '__main__':
    init_plot()

    for i in range(10, 20):
        n = Node("", "", "", "", i, i)
        plot_node(n)
        show_plot()
        plt.pause(0.5)
        time.sleep(1)
