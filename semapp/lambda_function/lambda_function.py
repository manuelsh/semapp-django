from builders import adgroups_builder, autobuilder_func

def lambda_handler(event, context):
    if event['action']=='build_adgroups':
        info = adgroups_builder(file_name_s3 = event['file_name_s3'], 
                                similarity_clusters = event['similarity_clusters'], 
                                number_of_clusters = event['number_of_clusters'], 
                                number_of_kw_per_adgroup = event['number_of_kw_per_adgroup'],
                                kw_column = event['kw_column'],
                                volume_column =  event['volume_column'])
    
    if event['action']=='autobuilder':
        info = autobuilder_func(kw_file_name=event['kw_file_name'], 
                                adgroups_file_name=event['adgroups_file_name'], 
                                kw_column=event['kw_column'], 
                                adgroups_column=event['adgroups_column'], 
                                kw_adgroups_column=event['kw_adgroups_column'])
    
    return info