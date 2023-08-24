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
    path("books/add", views.BookAdd.as_view(), name="books-add"),
    path("books/<str:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path("books/<str:pk>/delete/", views.BookDelete.as_view(), name="book-delete"),
    path("video-games/", views.VGListView.as_view(), name="videogames"),
    path("video-games/add", views.VGAdd.as_view(), name="videogames-add"),
    path("video-games/<str:pk>", views.VGDetailView.as_view(), name="videogame-detail"),
    path(
        "video-games/<str:pk>/delete", views.VGDelete.as_view(), name="videogame-delete"
    ),
    path("series/", views.SeriesListView.as_view(), name="series"),
    path("series/<str:pk>", views.SeriesDetailView.as_view(), name="series-detail"),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("authors/<str:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
]
