from typing import Optional
from django.contrib import admin
from django.http.request import HttpRequest
from .models import Author, Genre, Book, BookInstance, Borrower, Fine, BorrowerFine
from .forms import BorrowerFineAddForm


# Custom Actions
@admin.action(
    description="Return/Make Available Selected Items",
    permissions=["change"],
)
def make_items_available(modeladmin, request, queryset):
    queryset.update(status="a")
    queryset.update(borrower=None)
    queryset.update(due_back=None)


@admin.action(
    description="Make Selected Items Unavailable",
    permissions=["change"],
)
def make_items_unavailable(modeladmin, request, queryset):
    queryset.update(status="m")
    queryset.update(borrower=None)
    queryset.update(due_back=None)


# Admin Models.
class BookInline(admin.TabularInline):
    model = Book
    extra = 0


class BorrowerFileInline(admin.TabularInline):
    @admin.display(description="Payable Fine Total")
    def get_payable_fine_amount(self, obj):
        return obj.payable_fine_amount()

    model = BorrowerFine
    extra = 0
    can_delete = False
    can_add = False
    ordering = ["status"]
    readonly_fields = [
        "fine",
        "item",
        "get_payable_fine_amount",
        "resolved_date",
        "status",
    ]


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "last_name",
        "first_name",
        "date_of_birth",
        "date_of_death",
    )
    fields = [
        "display_name",
        ("first_name", "last_name"),
        ("date_of_birth", "date_of_death"),
    ]

    search_fields = (
        "display_name",
        "last_name",
        "first_name",
    )

    inlines = [BookInline]


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0
    fields = ("id", "imprint", "status", "borrower", "due_back")
    readonly_fields = ("status", "borrower", "due_back")


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")
    inlines = [BooksInstanceInline]

    @admin.display(description="Genre")
    def display_genre(self, obj):
        return ", ".join(genre.name for genre in obj.genre.all().order_by("name")[:3])


# Register the Admin classes for BookInstance using the decorator
class BookInstanceAdmin(admin.ModelAdmin):
    actions = [
        make_items_available,
        make_items_unavailable,
    ]

    @admin.display(description="Available to Borrow")
    def get_borrowable(self, obj):
        return obj.can_be_checked_out()

    list_filter = (
        "status",
        "due_back",
    )
    list_display = [
        "book",
        "status",
        "borrower",
        "due_back",
        "get_borrowable",
    ]
    readonly_fields = ("get_borrowable",)
    fieldsets = (
        (None, {"fields": ("book", "imprint", "id")}),
        (
            "Availability",
            {
                "fields": (
                    "get_borrowable",
                    "status",
                    "due_back",
                    "borrower",
                )
            },
        ),
    )


class FineAdmin(admin.ModelAdmin):
    model = Fine
    list_display = [
        "name",
        "value",
        "fine_frequency",
    ]


class BorrowerFineAdmin(admin.ModelAdmin):
    add_form = BorrowerFineAddForm
    model = BorrowerFine

    @admin.display(description="Live Fine Total")
    def get_current_fine_amount(self, obj):
        return round(obj.current_fine_amount(), 3)

    @admin.display(description="Payable Fine Total")
    def get_payable_fine_amount(self, obj):
        return obj.payable_fine_amount()

    @admin.display(description="Item Overdue by")
    def get_overdue_by(self, obj):
        return obj.item_overdue_by()

    list_display = [
        "borrower",
        "get_payable_fine_amount",
        "get_overdue_by",
        "fine",
        "status",
        "created_date",
        "modified_date",
    ]

    ordering = [
        "status",
        "borrower",
    ]

    list_filter = [
        "fine",
        "status",
        "created_date",
    ]

    search_fields = [
        "borrower__user__last_name",
        "borrower__user__first_name",
    ]

    readonly_fields = (
        "get_overdue_by",
        "get_current_fine_amount",
        "get_payable_fine_amount",
        "created_date",
        "modified_date",
        "resolved_date",
    )

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}

        # Add mode (i.e. obj doesn't exist)
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(**kwargs)
        return super().get_form(request, obj, **defaults)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj is not None:
            if request.user.is_superuser:
                return super().has_change_permission(request, obj)
            else:
                if obj.status == BorrowerFine.FineStatus.PAID:
                    return False
                else:
                    return True


class BorrowerAdmin(admin.ModelAdmin):
    inlines = [BorrowerFileInline]
    list_display = [
        "user",
        "status",
        "borrow_limit",
        "max_fine_amount",
    ]


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(Fine, FineAdmin)
admin.site.register(Borrower, BorrowerAdmin)
admin.site.register(BorrowerFine, BorrowerFineAdmin)
