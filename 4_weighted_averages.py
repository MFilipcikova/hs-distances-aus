import numpy as np
import pandas as pd


def weighted(x, cols, w='Person'):
    data = np.ma.masked_array(x[cols], np.isnan(x[cols]))
    return pd.Series(np.ma.average(data, weights=x[w], axis=0), cols)


if __name__ == '__main__':
    # read in the mb_2021_distances table
    dtype = {'SA2_CODE21': 'int64',
             'STE_CODE21': 'int32',
             'STE_NAME21': 'str',
             'MMM2019': 'float32',
             'POA_CODE_2021': 'int64',
             'Person': 'int32',
             'hospital_duration': 'float32',
             'hospital_distance': 'float32',
             'gp_duration': 'float32',
             'gp_distance': 'float32',
             'gp_bulk_billing_duration': 'float32',
             'gp_bulk_billing_distance': 'float32',
             'emergency_duration': 'float32',
             'emergency_distance': 'float32',
             'pharmacy_duration': 'float32',
             'pharmacy_distance': 'float32'}
    df = pd.read_csv('./data/mb_2021_distances.csv', usecols=dtype.keys(), dtype=dtype)

    # fill the empty cells
    columns_to_average = ['hospital_duration', 'hospital_distance',
                          'gp_duration', 'gp_distance',
                          'gp_bulk_billing_duration', 'gp_bulk_billing_distance',
                          'emergency_duration', 'emergency_distance',
                          'pharmacy_duration', 'pharmacy_distance']

    # compute weighted averages
    df_sa2_grouped = df.groupby(['SA2_CODE21'])
    df_poa_grouped = df.groupby(['POA_CODE_2021'])
    df_poa_mmm_grouped = df.groupby(['POA_CODE_2021', 'MMM2019'])
    df_ste_mmm_grouped = df.groupby(['STE_CODE21', 'STE_NAME21', 'MMM2019'])

    df_sa2 = df_sa2_grouped.apply(weighted, cols=columns_to_average, include_groups=False)
    df_poa = df_poa_grouped.apply(weighted, cols=columns_to_average, include_groups=False)
    df_poa_mmm = df_poa_mmm_grouped.apply(weighted, cols=columns_to_average, include_groups=False)
    df_ste_mmm = df_ste_mmm_grouped.apply(weighted, cols=columns_to_average, include_groups=False)

    # add state and person information
    agg_dict = {'Person': 'sum', 'STE_CODE21': 'first', 'STE_NAME21': 'first'}
    df_sa2 = pd.concat([df_sa2, df_sa2_grouped.agg(agg_dict)], axis=1)
    df_poa = pd.concat([df_poa, df_poa_grouped.agg(agg_dict)], axis=1)
    df_poa_mmm = pd.concat([df_poa_mmm, df_poa_mmm_grouped.agg(agg_dict)], axis=1)
    df_ste_mmm = pd.concat([df_ste_mmm, df_ste_mmm_grouped.agg({'Person': 'sum'})], axis=1)

    # turn index into column
    df_sa2.reset_index(inplace=True)
    df_poa.reset_index(inplace=True)
    df_poa_mmm.reset_index(inplace=True)
    df_ste_mmm.reset_index(inplace=True)

    # write out resulting tables
    df_sa2.to_csv('./data/weighted_averages_sa2.csv', index=False)
    df_poa.to_csv('./data/weighted_averages_poa.csv', index=False)
    df_poa_mmm.to_csv('./data/weighted_averages_poa_mmm.csv', index=False)
    df_ste_mmm.to_csv('./data/weighted_averages_ste_mmm.csv', index=False)
