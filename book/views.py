from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .consts import ITEM_PER_PAGE
from .models import Book, Review
from django.conf import settings

class ListBookView(LoginRequiredMixin, ListView):
    template_name='book/book_list.html'
    model=Book
    paginate_by=ITEM_PER_PAGE

    def get_queryset(self):
        qs = Book.objects.all()

        #カテゴリーで絞り込み
        category = self.request.GET.get('category')
        self.category = self.request.GET.get('category')
        self.sort = self.request.GET.get('sort')

        if category:
            qs = qs.filter(category=category)

        #ソート順
        sort = self.request.GET.get('sort')
        if sort == 'rating':
            qs = qs.annotate(avg_rating=Avg('review__rate')).order_by('-avg_rating')
        else:  #デフォルトは新着順
            qs = qs.order_by('-id')
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['sort'] = self.sort
        return context        
    
class DetailBookView(LoginRequiredMixin, DetailView):
    template_name='book/book_detail.html'
    model=Book

class CreateBookView(LoginRequiredMixin, CreateView):
    template_name='book/book_create.html'
    model=Book
    fields=('title', 'author', 'text', 'category', 'thumbnail')
    success_url=reverse_lazy('list_book')

    def form_valid(self, form):
        form.instance.user = self.request.user  # ログイン中ユーザーをセット
        return super().form_valid(form)
        

class DeleteBookView(LoginRequiredMixin, DeleteView):
    template_name='book/book_confirm_delete.html'
    model=Book
    success_url=reverse_lazy('list_book')

    def get_object(self, queryset=None):
        obj=super().get_object(queryset)

        if obj.user !=self.request.user:
            raise PermissionDenied
        
        return obj

class UpdateBookView(LoginRequiredMixin, UpdateView):
    template_name='book/book_update.html'
    model=Book
    fields=('title', 'author', 'text', 'category', 'thumbnail')

    def get_object(self, queryset=None):
        obj=super().get_object(queryset)

        if obj.user !=self.request.user:
            raise PermissionDenied
        
        return obj
    
    def get_success_url(self):
        return reverse('detail_book', kwargs={'pk': self.object.id})

def index_view(request):
    object_list=Book.objects.order_by('-id')  #新着順
    ranking_list=Book.objects.annotate(avg_rating=Avg('review__rate')).order_by('-avg_rating')

    paginator=Paginator(ranking_list, ITEM_PER_PAGE)
    page_number=request.GET.get('page',1)
    page_obj=paginator.page(page_number)

    return render(
        request,
        'book/index.html',
        {'object_list': object_list, 'ranking_list': ranking_list, 'page_obj':page_obj}
    )

class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ('book', 'title', 'text', 'rate')
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = Book.objects.get(pk=self.kwargs['book_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail_book', kwargs={'pk': self.object.book.id})

# Create your views here.
