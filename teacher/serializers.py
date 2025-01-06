#rest framework import
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

#app import
from .models import Test, Question, Answer
from users.models import UserProjects


class ProjectPagination(PageNumberPagination):
    page_size = 3  # Number of projects per page
    page_size_query_param = 'page_size'
    max_page_size = 20
    
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


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'teacher', 'title', 'description', 'created_at', 'questions', 'is_expired']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop('answers')
            question = Question.objects.create(test=test, **question_data)
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return test

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions')
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update or delete existing questions and answers
        existing_questions = {q.id: q for q in instance.questions.all()}
        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id and question_id in existing_questions:
                question = existing_questions.pop(question_id)
                question.text = question_data.get('text', question.text)
                question.save()

                # Update or delete existing answers
                existing_answers = {a.id: a for a in question.answers.all()}
                for answer_data in question_data.get('answers', []):
                    answer_id = answer_data.get('id')
                    if answer_id and answer_id in existing_answers:
                        answer = existing_answers.pop(answer_id)
                        answer.text = answer_data.get('text', answer.text)
                        answer.is_correct = answer_data.get('is_correct', answer.is_correct)
                        answer.save()
                    else:
                        # Create new answer
                        Answer.objects.create(question=question, **answer_data)

                # Delete removed answers
                for answer in existing_answers.values():
                    answer.delete()
            else:
                # Create new question and answers
                answers_data = question_data.pop('answers', [])
                question = Question.objects.create(test=instance, **question_data)
                for answer_data in answers_data:
                    Answer.objects.create(question=question, **answer_data)

        # Delete removed questions
        for question in existing_questions.values():
            question.delete()

        return instance

    def delete(self, instance):
        instance.delete()
        return {"message": "Test deleted successfully"}
