from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.core.paginator import Paginator
from ..models import *
from ..forms import ComplainBoardForm, AnswerForm
from rest_framework.authtoken.models import Token
from django.contrib import messages


# 컴플레인 게시판 글 작성 함수
def board_create(request):
    if request.method == 'POST':
        form = ComplainBoardForm(request.POST)
        if form.is_valid():
            new_board = form.save(commit=False)
            # 현재 로그인된 사용자를 author에 저장
            token_key = request.COOKIES.get('auth-token')   # 쿠키에서 토큰 가져오기
            try:
                token = Token.objects.get(key=token_key)    # 토큰으로 사용자 정보 가져오기
            except Token.DoesNotExist:
                messages.error(request, '로그인이 필요합니다.')
                return redirect('/common/login/')
            new_board.author = token.user
            new_board.save()
            return redirect('/main/complain_board_list/')
    else:
        form = ComplainBoardForm()
        
    return render(request, 'board/complain_board/board_create.html', {'form': form})


# 컴플레인 게시판 글 수정 함수
def board_update(request, complain_board_id):
    complain_board = get_object_or_404(ComplainBoard, id=complain_board_id)

    if request.method == 'POST':
        form = ComplainBoardForm(request.POST, instance=complain_board)
        if form.is_valid():
            # 현재 로그인된 사용자를 확인
            token_key = request.COOKIES.get('auth-token')   # 쿠키에서 토큰 가져오기

            try:
                token = Token.objects.get(key=token_key)    # 토큰으로 사용자 정보 가져오기
                if token.user == complain_board.author:     # 유효한 사용자 확인
                    updated_board = form.save(commit=False)
                    updated_board.author = token.user
                    updated_board.save()
                    return redirect('/main/complain_board_list/')
                else:
                    messages.error(request, '수정 권한이 없습니다.')
                    return redirect('/main/complain_board_list/')
            except Token.DoesNotExist:
                messages.error(request, '로그인이 필요합니다.')
                return redirect('/common/login/')
    else:
        form = ComplainBoardForm(instance=complain_board)

    return render(request, 'board/complain_board/board_update.html', {'form': form, 'complain_board_id': complain_board_id})

# 컴플레인 게시판 글 삭제 함수    
def board_delete(request, complain_board_id):
    complain_board = get_object_or_404(ComplainBoard, id=complain_board_id)

    if request.method == 'POST':
        # 현재 로그인된 사용자를 확인
        token_key = request.COOKIES.get('auth-token')  # 쿠키에서 토큰 가져오기

        if token_key:
            try:
                token = Token.objects.get(key=token_key)  # 토큰으로 사용자 정보 가져오기
                if token.user == complain_board.author:   # 유효한 사용자 확인
                    complain_board.delete()
                    return redirect('main:complain_board_list')
                else:
                    messages.error(request, '삭제 권한이 없습니다.')
                    return redirect('/main/complain_board_list/')
            except Token.DoesNotExist:
                messages.error(request, '로그인이 필요합니다.')
                return redirect('/common/login/')
        else:
            messages.error(request, '로그인이 필요합니다.')
            return redirect('/common/login/')

    context = {
        'form': ComplainBoardForm(instance=complain_board)
    }
    return render(request, 'board/complain_board/board_delete.html', context)

# 컴플레인 게시판 리스트 함수 (커뮤니티 게시판 리스트 함수와 동일)
def complain_board_list(request):
    '''
    board_list 출력
    '''

    # 입력 인자
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬 기준 / default 최신순

    if so == 'recent':
        board_list = ComplainBoard.objects.order_by('-created_date')
    elif so == 'late':
        board_list = ComplainBoard.objects.order_by('created_date')
    elif so == 'recommend':
        board_list = ComplainBoard.objects.annotate(
            num_voter=Count('voter')).order_by('-num_voter', '-created_date')
    elif so == 'popular':
        board_list = ComplainBoard.objects.annotate(
            num_reply=Count('reply')).order_by('-num_reply', '-created_date')
    else:  # 위 경우 제외 board_id 역순정렬
        board_list = ComplainBoard.objects.order_by('-id')

    if kw:
        kw = kw.replace('년', '')
        kw = kw.replace('월', '')
        kw = kw.replace('일', '')
        board_list = board_list.filter(
            Q(title__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(author__name__icontains=kw) |  # 작성자 검색
            Q(club__name__icontains=kw) |  # 클럽 이름 검색
            Q(club__category__icontains=kw) |  # 클럽 카테고리 검색
            Q(event_date__icontains=kw)  # 모임일 검색
        ).distinct()

    paginator = Paginator(board_list, 10)  # 페이지당 10개
    page_obj = paginator.get_page(page)
    context = {'board_list': page_obj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'board/complain_board/complain_board_list.html', context)


# 컴플레인 게시판에서 글 제목 눌렀을 때 이동되는 화면
def complain_board_detail(request, pk):
    board = get_object_or_404(ComplainBoard, pk=pk)
    return render(request, 'board/complain_board/complain_board_detail.html', {'board': board})
