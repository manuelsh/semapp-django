from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    similarity_threshold = forms.FloatField(max_value=0.99, min_value=0.70, initial=0.90, 
                                            help_text="Between 0.70 and 0.99")
    number_of_adgroups = forms.IntegerField(min_value=2, initial=1000, help_text="Number of adgroups to be created")
    max_number_keywords = forms.IntegerField(min_value=2,initial=10, 
                                             help_text="Maximum number of keywords per adgroup")
    #train_model = forms.BooleanField(help_text="Will train a new machine learning model, otherwise will use the default one.", required=False)
