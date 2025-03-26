from django import forms
from django.contrib.auth.models import User
from .models import BlogPost, Comment, UserProfile

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'excerpt', 'content', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters long.')
        return title

    def clean_excerpt(self):
        excerpt = self.cleaned_data['excerpt']
        if excerpt and len(excerpt) > 200:
            raise forms.ValidationError('Excerpt cannot be longer than 200 characters.')
        return excerpt

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 50:
            raise forms.ValidationError('Content must be at least 50 characters long.')
        return content

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            }),
        }

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
        if commit:
            instance.save()
        return instance 