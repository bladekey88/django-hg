from ninja import NinjaAPI
from ninja import Schema
from datetime import datetime
from users.models import CustomUser
from django.shortcuts import get_object_or_404

api = NinjaAPI()


class HelloSchema(Schema):
    name: str = "world"


@api.post("/hello/")
def hello(request, data: HelloSchema):
    return f"Hello {data.name}"


@api.get("/maths/")
def math(request, a: int, b: int):
    return {"add": a + b, "multiply": a * b, "divide": a / b, "floordivide": a // b}


class UserSchema(Schema):
    is_authenticated: bool
    is_active: bool
    is_staff: bool
    created_externally: bool
    date_joined: datetime
    last_login: datetime
    uid: str
    email: str
    idnumber: int
    title: str
    sex: str
    first_name: str
    common_name: str
    middle_name: str | None = None
    last_name: str
    full_name: str
    full_common_name: str
    is_student: str
    is_school_staff: str
    is_parent: str


class Error(Schema):
    message: str


@api.get("/me/", response={200: UserSchema, 403: Error})
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": "Authentication Required"}
    return request.user


@api.get("/user/", response={200: UserSchema, 403: Error})
def user(request, uid):
    if not request.user.is_authenticated:
        return 403, {"message": "Authentication Required"}
    return get_object_or_404(CustomUser, uid=uid)
