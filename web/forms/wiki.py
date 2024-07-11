from web import models
from django import forms

from web.forms.bootstrap import Bootstrap


class WikeModelForm(Bootstrap, forms.ModelForm):
    class Meta:
        model = models.Wiki
        fields = ['title', 'content', 'parent']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        total_data_list = [("", "请选择")]
        data_list = models.Wiki.objects.filter(project=request.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
