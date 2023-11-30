from django.contrib import admin, messages
from django.contrib.auth.models import Permission
from django.http.request import HttpRequest
from django.utils.translation import ngettext

from .models import (
    Author,
    Book,
    BookInstance,
    Borrower,
    CheckOut,
    GenericInstance,
    Genre,
    Language,
    Series,
    VGInstance,
    VideoGame,
)


class PermissionAdmin(admin.ModelAdmin):
    @admin.display(description="App")
    def display_app(self, obj):
        return obj.content_type.app_label

    @admin.display(description="Model")
    def display_model(self, obj):
        return obj.content_type.model

    model = Permission
    list_filter = ["content_type__app_label", "content_type__model"]
    list_display = ["display_app", "display_model", "codename", "name"]


admin.site.register(Permission, PermissionAdmin)


class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0
    can_delete = False


class BookAdmin(admin.ModelAdmin):
    inlines = [BookInstanceInline]
    model = Book
    filter_horizontal = ["author", "genre", "item_language"]

    @admin.display(description="Author(s)")
    def display_author(self, obj):
        return ", ".join(
            author.display_name for author in obj.author.all().order_by("last_name")[:3]
        )

    @admin.display(description="Genre(s)")
    def display_genre(self, obj):
        return ", ".join(genre.name for genre in obj.genre.all().order_by("name")[:3])

    @admin.display(description="Language")
    def display_language(self, obj):
        return ", ".join(lang.name for lang in obj.item_language.all())

    list_display = [
        "title",
        "isbn",
        "display_author",
        "display_genre",
        "series",
        "display_language",
        "visible",
        "restricted",
    ]

    list_filter = ["visible", "restricted"]


class BookInline(admin.TabularInline):
    model = Book
    extra = 0
    can_delete = False
    max_num = 0
    exclude = ["summary"]
    ordering = ["position_in_series", "title"]

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class BookInstanceAdmin(admin.ModelAdmin):
    model = BookInstance
    filter_horizontal = ["item_language"]

    @admin.display(description="Author(s)")
    def display_author(self, obj):
        return ", ".join(
            author.display_name
            for author in obj.book.author.all().order_by("last_name")[:3]
        )

    @admin.display(description="Genre(s)")
    def display_genre(self, obj):
        return ", ".join(
            genre.name for genre in obj.book.genre.all().order_by("name")[:3]
        )

    @admin.display(description="Language")
    def display_language(self, obj):
        return ", ".join(lang.name for lang in obj.item_language.all())

    list_display = [
        "book",
        "cover_type",
        "status",
        "isbn",
        "display_author",
        "display_genre",
        "display_language",
        "instance_id",
    ]

    list_filter = [
        "cover_type",
        "status",
        "publish_date",
        "item_language",
    ]

    search_fields = ["book__title", "book__authors__last_name"]


class VideoGameAdmin(admin.ModelAdmin):
    model = VideoGame

    @admin.display(description="Language(s)")
    def display_language(self, obj):
        return ", ".join(lang.name for lang in obj.item_language.all())

    list_display = [
        "title",
        "platform",
        "series",
        "display_language",
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
        "item_language",
    )


class VGInstanceAdmin(admin.ModelAdmin):
    model = VGInstance
    filter_horizontal = ["item_language"]

    @admin.display(description="Publisher(s)")
    def display_author(self, obj):
        return ", ".join(
            author.display_name
            for author in obj.videogame.author.all().order_by("last_name")[:3]
        )

    @admin.display(description="Developer(s)")
    def display_developer(self, obj):
        return ", ".join(
            author.display_name
            for author in obj.videogame.developer.all().order_by("last_name")[:3]
        )

    @admin.display(description="Genre(s)")
    def display_genre(self, obj):
        return ", ".join(
            genre.name for genre in obj.videogame.genre.all().order_by("name")[:3]
        )

    @admin.display(description="Language")
    def display_language(self, obj):
        return ", ".join(lang.name for lang in obj.item_language.all())

    list_display = [
        "videogame",
        "platform",
        "medium_type",
        "status",
        "display_developer",
        "display_genre",
        "display_language",
        "instance_id",
    ]

    list_filter = [
        "medium_type",
        "platform",
        "status",
        "publish_date",
        "item_language",
    ]

    search_fields = ["videogame__title", "videogame__developer__last_name"]


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
        "title",
        "publish_date",
        "display_author",
        "display_genre",
    ]

    list_filter = [
        "publish_date",
        "author__display_name",
    ]

    search_fields = ["title"]


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

    @admin.action(
        description="Activate selected Members",
        permissions=["change"],
    )
    def activate_members(self, request, queryset):
        updated = queryset.update(status="A")
        self.message_user(
            request,
            ngettext(
                "%d borrower was activated.",
                "%d borrowers were activated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    actions = [activate_members]

    @admin.display(description="Members")
    def borrower_name(self, obj):
        return obj.user.full_common_name()

    list_display = [
        "borrower_name",
        "status",
        "max_fine_amount",
        "borrow_limit",
        "librarian",
        "valid_librarian",
    ]
    list_filter = [
        "status",
        "borrow_limit",
    ]
    search_fields = [
        "user__last_name",
        "user__first_name",
        "user__last_name",
        "user__uid",
        "user__email",
    ]
    ordering = [
        "user__common_name",
    ]

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm("permanently_delete_borrower"):
            return True

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.status == Borrower.BorrowerStatus.INACTIVE:
                if request.user.has_perm("permanently_delete_borrower"):
                    return True
            else:
                return super().has_change_permission(request, obj)


class LanguageAdmin(admin.ModelAdmin):
    model = Language
    list_display = [
        "name",
        "name_local",
        "isocode",
        "sorting",
    ]
    search_fields = [
        "name",
        "name_local",
    ]
    ordering = [
        "-sorting",
        "name",
        "isocode",
    ]


class CheckOutAdmin(admin.ModelAdmin):
    model = CheckOut

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.return_date:
                return False
            else:
                return super().has_change_permission(request, obj)
        else:
            return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.return_date:
                return False
            else:
                return super().has_delete_permission(request, obj)
        else:
            return super().has_delete_permission(request, obj)


class GenericInstanceAdmin(admin.ModelAdmin):
    @admin.display(description="Can Be Checked Out")
    def display_cbco(self, obj):
        return obj.can_be_checked_out

    @admin.display(description="Currently Checked Out")
    def display_isco(self, obj):
        return obj.is_checked_out

    model = GenericInstance
    list_display = [
        "content_object",
        "content_type",
        "object_id",
        "status",
        "medium_type",
        "display_cbco",
        "display_isco",
    ]

    list_filter = ["content_type", "status", "platform", "status"]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Borrower, BorrowerAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(VideoGame, VideoGameAdmin)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(VGInstance, VGInstanceAdmin)
admin.site.register(GenericInstance, GenericInstanceAdmin)
admin.site.register(CheckOut, CheckOutAdmin)
