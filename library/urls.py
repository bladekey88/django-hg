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
    path("items/edit/<str:pk>/", views.ItemEdit.as_view(), name="item-edit"),
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/add", views.BookAdd.as_view(), name="book-add"),
    path("books/<str:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path("books/<str:pk>/edit/", views.BookEdit.as_view(), name="book-edit"),
    path("books/<str:pk>/delete/", views.BookDelete.as_view(), name="book-delete"),
    path("video-games/", views.VGListView.as_view(), name="videogames"),
    path("video-games/add", views.VGAdd.as_view(), name="videogame-add"),
    path("video-games/<str:pk>", views.VGDetailView.as_view(), name="videogame-detail"),
    path("video-games/<str:pk>/edit/", views.VGEdit.as_view(), name="videogame-edit"),
    path(
        "video-games/<str:pk>/delete", views.VGDelete.as_view(), name="videogame-delete"
    ),
    path("series/", views.SeriesListView.as_view(), name="series"),
    path("series/add", views.SeriesAdd.as_view(), name="series-add"),
    path("series/<str:pk>", views.SeriesDetailView.as_view(), name="series-detail"),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("authors/add/", views.AuthorAdd.as_view(), name="author-add"),
    path("authors/<str:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
    path("members/", views.BorrowerListView.as_view(), name="borrowers"),
    path("members/add/", views.BorrowerAdd.as_view(), name="borrowers-add"),
    path("members/<str:pk>/", views.BorrowerDetail.as_view(), name="borrower-detail"),
    path("members/<str:pk>/edit/", views.BorrowerEdit.as_view(), name="borrower-edit"),
    path(
        "members/<str:pk>/delete/",
        views.BorrowerDelete.as_view(),
        name="borrower-delete",
    ),
    path(
        "members/<str:pk>/activate/",
        views.BorrowerActivate.as_view(),
        name="borrowers-activate",
    ),
]
