from recordings.models import Snippet
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
    

def _get_snippets(request, per_page, page=1, **filters):
    page = request.GET.get('page') or page
    for field in fields:
        value = request.GET.get(field) or None
        if value:
            filters[field] = value
    print filters
    snippets_list = Snippet.objects.select_related().filter(**filters)
    paginator = Paginator(snippets_list, per_page)
    try:
        snippets = paginator.page(page)
    except PageNotAnInteger:
        snippets = paginator.page(1)
    except EmptyPage:
        snippets = paginator.page(paginator.num_pages)
    return snippets

def snippets(request):
    snippets = _get_snippets(request, 1)
    return render(request, 'recordings/snippets.html', {'snippets':snippets})

def snippets_list(request):
    snippets = _get_snippets(request, 500)
    return render(request, 'recordings/snippets_list.html', {'snippets':snippets})

    
    
