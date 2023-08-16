from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Book, Author, BookInstance
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group

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

        if not request.user.groups.filter(name="Library Members"):
            library_group = Group.objects.get(name="Library Members")
            request.user.groups.add(library_group)
            context["welcome"] = "You have been granted access to Hogwarts Library."

        return render(request, self.template_name, context)


class BookListView(ListView):
    model = Book
    paginate_by = 10


class BookDetailView(DetailView):
    model = Book


class AuthorListView(ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )
