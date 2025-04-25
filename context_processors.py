from .models import Category

def categories(request):
    """
    Context processor that adds the list of categories to every request context
    """
    return {'categories': Category.objects.all()}