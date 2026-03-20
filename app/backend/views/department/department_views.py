import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def list_view(request):

    return render(
        request,
        "department/list.html",
    )
