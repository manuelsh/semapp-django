from django.shortcuts import render    
from .forms import UploadFileFormAdgroup, UploadFileFormAutoBuilder   
from django.http import HttpResponse, FileResponse
from .builders import adgroups_builder, autobuilder_func
#from django.views.static import serve 
from django.contrib.auth.decorators import login_required

@login_required  
def build_adgroups(request):
    if request.method == 'POST':
        form = UploadFileFormAdgroup(request.POST, request.FILES)
        if form.is_valid():
            # record session
            request.session['similarity_threshold'] = form.cleaned_data['similarity_threshold']
            request.session['number_of_adgroups'] = form.cleaned_data['number_of_adgroups']
            request.session['max_number_keywords'] = form.cleaned_data['max_number_keywords']
            request.session['file_name'] = request.FILES['file'].name
                        
            error, request = adgroups_builder(uploaded_file = request.FILES['file'], 
                     similarity_clusters = form.cleaned_data['similarity_threshold'], 
                     number_of_clusters = form.cleaned_data['number_of_adgroups'], 
                     number_of_kw_per_adgroup = form.cleaned_data['max_number_keywords'],
                     request=request)
            
            if error:
                error = request.session['error']
                return HttpResponse(error)
            else:
                request.session['end_adgroups_builder'] = True

                # returns output
                filename = "./media/output_adgroup_build.xlsx"
                return FileResponse(open(filename, 'rb'))
            
    else:
        form = UploadFileFormAdgroup()
        if 'visits_build_adgroups_count' in request.session:
            request.session['visits_build_adgroups_count'] += 1
        else:
            request.session['visits_build_adgroups_count'] = 1
        return render(request, 'semapp/build_adgroups.html', {'form': form})

    
@login_required  
def autobuilder(request):
    if request.method == 'POST':
        form = UploadFileFormAutoBuilder(request.POST, request.FILES)
        if form.is_valid():
            # record session
            request.session['file_name_keywords'] = request.FILES['file_kw'].name
            request.session['file_name_adgroups'] = request.FILES['file_adgroups'].name
            
            error, request = autobuilder_func(kw_file=request.FILES['file_kw'], 
                                  adgroups_file=request.FILES['file_adgroups'], 
                                  kw_column=form.cleaned_data['new_keywords_column'], 
                                  adgroups_column=form.cleaned_data['adgroups_column'],
                                  kw_adgroups_column=form.cleaned_data['prev_keywords_column'], 
                                  request=request)
            if error:
                error = request.session['error']
                return HttpResponse(error)
            else:            
                request.session['end_autobuilder'] = True

                # returns output
                filename = "./media/output_autobuilder.xlsx"
                return FileResponse(open(filename, 'rb'))
            
    else:
        form = UploadFileFormAutoBuilder()
        if 'visits_autobuilder_count' in request.session:
            request.session['visits_autobuilder_count'] += 1
        else:
            request.session['visits_autobuilder_count'] = 1
        return render(request, 'semapp/autobuilder.html', {'form': form})
