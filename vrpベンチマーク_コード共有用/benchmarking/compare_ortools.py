# %% [markdown]
# # Compare solvers

# %%
import os
import re
import subprocess
import time
import datetime as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from itertools import permutations
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

DATA_DIR_PATH = '../DATA/SINTEF/100cust'
INSTANCE_NAMES = ['c101', 'c201', 'r101', 'r102', 'r201', 'rc101', 'rc102']

def compare(instance_name):
    # # %%
    # DATA_DIR_PATH = '../DATA/SINTEF/100cust'
    # INSTANCE_NAME = 'r201'
    # %% [markdown]
    # ## Read Test Files

    # %%
    instance_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}.txt'
    )
    instance_df = pd.read_csv(
        instance_file_path, 
        skiprows=8, 
        delim_whitespace=True, 
        header=None)
    instance_df.columns=[
        'CUST NO.', 
        'XCOORD', 
        'YCOORD', 
        'DEMAND', 
        'READY TIME', 
        'DUE DATE', 
        'SERVICE TIME']
    instance_df

    # %%
    fig = px.scatter(
        instance_df, 
        x="XCOORD", y="YCOORD", 
        text=instance_df['CUST NO.'], 
        width=1000, height=800)
    fig.show()

    # %%
    # save
    img_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}.png'
    )
    fig.write_image(img_file_path)

    # %% [markdown]
    # ## File creations

    # %% [markdown]
    # ### Input File

    # %%
    # make input data
    start_date = pd.to_datetime('1/1/2017')
    input_df = instance_df.copy()
    input_df = input_df.rename(
        columns={
        'XCOORD':'LATITUDE', 'YCOORD':'LONGITUDE',
        'READY TIME':'FROM TIME', 'DUE DATE':'TO TIME'})
    input_df['FROM TIME'] = input_df['FROM TIME'].apply(
        lambda x: (start_date + dt.timedelta(minutes = x)).strftime('%Y/%m/%d %H:%M:%S'))
    input_df['TO TIME'] = input_df['TO TIME'].apply(
        lambda x: (start_date + dt.timedelta(minutes = x)).strftime('%Y/%m/%d %H:%M:%S'))

    # %%
    # save
    input_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_input.csv'
    )
    input_df.to_csv(input_file_path, index=False)

    # %% [markdown]
    # ### Distance File

    # %%
    # make distance data
    distance_df = [
        [src, dst] 
        for src, dst in permutations(instance_df['CUST NO.'], 2)
        ]
    distance_df = pd.DataFrame(distance_df, columns=['START', 'END'])
    coords = instance_df.set_index('CUST NO.')
    distance_df['START_x'] = coords.loc[distance_df['START'], 'XCOORD'].values
    distance_df['START_y'] = coords.loc[distance_df['START'], 'YCOORD'].values
    distance_df['END_x'] = coords.loc[distance_df['END'], 'XCOORD'].values
    distance_df['END_y'] = coords.loc[distance_df['END'], 'YCOORD'].values
    distance_df['DIFF_x'] = distance_df['END_x']-distance_df['START_x']
    distance_df['DIFF_y'] = distance_df['END_y']-distance_df['START_y']
    distance_df['METERS'] = 1000*(distance_df['DIFF_x']**2+distance_df['DIFF_y']**2)**(1/2)
    distance_df['KM'] = (distance_df['METERS']/1000).astype(int)
    distance_df.head()

    # %%
    # save
    distance_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_dist.csv'
    )
    distance_df = distance_df[['START', 'END', 'METERS']]
    distance_df.to_csv(distance_file_path, index=False, header=False)

    # %% [markdown]
    # ### Time File

    # %%
    # make distance data
    time_df = distance_df[['START', 'END', 'METERS']]
    time_df['HRS'] = time_df['METERS']/(60*1000)

    # %%
    # save
    time_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_time.csv'
    )
    time_df = time_df[['START', 'END', 'HRS']]
    time_df.to_csv(time_file_path, index=False, header=False)

    # %% [markdown]
    # ### Other config

    # %%
    # make other cofig data
    conf_df = pd.read_csv(
        instance_file_path, 
        skiprows=3,
        nrows=1,
        delim_whitespace=True, 
        header=0).T
    conf_df

    # %%
    # save
    conf_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_conf.csv'
    )
    conf_df.to_csv(conf_file_path, header=False)

    # %% [markdown]
    # ## Run CARG Solver

    # %%
    output_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_output_CARG.csv'
    )
    start_time = input_df['FROM TIME'].min()
    end_time = input_df['TO TIME'].max()
    vehicle_num = conf_df.loc['NUMBER', 0]
    capacity = conf_df.loc['CAPACITY', 0]

    # %%
    std_out = subprocess.check_output([
            "pypy","../vrp_classical/code/main_tw.py",
            "-i", input_file_path,
            "-d", distance_file_path,
            "-t", time_file_path,
            "-o", output_file_path,
            "-v", str(vehicle_num), 
            "-rv", # reduce vehicle
            "-s", start_time,
            "-e", end_time,
            # "-mt", #multi-trip (rotation)
            "-dem", str(capacity),
            "-lpt", "hard", # hard constraint on package weight v.s. vehicle capacity
            #"-lpt", "soft", # hard constraint on package weight v.s. vehicle capacity
            #"-avedistper", "10"
            # "-l" #1.20.2022
            # "-multithread", "0"
            ])

    # %% [markdown]
    # ### Extract Results

    # %%
    result_df = {}

    # %%
    # extract results from detail output file
    detail_output_file_path = f'{output_file_path}.detail.csv'
    with open(detail_output_file_path, 'r') as f:
        lines = f.readlines()
    for l in lines:
        if 'TOTALCOST,' in l:
            result_df['TOTALCOST'] =\
                float(l.split(',')[1].replace('\n', ''))/1000

    # %%
    # extract results from std output
    pat = re.compile(r"=====.*?=====")
    texts = std_out.decode().split('\n')
    texts = [t for t in texts if pat.match(t)]
    result_row = texts.index('='*39)
    texts = texts[result_row:]
    pat = re.compile(r"[\d\.]+")
    result_cols = [
        'TOTAL_NUMBER_OF VEHICLES',
        'CONSTRUCTION_TIME',
        'IMPROVEMENT_TIME']
    for c in result_cols:
        for t in texts:
            if c in t:
                result_df[c] = float(pat.findall(t)[0])
    result_df['ELAPSED_TIME'] =\
        result_df['CONSTRUCTION_TIME']+result_df['IMPROVEMENT_TIME']

    # %%
    result_df = pd.Series(result_df).to_frame()
    result_df

    # %%
    # save
    result_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_result_CARG.csv'
    )
    result_df.to_csv(result_file_path, header=False)

    # %% [markdown]
    # ### Plot Route

    # %%
    # extract routes
    routes_df = []
    # get route
    pat = re.compile(r"[\d\.]+")
    with open(output_file_path, "r") as f:
        lines = f.read().splitlines()
        for line in lines[1:]:
            line = line.split(',')
            v = pat.findall(line[0])[0]
            pre_cust = 0
            for cust in line[1:]:
                cust = int(cust)
                routes_df.append([v, cust, pre_cust])
                pre_cust = cust
    routes_df = pd.DataFrame(
        routes_df, 
        columns=['vehicle', 'customer', 'pre_customer'])
    # get order
    routes_df['order'] = 1
    routes_df['order'] = routes_df.groupby('vehicle')['order'].cumsum()
    routes_df['order'] -= 1
    # get coordinate
    coords = instance_df.set_index('CUST NO.')
    routes_df['x'] = coords.loc[routes_df['customer'], 'XCOORD'].values
    routes_df['y'] = coords.loc[routes_df['customer'], 'YCOORD'].values
    # get demand
    demands = instance_df.set_index('CUST NO.')
    routes_df['demand'] = demands.loc[routes_df['customer'], 'DEMAND'].values
    routes_df['total_demand'] = routes_df.groupby('vehicle')['demand'].cumsum()
    # get distance
    dists = distance_df.set_index(['START', 'END'])
    dists.loc[(0,0), 'METERS'] = 0
    routes_df['distance'] =\
        dists.loc[
            routes_df.set_index(['customer', 'pre_customer']).index,
            'METERS'].values
    routes_df['total_distance'] =\
        routes_df.groupby('vehicle')['distance'].cumsum()

    # %%
    # plot routes
    vehicle_num = int(result_df.loc['TOTAL_NUMBER_OF VEHICLES', 0])
    total_cost = result_df.loc['TOTALCOST', 0]
    fig = px.line(
        routes_df, 
        x='x', y='y', 
        color='vehicle',
        hover_data=['order', 'x', 'y', 'demand', 'total_distance', 'total_demand'],
        text=routes_df['customer'],
        title=f'VEHICLE_NUM:{vehicle_num}\tDISTANCE:{total_cost}',
        width=1000, height=800)

    center = instance_df.set_index(
        'CUST NO.').loc[0, ['XCOORD', 'YCOORD']].values
    for vehicle, df in routes_df.groupby('vehicle'):
        no_stop = len(df)
        total_dist = int(df['total_distance'].iloc[-1]/1000)
        total_dem = int(df['total_demand'].iloc[-1])
        fig.add_trace(go.Scatter(
            name=f'{no_stop} Deliveries ({total_dist}km, {total_dem}pkg)',
            x=center[0:1], y=center[1:2],
            mode='markers', 
            marker=go.scatter.Marker(size=0),
            legendgroup=vehicle))
        
    fig.add_trace(
        go.Scatter(
            name='Central Depot', 
            x=center[0:1], y=center[1:2], 
            mode='markers',
            marker=go.scatter.Marker(size=15, color=px.colors.qualitative.G10[-2],opacity=0.9)))

    fig.show()

    # %%
    # save
    img_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_route_CARG.png'
    )
    fig.write_image(img_file_path)

    # %% [markdown]
    # ## Run OR-tools Solver

    # %%
    # make data
    data = {}
    data['distance_matrix'] =\
        distance_df.pivot_table(
            index=['START'], 
            columns=['END'],
            values=['METERS'], 
            aggfunc='first').fillna(0)
    data['distance_matrix'] = data['distance_matrix'].astype(int).values
    data['num_vehicles'] = int(conf_df.loc['NUMBER', 0])
    # data['num_vehicles'] = int(vehicle_num_carg)
    data['depot'] = 0
    data['demands'] = input_df.set_index('CUST NO.')['DEMAND'].tolist()
    data['vehicle_capacities'] = [capacity]*data['num_vehicles']
    data['time_windows'] = (instance_df[['READY TIME', 'DUE DATE']]*1000).values
    data['time_matrix'] = data['distance_matrix']
    data['service_time'] = (instance_df['SERVICE TIME']*1000).values

    # %%
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'], data['depot'])
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # %%
    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # %%
    # Demand Constraint
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # %%
    # Time Constraint
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node] + data['service_time'][from_node]

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    dimension_name = 'Time'
    routing.AddDimension(
        time_callback_index,
        int(data['time_windows'].max()),  # allow waiting time
        int(data['time_windows'].max()),  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(int(time_window[0]), int(time_window[1]))
    # Add time window constraints for each vehicle start node.
    depot_idx = data['depot']
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            int(data['time_windows'][depot_idx][0]),
            int(data['time_windows'][depot_idx][1]))
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # %%
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION)

    # %%
    # Solve the problem.
    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    elapsed_time = time.time()-start_time

    # %% [markdown]
    # ### Extract Results

    # %%
    # extract route
    routes_df = []
    max_route_distance = 0
    for vehicle in range(data['num_vehicles']):
        index = routing.Start(vehicle)
        previous_index = index
        route_distance = 0
        while not routing.IsEnd(index):
            cust = manager.IndexToNode(index)
            pre_cust = manager.IndexToNode(previous_index)
            routes_df.append([vehicle, cust, pre_cust])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle)
        cust = manager.IndexToNode(index)
        pre_cust = manager.IndexToNode(previous_index)
        routes_df.append([vehicle, cust, pre_cust])
        max_route_distance = max(route_distance, max_route_distance)
    routes_df = pd.DataFrame(
        routes_df, 
        columns=['vehicle', 'customer', 'pre_customer'])
    # get order
    routes_df['order'] = 1
    routes_df['order'] = routes_df.groupby('vehicle')['order'].cumsum()
    routes_df['order'] -= 1
    # get coordinate
    coords = instance_df.set_index('CUST NO.')
    routes_df['x'] = coords.loc[routes_df['customer'], 'XCOORD'].values
    routes_df['y'] = coords.loc[routes_df['customer'], 'YCOORD'].values
    # get demand
    demands = instance_df.set_index('CUST NO.')
    routes_df['demand'] = demands.loc[routes_df['customer'], 'DEMAND'].values
    routes_df['total_demand'] = routes_df.groupby('vehicle')['demand'].cumsum()
    # get distance
    dists = distance_df.set_index(['START', 'END'])
    dists.loc[(0,0), 'METERS'] = 0
    routes_df['distance'] =\
        dists.loc[
            routes_df.set_index(['customer', 'pre_customer']).index,
            'METERS'].values
    routes_df['total_distance'] =\
        routes_df.groupby('vehicle')['distance'].cumsum()
    # drop non used vehicles
    active_vehicles = (routes_df.groupby('vehicle')['distance'].sum()>0).to_dict()
    active_vehicles = [k for k,v in active_vehicles.items() if v]
    routes_df = routes_df[routes_df['vehicle'].isin(active_vehicles)]
    reindex = {
        v:new_v for v, new_v in zip(active_vehicles, range(len(active_vehicles)))}
    routes_df['vehicle'] = routes_df['vehicle'].map(reindex)
    routes_df

    # %%
    # make result
    result_df = {}
    result_df['TOTALCOST'] =\
        routes_df.groupby('vehicle')['total_distance'].last().sum()/1000
    result_df['TOTAL_NUMBER_OF VEHICLES'] = len(routes_df['vehicle'].unique())
    result_df['ELAPSED_TIME'] = elapsed_time
    result_df = pd.Series(result_df).to_frame()
    result_df

    # %%
    # save
    result_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_result_ortools.csv'
    )
    result_df.to_csv(result_file_path, header=False)

    # %%
    # make route output
    output_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_output_ortools.csv'
    )
    with open(output_file_path, 'w', newline='\n') as f:
        f.write('route#,Id\n')
        for v, df in routes_df.groupby('vehicle'):
            line = ','.join([f'route{v}'] + df['customer'].astype(str).to_list())
            line += '\n'
            f.write(line)

    # %%
    result_df

    # %% [markdown]
    # ### Plot Route

    # %%
    # plot routes
    vehicle_num = int(result_df.loc['TOTAL_NUMBER_OF VEHICLES', 0])
    total_cost = result_df.loc['TOTALCOST', 0]
    fig = px.line(
        routes_df, 
        x='x', y='y', 
        color='vehicle',
        hover_data=['order', 'x', 'y', 'demand', 'total_distance', 'total_demand'],
        text=routes_df['customer'],
        title=f'VEHICLE_NUM:{vehicle_num}\tDISTANCE:{total_cost}',
        width=1000, height=800)

    center = instance_df.set_index(
        'CUST NO.').loc[0, ['XCOORD', 'YCOORD']].values
    for vehicle, df in routes_df.groupby('vehicle'):
        no_stop = len(df)
        total_dist = int(df['total_distance'].iloc[-1]/1000)
        total_dem = int(df['total_demand'].iloc[-1])
        fig.add_trace(go.Scatter(
            name=f'{no_stop} Deliveries ({total_dist}km, {total_dem}pkg)',
            x=center[0:1], y=center[1:2],
            mode='markers', 
            marker=go.scatter.Marker(size=0),
            legendgroup=vehicle))
        
    fig.add_trace(
        go.Scatter(
            name='Central Depot', 
            x=center[0:1], y=center[1:2], 
            mode='markers',
            marker=go.scatter.Marker(size=15, color=px.colors.qualitative.G10[-2],opacity=0.9)))

    fig.show()

    # %%
    # save
    img_file_path = os.path.join(
        DATA_DIR_PATH, f'{instance_name}_route_ortools.png'
    )
    fig.write_image(img_file_path)

# %%

if __name__=='__main__':
    for ins in INSTANCE_NAMES:
        print(ins)
        compare(ins)

