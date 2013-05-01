from recordings.models import Score
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

fields = ('id',
    'energy_index__lt',
    'energy_index__gt',
    'kiwi_index__lt',
    'kiwi_index__gt',
    'datetime__gt',
    'datetime__lt',
    'sonogram__isnull',
    'kiwi__isnull',
    'kiwi',
    )
    

def _get_scores(request, per_page, page=1, **filters):
    page = request.GET.get('page') or page
    for field in fields:
        value = request.GET.get(field) or None
        if value:
            filters[field] = value
    print filters
    scores_list = Score.objects.select_related().filter(**filters)
    paginator = Paginator(scores_list, per_page)
    try:
        scores = paginator.page(page)
    except PageNotAnInteger:
        scores = paginator.page(1)
    except EmptyPage:
        scores = paginator.page(paginator.num_pages)
    return scores

def scores(request):
    scores = _get_scores(request, 1)
    return render(request, 'recordings/scores.html', {'scores':scores})

def scores_list(request):
    scores = _get_scores(request, 500)
    return render(request, 'recordings/scores_list.html', {'scores':scores})

    
    
