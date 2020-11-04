from builders import adgroups_builder, autobuilder_func

def lambda_handler(event, context):
    if event['action']=='build_adgroups':
        info = adgroups_builder(file_name_s3 = event['file_name_s3'], 
                                similarity_clusters = event['similarity_clusters'], 
                                number_of_clusters = event['number_of_clusters'], 
                                number_of_kw_per_adgroup = event['number_of_kw_per_adgroup'],
                                kw_column = event['kw_column'],
                                volume_column =  event['volume_column'])       
    return info