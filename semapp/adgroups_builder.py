import pandas as pd
import numpy as np
import time
from multiprocessing import  Pool
from functools import partial
import base64
import re 
import os
import io
import gc
from .functions import create_model
from .functions import pipeline

#from text_normalization import *
#from functions import *


def adgroups_builder(uploaded_file, 
                     similarity_clusters, 
                     number_of_clusters, 
                     number_of_kw_per_adgroup):

    search_terms_df = pd.read_excel(uploaded_file)
    search_terms_columns = search_terms_df.columns
    keywords_column = 'Keyword'
    volumn_column = 'Volume'
    
    # Some transformations
    search_terms_df = search_terms_df.astype({keywords_column:"str"})
    search_terms_df = search_terms_df.sort_values(by = volumn_column , ascending = False )
    search_terms_df = search_terms_df.reset_index(drop=True)
    
    # Todo: text normalization
    
#     text_norm_bool = st.sidebar.checkbox("Want to normalize text?")
#     if text_norm_bool:
#         lenguage = st.sidebar.selectbox("Select lenguage" , ["Spanish" , "English" , "French"])
#         search_terms_df['processed'] = parallelize_on_rows(search_terms_df[keywords_column],partial(preprocess,lenguage=lenguage))
#         keywords_column = 'processed'

    # Train model
    model = create_model(search_terms_df, column = keywords_column )
    
    # Create adgroups
    start = time.time()
    results_output , rest_df_output = pipeline(dataset = search_terms_df , keywords_column=keywords_column,
                                               model=model,
                                               similarity_clusters = similarity_clusters,
                                               number_of_clusters = int(number_of_clusters),
                                               number_of_kw = int(number_of_kw_per_adgroup),
                                               create_embedding_dataset = True)
    end = time.time()
    
    # Prepare file to be downloaded™
    results_output = results_output.drop(columns='embedding_average') 
    results_output.to_excel("./media/output.xlsx", index = False,  encoding = 'UTF-16',sheet_name='Ad_groups') 

