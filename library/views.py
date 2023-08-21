from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from .models import Book, VideoGame, Author, Series, Borrower
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group

# Create your views here.


class LibraryHomeView(ListView):
    template_name = "library/index.html"

    def get(self, request):
        # Generate counts of some of the main objects
        num_books = Book.objects.all().count()
        num_vg = VideoGame.objects.all().count()
        num_series = Series.objects.all().count()
        # num_instances = BookInstance.objects.all().count()

        # Available books (status = 'a')
        # num_instances_available = BookInstance.objects.filter(status__exact="a").count()

        # The 'all()' is implied by default.
        num_authors = Author.objects.count()

        # Number of visits to this view, as counted in the session variable.
        num_visits = request.session.get("num_visits", 0)
        request.session["num_visits"] = num_visits + 1

        context = {
            "num_books": num_books,
            "num_vg": num_vg,
            "num_series": num_series,
            "num_instances": 0,  # set to 0 until instances implemented
            "num_instances_available": 0,  # set to 0 until instances implemented
            "num_authors": num_authors,
            "num_visits": num_visits,
        }

        return render(request, self.template_name, context)


class LibraryCreateAccount(LoginRequiredMixin, TemplateView):
    template_name = "library/create-account.html"

    def get(self, request):
        if not request.user.is_anonymous:
            try:
                Borrower.objects.get(user=request.user)
            except Borrower.DoesNotExist:
                Borrower.objects.create(user=request.user, status="A")

            if not request.user.groups.filter(name="Library Members"):
                library_group = Group.objects.get(name="Library Members")
                request.user.groups.add(library_group)

                context = {
                    "welcome": "You have been granted access to Hogwarts Library."
                }

                return render(request, self.template_name, context)
            else:
                return redirect("library:index")


class NoPermissionMixin:
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            if (
                request.user.library_user.status != "A"
            ):  # library_user is related name from new library model
                return self.handle_no_permission()

        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        return redirect("library:index", permanent=False)


class BookListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["library.view_book"]
    model = Book
    paginate_by = 10


class BookDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = Book
    permission_required = ["library.view_book"]


class AuthorListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    model = Author
    paginate_by = 50
    permission_required = ["library.view_author"]


class AuthorDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = Author
    permission_required = ["library.view_author"]
