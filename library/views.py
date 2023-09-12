from django.apps import apps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
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
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser


# Create your views here.
def get_parent_model(pk):
    item_models = [Book, VideoGame, Series]
    item = None
    for model in item_models:
        try:
            item = model.objects.get(id=pk)
        except ObjectDoesNotExist:
            pass
    return item.__class__.__name__ if item else False


def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


class LibraryHomeView(ListView):
    template_name = "library/index.html"

    def get(self, request):
        # Generate counts of some of the main objects
        if request.user.groups.filter(name="Librarians"):
            num_books = Book.objects.count()
            num_vg = VideoGame.objects.count()
        else:
            num_books = Book.objects.filter(visible=True).count()
            num_vg = VideoGame.objects.filter(visible=True).count()

        num_series: int = Series.objects.count()
        num_borrowers = Borrower.objects.count()
        num_authors = Author.objects.count()
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
        item_type = get_parent_model(pk)
        if item_type:
            return redirect(f"library:{str(item_type).lower()}-edit", pk)
        else:
            raise Http404("Not Found")


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
        else:
            return super().get(request, *args, **kwargs)


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


class SeriesEdit(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, UpdateView
):
    permission_required = ["library.change_series"]
    template_name = "library/item_edit.html"
    model = Series
    fields = ["title", "author", "summary", "genre", "publish_date"]
    success_message = "Series updated successfully."

    def get_success_url(self) -> str:
        return reverse_lazy("library:series-detail", kwargs={"pk": self.object.pk})


class SeriesDelete(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView
):
    permission_required = [
        "library.delete_series",
        "library.change_book",
        "library.change_videogame",
    ]

    model = Series
    template_name = "library/item_delete.html"
    success_url = reverse_lazy("library:series")


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
    success_url = reverse_lazy("library:borrowers")

    # TODO ADD TO MODEL FORM TO OVERRIDE QUERYSET
    # def get_queryset(self):
    #     borrower_id_qs = Borrower.objects.all().values("user__id")
    #     user_qs = CustomUser.objects.exclude(id__in=borrower_id_qs)
    #     raise Exception(user_qs)


class BorrowerEdit(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, UpdateView
):
    permission_required = ["library.change_borrower"]
    model = Borrower
    fields = [
        "status",
        "borrow_limit",
        "max_fine_amount",
    ]
    template_name = "library/borrower_edit.html"
    raise_exception = True
    success_message = "Member updated successfully"

    def get_success_url(self) -> str:
        return reverse_lazy("library:borrower-detail", kwargs={"pk": self.object.pk})


class BorrowerDetail(NoPermissionMixin, DetailView):
    model = Borrower
    template_name = "library/borrower_detail.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name="Librarians"):
            return super().get(request, *args, **kwargs)
        else:
            if str(request.user.library_user.pk) == str(kwargs["pk"]):
                return super().get(request, *args, **kwargs)
            else:
                return redirect(
                    "library:borrower-detail", pk=request.user.library_user.pk
                )
                return redirect("library:borrower-detail", request.user.pk)


class BorrowerDelete(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView
):
    permission_required = ["library.delete_borrower"]
    permission_denied_message = "Access Forbidden"
    model = Borrower
    template_name = "library/borrower-delete.html"
    success_url = reverse_lazy("library:borrowers")
    success_message = (
        "Member has been marked for deletion. Deletion will occur after admin review."
    )

    def get_success_message(self, cleaned_data):
        return self.success_message

    def form_valid(self, form):
        self.object.status = "I"
        self.object.save()
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class ItemVisibility(NoPermissionMixin, PermissionRequiredMixin, View):
    permission_required = ["library.change_book", "library.change_videogame"]
    success_message = "Visibility has been changed"

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        pm = get_parent_model(pk)
        if pm:
            model = apps.get_model("library", pm)
            item = model.objects.get(id=pk)
            item.visible = not (item.visible)  # type: ignore
            item.save()

            if is_ajax(request):
                data = {}
                data["visible"] = item.visible  # type: ignore
                return JsonResponse(data)
            else:
                messages.success(
                    self.request, f"{self.success_message} for '{item.title}'."
                )
                return redirect(f"library:{str(pm).lower()}s")
        else:
            raise Http404("Not Found")
