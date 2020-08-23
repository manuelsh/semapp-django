from django.shortcuts import render    
from .forms import UploadFileForm   
from django.http import HttpResponse, FileResponse
from .adgroups_builder import adgroups_builder
from django.views.static import serve 

from django.contrib.auth.decorators import login_required

@login_required  
def build_adgroups(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # record session
            request.session['similarity_threshold'] = form.cleaned_data['similarity_threshold']
            request.session['number_of_adgroups'] = form.cleaned_data['number_of_adgroups']
            request.session['max_number_keywords'] = form.cleaned_data['max_number_keywords']
            request.session['file_name'] = request.FILES['file'].name
                        
            session = adgroups_builder(uploaded_file = request.FILES['file'], 
                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'],
                     request=request)
            
            request.session['end_adgroups_builder'] = True
            
            # returns output
            filename = "./media/output.xlsx"
            return FileResponse(open(filename, 'rb'))
            
    else:
        form = UploadFileForm()
        request.session['visited_build_adgroups'] = True
        return render(request, 'semapp/upload.html', {'form': form})
