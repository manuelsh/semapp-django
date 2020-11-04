import pandas as pd
import boto3
from io import BytesIO
import os

# in local it should be `from .functions ...`
from .functions import create_model, pipeline, ad_group_assignment, create_embedding, is_excel_file

def adgroups_builder(file_name_s3, 
                     similarity_clusters, 
                     number_of_clusters, 
                     number_of_kw_per_adgroup,
                     kw_column,
                     volume_column):
    
    info = {}
    
    # read file from S3
    s3 = boto3.client('s3', region_name=os.environ.get('REGION_NAME'))
    uploaded_file = BytesIO( s3.get_object( Bucket='adquity-app', Key=file_name_s3)['Body'].read() )
    
    # check file is excel file
    if not is_excel_file(uploaded_file):
        info['error'] = 'Not a valid excel file'
        return info
    
    # read file and check length    
    kw_df = pd.read_excel(uploaded_file)
    info['file_length'] = len(kw_df)
      
    # lower case column titles
    kw_df.columns = [c.lower() for c in kw_df.columns]
    kw_column = kw_column.lower()
    volume_column = volume_column.lower()
     
    # run checks
    for c in [kw_column, volume_column]:
        if c not in kw_df:
            info['error'] = c+' column not in the file.'
            return info
    
    if len(kw_df) == 0:
        info['error'] = 'File is empty. No keywords found.'
        return info
    
    # Some transformations
    kw_df = kw_df.astype({kw_column:"str"})
    kw_df = kw_df.sort_values(by = volume_column , ascending = False )
    kw_df = kw_df.reset_index(drop=True)
    
    # Todo: text normalization
    
#     text_norm_bool = st.sidebar.checkbox("Want to normalize text?")
#     if text_norm_bool:
#         lenguage = st.sidebar.selectbox("Select lenguage" , ["Spanish" , "English" , "French"])
#         kw_df['processed'] = parallelize_on_rows(kw_df[kw_column],partial(preprocess,lenguage=lenguage))
#         kw_column = 'processed'

    # Train model
    model = create_model(kw_df[kw_column])
    info['model_trained_adgroups'] = True
    
    # Create adgroups
    results_output , rest_df_output = pipeline(dataset = kw_df , kw_column=kw_column,
                                               model=model,
                                               number_of_clusters = int(number_of_clusters),
                                               number_of_kw = int(number_of_kw_per_adgroup),
                                               create_embedding_dataset = True)
    info['adgroups_created'] = True
         
       
    # store file in S3
    results_output = results_output.drop(columns='embedding_average')
    xls_buffer = BytesIO()
    results_output.to_excel(xls_buffer, index = False,  encoding = 'UTF-16', sheet_name='adgroups')
    output_file_name =  file_name_s3[:-5]+'out' +'.xlsx'
    s3.put_object(Bucket='adquity-app', Key=output_file_name, Body=xls_buffer.getvalue(), ACL='public-read')
    info['output_file_name'] = output_file_name
    return info


def autobuilder_func(kw_file, adgroups_file, kw_column, adgroups_column, kw_adgroups_column):
        info = {}
            # check files are excel files
        for uploaded_file in [kw_file, adgroups_file]:
            if not is_excel_file(uploaded_file):
                info['error'] = uploaded_file.name + ' is not a valid excel file.'
                return info
         
        # read & preprocess pandas
        adgroups_df = pd.read_excel(adgroups_file) 
        kw_df = pd.read_excel(kw_file) 
        info['adgroups_rows'] = len(adgroups_df)
        info['kw_rows'] = len(kw_df)
        
        # lower case column titles
        kw_df.columns = [c.lower() for c in kw_df.columns]
        adgroups_df.columns = [c.lower() for c in adgroups_df.columns]
        kw_column = kw_column.lower()
        adgroups_column = adgroups_column.lower()
        kw_adgroups_column = kw_adgroups_column.lower()
        
        # run checks
        if kw_column not in kw_df:
            info['error'] = kw_column+' column not in the keywords file.'
            return info
        
        for c in [adgroups_column, kw_adgroups_column]:
            if c not in adgroups_df:
                info['error'] = c+' column not in the adgroups file.'
                return info

        if len(kw_df) == 0:
            info['error'] = 'Keyword file is empty. No keywords found.'
            return info
        
        if len(adgroups_df) == 0:
            info['error'] = 'Ad groups file is empty. No adgroups found.'
            return info  
        
        for column in adgroups_df.columns:
            adgroups_df = adgroups_df.astype({column:"str"})
            adgroups_df[column] = adgroups_df[column].str.lower()
        
        for column in kw_df.columns:
            kw_df = kw_df.astype({column:"str"})
            kw_df[column] = kw_df[column].str.lower()

        i1 = kw_df.set_index(kw_column).index
        i2 = adgroups_df.set_index(kw_adgroups_column).index
        kw_df = kw_df[~i1.isin(i2)]
        if len(kw_df) == 0:
            info['error'] = 'New keywords not found. Maybe the "new keywords file" is empty or contains the same keywords as the "ad groups file"?'
            return info
        # Creating model
        concat_all_kw = pd.concat([ adgroups_df[kw_adgroups_column], kw_df[kw_column] ])
        model = create_model(concat_all_kw)
        info['model_trained_autobuilder'] = True

        # Assigning cluster
        clusters_names = adgroups_df[adgroups_column].unique()
        clusters_names_df = pd.DataFrame(clusters_names , columns = ['ad_group'])

        kw_df = create_embedding(kw_df , kw_column, model)
        clusters_names_df = create_embedding(clusters_names_df , 'ad_group', model)
        kw_df['index'] = ad_group_assignment(kw_df, clusters_names_df)
        kw_df['ad_group'] =  kw_df['index'].apply(lambda x: clusters_names_df['ad_group'][x] )
        info['clusters_assigned'] = True
        
        # Prepare file to be downloaded
        results_output = kw_df.drop(columns='embedding_average') 
        results_output.to_excel("./media/output_autobuilder.xlsx", index = False,  encoding = 'UTF-16',sheet_name='adgroups') 
        info['file_saved'] = True
        return info