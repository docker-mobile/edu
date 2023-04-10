from django import forms
from .models import Post

# forms are here
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('header_img', 'title', 'category', 'content', 'file')
        labels = {
            'header_img': 'تصویر اول',
            'title': 'موضوع',
            'category': 'دسته بندی',
            'content': 'متن',
            'file': 'ضمیمه',
        }
        widgets = {
            'header_img': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'required': False}),
        }
