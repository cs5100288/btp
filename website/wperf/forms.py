from django import forms

class UploadForm(forms.Form):
    uploadfile = forms.FileField(
        label='Select a file',
        help_text='max. size limit: none'
    )
