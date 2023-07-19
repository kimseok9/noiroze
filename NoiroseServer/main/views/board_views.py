from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from ..models import *

# 커뮤니티 게시판 리스트 
def community_board_list(request):
    
    # 입력 인자
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬 기준 / default 최신순

    # 정렬 기준에 따라 게시물을 가져옴
    if so == 'recent':
        board_list = CommunityBoard.objects.order_by('-created_date')
    elif so == 'late':
        board_list = CommunityBoard.objects.order_by('created_date')
    elif so == 'recommend':
        board_list = CommunityBoard.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-created_date')
    elif so == 'popular':
        board_list = CommunityBoard.objects.annotate(num_reply=Count('reply')).order_by('-num_reply', '-created_date')
    else:
        board_list = CommunityBoard.objects.order_by('-id')

    # 검색어에 따라 필터링
    if kw:
        kw = kw.replace('년', '')
        kw = kw.replace('월', '')
        kw = kw.replace('일', '')
        board_list = board_list.filter(
    Q(title__icontains=kw) |  # 제목 검색
    Q(content__icontains=kw) |  # 내용 검색
    Q(author__name__icontains=kw)  # 작성자 검색
    ).distinct()


    paginator = Paginator(board_list, 10)  # 페이지당 10개
    page_obj = paginator.get_page(page)
    context = {'board_list': page_obj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'board/community_board/community_board_list.html', context)