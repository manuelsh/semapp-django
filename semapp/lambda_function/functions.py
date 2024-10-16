import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm

from fasttext import train_unsupervised
from scipy.spatial import distance

import re
import os
import io

import copy 
import time
from multiprocessing import Pool

from functools import partial
import warnings
import base64
# from text_processing import *


def create_model(series):
    with open('/tmp/output.txt', 'w') as f:
        f.write(series.str.cat(sep='\n'))
    model = train_unsupervised('/tmp/output.txt', epoch = 1000 )
    return model

def pipeline(dataset, model, kw_column,
            number_of_clusters = 800,
            number_of_kw = 10,
            similarity_clusters = 0.95,
            similarity_categories = 0.9,
            create_embedding_dataset = True,
            categories = False):
    
    if create_embedding_dataset:
        dataset = create_embedding(dataset , kw_column, model)
        product_queries = clean_embedding(dataset)
    else:
        product_queries = dataset
    
    product_queries = product_queries.drop_duplicates(subset = kw_column, keep = False)
    product_queries = product_queries.reset_index( drop = True)        
    clusters_df , rest_df = making_clusters(product_queries ,
                                            number_of_clusters = number_of_clusters ,
                                            similarity_threshold=similarity_clusters , 
                                            number_of_kw = number_of_kw,
                                           kw_column=kw_column)
    
    results =  clusters_df
    return results , rest_df


def making_clusters(data_set, number_of_clusters ,  similarity_threshold  , number_of_kw, kw_column):
    data_set_mutable = copy.copy(data_set)
    result_kw = pd.DataFrame()
    clusters = pd.DataFrame()
    for i in range(number_of_clusters):
        if len(data_set_mutable)==0:
            'Breaking on first grouping , you have groupped all the KW' #error
            break
        distances = 1 - distance.cdist([data_set_mutable.iloc[0]['embedding_average'].tolist()]
                                    , data_set_mutable['embedding_average'].tolist()
                                        , 'cosine')
                                
        distances =pd.Series( distances.tolist()[0])

        distances = distances[distances >= similarity_threshold]
        sorted_distances = (distances.sort_values(ascending=False))
        indices = sorted_distances[0:number_of_kw].index

        result_kw =  data_set_mutable.loc[indices]
        result_kw['Ad_group_name'] = data_set_mutable.iloc[0][kw_column]
        result_kw['Ad_group_number'] = i
        data_set_mutable = data_set_mutable.drop(indices)
        data_set_mutable = data_set_mutable.reset_index(drop=True)

        clusters = clusters.append(result_kw, ignore_index = True)
    
    return clusters , data_set_mutable

def average_over_terms(sentence, model):
    embbeding = []
    for word in sentence.split(' '):
        embbeding.append(model[word])
    return np.array(embbeding).mean(0)


def create_embedding(data_set, kw_column, model):
    data_set['embedding_average'] =  data_set[kw_column].apply(lambda x: average_over_terms(x, model))
    return data_set

def clean_embedding(data_set):
    data_set = data_set[ ~data_set['embedding_average'].isnull()]
    return data_set

def cos_sim(a, b):
    # return 1 - spatial.distance.cosine(a, b)
    return dot(a, b)/(norm(a)*norm(b))


def ad_group_assignment(data_subset, ad_groups_clusters_centers):

    list_distances = 1 - distance.cdist(data_subset['embedding_average'].tolist(),
                                        ad_groups_clusters_centers['embedding_average'].tolist(),
                                        'cosine')

    index_sol =  [np.where(list_distance==max(list_distance))[0][0] for list_distance in list_distances]
    data_subset['test'] = np.array(index_sol)
    return data_subset['test']

    
def is_excel_file(file):

    excelSigs = [
        ('xlsx', b'\x50\x4B\x05\x06', 2, -22, 4),
        ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 512, 8),  #Saved from Excel
        ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 1536, 8), #Saved from LibreOffice Calc
        ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 2048, 8)  #Saved from Excel then saved from Calc
]

    for sigType, sig, whence, offset, size in excelSigs:
        file.seek(offset, whence)
        bytes = file.read(size)
        if bytes == sig:
            return True

    return False

# def parallelize(data, func, num_of_processes=12):
#     data_split = np.array_split(data, num_of_processes)
#     pool = Pool(num_of_processes)
#     data = pd.concat(pool.map(func, data_split))
#     pool.close()
#     pool.join()
#     return data

# def run_on_subset(func, data_subset):
#     return data_subset.apply(func)

# def parallelize_on_rows(data, func, num_of_processes=12):
#     return parallelize(data, partial(run_on_subset, func), num_of_processes)

# def create_embedding_parallel(data_set , column , model):
#     data_set['embedding_average'] =  parallelize_on_rows(data_set[column] ,lambda x: average_over_terms(x, model) )
#     return data_set 