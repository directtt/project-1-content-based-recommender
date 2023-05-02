import pandas as pd
import numpy as np


class UserFE(object):
    def __init__(self):
        self.user_fe_columns = ['term', 'length_of_stay_bucket', 'rate_plan',
                                'room_segment', 'n_people_bucket', 'weekend_stay']
        self.user_features = []
        self.buckets_to_average_dict = {
            '[0-1]': 0.5,
            '[2-3]': 2.5,
            '[4-7]': 5.5,
            '[8-inf]': 9,
            '[0-160]': 80,
            '[160-260]': 210,
            '[260-360]': 310,
            '[360-500]': 430,
            '[500-900]': 700,
            '[1-1]': 1,
            '[2-2]': 2,
            '[3-4]': 3.5,
            '[5-inf]': 6
        }

    def features_distribution(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Function for calculating distribution of features.

        :param users_df: input users_df dataframe
        :return: updated users_df dataframe
        """
        for column in self.user_fe_columns:
            pivot_term = users_df.pivot_table(index='user_id', columns=column,
                                              
                                              aggfunc='size', fill_value=0).reset_index()
            pivot_term.iloc[:, 1:] = pivot_term.iloc[:, 1:] / pivot_term.iloc[:, 1:].sum(axis=1).values.reshape(-1, 1)
            pivot_term = pivot_term.add_prefix(f"user_{column}_")
            pivot_term = pivot_term.rename(columns={f'user_{column}_user_id': 'user_id'})
            users_df = users_df.merge(pivot_term, on='user_id', how='left')
            self.user_features += pivot_term.iloc[:, 1:].columns.tolist()

        return users_df

    def bucket_features_to_average(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Function for converting bucket features to average values.

        :param users_df: input users_df dataframe
        :return: updated users_df dataframe
        """
        for column in ['length_of_stay_bucket', 'room_segment', 'n_people_bucket']:
            new_column = f"user_{column}_avg"
            users_df[new_column] = users_df[column].apply(
                lambda x: self.buckets_to_average_dict[x]).astype(float)
            users_df[new_column] = users_df.groupby('user_id')[new_column].transform('mean')
            self.user_features.append(new_column)

        return users_df
