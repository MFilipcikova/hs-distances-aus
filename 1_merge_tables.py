import pandas as pd

if __name__ == '__main__':
    # read in data on mesh blocks and centroids
    dtype = {'MB_CODE21': 'int64',
             'SA1_CODE21': 'int64',
             'SA2_CODE21': 'int64',
             'STE_CODE21': 'int32',
             'STE_NAME21': 'str',
             'latitude': 'float32',
             'longitude': 'float32'}
    mb_2021_centroids = pd.read_csv('./data/mb_2021_centroids.csv', usecols=dtype.keys(), dtype=dtype)

    # drop mbs with missing data (e.g., no usual address)
    mb_2021_centroids = mb_2021_centroids.dropna()

    # read in population counts
    dtype = {'MB_CODE_2021': 'int64',
             'Person': 'int32'}
    mb_counts_2021 = pd.read_excel('./data/mb_counts_2021.xlsx', sheet_name='Table 1', usecols=dtype.keys(),
                                   dtype=dtype)
    # concat sheets in the Excel file
    for sheet in ["1.1", "2", "2.1", "3", "3.1", "4", "5", "6", "7", "8", "9"]:
        tmp = pd.read_excel('./data/mb_counts_2021.xlsx', sheet_name="Table "+sheet, usecols=dtype.keys(),
                            dtype=dtype)
        mb_counts_2021 = pd.concat([mb_counts_2021, tmp], ignore_index=True)
    mb_counts_2021 = mb_counts_2021.rename(columns={"MB_CODE_2021": "MB_CODE21"})

    # merge data on mesh blocks and centroids with population counts
    mb_2021_merged = pd.merge(mb_2021_centroids, mb_counts_2021, how="left", on="MB_CODE21")

    # read in the mmm 2019 table
    dtype = {'SA1_MAIN16': 'int64',
             'MMM2019': 'int32'}
    mmm_2019 = pd.read_csv('./data/mmm_2019.csv', usecols=dtype.keys(), dtype=dtype)

    # read in the SA1 2016 to 2021 correspondences table
    dtype = {'SA1_MAINCODE_2016': 'int64',
             'SA1_CODE_2021': 'float64',
             'RATIO_FROM_TO': 'float32'}
    SA1_2016_to_2021 = pd.read_csv('./data/CG_SA1_2016_SA1_2021.csv', usecols=dtype.keys(), dtype=dtype)
    SA1_2016_to_2021 = SA1_2016_to_2021.rename(columns={"SA1_MAINCODE_2016": "SA1_MAIN16"})
    SA1_2016_to_2021 = SA1_2016_to_2021.dropna()
    SA1_2016_to_2021 = SA1_2016_to_2021.astype({"SA1_CODE_2021": int})

    # merge mmm_2019 with SA1_2016_to_2021
    mmm_2019 = pd.merge(mmm_2019, SA1_2016_to_2021, how="left", on="SA1_MAIN16")
    # remove correspondences to multiple 2021 SA1s
    mmm_2019 = mmm_2019.sort_values(by=["SA1_CODE_2021", "RATIO_FROM_TO"], ascending=[True, False])
    mmm_2019 = mmm_2019.groupby(by="SA1_CODE_2021").first().reset_index()
    # clean up
    mmm_2019 = mmm_2019.drop(columns=["SA1_MAIN16", "RATIO_FROM_TO"])
    mmm_2019 = mmm_2019.rename(columns={"SA1_CODE_2021": "SA1_CODE21"})

    # merge mb_2021_merged with mmm_2019
    mb_2021_merged = pd.merge(mb_2021_merged, mmm_2019, how="left", on="SA1_CODE21")

    # read in the postal areas 2021 table
    dtype = {'MB_CODE_2021': 'int64',
             'POA_CODE_2021': 'int64'}
    postal_areas_2021 = pd.read_excel('./data/postal_areas_2021.xlsx', usecols=dtype.keys(), dtype=dtype)
    postal_areas_2021 = postal_areas_2021.rename(columns={"MB_CODE_2021": "MB_CODE21"})

    # merge postal codes with mb_2021_merged
    mb_2021_merged = pd.merge(mb_2021_merged, postal_areas_2021, how="left", on="MB_CODE21")

    # fill empty MMMs
    print(mb_2021_merged.isnull().sum())
    mb_2021_merged['MMM2019'] = mb_2021_merged['MMM2019'].fillna(99)

    # write out resulting table
    mb_2021_merged.to_csv('./data/mb_2021_merged.csv', index=False)
