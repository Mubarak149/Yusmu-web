from django.db import models
from django.db.models import Avg
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.timezone import now

class Teacher(models.Model):
    user = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE)
    specialise = models.ForeignKey("student.StudentCourses", on_delete=models.CASCADE)
    student = models.ManyToManyField(
        "student.Student",
        through="TeacherStudents",
        related_name="teachers"
    )
    def __str__(self):
        return self.user.username

class TeacherStudents(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.user.username} -> {self.student.user.username}"

class TeacherRating(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()  # Rating from 1 to 5, for example
    comment = models.TextField(blank=True, null=True)
    rated_by = models.ForeignKey("student.Student", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for {self.teacher.user.username} by {self.rated_by.username}"

    def average_rating(self):
        return self.teacher.ratings.aggregate(Avg('rating'))['rating__avg'] or 0


class Test(models.Model):
    teacher = models.ForeignKey(
        "Teacher", 
        on_delete=models.CASCADE, 
        related_name="tests"
    )
    course = models.ForeignKey(
        "student.StudentCourses", 
        on_delete=models.CASCADE, 
        related_name="tests", 
        null=True
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """Check if the test has expired."""
        return now() > self.created_at + timedelta(days=7)

    
    class Meta:
        ordering = ["-created_at"]  # Newest first by default


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return f"{self.text[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.is_correct and Answer.objects.filter(question=self.question, is_correct=True).exists():
            raise ValidationError("Only one correct answer is allowed per question.")
        super().save(*args, **kwargs)
