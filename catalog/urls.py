from django.urls import path
from . import views
import library.urls

app_name = "catalog"

urlpatterns = library.urls.urlpatterns
# urlpatterns = library.urls.urlpatterns + [
#     path("", views.LibraryHomeView.as_view(), name="index"),
#     path(
#         "create-account/",
#         views.LibraryCreateAccount.as_view(),
#         name="create-account",
#     ),
#     path("books/", views.BookListView.as_view(), name="books"),
#     path("book/<int:pk>", views.BookDetailView.as_view(), name="book-detail"),
#     path("authors/", views.AuthorListView.as_view(), name="authors"),
#     path("authors/<int:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
#     path("my-items/", views.LoanedBooksByUserListView.as_view(), name="my-items"),
#     path("librarian/", views.OverdueItemsListView.as_view(), name="overdue-items,"),
# ]
