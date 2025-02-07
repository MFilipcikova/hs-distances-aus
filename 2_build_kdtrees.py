import pandas as pd
from sklearn.neighbors import KDTree
import pickle

if __name__ == '__main__':
    # read in healthcare services information
    dtype = {'Healthcare Service Type': 'str',
             'Healthcare Service Billing Options': 'str',
             'Location Latitude': 'float32',
             'Location Longitude': 'float32'}
    df = pd.read_excel('./data/health_services_info.xlsx', sheet_name='HealthcareServices', usecols=dtype.keys(),
                       dtype=dtype)

    # create dataframes for various services
    df_hospital = df[df['Healthcare Service Type'] == 'Hospital service']
    df_gp = df[df['Healthcare Service Type'] == 'General practice service']
    df_gp_bulk_billing = df[(df['Healthcare Service Type'] == 'General practice service') &
                            (df['Healthcare Service Billing Options'] == 'Bulk Billing Only')]
    df_emergency = df[df['Healthcare Service Type'] == 'Emergency department service']

    # get arrays with coordinates
    X_hospital = df_hospital[['Location Longitude', 'Location Latitude']].to_numpy()
    X_gp = df_gp[['Location Longitude', 'Location Latitude']].to_numpy()
    X_gp_bulk_billing = df_gp_bulk_billing[['Location Longitude', 'Location Latitude']].to_numpy()
    X_emergency = df_emergency[['Location Longitude', 'Location Latitude']].to_numpy()

    # create K-D Trees
    tree_hospital = KDTree(X_hospital)
    tree_gp = KDTree(X_gp)
    tree_gp_bulk_billing = KDTree(X_gp_bulk_billing)
    tree_emergency = KDTree(X_emergency)

    # create dictionary of trees
    dict_trees = {'hospital': tree_hospital, 'gp': tree_gp, 'gp_bulk_billing': tree_gp_bulk_billing,
                  'emergency': tree_emergency}

    # save K-D Trees
    pickle.dump(dict_trees, open('./data/dict_trees', 'wb'))
