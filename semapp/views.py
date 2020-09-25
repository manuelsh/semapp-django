from django.shortcuts import render    
from .forms import UploadFileFormAdgroup, UploadFileFormAutoBuilder   
from django.http import HttpResponse, FileResponse
from .builders import adgroups_builder, autobuilder_func
from django.contrib.auth.decorators import login_required
from .models import Event
from django.forms.fields import JSONField
from datetime import datetime
import json

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
            info = adgroups_builder(uploaded_file = request.FILES['file'], 
                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'])
            # todo: if adgroups_builder returns error retrieve it as an event and inform user

            # returns output
            filename = "./media/output_adgroup_build.xlsx"
            Event(event_type='process', 
                  time=datetime.now(), 
                  user_name=request.user.username, 
                  origin=origin, 
                  info=info.update(clean_f(form))).save()
            return FileResponse(open(filename, 'rb'))
            
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
