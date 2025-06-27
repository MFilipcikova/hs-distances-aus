import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # read in the mb_2021_distances table
    dtype = {'STE_NAME21': 'str',
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

    df = df[df['STE_NAME21'] != 'Other Territories']

    duration_cols = ['hospital_duration', 'gp_duration', 'gp_bulk_billing_duration', 'emergency_duration',
                     'pharmacy_duration']
    distance_cols = ['hospital_distance', 'gp_distance', 'gp_bulk_billing_distance', 'emergency_distance',
                     'pharmacy_distance']
    df[duration_cols] = df[duration_cols]/60
    df[distance_cols] = df[distance_cols]/1000

    # durations plot
    f, axs = plt.subplots(3, 2, figsize=(12, 12))

    sns.kdeplot(df, x='hospital_duration', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[0, 0])
    sns.move_legend(axs[0, 0], title='', loc='best')
    axs[0, 0].set(xlim=(0, 40), xlabel='Duration to Hospital [min]')

    sns.kdeplot(df, x='gp_duration', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[0, 1])
    sns.move_legend(axs[0, 1], title='', loc='best')
    axs[0, 1].set(xlim=(0, 10), xlabel='Duration to GP [min]')

    sns.kdeplot(df, x='gp_bulk_billing_duration', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[1, 0])
    sns.move_legend(axs[1, 0], title='', loc='best')
    axs[1, 0].set(xlim=(0, 40), xlabel='Duration to Bulk Billing GP [min]')

    sns.kdeplot(df, x='emergency_duration', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[2, 0])
    sns.move_legend(axs[2, 0], title='', loc='best')
    axs[2, 0].set(xlim=(0, 40), xlabel='Duration to ED [min]')

    sns.kdeplot(df, x='pharmacy_duration', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[1, 1])
    sns.move_legend(axs[1, 1], title='', loc='best')
    axs[1, 1].set(xlim=(0, 10), xlabel='Duration to Pharmacy [min]')

    axs[2, 1].axis('off')

    f.tight_layout()
    plt.savefig('plots/duration.pdf', format='pdf', bbox_inches='tight')
    plt.show()

    # distances plot
    f, axs = plt.subplots(3, 2, figsize=(12, 12))

    sns.kdeplot(df, x='hospital_distance', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[0, 0])
    sns.move_legend(axs[0, 0], title='', loc='best')
    axs[0, 0].set(xlim=(0, 30), xlabel='Distance to Hospital [km]')

    sns.kdeplot(df, x='gp_distance', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[0, 1])
    sns.move_legend(axs[0, 1], title='', loc='best')
    axs[0, 1].set(xlim=(0, 6), xlabel='Distance to GP [km]')

    sns.kdeplot(df, x='gp_bulk_billing_distance', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[1, 0])
    sns.move_legend(axs[1, 0], title='', loc='best')
    axs[1, 0].set(xlim=(0, 30), xlabel='Distance to Bulk Billing GP [km]')

    sns.kdeplot(df, x='emergency_distance', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[2, 0])
    sns.move_legend(axs[2, 0], title='', loc='best')
    axs[2, 0].set(xlim=(0, 30), xlabel='Distance to ED [km]')

    sns.kdeplot(df, x='pharmacy_distance', hue='STE_NAME21', weights='Person', fill=False, common_norm=False,
                bw_method=0.2, ax=axs[1, 1])
    sns.move_legend(axs[1, 1], title='', loc='best')
    axs[1, 1].set(xlim=(0, 6), xlabel='Distance to Pharmacy [km]')

    axs[2, 1].axis('off')

    f.tight_layout()
    plt.savefig('plots/distance.pdf', format='pdf', bbox_inches='tight')
    plt.show()
