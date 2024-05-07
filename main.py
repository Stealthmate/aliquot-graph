import pygraphviz as pgv
import typing
import colorsys
import math
from collections import deque

def node_color(seq_len: int) -> str:
    if seq_len == -1:
        return 'red'
    if seq_len == 0:
        return 'coral'
    if seq_len == 1:
        return 'green'
    hsv = (199 / 360, (1 + math.log(seq_len, 2)) / 20, 1.0)
    r, g, b = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*hsv))
    return f'#{r:02x}{g:02x}{b:02x}'

def get_next(i: int) -> int:
    q_sum = 1
    for j in range(2, math.ceil(math.sqrt(i))):
        if i % j == 0:
            q_sum += j + (i // j)
    return q_sum

def node_name(i: int) -> str:
    return f'{i}'

G = pgv.AGraph(name='Aliquot', directed=True, dpi=50)
G.node_attr['style'] = 'filled'
G.node_attr['color'] = 'grey'

for i in range(3, 1000):
    stack = deque()
    stack.append(i)
    print(i)
    while stack:
        x = stack.pop()
        if x > int(1e12):
            print('Nope', i, x)
            G.add_node(node_name(i), seq_len=-1)
            break
        if node_name(x) in G.nodes():
            break
        y = get_next(x)
        if y == 1:
            G.add_node(node_name(x), seq_len=1)
        elif y == x:
            G.add_node(node_name(x), seq_len=0)
            G.add_edge(node_name(x), node_name(x))
        elif node_name(y) in G.nodes():
            G.add_node(node_name(x), seq_len=int(G.get_node(y).attr['seq_len']) + 1)
            G.add_edge(node_name(y), node_name(x), dir='back')
        elif y in stack:
            stack_copy = list(stack.copy())
            stack = deque()
            last = stack_copy[-1]
            G.add_node(node_name(last), seq_len=len(stack_copy))
            for z in stack_copy[:-1:-1]:
                G.add_node(node_name(z), seq_len=len(stack_copy))
                G.add_edge(node_name(last), node_name(z), dir='back')
                last = z
        else:
            stack.append(x)
            stack.append(y)

for node in G.nodes_iter():
    node.attr['color'] = node_color(int(node.attr['seq_len']))
    if node.attr['seq_len'] in ['0', '1']:
        node.attr['rank'] = 'max'

G.write('source.dot')