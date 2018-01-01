"""
Will identify and write xml files from all path images in the current directory

Path images have red lines and nodes created at every intersection.
Green lines represent stairs.

a path must be ORTHOGONALLY connected to create a path.

pixels adjacent to only two other pixels are considered part of an edges.
pixels adjacent to one or three or more pixels are considered a node
"""

from PIL import Image
from lxml import etree as ET
import os

EMPTY = (0, 0, 0)
MAIN_COLOR = (255, 0, 0)
STAIR_COLOR = (0, 255, 0)
FLAT = "FLAT"
STAIR = "STAIR"

class Node:
    def __init__(self, pos):
        self.neighbors = set()
        self.name = "None"
        self.edges = dict()
        self.pos = pos
    
    def add_neighbor(self, neighbor, type):
        self.neighbors.add(neighbor)
        self.edges[neighbor] = type
    
def get_pixel_safe(image, x, y):
    if x < 0 or x >= image.width or y < 0 or y >= image.height:
        return EMPTY
    return image.getpixel((x, y))

def get_num_adj(image, x, y):
    total = 0
    for pixel in [(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)]:
        if get_pixel_safe(image, pixel[0], pixel[1]) != EMPTY:
            total += 1
    return total

def is_node(image, x, y):
    total = 0
    px = get_pixel_safe(image, x, y)
    if px == EMPTY:
        return False
    for pixel in [(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)]:
        if get_pixel_safe(image, pixel[0], pixel[1]) != EMPTY:
            if px == MAIN_COLOR and get_pixel_safe(image, pixel[0], pixel[1]) != px:
                return True
            total += 1
    return total > 0 and total != 2
    
def find_adj(image, nodes, x, y):
    checked = set()
    start = (x, y)
    def get_adj(x, y, stair=False):
        if (x, y) in checked or get_pixel_safe(image, x, y) == EMPTY:
            return set()
        if get_pixel_safe(image, x, y) == STAIR_COLOR:
            stair = True
        if (x, y) in nodes and (x, y) != start:
            if stair:
                return set([((x, y), STAIR)])
            else:
                return set([((x, y), FLAT)])
        checked.add((x, y))
        return get_adj(x + 1, y, stair) | get_adj(x - 1, y, stair) | get_adj(x, y + 1, stair) | get_adj(x, y - 1, stair)
    return get_adj(x, y)
    
for file in [f for f in os.listdir(".") if f.endswith("PATH.png")]:
    print("Processing " + file)
    name, floor, _ = file.split('-')
    img = Image.open(file, 'r').convert("RGB")
    w, h = img.size
    
    nodes = dict()
    
    for x in range(w):
        for y in range(h):
            if is_node(img, x, y):
                nodes[(x, y)] = Node((x, y))
    edges = 0
    for pos in nodes:
        node = nodes[pos]
        adj_nodes = find_adj(img, nodes, pos[0], pos[1])
        for adj_val in adj_nodes:
            adj_pos, type = adj_val
            node.add_neighbor(adj_pos, type)
        edges += len(adj_nodes)
    
    edges //= 2
    num = len(nodes)
    print("Graph has " + str(num) + " nodes and " + str(edges) + " edges")
    
    root = ET.Element("Map", name=name, floor = str(int(floor)), edges = str(edges), nodes = str(num))
    for pos in nodes:
        point = ET.SubElement(root, "Node", name = node.name, pos = str(pos))
        node = nodes[pos]
        for neighbor in node.neighbors:
            neighbor = ET.SubElement(point, "Edge", name = node.name, to = str(neighbor), type = node.edges[neighbor])
    tree = ET.ElementTree(root)
    tree.write(name + "-" + floor + "-" + "map.xml", pretty_print=True)
    print("Write file out to '" + name + "-" + floor + "-" + "map.xml" + "'")
