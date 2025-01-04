#rest framework import
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

#app import
from .models import Student, Enrollment, StudentTestResult
from users.serializers import StudentUserSerializer
from users.models import UserProjects



class CourseSerializer(serializers.Serializer):
    #id = serializers.IntegerField(read_only=True)  # Assuming the ID is an integer
    course_title = serializers.CharField(max_length=200, read_only=True)
    course_desc = serializers.CharField(read_only=True)
    course_price = serializers.IntegerField(read_only=True)

class EnrollmentProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.course_title")

    class Meta:
        model = Enrollment
        fields = ['course_title', 'progress', 'completed']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProjects
        fields = ['id','title', 'description', 'url', 'image']

        
    def create(self, validated_data):
        request = self.context.get('request')

        if not request or not hasattr(request, 'user'):
            raise ValueError("Authentication credentials were not provided.")
 
        project = UserProjects.objects.create(user=request.user, **validated_data)

        return project


class ProjectPagination(PageNumberPagination):
    page_size = 3  # Number of projects per page
    page_size_query_param = 'page_size'
    max_page_size = 20
    
class StudentDashboardSerializer(serializers.ModelSerializer):
    user = StudentUserSerializer()
    projects = serializers.SerializerMethodField()
    course_progress = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['user', 'is_active', 'projects', 'course_progress']

    def get_projects(self, obj):
        """
        Paginate and serialize the projects associated with the student.
        """
        request = self.context.get('request')
        paginator = ProjectPagination()
        projects = obj.my_projects()
        paginated_projects = paginator.paginate_queryset(projects, request)
        return paginator.get_paginated_response(ProjectSerializer(paginated_projects, many=True).data).data

    def get_course_progress(self, obj):
        """
        Return the progress and completion status for each enrolled course.
        """
        progress = obj.my_course_progress()
        return list(progress)  # Convert QuerySet values to a list

class StudentVerifySerializer(serializers.Serializer):
    user = StudentUserSerializer()
    course_progress = serializers.SerializerMethodField()
    course_grade = serializers.SerializerMethodField()
    projects = ProjectSerializer(many=True)

    def get_course_progress(self, obj):
        # Query enrollments for the student
        enrollments = Enrollment.objects.filter(student=obj)
        # Serialize the progress for each enrollment
        progress_data = [
            {
                "course_title": enrollment.course.course_title,
                "progress": enrollment.progress,
                "completed": enrollment.completed,
            }
            for enrollment in enrollments
        ]
        return progress_data

    def get_course_grade(self, obj):
        # Placeholder logic for grades, implement as needed
        return None
    
    # def get_projects(self, obj):
    #     return None
             
class StudentDetailSerializer(serializers.ModelSerializer):
    user = StudentUserSerializer()  # Nested serializer for user details
    courses = CourseSerializer()
    class Meta:
        model = Student
        fields = ['user', 'courses']  # Include other fields as needed

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTestResult
        fields = ['student', 'score']



