from django.shortcuts import render    
from .forms import UploadFileForm   
import pandas as pd
from django.http import HttpResponse
from .adgroups_builder import adgroups_builder
from django.views.static import serve 
import os
    
def build_adgroups(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #similarity_threshold = form.cleaned_data['similarity_threshold']
            adgroups_builder(uploaded_file = request.FILES['file'], 
                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'])
            file = open("./media/output.xlsx", 'rb') 
            response = HttpResponse(content=file)
            response['Content-Type'] = 'application/xlsx'
            response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' \
                                              % 'output'            
            return serve_file(filepath)
            #return serve(request, os.path.basename(filepath),os.path.dirname(filepath))
    else:
        form = UploadFileForm()
        return render(request, 'semapp/upload.html', {'form': form})
    

def serve_file(file_path):
    file = open(file_path, 'rb')
    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/xlsx'
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' \
                                      % 'whatever'
    return response