from django.contrib import admin
from .models import Author, Genre, Series, Book, VideoGame, Borrower
from django.contrib.auth.models import Permission


class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    search_fields = ["name", "content_type__app_label"]
    list_filter = ["content_type__app_label"]


admin.site.register(Permission, PermissionAdmin)
# Register your models here.


class BookAdmin(admin.ModelAdmin):
    model = Book
    filter_horizontal = ["author", "genre"]

    @admin.display(description="Author(s)")
    def display_author(self, obj):
        return ", ".join(
            author.display_name for author in obj.author.all().order_by("last_name")[:3]
        )

    @admin.display(description="Genre(s)")
    def display_genre(self, obj):
        # raise Exception()
        return ", ".join(genre.name for genre in obj.genre.all().order_by("name")[:3])

    list_display = [
        "title",
        "isbn",
        "display_author",
        "display_genre",
        "series",
        "item_language",
    ]


class BookInline(admin.TabularInline):
    model = Book
    extra = 0
    can_delete = False
    readonly_fields = [
        "title",
        "genre",
        "author",
        "publish_date",
        "part_of_series",
        "series",
        "position_in_series",
        "id",
        "item_language",
        "isbn",
    ]
    max_num = 0
    exclude = ["summary"]
    ordering = ["position_in_series", "title"]


class VideoGameAdmin(admin.ModelAdmin):
    model = VideoGame
    list_display = [
        "title",
        "platform",
        "series",
        "item_language",
        "publish_date",
    ]

    list_filter = [
        "platform",
        "series",
        "publish_date",
        "item_language",
        "author",
        "developer",
    ]

    search_fields = [
        "title",
    ]

    filter_horizontal = (
        "genre",
        "author",
        "developer",
    )


class SeriesAdmin(admin.ModelAdmin):
    model = Series
    inlines = [BookInline]

    @admin.display(description="Author(s)")
    def display_author(self, obj):
        return ", ".join(
            author.display_name for author in obj.author.all().order_by("last_name")[:3]
        )

    @admin.display(description="Genre(s)")
    def display_genre(self, obj):
        # raise Exception()
        return ", ".join(genre.name for genre in obj.genre.all().order_by("name")[:3])

    list_display = [
        "name",
        "publish_date",
        "display_author",
        "display_genre",
    ]

    list_filter = [
        "publish_date",
        "author__display_name",
    ]

    search_fields = [
        "name",
    ]


class GenreAdmin(admin.ModelAdmin):
    model = Genre

    list_display = [
        "name",
        "genre_object",
        "genre_type",
    ]

    list_filter = [
        "genre_object",
        "genre_type",
    ]

    search_fields = [
        "name",
    ]

    ordering = [
        "genre_object",
        "genre_type",
        "name",
    ]


class AuthorAdmin(admin.ModelAdmin):
    model = Author
    list_display = [
        "display_name",
        "last_name",
        "first_name",
        "author_type",
    ]
    list_filter = [
        "date_of_birth",
        "date_of_death",
        "author_type",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "display_name",
    ]
    ordering = [
        "author_type",
        "display_name",
    ]


class BorrowerAdmin(admin.ModelAdmin):
    model = Borrower

    @admin.display(description="Author(s)")
    def borrower_name(self, obj):
        return obj.user.full_common_name()

    list_display = [
        "borrower_name",
        "status",
        "max_fine_amount",
        "borrow_limit",
    ]
    list_filter = [
        "status",
        "borrow_limit",
    ]
    search_fields = [
        "user__common_name",
        "user__uid",
        "user__email",
    ]
    ordering = [
        "user__first_name",
    ]


admin.site.register(Borrower, BorrowerAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(VideoGame, VideoGameAdmin)
