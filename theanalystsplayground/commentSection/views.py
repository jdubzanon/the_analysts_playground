from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from theanalystsplayground.commentSection.forms import CommentsForm
from theanalystsplayground.commentSection.models import Comments


def comments_view(request):
    context = {}
    context["allComments"] = Comments.objects.all().order_by("-date")
    if request.method == "POST":
        form = CommentsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                reverse("commentSection:commentsView"),
            )  # Redirect to prevent form resubmission

    else:
        context["form"] = CommentsForm()
        if not context["allComments"].exists():
            context["noComments"] = True

    return render(request, "commentSection/commentSection.html", context)
