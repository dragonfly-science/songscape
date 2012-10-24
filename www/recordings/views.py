from recordings.models import Score
from django.shortcuts import render, get_object_or_404

def scores(request):
    scores = Score.objects.filter(kiwi_index__gt=5, kiwi=None)
    return render(request, 'recordings/scores.html', {'scores':scores})
