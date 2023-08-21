from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from .models import Book, Author, BookInstance, Borrower
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.utils import timezone


# Create your views here.


class LibraryHomeView(ListView):
    template_name = "catalog/index.html"

    def get(self, request):
        # Generate counts of some of the main objects
        num_books = Book.objects.all().count()
        num_instances = BookInstance.objects.all().count()

        # Available books (status = 'a')
        num_instances_available = BookInstance.objects.filter(status__exact="a").count()

        # The 'all()' is implied by default.
        num_authors = Author.objects.count()

        # Number of visits to this view, as counted in the session variable.
        num_visits = request.session.get("num_visits", 0)
        request.session["num_visits"] = num_visits + 1

        context = {
            "num_books": num_books,
            "num_instances": num_instances,
            "num_instances_available": num_instances_available,
            "num_authors": num_authors,
            "num_visits": num_visits,
        }

        return render(request, self.template_name, context)


class LibraryCreateAccount(LoginRequiredMixin, TemplateView):
    template_name = "catalog/create-account.html"

    def get(self, request):
        if not request.user.is_anonymous:
            try:
                Borrower.objects.get(user=request.user)
            except Borrower.DoesNotExist as e:
                print(e)
                Borrower.objects.create(user=request.user)

            if not request.user.groups.filter(name="Library Members"):
                library_group = Group.objects.get(name="Library Members")
                request.user.groups.add(library_group)

                context = {
                    "welcome": "You have been granted access to Hogwarts Library."
                }

                return render(request, self.template_name, context)
            else:
                return redirect("catalog:index")


class NoPermissionMixin:
    def handle_no_permission(self):
        return redirect("catalog:index", permanent=False)


class BookListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["catalog.view_book"]
    model = Book
    paginate_by = 10


class BookDetailView(PermissionRequiredMixin, DetailView):
    model = Book
    permission_required = ["catalog.view_book"]


class AuthorListView(PermissionRequiredMixin, ListView):
    model = Author
    paginate_by = 50
    permission_required = ["catalog.view_book"]


class AuthorDetailView(PermissionRequiredMixin, DetailView):
    model = Author
    permission_required = ["catalog.view_book"]


class LoanedBooksByUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10
    permission_required = ["catalog.view_book"]

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class OverdueItemsListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_required = [
        "catalog.view_borrowerfine",
        "catalog.view_addborrowerfine",
    ]
    model = BookInstance
    template_name = "catalog/bookinstance_overdue_items.html"

    def get_queryset(self):
        qs = BookInstance.objects.filter(
            Q(status__exact="o") & Q(due_back__lte=timezone.now())
        ).order_by("due_back")
        return qs
