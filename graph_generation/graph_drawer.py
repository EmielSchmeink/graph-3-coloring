import graph_tool.all as gt
from matplotlib import pyplot as plt

plt.switch_backend("cairo")


def draw_graph(graph, colors):
    fig, ax = plt.subplots(2, 2, figsize=(12, 11.5))
    if gt.is_planar(graph):
        pos = gt.planar_layout(graph)

        gt.graph_draw(graph, pos=pos, mplfig=fig)
    else:

        gt.graph_draw(graph, mplfig=ax[0, 0])
    plt.show(block=True)
