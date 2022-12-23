import re, csv, math, networkx as nx, matplotlib.pyplot as plt, json, plotly.express as px, pandas as pd
from urllib.request import urlopen

class County:
	def __init__(self, adjacent):
		self.adjacent = adjacent
		self.population = 0
		self.latitude = 0
		self.longitude = 0
	def distance(self, target):
		return 3958.7613 * math.acos(math.sin(math.radians(self.latitude)) * math.sin(math.radians(target.latitude)) + math.cos(math.radians(self.latitude)) * math.cos(math.radians(target.latitude)) * math.cos(math.radians(target.longitude - self.longitude)))
	def __repr__(self):
		return f"(Population: {self.population}, coordinates: {(self.latitude, self.longitude)}, adjacent to: {self.adjacent})"

counties = {}
with open("county_adjacency.txt", "r", encoding = "latin1") as adjacencies:
	response = adjacencies.read().split("\n\"")
	for county in response:
		fips = re.findall(r"(\d{5})", county)
		counties[fips[0]] = County([x for x in fips[1 : ] if x != fips[0]])

with open("CenPop2020_Mean_CO.txt", "r") as populations:
	reader = csv.reader(populations)
	next(reader)
	for row in reader:
		try:
			counties[row[0] + row[1]].population = int(row[4])
			counties[row[0] + row[1]].latitude = float(row[5])
			counties[row[0] + row[1]].longitude = float(row[6])
		except KeyError:
			counties[row[0] + row[1]] = County([])
			counties[row[0] + row[1]].population = 0
			counties[row[0] + row[1]].latitude = 0
			counties[row[0] + row[1]].longitude = 0

def weight(start, end, attributes):
	global counties
	return counties[start].distance(counties[end]) / (counties[end].population + 1)

g = nx.Graph()
g.add_nodes_from([(x, {"weight": counties[x].population}) for x in counties][ : 100])
edges = []
for county in counties:
	for a in counties[county].adjacent:
		edges.append((county, a))
g.add_edges_from(edges)
shortest = nx.shortest_path(g, source = "53033", target = "12086", weight = weight)

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    county_info = json.load(response)

df = pd.DataFrame(data = {"fips": list(counties.keys()), "visited": [int(x in shortest) for x in counties]})
fig = px.choropleth(df, geojson = county_info, locations = "fips", color = "visited", scope = "usa")
fig.show()
