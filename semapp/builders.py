import pandas as pd

from .functions import create_model, pipeline, ad_group_assignment, create_embedding

def adgroups_builder(uploaded_file, 
                     similarity_clusters, 
                     number_of_clusters, 
                     number_of_kw_per_adgroup,
                     request):

    kw_df = pd.read_excel(uploaded_file)
    
    request.session['file_size'] = len(kw_df)
    
    kw_columns = kw_df.columns
    kw_column = 'Keyword'
    volumn_column = 'Volume'
    
    # Some transformations
    kw_df = kw_df.astype({kw_column:"str"})
    kw_df = kw_df.sort_values(by = volumn_column , ascending = False )
    kw_df = kw_df.reset_index(drop=True)
    
    # Todo: text normalization
    
#     text_norm_bool = st.sidebar.checkbox("Want to normalize text?")
#     if text_norm_bool:
#         lenguage = st.sidebar.selectbox("Select lenguage" , ["Spanish" , "English" , "French"])
#         kw_df['processed'] = parallelize_on_rows(kw_df[kw_column],partial(preprocess,lenguage=lenguage))
#         kw_column = 'processed'

    # Train model
    model = create_model(kw_df[kw_column])
    request.session['model_trained_adgroups'] = True
    
    # Create adgroups
    results_output , rest_df_output = pipeline(dataset = kw_df , kw_column=kw_column,
                                               model=model,
                                               number_of_clusters = int(number_of_clusters),
                                               number_of_kw = int(number_of_kw_per_adgroup),
                                               create_embedding_dataset = True)
    request.session['adgroups_created'] = True
         
       
    # Prepare file to be downloaded
    results_output = results_output.drop(columns='embedding_average') 
    results_output.to_excel("./media/output_adgroup_build.xlsx", index = False,  encoding = 'UTF-16',sheet_name='adgroups') 
    
    return request


def autobuilder(kw_file, adgroups_file, kw_column, adgroups_column, kw_adgroups_column, request):

        # read & preprocess pandas
        adgroups_df = pd.read_excel(adgroups_file) 
        kw_df = pd.read_excel(kw_file) 
        
        for column in adgroups_df.columns:
            adgroups_df = adgroups_df.astype({column:"str"})
            adgroups_df[column] = adgroups_df[column].str.lower()
        
        for column in kw_df.columns:
            kw_df = kw_df.astype({column:"str"})
            kw_df[column] = kw_df[column].str.lower()

        i1 = kw_df.set_index(kw_column).index
        i2 = adgroups_df.set_index(kw_adgroups_column).index
        kw_df = kw_df[~i1.isin(i2)]
            
        # Creating model
        concat_all_kw = pd.concat([ adgroups_df[kw_adgroups_column], kw_df[kw_column] ])
        model = create_model(concat_all_kw)
        request.session['model_trained_autobuilder'] = True

        # Assigning cluster
        clusters_names = adgroups_df[adgroups_column].unique()
        clusters_names_df = pd.DataFrame(clusters_names , columns = ['ad_group'])

        kw_df = create_embedding(kw_df , column=kw_column)
        clusters_names_df = create_embedding(clusters_names_df , column='ad_group')
        kw_df['index'] = ad_group_assignment(kw_df)
        kw_df['ad_group'] =  kw_df['index'].apply(lambda x: clusters_names_df['ad_group'][x] )
        request.session['clusters_assigned'] = True
        
        # Prepare file to be downloaded
        results_output = kw_df.drop(columns='embedding_average') 
        results_output.to_excel("./media/output_autobuilder.xlsx", index = False,  encoding = 'UTF-16',sheet_name='adgroups') 

        return request