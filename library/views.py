from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
)
from .models import Book, VideoGame, Author, Series, Borrower
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.http import Http404

# Create your views here.


class LibraryHomeView(ListView):
    template_name = "library/index.html"

    def get(self, request):
        # Generate counts of some of the main objects
        num_books = Book.objects.count()
        num_vg = VideoGame.objects.count()
        num_series = Series.objects.count()
        # num_instances = BookInstance.objects.all().count()
        num_borrowers = Borrower.objects.count()
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
            "num_instances_available": 0,  # set to 0 until instances
            "num_authors": num_authors,
            "num_borrowers": num_borrowers,
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
                    "welcome": "Access granted to Hogwarts Library.",
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

        return super().get(request, *args, **kwargs)  # type: ignore

    def handle_no_permission(self):
        return redirect("library:index", permanent=False)


class BookListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["library.view_book"]
    model = Book
    paginate_by = 10
    template_name = "library/item_list.html"

    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="Librarians")
            or self.request.user.is_superuser
        ):
            return Book.objects.all()
        else:
            return Book.objects.filter(visible=True)


class BookDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = Book
    permission_required = ["library.view_book"]

    def get(self, request, *args, **kwargs):
        if request.user.library_user.status != "A":
            return self.handle_no_permission()

        book = Book.objects.get(id=kwargs["pk"])
        if not book.visible:
            if request.user.is_superuser or request.user.groups.filter(
                name="Librarians"
            ):
                return super().get(request, *args, **kwargs)
            else:
                raise Http404
        else:
            return super().get(request, *args, **kwargs)


class BookAdd(NoPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["library.add_book"]
    model = Book
    fields = [
        "title",
        "summary",
        "isbn",
        "author",
        "genre",
        "item_language",
        "publish_date",
        "part_of_series",
        "series",
        "position_in_series",
        "visible",
        "restricted",
    ]
    template_name = "library/item_add.html"
    raise_exception = True
    success_message = "Book created successfully."

    def form_valid(self, form):
        if not form.instance.part_of_series and (
            form.instance.series or form.instance.position_in_series
        ):
            form.instance.series = None
            form.instance.position_in_series = None
        return super().form_valid(form)


class ItemEdit(NoPermissionMixin, PermissionRequiredMixin, View):
    permission_required = [
        "library.change_book",
        "library.change_videogame",
    ]

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            item = Book.objects.get(id=pk)
        except Book.DoesNotExist:
            try:
                item = VideoGame.objects.get(id=pk)
            except VideoGame.DoesNotExist:
                raise Http404("Not Found")

        if item:
            return redirect(item.get_absolute_url() + "/edit")


class BookEdit(NoPermissionMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = ["library.change_book"]
    fields = [
        "title",
        "summary",
        "author",
        "genre",
        "part_of_series",
        "series",
        "position_in_series",
        "isbn",
        "visible",
        "restricted",
        "publish_date",
    ]
    template_name = "library/item_edit.html"


class BookDelete(NoPermissionMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ["library.delete_book"]
    permission_denied_message = "Access Forbidden"
    model = Book
    template_name = "library/item_delete.html"
    slug_field = "id"
    success_url = reverse_lazy("library:books")


class VGListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["library.view_videogame"]
    model = VideoGame
    paginate_by = 10
    template_name = "library/item_list.html"

    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="Librarians")
            or self.request.user.is_superuser
        ):
            return VideoGame.objects.all()
        else:
            return VideoGame.objects.filter(visible=True)


class VGDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = VideoGame
    permission_required = ["library.view_videogame"]

    def get(self, request, *args, **kwargs):
        vg = VideoGame.objects.get(id=kwargs["pk"])
        if not vg.visible:
            if request.user.is_superuser or request.user.groups.filter(
                name="Librarians"
            ):
                return super().get(request, *args, **kwargs)
            else:
                raise Http404


class VGAdd(NoPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["library.add_videogame"]
    model = VideoGame
    fields = [
        "title",
        "summary",
        "author",
        "developer",
        "platform",
        "genre",
        "item_language",
        "publish_date",
        "part_of_series",
        "series",
        "position_in_series",
        "visible",
        "restricted",
    ]
    template_name = "library/item_add.html"
    raise_exception = True
    success_message = "Video Game created successfully."

    def form_valid(self, form):
        if not form.instance.part_of_series and (
            form.instance.series or form.instance.position_in_series
        ):
            form.instance.series = None
            form.instance.position_in_series = None
        return super().form_valid(form)


class VGEdit(NoPermissionMixin, PermissionRequiredMixin, UpdateView):
    model = VideoGame
    permission_required = ["library.change_book"]
    fields = [
        "title",
        "summary",
        "author",
        "developer",
        "platform",
        "genre",
        "item_language",
        "publish_date",
        "part_of_series",
        "series",
        "position_in_series",
        "visible",
        "restricted",
        "publish_date",
    ]
    template_name = "library/item_edit.html"


class VGDelete(NoPermissionMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ["library.delete_videogame"]
    permission_denied_message = "Access Forbidden"
    model = VideoGame
    template_name = "library/item_delete.html"
    success_url = reverse_lazy("library:videogames")


class AuthorListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    model = Author
    paginate_by = 100
    permission_required = ["library.view_author"]


class AuthorAdd(NoPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["library.add_author"]
    model = Author
    template_name = "library/author-add.html"
    fields = "__all__"


class AuthorDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = Author
    permission_required = ["library.view_author"]


class SeriesListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    model = Series
    paginate_by = 10
    permission_required = ["library.view_series"]
    template_name = "library/item_list.html"


class SeriesDetailView(NoPermissionMixin, PermissionRequiredMixin, DetailView):
    model = Series
    permission_required = ["library.view_series"]


class SeriesAdd(NoPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["library.add_series"]
    model = Series
    fields = [
        "title",
        "summary",
        "author",
        "genre",
        "publish_date",
    ]
    template_name = "library/item_add.html"
    raise_exception = True
    success_message = "Series created successfully."


class BorrowerListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["library.view_borrower"]
    model = Borrower
    paginate_by = 0


class BorrowerActivate(NoPermissionMixin, PermissionRequiredMixin, View):
    model = Borrower
    permission_required = [
        "library.view_borrower",
        "library.change_borrower",
    ]

    def get(self, request, *args, **kwargs):
        borrower_id = kwargs["pk"]
        try:
            borrower = Borrower.objects.get(id=borrower_id)
            if borrower.status == Borrower.BorrowerStatus.PENDING:
                borrower.status = Borrower.BorrowerStatus.ACTIVE
                borrower.save()
        except Borrower.DoesNotExist:
            pass  # Do Nothing for now
        return redirect("library:borrowers")


class BorrowerAdd(NoPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["library.add_borrower"]
    model = Borrower
    fields = [
        "user",
        "status",
    ]
    readonly_fields = ["borrow_limit"]
    template_name = "library/borrower_add.html"
    raise_exception = True
    success_message = "Borrower created successfully."


class BorrowerEdit(NoPermissionMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ["library.change_borrower"]
    model = Borrower
    fields = [
        "status",
        "borrow_limit",
        "max_fine_amount",
    ]
    template_name = "library/borrower_edit.html"
    raise_exception = True
    success_message = "Borrower updated successfully."
    success_url = reverse_lazy("library:borrower")
