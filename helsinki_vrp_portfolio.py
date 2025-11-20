import math
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import contextily as ctx
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# ---------------------------
# 1. Load data
# ---------------------------
df = pd.read_csv("helsinki_vrp.csv")

cities = df["city"].tolist()
lats = df["lat"].tolist()
lons = df["lon"].tolist()
demands = df["demand"].tolist()
time_windows = list(zip(df["tw_start"], df["tw_end"]))

num_nodes = len(cities)
depot_index = 0

num_vehicles = 3
vehicle_capacities = [15, 15, 15]

# ---------------------------
# 2. Distance & time matrix
# ---------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# distance in km and travel time in minutes (assume 30 km/h → 2 min per km)
dist_matrix = [[0]*num_nodes for _ in range(num_nodes)]
time_matrix = [[0]*num_nodes for _ in range(num_nodes)]

for i in range(num_nodes):
    for j in range(num_nodes):
        if i == j:
            continue
        d = haversine(lats[i], lons[i], lats[j], lons[j])
        dist_matrix[i][j] = d
        time_matrix[i][j] = int(round(d * 2))  # minutes

# ---------------------------
# 3. OR-Tools VRPTW + Capacity
# ---------------------------
manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot_index)
routing = pywrapcp.RoutingModel(manager)

def time_callback(from_index, to_index):
    f = manager.IndexToNode(from_index)
    t = manager.IndexToNode(to_index)
    return time_matrix[f][t]

transit_callback_index = routing.RegisterTransitCallback(time_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Capacity dimension
def demand_callback(from_index):
    node = manager.IndexToNode(from_index)
    return demands[node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,                    # no slack
    vehicle_capacities,   # capacity of each vehicle
    True,
    "Capacity"
)

# Time dimension
max_route_duration = 240  # minutes
routing.AddDimension(
    transit_callback_index,
    30,                    # waiting allowed
    max_route_duration,
    False,
    "Time"
)

time_dim = routing.GetDimensionOrDie("Time")

# Time windows for each node
for node_idx, (start, end) in enumerate(time_windows):
    index = manager.NodeToIndex(node_idx)
    time_dim.CumulVar(index).SetRange(start, end)

# Depot start times
for v in range(num_vehicles):
    start_index = routing.Start(v)
    time_dim.CumulVar(start_index).SetRange(0, max_route_duration)

# Search parameters
params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
params.time_limit.seconds = 10

solution = routing.SolveWithParameters(params)

if not solution:
    print("No solution found.")
    exit()

# ---------------------------
# 4. Extract routes per vehicle
# ---------------------------
vehicle_routes = {}
vehicle_times = {}
vehicle_loads = {}

for v in range(num_vehicles):
    index = routing.Start(v)
    route_nodes = []
    route_times = []
    total_load = 0

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        tvar = time_dim.CumulVar(index)
        time_val = solution.Value(tvar)
        route_nodes.append(node)
        route_times.append(time_val)
        total_load += demands[node]
        index = solution.Value(routing.NextVar(index))

    # add final depot
    node = manager.IndexToNode(index)
    tvar = time_dim.CumulVar(index)
    time_val = solution.Value(tvar)
    route_nodes.append(node)
    route_times.append(time_val)

    if len(route_nodes) > 2:  # ignore empty routes (depot -> depot)
        vehicle_routes[v] = route_nodes
        vehicle_times[v] = route_times
        vehicle_loads[v] = total_load

# Print routes (nice for console)
for v, nodes in vehicle_routes.items():
    names = [cities[i] for i in nodes]
    times_v = vehicle_times[v]
    print(f"\nVehicle {v} route (load={vehicle_loads[v]}):")
    for name, t in zip(names, times_v):
        print(f"  {name} at t={t}")
    print()

# ---------------------------
# 5. Map visualization
# ---------------------------
# GeoDataFrame of points
gdf_points = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["lon"], df["lat"]),
    crs="EPSG:4326"
).to_crs(epsg=3857)

coords = {row["city"]: row.geometry for _, row in gdf_points.iterrows()}

colors = ["blue", "red", "orange", "purple", "brown"]

fig, ax = plt.subplots(figsize=(12, 10))

# Plot each vehicle route
for idx, (v, nodes) in enumerate(vehicle_routes.items()):
    route_cities = [cities[i] for i in nodes]
    pts = [coords[c] for c in route_cities]
    line = LineString(pts)

    color = colors[idx % len(colors)]

    gpd.GeoSeries([line], crs="EPSG:3857").plot(
        ax=ax, linewidth=3.5, color=color, alpha=0.9, label=f"Vehicle {v}"
    )

    # Draw arrows
    for i in range(len(pts) - 1):
        ax.annotate(
            "",
            xy=(pts[i+1].x, pts[i+1].y),
            xytext=(pts[i].x, pts[i].y),
            arrowprops=dict(arrowstyle="->", color=color, lw=2),
        )

# Plot points
for _, row in gdf_points.iterrows():
    p = row.geometry
    name = row["city"]
    if _ == depot_index:
        ax.scatter(p.x, p.y, s=260, color="green", edgecolor="black", zorder=5)
        ax.text(p.x + 60, p.y + 60, f"{name} (Depot)", fontsize=13, color="green", fontweight="bold")
    else:
        ax.scatter(p.x, p.y, s=150, color="black", zorder=5)
        ax.text(p.x + 60, p.y + 60, name, fontsize=11)

# Basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

plt.title("Helsinki Multi-Vehicle Routing Optimization (VRP with Time Windows & Capacities)", fontsize=16)
plt.legend(fontsize=10)
ax.set_xticks([])
ax.set_yticks([])
plt.tight_layout()

# Save for portfolio
plt.savefig("helsinki_vrp_portfolio.png", dpi=300)
plt.savefig("helsinki_vrp_portfolio.pdf", dpi=300)

plt.show()
