from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.core.paginator import Paginator
from ..models import *
from ..forms import ComplainBoardForm, AnswerForm
from rest_framework.authtoken.models import Token
from django.contrib import messages


# 기본 render 함수
def base_request(request):
    return render(request, 'base.html')

def dash_request(request):
    return render(request, 'dash.html')

def dong_101_request(request):
    return render(request, 'board/decibel_dong/dong_101.html')

def dong_102_request(request):
    return render(request, 'board/decibel_dong/dong_102.html')

def dong_103_request(request):
    return render(request, 'board/decibel_dong/dong_103.html')

def dong_104_request(request):
    return render(request, 'board/decibel_dong/dong_104.html')

def dong_105_request(request):
    return render(request, 'board/decibel_dong/dong_105.html')

# 녹음파일 서버에 저장하는 함수
@csrf_exempt
def download_sound_file(request):
    if request.method == 'POST':
        dong = request.POST['dong']
        ho = request.POST['ho']
        file_name = request.POST['file_name']
        sound_file = request.FILES['sound_file']
        model = models.Sound_File(dong=dong, ho=ho, file_name=file_name, sound_file=sound_file)
        model.save()

        print('Downloaded sound file:', dong, ho, file_name, sound_file)
        msg = {'result': 'success'}

    else:
        msg = {'result': 'fail'}

    return JsonResponse(msg)
