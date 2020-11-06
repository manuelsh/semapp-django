from django.shortcuts import render    
from .forms import UploadFileFormAdgroup, UploadFileFormAutoBuilder   
from django.http import HttpResponse, FileResponse

from django.contrib.auth.decorators import login_required
from .models import Event
from django.forms.fields import JSONField
from datetime import datetime
import json
import string
import boto3

# for download_file
import os
import mimetypes
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

from .lambda_function.builders import adgroups_builder, autobuilder_func


def download_file(request, file_name_raw):
    filename = os.path.basename(file_name_raw)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(file_name_raw, 'rb'), chunk_size),
                           content_type=mimetypes.guess_type(file_name_raw)[0])
    response['Content-Length'] = os.path.getsize(file_name_raw)    
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def clean_f(form):
    clean = form.cleaned_data.copy()
    keys_to_remove = []
    for k in clean.keys():
        if 'file' in k:
            keys_to_remove.append(k)
    for k in keys_to_remove:
        del clean[k]
    return clean

    
@login_required  
def build_adgroups(request):
    origin = 'build_adgroups_view'
    if request.method == 'POST':        
        form = UploadFileFormAdgroup(request.POST, request.FILES)
        if form.is_valid():
            Event(event_type='submit', time=datetime.now(), user_name=request.user.username, origin=origin, info=clean_f(form)).save()
            
            # Save file to S3
            #   give a proper s3 name without punctuation
            file_name_s3 = (request.user.username+str(datetime.now())).translate(str.maketrans('', '', string.punctuation+' '))+'.xlsx' 
            
            #   stores file
            s3 = boto3.client('s3',
                      aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                      region_name=os.environ.get('REGION_NAME')
                     )
            s3.put_object( Body=request.FILES['file'].file, Bucket='adquity-app', Key=file_name_s3)
            
            # run lambda function
            lambda_func = boto3.client('lambda',
                      aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                      region_name=os.environ.get('REGION_NAME')
                     )
            payload = f"""{{"file_name_s3":"{file_name_s3}",
                            "similarity_clusters":"{form.cleaned_data['similarity_threshold']}", 
                            "number_of_clusters":"{form.cleaned_data['number_of_adgroups']}",
                            "number_of_kw_per_adgroup":"{form.cleaned_data['max_number_keywords']}",
                            "kw_column":"{form.cleaned_data['keyword_column']}",
                            "volume_column":"{form.cleaned_data['volume_column']}",
                            "action":"build_adgroups"
                            }}"""
            
            
            info = lambda_func.invoke(FunctionName='builders', Payload = payload)

#             info = adgroups_builder(file_name_s3 = file_name_s3, 
#                                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
#                                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
#                                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'],
#                                     kw_column =  form.cleaned_data['keyword_column'],
#                                     volume_column =  form.cleaned_data['volume_column'])
            
            response = json.loads(info['Payload'].read())
            if 'error' in response:
                Event(event_type='error', time=datetime.now(), user_name=request.user.username, origin=origin, info=info).save()
                return HttpResponse(info['error'])
            
            http_bucket_address = 'https://adquity-app.s3-eu-west-1.amazonaws.com/'
            file_url = http_bucket_address+response['output_file_name']
            return render(request, 'semapp/download_file.html', {'file_url': file_url})

            # returns output
#             filename = "./media/output_adgroup_build.xlsx"
#             Event(event_type='process', 
#                   time=datetime.now(), 
#                   user_name=request.user.username, 
#                   origin=origin, 
#                   info=info.update(clean_f(form))).save()
#             return download_file(request, filename)

            
    else:
        form = UploadFileFormAdgroup()
        Event(event_type='view', time=datetime.now(), user_name=request.user.username, origin=origin).save()
        return render(request, 'semapp/build_adgroups.html', {'form': form})

    
@login_required  
def autobuilder(request):
    origin = 'autobuilder_view'
    if request.method == 'POST':
        form = UploadFileFormAutoBuilder(request.POST, request.FILES)       
        if form.is_valid():
            Event(event_type='submit', time=datetime.now(), user_name=request.user.username, origin=origin, info=clean_f(form)).save()
                       
            info = autobuilder_func(kw_file=request.FILES['file_kw'], 
                                  adgroups_file=request.FILES['file_adgroups'], 
                                  kw_column=form.cleaned_data['new_keywords_column'], 
                                  adgroups_column=form.cleaned_data['adgroups_column'],
                                  kw_adgroups_column=form.cleaned_data['prev_keywords_column'])
            if 'error' in info:
                Event(event_type='error', time=datetime.now(), user_name=request.user.username, origin=origin, info=info).save()
                return HttpResponse(info['error'])
            else:            

                # returns output
                filename = "./media/output_autobuilder.xlsx"
                Event(event_type='process', time=datetime.now(), user_name=request.user.username, origin=origin, info=info).save()
                return FileResponse(open(filename, 'rb'))
            
    else:
        form = UploadFileFormAutoBuilder()
        Event(event_type='view', time=datetime.now(), user_name=request.user.username, origin=origin).save()
        return render(request, 'semapp/autobuilder.html', {'form': form})
