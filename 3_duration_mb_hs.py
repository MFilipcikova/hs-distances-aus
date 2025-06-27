import pickle
import numpy as np
import pandas as pd
import re
import requests as req
from tqdm import tqdm


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
               + health_service_coordinates_str + '?sources=0&annotations=duration,distance')
        response = req.get(url)

        # get closest health service (in terms of trip duration), duration and distance to it
        s = response.json()
        if s['code'] == 'Ok':
            try:
                index_min_duration = np.nanargmin(np.array(s['durations'][0][1:], dtype=float))
                min_duration = s['durations'][0][index_min_duration + 1]
                min_distance = s['distances'][0][index_min_duration + 1]
                longitude_closest = s['destinations'][index_min_duration + 1]['location'][0]
                latitude_closest = s['destinations'][index_min_duration + 1]['location'][1]
            except ValueError:  # all nan durations
                return np.nan, np.nan, np.nan, np.nan
        else:
            print(s)

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
    for health_service in ['hospital', 'gp', 'gp_bulk_billing', 'emergency', 'pharmacy']:
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
