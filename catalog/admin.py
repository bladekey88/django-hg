from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Register your models here.


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "date_of_birth",
        "date_of_death",
    )
    fields = [
        "first_name",
        "last_name",
        ("date_of_birth", "date_of_death"),
    ]
    inlines = [BookInline]


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")
    inlines = [BooksInstanceInline]

    @admin.display(description="Genre")
    def display_genre(self, obj):
        return ", ".join(genre.name for genre in obj.genre.all().order_by("name")[:3])


# Register the Admin classes for BookInstance using the decorator
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = (
        "status",
        "due_back",
    )
    list_display = [
        "book",
        "status",
        "borrower",
        "due_back",
    ]

    fieldsets = (
        (None, {"fields": ("book", "imprint", "id")}),
        (
            "Availability",
            {
                "fields": (
                    "status",
                    "due_back",
                    "borrower",
                )
            },
        ),
    )


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
