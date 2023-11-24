from django.shortcuts import render


def page_not_found(request, exception):
    """Custom page 404"""
    return render(request, 'pages/404.html', status=404)