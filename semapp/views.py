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
from botocore.exceptions import ReadTimeoutError
import botocore
import traceback
import os

BUCKET = os.environ.get("S3_BUCKET")
HTTP_S3_BUCKET_ADDRESS = f'https://{BUCKET}.s3-eu-west-1.amazonaws.com/'

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

def run_lambda_function(payload):
    config = botocore.config.Config(connect_timeout=905, read_timeout=905)
    lambda_func = boto3.client('lambda',
                               aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                               aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                               region_name=os.environ.get('REGION_NAME'),
                               config=config)
    info = lambda_func.invoke(FunctionName='builders', Payload = payload)
    return info

def log_exception_event(request, origin, error_info):
    Event(event_type='exception', 
          time=datetime.now(), 
          user_name=request.user.username,
          origin=origin, 
          info=error_info,
                ).save()

@login_required
def build_adgroups(request):
    try:
        origin = 'build_adgroups_view'
        if request.method == 'POST':        
            form = UploadFileFormAdgroup(request.POST, request.FILES)
            if form.is_valid():
                Event(event_type='submit', time=datetime.now(), user_name=request.user.username, origin=origin, info=clean_f(form)).save()

                # Save file to S3
                #   give a proper s3 name without punctuation
                file_name_s3 = (request.user.username+str(datetime.now())).translate(str.maketrans('', '', string.punctuation+' '))+'.xlsx' 

                #   stores file
                s3 = boto3.client('s3', region_name=os.environ.get('REGION_NAME') )
                s3.put_object( Body=request.FILES['file'].file, Bucket=BUCKET, Key=file_name_s3)

                # run lambda function

                payload = f"""{{"file_name_s3":"{file_name_s3}",
                                "similarity_clusters":"{form.cleaned_data['similarity_threshold']}", 
                                "number_of_clusters":"{form.cleaned_data['number_of_adgroups']}",
                                "number_of_kw_per_adgroup":"{form.cleaned_data['max_number_keywords']}",
                                "kw_column":"{form.cleaned_data['keyword_column']}",
                                "volume_column":"{form.cleaned_data['volume_column']}",
                                "action":"build_adgroups"
                                }}"""
                info = run_lambda_function(payload)

    #           info = adgroups_builder(file_name_s3 = file_name_s3, 
    #                                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
    #                                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
    #                                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'],
    #                                     kw_column =  form.cleaned_data['keyword_column'],
    #                                     volume_column =  form.cleaned_data['volume_column'])

                response = json.loads(info['Payload'].read())
                if 'error' in response:
                    Event(event_type='error', time=datetime.now(), user_name=request.user.username, origin=origin, info=response).save()
                    return render(request, 'semapp/error_message.html', {'error': response['error']})

                file_url = HTTP_S3_BUCKET_ADDRESS + response['output_file_name']
                Event(event_type='process', time=datetime.now(), user_name=request.user.username, origin=origin, info=response).save()
                return render(request, 'semapp/download_file.html', {'file_url': file_url})

        else:
            form = UploadFileFormAdgroup()
            Event(event_type='view', time=datetime.now(), user_name=request.user.username, origin=origin).save()
            return render(request, 'semapp/build_adgroups.html', {'form': form})
        
    except ReadTimeoutError as error:
        error_info = {"Error type":f"ReadTimeoutError error: {str(error)}",
                      'Tracebak': traceback.format_exc(),
                      'File': file_name_s3,
                      'Form':clean_f(form)}
        log_exception_event(request, origin, error_info)
        return render(request, 
                      'semapp/error_message.html', 
                      {'error': 'Time out error. The file may be too big. We are working to fix this, In the meantime you can try to break it in smaller pieces...'})
    
    except BaseException as error:
        error_info={"Error type":str(error),
                    'Tracebak': traceback.format_exc(),
                    'File': file_name_s3,
                    'Form':clean_f(form)}
        log_exception_event(request, origin, error_info)
        return render(request, 
                      'semapp/error_message.html', 
                      {'error': f'Error: {str(error)}. If the error is a problem to you, contact the administrator at info@adquity.io'})

    
@login_required  
def autobuilder(request):
    try:
        origin = 'autobuilder_view'
        if request.method == 'POST':
            form = UploadFileFormAutoBuilder(request.POST, request.FILES)       
            if form.is_valid():
                Event(event_type='submit', time=datetime.now(), user_name=request.user.username, origin=origin, info=clean_f(form)).save()

                # Save files to S3 with a proper s3 name without punctuation
                s3 = boto3.client('s3', region_name=os.environ.get('REGION_NAME') )
                file_name_s3 = (request.user.username+str(datetime.now())).translate(str.maketrans('', '', string.punctuation+' ')) 
                adgroups_file_name = file_name_s3 + 'adgroups.xlsx'
                kw_file_name = file_name_s3 + 'kw.xlsx'
                s3.put_object( Body=request.FILES['file_adgroups'].file, Bucket=BUCKET, Key=adgroups_file_name)
                s3.put_object( Body=request.FILES['file_kw'].file, Bucket=BUCKET, Key=kw_file_name)

                # Define payload and run lambda function
                payload = f"""{{"kw_file_name":"{kw_file_name}",
                    "adgroups_file_name":"{adgroups_file_name}", 
                    "kw_column":"{form.cleaned_data['new_keywords_column']}",
                    "adgroups_column":"{form.cleaned_data['adgroups_column']}",
                    "kw_adgroups_column":"{form.cleaned_data['prev_keywords_column']}",
                    "action":"autobuilder"
                    }}"""
                info = run_lambda_function(payload)
                response = json.loads(info['Payload'].read())

    #             info = autobuilder_func(kw_file=request.FILES['file_kw'], 
    #                                   adgroups_file=request.FILES['file_adgroups'], 
    #                                   kw_column=form.cleaned_data['new_keywords_column'], 
    #                                   adgroups_column=form.cleaned_data['adgroups_column'],
    #                                   kw_adgroups_column=form.cleaned_data['prev_keywords_column'])


                if 'error' in response:
                    Event(event_type='error', time=datetime.now(), user_name=request.user.username, origin=origin, info=response).save()
                    return render(request, 'semapp/error_message.html', {'error': response['error']})           

                file_url = HTTP_S3_BUCKET_ADDRESS + response['output_file_name']
                Event(event_type='process', time=datetime.now(), user_name=request.user.username, origin=origin, info=response).save()
                return render(request, 'semapp/download_file.html', {'file_url': file_url})


        else:
            form = UploadFileFormAutoBuilder()
            Event(event_type='view', time=datetime.now(), user_name=request.user.username, origin=origin).save()
            return render(request, 'semapp/autobuilder.html', {'form': form})
        
    except ReadTimeoutError as error:
        error_info = {"Error type":f"ReadTimeoutError error: {str(error)}",
                      'Tracebak': traceback.format_exc(),
                      'File': file_name_s3,
                      'Form':clean_f(form)}
        log_exception_event(request, origin, error_info)
        return render(request, 
                      'semapp/error_message.html', 
                      {'error': 'Time out error. The file may be too big. We are working to fix this, In the meantime you can try to break it in smaller pieces...'})
    
    except BaseException as error:
        error_info={"Error type":str(error),
                    'Tracebak': traceback.format_exc(),
                    'File': file_name_s3,
                    'Form':clean_f(form)}
        log_exception_event(request, origin, error_info)
        return render(request, 
                      'semapp/error_message.html', 
                      {'error': f'Error: {str(error)}. If the error is a problem to you, contact the administrator at info@adquity.io'})
