# graph renderer based on Graphviz; see http://www.graphviz.org/

__all__ = (
    "GraphvizGraphRenderer",)

import logging

import pydotplus
import pygraphviz
import six

import core
from base import BaseRenderer

_logger = logging.getLogger(__name__)

class GraphvizGraphRenderer (BaseRenderer):
    MIME_TYPES = ("text/vnd.graphviz",)

    SUPPORTED_PROGRAMS = ("dot", "neato", "twopi", "circo", "fdp", "sfdp")
    SUPPORTED_FORMATS = ("gif", "png", "svg")

    _layout_program = "dot"
    _output_format = "png"

    def __init__ (self):
        self.reset_graph_properties(None)
        self.reset_node_properties(None)
        self.reset_edge_properties(None)

    def set_layout_program (self, code, **kwargs):
        """ Usage: set-layout-program <NAME>

            Options:
                <NAME>  One of the supported programs (see
                        GraphvizGraphRenderer.SUPPORTED_PROGRAMS)
        """
        layout_program = kwargs["<NAME>"].lower()
        if (not layout_program in self.SUPPORTED_PROGRAMS):
            raise Exception(
                "Unknown program: %s" % layout_program)

        self._layout_program = layout_program
        _logger.debug("set graphviz layout program to '%s'" % layout_program)

    def set_output_format (self, code, **kwargs):
        """ Usage: set-output-format <NAME>

            Options:
                <NAME>  One of the supported formats (see
                        GraphvizGraphRenderer.SUPPORTED_FORMATS)
        """
        output_format = kwargs["<NAME>"].lower()
        if (not output_format in self.SUPPORTED_FORMATS):
            raise Exception(
                "Unknown or unsupported format: %s" % output_format)

        self._output_format = output_format
        _logger.debug("set graphviz output format to '%s'" % output_format)

    def reset_graph_properties (self, code, **kwargs):
        """ Usage: reset-graph-properties
        """
        self._graph_properties = {}

    def set_graph_property (self, code, **kwargs):
        """ Usage: set-graph-property <NAME> <VALUE>

            Options:
                <NAME>   Name of a graph property supported by Graphviz
                <VALUE>  Value for this graph property
        """
        property_name = kwargs["<NAME>"]
        property_value = kwargs["<VALUE>"]

        if (not property_name in pydotplus.GRAPH_ATTRIBUTES):
            raise Exception("Unknown graph property: %s" % property_name)

        self._graph_properties[property_name] = property_value

    def reset_node_properties (self, code, **kwargs):
        """ Usage: reset-node-properties
        """
        self._node_properties = {}

    def set_node_property (self, code, **kwargs):
        """ Usage: set-node-property <NAME> <VALUE>

            Options:
                <NAME>   Name of a node property supported by Graphviz
                <VALUE>  Value for this node property
        """
        property_name = kwargs["<NAME>"]
        property_value = kwargs["<VALUE>"]

        if (not property_name in pydotplus.NODE_ATTRIBUTES):
            raise Exception("Unknown node property: %s" % property_name)

        self._node_properties[property_name] = property_value

    def reset_edge_properties (self, code, **kwargs):
        """ Usage: reset-edge-properties
        """
        self._edge_properties = {}

    def set_edge_property (self, code, **kwargs):
        """ Usage: set-edge-property <NAME> <VALUE>

            Options:
                <NAME>   Name of an edge property supported by Graphviz
                <VALUE>  Value for this edge property
        """
        property_name = kwargs["<NAME>"]
        property_value = kwargs["<VALUE>"]

        if (not property_name in pydotplus.EDGE_ATTRIBUTES):
            raise Exception("Unknown edge property: %s" % property_name)

        self._edge_properties[property_name] = property_value

    def render (self, content, content_type):
        # parse the DOT-formatted content
        try:
            g = pygraphviz.AGraph(string = content)

        except Exception as e:
            raise Exception(
                "Unable to parse DOT document: %s; "
                "content was: %s" % (e, content))

        # set user-defined properties
        for (key, value) in self._graph_properties.items():
            g.graph_attr[key] = value

        for (key, value) in self._node_properties.items():
            g.node_attr[key] = value

        for (key, value) in self._edge_properties.items():
            g.edge_attr[key] = value

        # generate a picture out of the DOT document
        try:
            content_type = {
                "gif": core.MIME_TYPE.GIF,
                "png": core.MIME_TYPE.PNG,
                "svg": core.MIME_TYPE.SVG,
            }[self._output_format]

            content = six.BytesIO()

            g.draw(content,
                format = self._output_format,
                prog = self._layout_program)

            content.seek(0)
            content = content.read()

            yield (content_type, content)

        except Exception as e:
            raise Exception("Unable to render DOT document: %s" % e)