import csv
import numpy as np
from pygraphviz import AGraph as DotGraph


class Digraph(object):
    def __init__(self, vertices, arcs):
        self._vertices = vertices
        self._arcs = arcs
        self._indexed_vertices = {v: i for (i, v) in enumerate(self._vertices)}

    def initial_vertices(self):
        """Return the list of all initial vertices.

        :return: Initial vertices.
        :rtype: list
        """
        return set([v for v in self._vertices if
                    self._arcs[:, self.get_index(v)].sum() == 0 and self._arcs[self.get_index(v), :].sum() > 0])

    def end_vertices(self):
        """Return the list of all end vertices.

        :return: End vertices.
        :rtype: list
        """
        return set([v for v in self._vertices if
                    self._arcs[:, self.get_index(v)].sum() > 0 and self._arcs[self.get_index(v), :].sum() == 0])

    def draw_all_paths(self, initial, end, filename, relative_value=False):
        paths = self.all_paths(initial, end)

        for path in paths:
            name, extension = filename.rsplit('.', 1)
            path_filename = "{}_{}.{}".format(name, "-".join([str(self.get_index(p)) for p in path]), extension)
            self._draw_path(path, path_filename, relative_value)

    def _draw_path(self, path, filename, relative_value=False):
        dot = DotGraph(strict=True, directed=True)

        # Add initial vertices
        dot.add_node(
            path[0],
            fillcolor='#4CAF50',
            style='filled',
            fontcolor='#FFFFFF'
        )

        if len(path) > 1:
            # Add end vertices
            dot.add_node(
                path[-1],
                fillcolor='#2196F3',
                style='filled',
                fontcolor='#FFFFFF',
            )

            # Add rest of vertices
            dot.add_nodes_from(
                path[1:-1],
                fillcolor='#9E9E9E',
                style='filled'
            )

            total = self._arcs.sum()
            while len(path) > 1:
                i, j = path[0:2]
                value = self._arcs[self.get_index(i), self.get_index(j)]
                if value:
                    if relative_value:
                        value = value * 100. / total
                        formatted_value = "{:.2f}%".format(value)
                    else:
                        formatted_value = str(value)
                    dot.add_edge(i, j, label=formatted_value)
                path = path[1:]

        dot.layout(prog='dot')
        dot.draw(filename)

    def all_paths(self, initial, end):
        """Get all paths between two vertices. Initial and end vertices can be the label or the index.

        :param initial: Initial vertex.
        :param end: End vertex.
        :return: List of paths.
        :rtype: list
        """
        # Parse parameters
        if not isinstance(initial, int):
            initial = self.get_index(initial)

        if not isinstance(end, int):
            end = self.get_index(end)

        # Get all paths
        paths = self._all_paths(initial, end)

        # Use list for associate vertex name with his own index
        vertices = list(self._vertices)

        # Replace vertex index with his name
        named_paths = [[vertices[sp] for sp in p] for p in paths]

        return named_paths

    def _all_paths(self, i, e, path=None):
        if path is None:
            path = []

        if i == e:
            path.append(i)
            result = path
        else:
            result = []
            for vertice, value in [(ve, va) for ve, va in enumerate(self._arcs[i]) if va > 0 and ve != i]:
                if vertice not in path:
                    clone_path = path[:]
                    clone_path.append(i)
                    partial_result = self._all_paths(vertice, e, clone_path)
                    if partial_result:
                        appended = False
                        for r in [res for res in partial_result if isinstance(res, list)]:
                            result.append(r)
                            appended = True
                        if not appended:
                            result.append(partial_result)

        return result

    def get_index(self, vertex):
        """Get a vertex index given his name.

        :param vertex: Vertex name.
        :type vertex: str
        :return: Vertex index.
        :rtype: int
        """
        return self._indexed_vertices[vertex]

    def draw(self, filename, relative_value=False, prog='dot'):
        """Draw digraph using Graphviz.

        :param filename: Output filename to draw.
        :type filename: str
        :param relative_value: If true, arc values will be printed as percentages.
        :type relative_value: bool
        """
        dot = DotGraph(strict=True, directed=True)

        # Add initial vertices
        dot.add_nodes_from(
            self.initial_vertices(),
            fillcolor='#4CAF50',
            style='filled',
            fontcolor='#FFFFFF'
        )

        # Add end vertices
        dot.add_nodes_from(
            self.end_vertices(),
            fillcolor='#2196F3',
            style='filled',
            fontcolor='#FFFFFF',
        )

        # Add rest of vertices
        dot.add_nodes_from(
            self._vertices - self.initial_vertices() - self.end_vertices(),
            fillcolor='#9E9E9E',
            style='filled'
        )

        total = self._arcs.sum()
        for (i, j) in ((i, j) for i in self._vertices for j in self._vertices):
            value = self._arcs[self.get_index(i), self.get_index(j)]
            if value:
                if relative_value:
                    value = value * 100. / total
                    formatted_value = "{:.2f}%".format(value)
                else:
                    formatted_value = str(value)
                dot.add_edge(i, j, label=formatted_value)

        dot.layout(prog=prog)
        dot.draw(filename)

    def subgraph(self, vertices):
        vertices = set(sorted(vertices))
        rows = [False] * len(self._vertices)
        for i in [self._indexed_vertices[v] for v in vertices]:
            rows[i] = True

        nprows = np.array(rows, dtype=bool)

        arcs = self._arcs[nprows][:, nprows]

        return Digraph(vertices, arcs)

    @staticmethod
    def from_csv(filename, separator=','):
        """Make a digraph from a csv file. Format must be:
        origin_vertex,destination_vertex
        origin_vertex,destination_vertex
        ...

        :param filename: Input csv file.
        :type filename: str
        :param separator: Csv separator.
        :type separator: str
        :return: Digraph.
        :rtype: Digraph
        """
        with open(filename, 'r') as csvfile:
            vertices = set()

            # Get all vertices
            reader = csv.reader(csvfile)
            for (origin, destination) in reader:
                vertices.add(origin)
                vertices.add(destination)

            # Sort vertices
            vertices = set(sorted(vertices))

            # Return pointer to beginning
            csvfile.seek(0)

            # Create zeros array for arcs
            arcs = np.zeros((len(vertices), len(vertices)), dtype=np.int8)

            # Index all vertices for fast accessing
            indexed_vertices = {v: i for (i, v) in enumerate(vertices)}

            # Store each arc (weight based)
            reader = csv.reader(csvfile)
            for (origin, destination) in reader:
                arcs[indexed_vertices[origin], indexed_vertices[destination]] += 1

        return Digraph(vertices, arcs)