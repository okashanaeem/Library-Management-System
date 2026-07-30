from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Book, Member, BookIssue
from .forms import BookForm, MemberForm, BookIssueForm


def dashboard(request):
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    active_issues = BookIssue.objects.filter(returned=False).count()
    overdue_issues = BookIssue.objects.filter(returned=False, due_date__lt=timezone.now().date()).count()
    recent_issues = BookIssue.objects.all().order_by('-issue_date')[:5]
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'active_issues': active_issues,
        'overdue_issues': overdue_issues,
        'recent_issues': recent_issues,
        'today': timezone.now().date(),
    }
    return render(request, 'library/dashboard.html', context)


def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return render(request, 'library/book_list.html', {'books': books, 'query': query})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add Book'})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Edit Book'})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


def member_list(request):
    query = request.GET.get('q', '')
    members = Member.objects.all()
    if query:
        members = members.filter(Q(name__icontains=query) | Q(email__icontains=query))
    return render(request, 'library/member_list.html', {'members': members, 'query': query})


def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'library/member_form.html', {'form': form, 'title': 'Add Member'})


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'library/member_form.html', {'form': form, 'title': 'Edit Member'})


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'library/member_confirm_delete.html', {'member': member})


def issue_list(request):
    issues = BookIssue.objects.all().order_by('-issue_date')
    today = timezone.now().date()
    return render(request, 'library/issue_list.html', {'issues': issues, 'today': today})


def issue_add(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            if book.available_copies > 0:
                issue = form.save(commit=False)
                issue.save()
                book.available_copies -= 1
                book.save()
                return redirect('issue_list')
            else:
                form.add_error('book', 'No copies available for this book.')
    else:
        form = BookIssueForm()
    return render(request, 'library/issue_form.html', {'form': form, 'title': 'Issue Book'})


def issue_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    if not issue.returned:
        issue.returned = True
        issue.save()
        book = issue.book
        book.available_copies += 1
        book.save()
    return redirect('issue_list')