import pygraphviz as pgv
import pickle
import math
from collections import deque
import os

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


def get_next(i: int) -> int:
    q_sum = 1
    for j in range(2, math.ceil(math.sqrt(i))):
        if i % j == 0:
            q_sum += j + (i // j)
    return q_sum

def generate_from(i: int) -> tuple[set[int], set[tuple[int, int]]]:
    nodes = set()
    edges = set()
    nodes.add(i)
    while True:
        next_i = get_next(i)
        if next_i > int(1e12):
            break
        edges.add((i, next_i))
        if next_i in nodes:
            break
        nodes.add(next_i)
        if next_i == 1:
            break
        i = next_i
    return (nodes, edges)

def generate_graph(start: int, end: int) -> tuple[set[int], set[tuple[int, int]]]:
    nodes = set()
    edges = set()

    for i_start in range(start, end):
        print(i_start)
        i = i_start
        nodes.add(i)
        while True:
            next_i = get_next(i)
            if next_i > int(1e12):
                break
            edges.add((i, next_i))
            if next_i in nodes:
                break
            nodes.add(next_i)
            if next_i == 1:
                break
            i = next_i
    nodes.remove(1)
    return (nodes, edges)

def node_name(i: int) -> str:
    return f'{i}'

def generate_dot_graph(nodes: set[int], edges: set[tuple[int, int]]) -> pgv.AGraph:
    edge_idx = {
        n: [v for u, v in edges if u == n]
        for n in nodes
    }
    print('built idx')
    G = pgv.AGraph(name='Aliquot', directed=True)
    G.node_attr['style'] = 'filled'
    G.node_attr['color'] = 'grey'

    finished_nodes: set[str] = set()

    for node in nodes:
        print(node)
        stack = deque()
        stack.append(node)
        while stack:
            current_node = stack.pop()
            print('', ' ' * len(stack), current_node)
            if node_name(current_node) in finished_nodes:
                continue
            if current_node in stack:
                loop = [current_node]
                prev_in_loop = stack.pop()
                while prev_in_loop != current_node:
                    loop.append(prev_in_loop)
                    prev_in_loop = stack.pop()
                G.add_node(node_name(loop[0]), **{ **LOOPED_NODE_ATTRS, 'custom_seq_len': len(loop) })
                finished_nodes.add(node_name(loop[0]))
                for i, loop_node in enumerate(loop[1:]):
                    G.add_node(node_name(loop_node), **{ **LOOPED_NODE_ATTRS, 'custom_seq_len': len(loop) })
                    finished_nodes.add(node_name(loop_node))
                    G.add_edge(loop[i], loop_node, dir='back')
                G.add_edge(node_name(loop[-1]), node_name(loop[0]), dir='back')
                continue
            
            edgeFound = False
            for v in edge_idx[current_node]:
                edgeFound = True
                if v == 1:
                    G.add_node(current_node, **{ **DEFAULT_NODE_ATTRS, 'custom_seq_len': '1' })
                    finished_nodes.add(node_name(current_node))
                    break
                elif node_name(v) in finished_nodes:
                    node_v = G.get_node(node_name(v))
                    seq_len = 1
                    if int('0' + node_v.attr['custom_looped']) != 1:
                        seq_len += int(node_v.attr['custom_seq_len'])
                    G.add_node(
                        node_name(current_node),
                        **{
                            **DEFAULT_NODE_ATTRS,
                            'custom_seq_len': seq_len,
                            'custom_diverged': node_v.attr['custom_diverged'],
                            'color': node_v.attr['color'] if node_v.attr['custom_diverged'] == '1' else '#00aaff'
                        }
                    )
                    finished_nodes.add(node_name(current_node))
                    G.add_edge(node_name(v), node_name(current_node), dir='back')
                else:
                    stack.append(current_node)
                    stack.append(v)
                    break
            if not edgeFound:
                G.add_node(node_name(current_node), **DIVERGED_NODE_ATTRS)
                finished_nodes.add(node_name(current_node))

    return G

nodes = set()
edges = set()
if os.path.exists('nodes.pkl'):
    print('loading')
    with open('nodes.pkl', mode='rb') as f:
        nodes = pickle.load(f)
    with open('edges.pkl', mode='rb') as f:
        edges = pickle.load(f)
else:
    nodes, edges = generate_graph(3, 10000)
with open('nodes.pkl', mode='wb') as f:
    pickle.dump(nodes, f)
with open('edges.pkl', mode='wb') as f:
    pickle.dump(edges, f)
print('generating', len(nodes), 'nodes and', len(edges), 'edges')
G = generate_dot_graph(nodes, edges)
G.write('source.dot')
