import networkx as nx
import itertools
from networkx.algorithms.approximation import traveling_salesman_problem

def construct_graph(locations, routes):
    citygraph = nx.Graph()
    for loc in locations:
        citygraph.add_node(loc)
    for (frm, to, distance) in routes:
        citygraph.add_edge(frm, to, weight=distance)
    return citygraph

def brute_force_tsp(citygraph, source):
    # Brute force by checking all permutations of locations
    nodes = list(citygraph.nodes)
    nodes.remove(source)
    min_route = None
    min_cost = float('inf')

    for perm in itertools.permutations(nodes):
        route = [source] + list(perm)
        cost = 0
        valid = True
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if citygraph.has_edge(u, v):
                cost += citygraph[u][v]['weight']
            else:
                valid = False
                break
        if valid and cost < min_cost:
            min_cost = cost
            min_route = route

    return min_route, min_cost

def fix_start(shortest_route, source):
    # Rotate the path to always start at source
    idx = shortest_route.index(source)
    return shortest_route[idx:] + shortest_route[:idx]

def christofides_tsp(citygraph, source):
    # Use Christofides approximation (via networkx TSP API)
    tsp_path = traveling_salesman_problem(citygraph, cycle=False, weight='weight')
    tsp_path = fix_start(tsp_path, source)

    cost = 0
    for i in range(len(tsp_path) - 1):
        u, v = tsp_path[i], tsp_path[i + 1]
        cost += citygraph[u][v]['weight']

    return tsp_path, cost

def find_best_route(citygraph, source):
    # Decide based on size of input
    if len(citygraph.nodes) <= 6:
        return brute_force_tsp(citygraph, source)
    else:
        return christofides_tsp(citygraph, source)

if __name__ == "__main__":
    locations = ['narot', 'pathankot', 'bamial', 'kathua']
    routes = [
        ('narot', 'pathankot', 40),
        ('narot', 'bamial', 8),
        ('bamial', 'pathankot', 25),
        ('kathua', 'pathankot', 45),
        ('bamial', 'kathua', 35),
        ('narot', 'kathua', 15)
    ]

    citygraph = construct_graph(locations, routes)
    best_route, best_distance = find_best_route(citygraph, 'narot')

    print("\n📦 Optimal Delivery Route:")
    print(" → ".join(best_route))
    print("🚚 Total Distance:", best_distance, "km")
