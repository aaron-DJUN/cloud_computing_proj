#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 00:09:41 2020

@author: damengjin
"""
# Load Model Using Pickle
import pandas as pd
import pickle

#load the dataset:
df_new = pd.read_csv('./psrPlatform/recom_model/df_new.csv', index_col=None)

# load the model from disk
SVDpp_val = pickle.load(open('./psrPlatform/recom_model/SVDpp_model.sav', 'rb'))
user_knn = pickle.load(open('./psrPlatform/recom_model/Knn_model.sav', 'rb'))


def get_similar_users(top_k, user_id):
    """
    Args:
        top_k(int): no of similar user
        user_id(str): target user id

    Returns:
        list generator
    """
    user_inner_id = user_knn.trainset.to_inner_uid(user_id)
    user_neighbors = user_knn.get_neighbors(user_inner_id, k=top_k)
    user_neighbor_ids = (user_knn.trainset.to_raw_uid(inner_id) for inner_id in user_neighbors)
    return user_neighbor_ids



def get_top_N_recommended_items(user, top_sim_user=3, N=5):
    similar_id_list = list(get_similar_users(top_sim_user, user))
    unique_item = df_new.item.unique() 
    predict_target = []
    for i in similar_id_list:
        for j in unique_item:
            est = SVDpp_val.predict(iid=j, uid=i)[3]
            tup = [i,j,est]
            predict_target.append(tup)
    target_pred = pd.DataFrame(predict_target, columns = ['uid', 'iid', 'est'])
    predct_base = target_pred[['iid', 'est']].groupby(['iid'], as_index=False).mean().sort_values('est', ascending=False)
    rated_item_by_user = df_new[['item','rating']][df_new.user == user]
    result = pd.merge(predct_base, rated_item_by_user, how='left', left_on=['iid'], right_on=['item'])
    non_rated_result = result[result['rating']!=result['rating']]
    output = list(non_rated_result.iid[:N])
    #print(output)
    return output

if __name__=='__main__':
    userId = 'A1EO9BFUHTGWKZ'
    get_top_N_recommended_items(userId)