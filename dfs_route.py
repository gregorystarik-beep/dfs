import requests
import os
import pandas as pd
##import osmnx as ox
import networkx as nx
from matplotlib import pyplot as plt
import urllib.parse
import ast
def build_graph_from_api(api_url):
    pos_dict={}
    file_name:str= "my_graph_data.csv"
    if os.path.exists(file_name):##for offline
       df = pd.read_csv(file_name)# noqa
       df["nodes"]=df["nodes"].apply(lambda x: ast.literal_eval(x)if isinstance(x, str) else x)##fixes nodes from string to list
    else:##for online
        headers = {'User-Agent': 'DFS_Route_Project_Greg/1.0 (gregory.starik@gmail.com)'}##a dictionary who tells who am I
        r = requests.get(api_url, headers=headers,timeout=60)##we get the api give our info from the header and give a time limit


        print("Status:", r.status_code)
        print("Server Response:", r.text)
        if r.status_code != 200 or not r.text.strip():
            raise Exception(f"Server returned empty or error response. Status: {r.status_code}, Text: {r.text}")
        df = pd.DataFrame(r.json()["elements"])
        df.to_csv(file_name, index=False)
    graph ={ }##graph is a dictionary the key is the node the value list of all nodes
    for i,row in df.iterrows():
        ##extarcting from data frame cols to nodes in graph
        if row["type"] == "way":##found way
            neighbors = row["nodes"]
            for j in range(len(neighbors) - 1):##loop runs on road
                u = neighbors[j]##node u
                v = neighbors[j + 1]##node v
                if u not in graph:
                    graph[u] = []##if u is not in graph we put blank
                if v not in graph:
                    graph[v] = []##if v is not in graph we put blank
                graph[u].append(v)##everyting normal we put in list both to create graph
                graph[v].append(u)
        if row["type"]=="node":
            node_id=row["id"]##take id to create position on graph
            lat=row["lat"]
            lon=row["lon"]
            pos_dict[node_id]=(lat,lon)
    return graph,pos_dict
def dfs_find_path(graph, current_node, target_node, path=None, visited=None):
    if path is None:
        path=[]##if path is null
    if visited is None:
        visited = set()##if visited is empty we use set because it uses c(n,k)
    path.append(current_node)##we add the current node to the path and visited
    visited.add(current_node)
    if current_node == target_node:##if we got to our destination
        return path
    for neighbor in graph.get(current_node, []):##if not we do dfs on the graph
        if neighbor not in visited:##if we haven't visited the node
            res = dfs_find_path(graph, neighbor, target_node, path, visited)##we do recursion
            if res is not None:##if we found a path
                return res
        if path:
            path.pop()##if got to an end of a line and want to go back
    return None
if __name__ == '__main__':
    query = '[out:json][timeout:25];way["highway"](32.015,34.773,32.016,34.775);(._;>;);out skel;'##שאילתה
    api_url_main = f"https://overpass-api.de/api/interpreter?data={urllib.parse.quote(query)}"##the api
   ## print(api_url_main)
    my_graph,my_pos = build_graph_from_api(api_url_main)##graph and position
    largest = max(nx.connected_components(nx.Graph(my_graph)),key=len)##find the largest part the is connected
    node_list= list(largest)# noqa
    start_node =node_list[0]
    end_node = node_list[-1]
    path_result = dfs_find_path(my_graph, start_node, end_node)##the result of the dfs search
    print("Found path:", path_result)
    ##giving a picture of graph
    G=nx.Graph(my_graph)
    nx.draw_networkx(G,pos=my_pos ,with_labels=False,node_size=30,node_color = 'blue')# noqa##node are blue
    if path_result is not None and len(path_result)>0:
       nx.draw_networkx_nodes(G, pos=my_pos, nodelist=path_result,node_size=60, node_color='red')##connected nodes are red
       path_edges = list(zip(path_result,path_result[1:]))##merges path
       nx.draw_networkx_edges(G,pos=my_pos,edgelist=path_edges,edge_color='red',width=2)##colors path in red
    plt.show()


