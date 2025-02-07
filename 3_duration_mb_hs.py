import pickle
import numpy as np
import pandas as pd
import re
import requests as req
from tqdm import tqdm
from geopy import distance as gpdist


# return duration and distance to health service closest to mesh block coordinates
def get_metrics(row, tree):
    min_duration, min_distance, longitude_closest, latitude_closest = np.nan, np.nan, np.nan, np.nan

    if (row['Person'] > 0) and (not np.isnan(row['longitude'])):
        # get coordinates of 10 closes health services
        tree_data, _, _, _ = tree.get_arrays()
        indices = tree.query(row[['longitude', 'latitude']].to_numpy().reshape(1, -1), k=10,
                             return_distance=False, sort_results=False)
        health_service_coordinates = tree_data[indices.squeeze(), :]

        # create string of hospital longitude1,latitude1;longitude2,latitude2;...
        health_service_coordinates_str = ','.join(map(str, health_service_coordinates.flatten().tolist()))
        health_service_coordinates_str = re.sub('(,[^,]*),', r'\1;', health_service_coordinates_str)

        # compute durations using OSRM table service
        url = ('http://127.0.0.1:5000/table/v1/driving/' + str(row['longitude']) + ',' + str(row['latitude']) + ';'
               + health_service_coordinates_str + '?sources=0')
        response = req.get(url)

        # get closest health service (in terms of trip duration)
        s = response.text
        start = '"durations":[[0,'
        end = ']]'
        durations = s[s.find(start) + len(start):s.rfind(end)].split(',')
        durations = [d if d != 'null' else '1e10' for d in durations]  # map nulls to very high duration in seconds
        durations = np.array(durations, dtype=np.float32)
        index_min_duration = durations.argmin()

        # compute duration and distance to closest health service using OSRM route service
        longitude_closest = health_service_coordinates[index_min_duration, 0]
        latitude_closest = health_service_coordinates[index_min_duration, 1]
        url = ('http://127.0.0.1:5000/route/v1/driving/' + str(row['longitude']) + ',' + str(row['latitude']) + ';'
               + str(longitude_closest) + ',' + str(latitude_closest) + '?overview=false')
        response = req.get(url)

        # get duration and distance to closest health service
        s = response.text
        # extract substring with duration and distance
        start = '"weight_name":"routability"'
        end = '"waypoints"'
        s = s[s.find(start) + len(start):s.rfind(end)]
        # extract duration and distance
        start = '"duration":'
        end = ',"distance"'
        min_duration = s[s.find(start) + len(start):s.rfind(end)]
        start = '"distance":'
        end = '}],'
        min_distance = s[s.find(start) + len(start):s.rfind(end)]

        try:
            # convert strings to numbers if successful
            min_duration = float(min_duration)
            min_distance = float(min_distance)
        except:
            # otherwise compute 'as the crow flies' distance between MB and health service
            c_lon, c_lat = row["longitude"], row["latitude"]
            h_lon = health_service_coordinates[index_min_duration, 0]
            h_lat = health_service_coordinates[index_min_duration, 1]
            dist = gpdist.distance((c_lat, c_lon), (h_lat, h_lon)).m
            print(f'Warning, cannot find driving route between {(str(c_lat), str(c_lon))} and '
                  f'{(str(h_lat), str(h_lon))}. The distance between the two is {dist}m.')
            if dist < 100:  # no route found because MB centroid and health service are very close
                min_duration, min_distance = 0, 0
            else:  # no route found between MB and health service, this can be the case for islands
                min_duration, min_distance = np.nan, np.nan

    return min_duration, min_distance, longitude_closest, latitude_closest


if __name__ == '__main__':
    # compute distances between mesh blocks and hospitals
    dtype = {'MB_CODE21': 'int64',
             'SA2_CODE21': 'int64',
             'STE_CODE21': 'int32',
             'STE_NAME21': 'str',
             'MMM2019': 'float32',
             'POA_CODE_2021': 'int64',
             'longitude': 'float32',
             'latitude': 'float32',
             'Person': 'int32'}
    df = pd.read_csv('./data/mb_2021_merged.csv', usecols=dtype.keys(), dtype=dtype)

    # read in the K-D Trees to quickly get nearest health services
    dict_trees = pickle.load(open('./data/dict_trees', 'rb'))

    # iterate over health service type
    for health_service in ['hospital', 'gp', 'gp_bulk_billing', 'emergency']:
        tree = dict_trees[health_service]

        # store durations, distances and coordinates
        duration_list = []
        distance_list = []
        longitude_list = []
        latitude_list = []

        # iterate over mesh blocks
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            duration, distance, longitude_closest, latitude_closest = get_metrics(row, tree)
            duration_list.append(duration)
            distance_list.append(distance)
            longitude_list.append(longitude_closest)
            latitude_list.append(latitude_closest)

        # create new columns with durations, distances and coordinates
        df[health_service + '_duration'] = pd.Series(duration_list)
        df[health_service + '_distance'] = pd.Series(distance_list)
        df[health_service + '_longitude'] = pd.Series(longitude_list)
        df[health_service + '_latitude'] = pd.Series(latitude_list)

    # write out distances, durations and coordinates
    df.to_csv('./data/mb_2021_distances.csv', index=False)
