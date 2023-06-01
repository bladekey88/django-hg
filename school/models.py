from django.db import models

# Create your models here.


class BasicCourse(models.Model):
    class Meta:
        verbose_name = "Basic Course"
        verbose_name_plural = "Basic Courses"
        ordering = [
            "name",
        ]

    name = models.CharField("Name", max_length=50)
    description = models.TextField(
        "Description", max_length=2500, null=True, blank=True
    )
    course_code = models.CharField("Course Code", max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.course_code})"

    def __repr__(self):
        return self.name
