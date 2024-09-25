import pygraphviz as pgv
from collections import deque

DEFAULT_NODE_ATTRS = {
    'custom_diverged': '0',
    'custom_looped': '0',
    'custom_seq_len': '0',
    'color': '#00FF00'
}
LOOPED_NODE_ATTRS = {
    'custom_diverged': '0',
    'custom_looped': '1',
    'color': '#FF5555',
    'custom_seq_len': '1'
}
DIVERGED_NODE_ATTRS = {
    'custom_diverged': '1',
    'custom_looped': '1',
    'color': '#FFCCAA',
    'custom_seq_len': '1'
}

class GVBuilder:
    def __init__(self) -> None:
        self.edge_idx: dict[str, str] = {}
        self.G = pgv.AGraph(name='Aliquot', directed=True)
        self.G.node_attr['style'] = 'filled'
        self.G.node_attr['color'] = 'grey'
        self._finished_nodes: set[str] = set()

    def _build_edge_idx(self, nodes: set[int], edges: set[tuple[int, int]]) -> None:
        self.edge_idx = {
            n: [v for u, v in edges if u == n]
            for n in nodes
        }
    
    def _node_name(self, node: int) -> str:
        return f'{node}'

    def _add_node(self, node: int, diverged: bool = False, looped: bool = False, seq_len: int = 0, color: str = '#00AAFF') -> None:
        self.G.add_node(
            self._node_name(node),
            custom_diverged='1' if diverged else '0',
            custom_looped='1' if looped else '0',
            custom_seq_len=str(seq_len),
            color=color
        )
        self._finished_nodes.add(self._node_name(node))

    def _add_looped_node(self, node: int, seq_len: int) -> None:
        return self._add_node(node, seq_len=seq_len)
    
    def _add_parent_node(self, node, child: pgv.Node) -> None:
        seq_len = 1
        if int('0' + child.attr['custom_looped']) != 1:
            seq_len += int(child.attr['custom_seq_len'])
        diverged = child.attr['custom_diverged'] == '1'
        return self._add_node(node, seq_len=seq_len, diverged=diverged, color=child.attr['color'] if diverged else '#00AAFF')

    def _unwind_loop(self, current_node: int, stack: deque[int]) -> None:
        loop = [current_node]
        prev_in_loop = stack.pop()
        while prev_in_loop != current_node:
            loop.append(prev_in_loop)
            prev_in_loop = stack.pop()
        self._add_looped_node(loop[0], len(loop))
        for i, loop_node in enumerate(loop[1:]):
            self._add_looped_node(loop_node, len(loop))
            self.G.add_edge(self._node_name(loop[i]), loop_node, dir='back')
        self.G.add_edge(self._node_name(loop[-1]), self._node_name(loop[0]), dir='back')

    def _trace_node(self, node: int) -> None:
        stack = deque()
        stack.append(node)
        while stack:
            current_node = stack.pop()
            current_node_name = self._node_name(current_node)
            if current_node_name in self._finished_nodes:
                continue
            if current_node in stack:
                self._unwind_loop(current_node, stack)
                continue
            
            edgeFound = False
            for v in self._edge_idx[current_node]:
                edgeFound = True
                if v == 1:
                    self._add_node(current_node, seq_len=1, color='#00FF00')
                    break
                elif self._node_name(v) in self._finished_nodes:
                    self._add_parent_node(current_node, self.G.get_node(v))
                    self.G.add_edge(self._node_name(v), self._node_name(current_node), dir='back')
                else:
                    stack.append(current_node)
                    stack.append(v)
                    break
            if not edgeFound:
                self._add_node(current_node, diverged=True, color='#FFCCAA', seq_len=1)

    def build(self, nodes: set[int], edges: set[tuple[int, int]]) -> pgv.AGraph:
        self._build_edge_idx(nodes, edges)
        for node in nodes:
            self._trace_node(node)
        return self.G
