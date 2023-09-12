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
from .models import Book, VideoGame, Author, Series, Borrower, BookInstance, VGInstance
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from users.models import Student, Staff
from django.db.models import Q


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
            num_book_instance = BookInstance.objects.count()
            num_vg_instance = VGInstance.objects.count()
            num_book_instance_available = BookInstance.objects.filter(status="A")
            num_vg_instance_available = VGInstance.objects.filter(status="A")
        else:
            num_books = Book.objects.filter(visible=True).count()
            num_vg = VideoGame.objects.filter(visible=True).count()
            num_book_instance = BookInstance.objects.filter(book__visible=True).count()
            num_vg_instance = VGInstance.objects.filter(videogame__visible=True).count()
            num_book_instance_available = BookInstance.objects.filter(
                status="A", book__visible=True
            )
            num_vg_instance_available = VGInstance.objects.filter(
                status="A", videogame__visible=True
            )

        num_series: int = Series.objects.count()
        num_borrowers = Borrower.objects.count()
        num_authors = Author.objects.count()
        num_visits = request.session.get("num_visits", 0)

        num_instances = num_vg_instance + num_book_instance
        num_book_instance_available = num_book_instance_available.count()
        num_vg_instance_available = num_vg_instance_available.count()
        request.session["num_visits"] = num_visits + 1

        context = {
            "num_books": num_books,
            "num_vg": num_vg,
            "num_series": num_series,
            "num_instances": num_instances,
            "num_authors": num_authors,
            "num_borrowers": num_borrowers,
            "num_visits": num_visits,
            "num_instances_available": num_book_instance_available
            + num_vg_instance_available,
        }

        return render(request, self.template_name, context)


class LibraryCreateAccount(LoginRequiredMixin, TemplateView):
    template_name = "library/create_account.html"

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
    template_name = "library/author_add.html"
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


class BorrowerSeach(NoPermissionMixin, PermissionRequiredMixin, TemplateView):
    permission_required = [
        "library.view_borrower",
    ]
    template_name = "library/borrower_search.html"

    def generate_alphabet_index(self):
        """
        Iterate through student objects add increment letter dict using
        surname. After iteration, in template check if count/len>0 render in
        colour if exists, else disabled/greyed out if not. In the corresponding view,
        raise 404 is letter has no surnames that begin with that letter
        """
        import string

        letters = {letter: 0 for letter in string.ascii_lowercase}
        qs = Borrower.objects.all()
        for borrower in qs:
            letters[borrower.user.full_name(False, True)[0].lower()] += 1
        return letters

    def get_context_data(self):
        context = super().get_context_data()
        context["houses"] = Student.House
        context["years"] = Student.Year
        context["alpha"] = self.generate_alphabet_index()
        context["stafftype"] = Staff.StaffType
        return context

    def post(self, request):
        search_string = request.POST["search-member-text"].strip()
        context = self.get_context_data()
        if len(search_string) >= 3:
            q1 = Q(user__first_name__icontains=search_string)
            q2 = Q(user__common_name__icontains=search_string)
            q3 = Q(user__last_name__icontains=search_string)
            q4 = Q(user__idnumber=search_string)
            members = Borrower.objects.filter(q1 | q2 | q3 | q4)
            context["query"] = search_string
            context["members"] = members
        else:
            context["query_error"] = True
        return render(request, self.template_name, context=context)


class BorrowerViewAlpha(NoPermissionMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["library.view_borrower"]
    template_name = "library/borrower_list_a_z.html"
    paginate_by = 10

    def get(self, request, letter):
        letter = letter.upper()
        qs = (
            Borrower.objects.filter(user__last_name__istartswith=letter)
            .all()
            .order_by("user__first_name")
        )
        if not qs:
            raise Http404(f"No members with surnames that begin with {letter}")
        context = dict()
        context["borrowers"] = qs
        context["letter"] = letter
        return render(request, self.template_name, context=context)


class BorrowerViewHouse(NoPermissionMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "library/borrower_list_house.html"

    def get(self, request, house):
        if house.lower() in [e.name.lower() for e in Student.House]:
            output = [e.value for e in Student.House if house.lower() == e.name.lower()]
            qs = (
                Borrower.objects.filter(user__student__house=output[0])
                .all()
                .order_by(
                    "user__student__year",
                    "user__first_name",
                )
            )
            if qs.count() > 0:
                context = {}
                context["borrowers"] = qs
                context["house"] = house
                return render(request, self.template_name, context=context)
            else:
                raise Http404("House has no students.")

        else:
            raise Http404("House does not exist or is not accessible.")


class BorrowerViewYear(NoPermissionMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["library.view_borrower"]
    template_name = "library/borrower_list_year.html"

    def get(self, request, year):
        if year.lower() in [e.name.lower() for e in Student.Year]:
            output = [e.value for e in Student.Year if year.lower() == e.name.lower()]
            qs = (
                Borrower.objects.filter(user__student__year=output[0])
                .all()
                .order_by(
                    "user__student__house",
                    "user__first_name",
                )
            )
            if qs.count() > 0:
                context = {}
                context["borrowers"] = qs
                context["year"] = year
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Year has no students.")
        else:
            raise Http404("Year does not exist or is not accessible.")


class BorrowerViewStaff(NoPermissionMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["library.view_borrower"]
    template_name = "library/borrower_list_staff.html"

    def get(self, request, stafftype):
        if stafftype.lower() in [e.name.lower() for e in Staff.StaffType]:
            output = [
                e.value for e in Staff.StaffType if stafftype.lower() == e.name.lower()
            ]
            qs = (
                Borrower.objects.filter(user__staff__staff_type=output[0])
                .all()
                .order_by(
                    "user__first_name",
                )
            )
            if qs.count() > 0:
                context = {}
                context["borrowers"] = qs
                context["stafftype"] = stafftype
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Staff type has no members")
        else:
            raise Http404("Staff type does not exist or is not accessible.")


class BorrowerListView(NoPermissionMixin, PermissionRequiredMixin, ListView):
    permission_required = ["library.view_borrower"]
    model = Borrower
    paginate_by = 0
    template_name = "library/borrower_list_all.html"


class BorrowerActivate(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, View
):
    model = Borrower
    permission_required = [
        "library.view_borrower",
        "library.change_borrower",
    ]
    success_message = "Member activated successfully."

    def get(self, request, *args, **kwargs):
        borrower_id = kwargs["pk"]
        try:
            borrower = Borrower.objects.get(id=borrower_id)
            if borrower.status == Borrower.BorrowerStatus.PENDING:
                borrower.status = Borrower.BorrowerStatus.ACTIVE
                borrower.save()
        except Borrower.DoesNotExist:
            pass  # Do Nothing for now

        messages.success(self.request, self.success_message)
        return redirect("library:borrower-detail", borrower_id)


class BorrowerAdd(
    NoPermissionMixin, SuccessMessageMixin, PermissionRequiredMixin, CreateView
):
    permission_required = ["library.add_borrower"]
    model = Borrower
    fields = [
        "user",
        "status",
    ]
    readonly_fields = ["borrow_limit"]
    template_name = "library/borrower_add.html"
    raise_exception = True
    success_url = reverse_lazy("library:borrowers-search")
    success_message = "Borrower created successfully."

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


class BorrowerDetail(NoPermissionMixin, SuccessMessageMixin, DetailView):
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
    template_name = "library/borrower_delete.html"
    success_url = reverse_lazy("library:borrowers-search")
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
