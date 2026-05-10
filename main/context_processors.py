from .models import Subject

def subjects_processor(request):
    return {
        'subjects': Subject.objects.all()
    } 

#dfsdafg
