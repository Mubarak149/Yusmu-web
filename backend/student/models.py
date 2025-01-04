from django.db import models
from django.core.exceptions import ValidationError

from users.models import UserProjects

class Student(models.Model):
    user = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE)
    courses = models.ManyToManyField(
        "StudentCourses",
        through="Enrollment",
        related_name="students"
    )
    is_active =  models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    
    def my_courses(self):
        """
        Retrieve all courses the student is enrolled in via the Enrollment model.
        """
        return self.courses.all()
    
    def my_projects(self):
        """
        Retrieve all projects associated with the student.
        """
        return UserProjects.objects.filter(user=self.user)
    
    def my_course_progress(self):
        """
        Retrieve the progress and completion status for each enrolled course.
        """

        enrollments = Enrollment.objects.filter(student=self)
        return enrollments.values(
            "course__course_title",  # Course title
            "progress",  # Progress percentage
            "completed"  # Completion status
        )


class StudentCourses(models.Model):
    course_title = models.CharField(max_length=50)
    course_desc = models.TextField()
    course_price = models.IntegerField()

    def __str__(self):
        return self.course_title


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(StudentCourses, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # e.g., percentage of completion
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.username} - {self.course.course_title}"
    
    class Meta:
        unique_together = ('student', 'course')

class StudentTestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.FloatField()
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.score} - {self.test_date}"


class SchoolFees(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(StudentCourses, on_delete=models.CASCADE)
    fee = models.IntegerField()  # Paid amount
    remaining_fee = models.IntegerField(default=0)  # Calculated field
    total_fee = models.IntegerField(default=0)  # Course price

    def save(self, *args, **kwargs):
        if not self.course:
            raise ValidationError("Course must be selected.")
        
        self.total_fee = self.course.course_price
        if self.fee > self.total_fee:
            raise ValidationError("Fee paid cannot exceed the total course fee.")
        
        self.remaining_fee = self.total_fee - self.fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fees for {self.student.user.username} - {self.course.course_title}"

