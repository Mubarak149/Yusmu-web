#other import
import openai
# rest_framework import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
#django import
from django.conf import settings
#app import
from .models import Test, Question,Answer
from .permissions import isTeacher
from users.models import UserProjects
from .serializers import ProjectSerializer


class TeacherDashboard(APIView):
    pass

class TeacherProjectsViewSet(viewsets.ModelViewSet):
    queryset = UserProjects.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, isTeacher]
    
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
    
class TeacherSetTestView(APIView):
    def post(self, request ,*args, **kwargs):
        pass
    

class AITestGeneration(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, isTeacher]  # Allow only teachers to create tests

    def post(self, request, *args, **kwargs):
        title = request.data.get("title")
        if not title:
            return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate AI-based questions and answers
            questions_and_answers = self.generate_test_questions(title)

            # Create the test in the database
            test = Test.objects.create(
                teacher=request.user,  # Assuming teacher is logged in
                title=title,
                description=f"AI-generated test for {title}"
            )

            # Add questions and answers
            for qa in questions_and_answers:
                question = Question.objects.create(test=test, text=qa["question"])
                for answer in qa["answers"]:
                    Answer.objects.create(question=question, text=answer["text"], is_correct=answer["is_correct"])

            return Response({"message": "Test created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_test_questions(self, title):
        # Use OpenAI's GPT model to generate questions and answers
        try:
            openai.api_key = "your_openai_api_key"  # Replace with your actual API key

            # Define the prompt for the AI
            prompt = f"""
            Create a set of multiple-choice questions and answers about the topic "{title}".
            Each question should have 3 possible answers, with one being correct.
            Return the questions and answers as a JSON object with this format:
            [
                {{
                    "question": "Your question here?",
                    "answers": [
                        {{"text": "Correct answer", "is_correct": true}},
                        {{"text": "Wrong answer 1", "is_correct": false}},
                        {{"text": "Wrong answer 2", "is_correct": false}}
                    ]
                }},
                ...
            ]
            """

            # Make the API request
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use a GPT model
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )

            # Parse and return the AI-generated questions and answers
            ai_generated_data = eval(response["choices"][0]["text"].strip())
            return ai_generated_data

        except openai.error.OpenAIError as e:
            raise Exception(f"AI generation failed: {e}")
