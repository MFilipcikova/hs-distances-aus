import pandas as pd
from sklearn.neighbors import KDTree
import pickle

if __name__ == '__main__':
    # read in GP information
    dtype_common = {'svc_classification': 'str',
                    'pl_latitude': 'float32',
                    'pl_longitude': 'float32'}
    dtype = dtype_common | {'pls_billingOptions': 'str'}
    df_gp = pd.read_excel('./data/health_services_info_jul25.xlsx', sheet_name='General Practice Service',
                          usecols=dtype.keys(), dtype=dtype)

    # read in hospital and emergency information
    dtype = dtype_common | {'Public/Private': 'str'}
    df_hosp_ed = pd.read_excel('./data/health_services_info_jul25.xlsx', sheet_name='Hospital and Emergency',
                               usecols=dtype.keys(), dtype=dtype)

    # read in pharmacies information and append to other HS information
    dtype = dtype_common
    df_pharmacy = pd.read_excel('./data/nhsd_pharmacies.xlsx', usecols=dtype.keys(), dtype=dtype)

    # remove rows with missing values
    df_gp = df_gp.dropna()
    df_hosp_ed = df_hosp_ed.dropna()
    df_pharmacy = df_pharmacy.dropna()

    # create dataframes for various services
    df_hospital_public = df_hosp_ed[(df_hosp_ed['svc_classification'] == 'Hospital service') &
                                    (df_hosp_ed['Public/Private'] == 'Public')]
    df_hospital_private = df_hosp_ed[(df_hosp_ed['svc_classification'] == 'Hospital service') &
                                    (df_hosp_ed['Public/Private'] == 'Private')]
    df_emergency = df_hosp_ed[df_hosp_ed['svc_classification'] == 'Emergency department service']
    df_gp_bulk_billing = df_gp[df_gp['pls_billingOptions'] == 'Bulk Billing Only']

    # get arrays with coordinates
    X_hospital_public = df_hospital_public[['pl_longitude', 'pl_latitude']].to_numpy()
    X_hospital_private = df_hospital_private[['pl_longitude', 'pl_latitude']].to_numpy()
    X_gp = df_gp[['pl_longitude', 'pl_latitude']].to_numpy()
    X_gp_bulk_billing = df_gp_bulk_billing[['pl_longitude', 'pl_latitude']].to_numpy()
    X_emergency = df_emergency[['pl_longitude', 'pl_latitude']].to_numpy()
    X_pharmacy = df_pharmacy[['pl_longitude', 'pl_latitude']].to_numpy()

    # create K-D Trees
    tree_hospital_public = KDTree(X_hospital_public)
    tree_hospital_private = KDTree(X_hospital_private)
    tree_gp = KDTree(X_gp)
    tree_gp_bulk_billing = KDTree(X_gp_bulk_billing)
    tree_emergency = KDTree(X_emergency)
    tree_pharmacy = KDTree(X_pharmacy)

    # create dictionary of trees
    dict_trees = {'hospital_public': tree_hospital_public, 'hospital_private': tree_hospital_private, 'gp': tree_gp,
                  'gp_bulk_billing': tree_gp_bulk_billing, 'emergency': tree_emergency, 'pharmacy': tree_pharmacy}

    # save K-D Trees
    pickle.dump(dict_trees, open('./data/dict_trees', 'wb'))
