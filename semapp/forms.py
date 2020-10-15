from django import forms

class UploadFileFormAdgroup(forms.Form):
    file = forms.FileField()
    similarity_threshold = forms.FloatField(max_value=0.99, min_value=0.70, initial=0.90, 
                                            help_text="Between 0.70 and 0.99")
    number_of_adgroups = forms.IntegerField(min_value=2, initial=100, 
                                            help_text="Number of adgroups to be created", label='Number of ad groups:')
    max_number_keywords = forms.IntegerField(min_value=2,initial=10, 
                                             help_text="Maximum number of keywords per ad group")
    keyword_column = forms.CharField(label="Keyword column", 
                                          initial="Keyword", 
                                          help_text="Name of column containing the keywords", )
    volume_column = forms.CharField(label="Volume column", 
                                          initial="Volume", 
                                          help_text="Name of column containing the volume of each keyword", )
    
    
class UploadFileFormAutoBuilder(forms.Form):  
    file_kw = forms.FileField(label="Keywords file",
                              help_text="Upload the excel file with the new keywords")
#                               widget=forms.FileInput(attrs = {'class' : 'custom-control-file form-control-sm'}))
    
    new_keywords_column = forms.CharField(label="New keywords column", 
                                          initial="Keywords", 
                                          help_text="Name of column containing the new keywords to add", )
#                                           widget=forms.TextInput(attrs = {'class' : 'form-control form-control-sm'}) )
    file_adgroups = forms.FileField(label="Ad groups file", 
                                    help_text="Upload the excel file with the ad groups",)
#                                     widget=forms.FileInput(attrs = {'class' : 'form-control-file form-control-sm'}))
        
    adgroups_column = forms.CharField(label="Ad groups column", 
                                      initial="Adgroup", 
                                      help_text="Name of column containing the previous ad groups where the new keywords will be added",)
#                                      widget=forms.TextInput(attrs = {'class' : 'form-control form-control-sm'}))
    prev_keywords_column = forms.CharField(label="Previous keywords column", 
                                           initial="Keyword", 
                                           help_text="Name of column containing the previous keywords, already in the ad groups",)
#                                            widget=forms.TextInput(attrs = {'class' : 'form-control form-control-sm'}) )
    