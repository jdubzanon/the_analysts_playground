from django import forms

from theanalystsplayground.commentSection.models import Comments


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["name", "title", "comments"]
        labels = {
            "name": "Name",
            "title": "Title",
            "comments": "",
        }
