from recordings.models import Score
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def scores(request):
    scores_list = Score.objects.filter(kiwi_index__gt=5, kiwi=None)
    paginator = Paginator(scores_list, 1)
    page = request.GET.get('page') or 1
    try:
        scores = paginator.page(page)
    except PageNotAnInteger:
        scores = paginator.page(1)
    except EmptyPage:
        scores = paginator.page(paginator.num_pages)

    return render(request, 'recordings/scores.html', {'scores':scores})

