import requests
#rest import
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
#django import
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from django.db import transaction
#app import
from .permissions import IsStudent
from users.models import UserProjects
from teacher.models import Test,Question,Answer
from teacher.serializers import TestSerializer
from .models import StudentCourses, Student, StudentTestResult
from .serializers import CourseSerializer, StudentDetailSerializer, StudentVerifySerializer
from users.serializers import StudentUserSerializer
from .serializers import StudentDashboardSerializer, ProjectSerializer

class CourseListView(generics.ListAPIView):
    
    queryset = StudentCourses.objects.all()
    serializer_class = CourseSerializer

class CourseDetailsPayment(APIView):
    def get(self, request, id, *args, **kwargs):
        
        try:
            # Retrieve course from the database
            course = StudentCourses.objects.get(id=id)
        except StudentCourses.DoesNotExist:
            raise NotFound("Course not found")
        
        # Prepare the response data
        course_data = CourseSerializer(course).data
        #course_data['user'] = str(request.user)
        return Response(course_data)

class NewStudentView(APIView):
    # Apply throttling to this specific view
    throttle_classes = [ AnonRateThrottle, UserRateThrottle]
    
    def post(self, request):
        serializer = StudentUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Use a transaction to ensure both CustomUser and Student are created together
                with transaction.atomic():
                    user = serializer.save()  # The `create` method in the serializer handles both user and student creation
                    
                    # Log in the user
                    login(request, user)
                    
                    # Redirect to the user's dashboard
                    return redirect(reverse('dashboard'))
                
                
            except Exception as e:
                print(str(e)) 
                return Response(
                    {"error": f"Failed to create student: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StudentView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    """
    Handles GET and POST requests for Student data.
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Ensure the user is a student
            if request.user.user_type != "3":
                return Response(
                    {"error": "Access denied. Only students can access this view."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            # Retrieve the student object associated with the logged-in user
            student = Student.objects.get(user=request.user)
            serializer = StudentDetailSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student record not found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )
           
    def put(self, request):
        try:
            # Ensure the user is a student
            if request.user.user_type != "3":
                return Response(
                    {"error": "Access denied. Only students can update their data."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            # Retrieve the student object associated with the logged-in user
            student = Student.objects.get(user=request.user)
            serializer = StudentUserSerializer(student.user, data=request.data, partial=True)  # Allow partial updates
            
            if serializer.is_valid():
                try:
                    # Use a transaction to ensure both CustomUser and Student are updated together
                    with transaction.atomic():
                        updated_user = serializer.save()  # Save the updated CustomUser details
                        
                        # Update the associated Student instance if needed (extend this if you want to update Student model fields)
                        #student.save()
                        
                        return Response(
                            StudentDetailSerializer(student).data,
                            status=status.HTTP_200_OK,
                        )
                except Exception as e:
                    print(str(e))
                    return Response(
                        {"error": f"Failed to update student: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Student.DoesNotExist:
            return Response(
                {"error": "Student record not found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            ) 

class StudentDashboardView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the student object for the logged-in user
            student = Student.objects.get(user=request.user)
            
            # Pass the request object to the serializer for pagination
            serializer = StudentDashboardSerializer(student, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Generic error handler
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class StudentVerify(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        try:
            # Fetch the student object for the logged-in user
            student = Student.objects.get(user__username=username)
            serializer =StudentVerifySerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Generic error handler
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
              
class StudentProjectsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = UserProjects(data=request.data)
        if serializer.is_valid():
            try:
                # Use a transaction to ensure both CustomUser and Student are created together
                with transaction.atomic():
                    project = serializer.save()  # The `create` method in the serializer handles both user and student creation
                    return Response(
                    {"Success": "Projects Created Sucessfully"},
                    status=status.HTTP_201_CREATED,
                )
                
                
            except Exception as e:
                print(str(e)) 
                return Response(
                    {"error": f"Failed to create student: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StudentProjectsViewSet(viewsets.ModelViewSet):
    queryset = UserProjects.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This method filters the queryset to only include the projects
        belonging to the logged-in user.
        """
        try:
            return UserProjects.objects.filter(user=self.request.user)
        except Exception as e:
            raise ValidationError(f"Error retrieving projects: {str(e)}")

    def perform_create(self, serializer):
        """
        Automatically associate the created project with the logged-in user's student.
        """
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(f"Error creating project: {str(e)}")

    def perform_update(self, serializer):
        """
        This method ensures that the user can only update their own project.
        """
        try:
            project = self.get_object()
            if project.user != self.request.user:
                raise PermissionDenied("You do not have permission to edit this project.")
            serializer.save()
        except PermissionDenied as e:
            raise e
        except NotFound as e:
            raise NotFound("Project not found.")
        except Exception as e:
            raise ValidationError(f"Error updating project: {str(e)}")

    def perform_destroy(self, instance):
        """
        This method ensures that the user can only delete their own project.
        """
        try:
            if instance.user != self.request.user:
                raise PermissionDenied("You do not have permission to delete this project.")
            instance.delete()
        except PermissionDenied as e:
            raise e
        except NotFound as e:
            raise NotFound("Project not found.")
        except Exception as e:
            raise ValidationError(f"Error deleting project: {str(e)}")
    

class StudentTakingTest(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Allow all authenticated users to view tests
        test = Test.objects.filter(is_expired=False)
        serializer = TestSerializer(test, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Restrict POST access to students
        self.permission_classes = [IsAuthenticated, IsStudent]
        self.check_permissions(request)

        student = request.user  # Assuming user is a student
        answers = request.data.get('answers', [])
        test_id = request.data.get('test_id')

        try:
            test = Test.objects.get(id=test_id, is_expired=False)
        except Test.DoesNotExist:
            return Response({"error": "Test not found or expired"}, status=status.HTTP_404_NOT_FOUND)

        score = self.calculate_score(test, answers)
        test_result = Test.objects.create(student=student, score=score, title=test.title)

        return Response({"message": "Test submitted", "score": score}, status=status.HTTP_201_CREATED)

    def calculate_score(self, test, answers):
        # Validate answers and calculate score
        score = 0
        for answer in answers:
            question_id = answer.get('question_id')
            selected_answer_id = answer.get('answer_id')

            try:
                question = test.questions.get(id=question_id)
                correct_answer = question.answers.filter(is_correct=True).first()

                if correct_answer and correct_answer.id == selected_answer_id:
                    score += 1
            except Question.DoesNotExist:
                continue

        return score
