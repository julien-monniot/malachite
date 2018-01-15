""" Use data gathered and reinforced by Loader to build and eventually display
    a plotly 3D  network graph
"""

from plotly.offline import plot
from plotly.graph_objs import (
    Scatter3d, Line, Marker,
    Layout, Scene, XAxis, YAxis, ZAxis,
    Margin, Data, Figure
)


class PlotlyHelper:

    def __init__(self, nodes):
        """Local storage and processing functions for plotly objects"""
        self.node_scatters = {}
        self.edge_scatters = {}

        self.nodes = nodes
        self._build_node_scatter("Main scatter")

    def _build_edges_coordinates(self, edges):
        """Build 3-dim edges coordinates from igraph layout and edge list"""

        Xe = []
        Ye = []
        Ze = []
        for e in edges:
            Xe += [e.source.x_coord, e.destination.x_coord, None]
            Ye += [e.source.y_coord, e.destination.y_coord, None]
            Ze += [e.source.z_coord, e.destination.z_coord, None]

        return [Xe, Ye, Ze]

    def _build_node_scatter(self, scatter_name):
        """ Generate a scatter trace for plotly
            from coordinates computed by _build_nodes_coordinates
        """

        nodes_coords_x = [n.x_coord for n in self.nodes]
        nodes_coords_y = [n.y_coord for n in self.nodes]
        nodes_coords_z = [n.z_coord for n in self.nodes]

        node_scatter = Scatter3d(
            x=nodes_coords_x,
            y=nodes_coords_y,
            z=nodes_coords_z,
            mode='markers',
            name=scatter_name,
            marker=Marker(
                symbol='dot',
                size=6,
                line=Line(color='rgb(50,50,50)', width=0.5)
            ),
            hoverinfo=[node.appliance.name for node in self.nodes],
            text=[node.appliance.name for node in self.nodes]
        )

        self.node_scatters[scatter_name] = node_scatter

    def build_edge_scatter(self, edges, scatter_name):
        """ Generate a scatter trace for plotly
            from coordinates computed by _build_nodes_coordinates
        """

        coord = self._build_edges_coordinates(edges)

        edge_scatter = Scatter3d(
            x=coord[0],
            y=coord[1],
            z=coord[2],
            mode='lines',
            line=Line(color='rgb(125,125,125)', width=1),
            hoverinfo=[e.__str__() for e in edges]
        )

        self.edge_scatters[scatter_name] = edge_scatter

    def _get_axis(self, titles=None):
        """Come on, we can do better than that"""
        if not titles:
            titles = ['', '', '']

        axis = dict(
            showbackground=False,
            showline=True,
            zeroline=True,
            showgrid=True,
            showticklabels=False,
            title=titles
        )

        return axis

    def _get_layout(self, axis, title=""):
        """Here too"""
        layout = Layout(
            title=title,
            width=1400,
            height=1000,
            showlegend=False,
            scene=Scene(
                xaxis=XAxis(axis),
                yaxis=YAxis(axis),
                zaxis=ZAxis(axis),
            ),
            margin=Margin(
                t=100
            ),
            hovermode='closest',
        )

        return layout

    def _plot(self, plotly_layout, filename):
        """ Last few hidden computations before that lead to
            the actual plot.
        """

        # Add up all traces computed so far into a single list
        traces = [trace for trace in self.node_scatters.values()]
        traces += [trace for trace in self.edge_scatters.values()]

        data = Data(traces)
        fig = Figure(data=data, layout=plotly_layout)

        plot(fig, filename=filename)

    def plot(self, filename):
        """Create 3D figure and plot it in browser"""

        # Prepare plotly layout with axis
        # (Doesn't really depend on any of the scatters)
        axis = self._get_axis()
        plotly_layout = self._get_layout(axis)

        self._plot(plotly_layout, filename)
