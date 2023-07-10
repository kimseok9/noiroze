from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.core.paginator import Paginator
from ..models import *
from ..forms import ComplainBoardForm, AnswerForm
from rest_framework.authtoken.models import Token
from django.contrib import messages



# 컴플레인 게시판에서 답변을 수정하는 함수
def answer_update(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            token_key = request.COOKIES.get('auth-token')
            
            try:
                token = Token.objects.get(key=token_key)
                if token.user == answer.author:
                    updated_answer = form.save(commit=False)
                    updated_answer.author = token.user
                    updated_answer.save()
                    return redirect('main:complain_board_detail', pk = answer.question.id)
                else:
                    messages.error(request, '수정 권한이 없습니다.')
                    return redirect('main:complain_board_detail', pk = answer.question.id)
            except Token.DoesNotExist:
                messages.error(request, '로그인이 필요합니다.')
                return redirect('/common/login/')
    else:
        form = AnswerForm(instance=answer)

    return render(request, 'board/complain_board/update_answer.html', {'form': form, 'answer_id': answer_id})

def answer_create(request, question_id):
    question = get_object_or_404(ComplainBoard, pk=question_id)
    form = AnswerForm()

    if request.method == "POST":
        form = AnswerForm(request.POST)
        
        if form.is_valid():
            answer = form.save(commit=False)

            # 토큰 인증 방식 적용
            token_key = request.COOKIES.get('auth-token')  # 쿠키에서 토큰 가져오기
            try:
                token = Token.objects.get(key=token_key)  # 토큰으로 사용자 정보 가져오기
            except Token.DoesNotExist:
                messages.error(request, '로그인이 필요합니다.')
                return redirect('/common/login/')

            answer.author = token.user  # author 속성에 로그인 계정 저장
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('main:complain_board_detail', pk=question.id)
    else:
        form = AnswerForm()
        

    context = {'question': question, 'form': form}
    return render(request, 'board/complain_board/complain_board_detail.html', context)
##################################################################################################################################################################

def answer_delete(request, question_id, answer_id):
    if request.method == "POST":
        answer = get_object_or_404(Answer, pk=answer_id)
        token_key = request.COOKIES.get('auth-token')
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            messages.error(request, '로그인이 필요합니다.')
            return redirect('/common/login/')
        
        if token.user == answer.author:
            answer.delete()
            messages.success(request, '답변이 삭제되었습니다.')
        else:
            messages.error(request, '자신의 답변만 삭제할 수 있습니다.')
    
    return redirect('main:complain_board_detail', pk=question_id)
