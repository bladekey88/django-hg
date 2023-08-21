from django.urls import path
from . import views

app_name = "library"


urlpatterns = [
    path("", views.LibraryHomeView.as_view(), name="index"),
    path(
        "create-account/",
        views.LibraryCreateAccount.as_view(),
        name="create-account",
    ),
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/<str:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path(
        "authors/<str:pk>",
        views.AuthorDetailView.as_view(),
        name="author-detail",
    ),
]
