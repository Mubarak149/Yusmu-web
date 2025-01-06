from rest_framework.serializers import Serializer, CharField, ModelSerializer
from student.models import Student
from .models import *

class LoginSerializer(Serializer):
    # Serializer to validate the input data for login
    username = CharField(required=True)  # Username is a required field
    password = CharField(required=True, write_only=True)  # Password is required and write-only to enhance security


class StudentUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'dob', 'pic', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Create the user with user_type set to "Student"
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            dob=validated_data.get('dob', None),
            pic=validated_data.get('pic', None),
            user_type="3",  # Force user_type to Student
        )
        
        # Create the associated Student instance
        Student.objects.create(user=user)
        return user
    
    def update(self, instance, validated_data):
        # Update user fields
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.pic = validated_data.get('pic', instance.pic)

        # # If password is provided, set it
        # password = validated_data.get('password', None)
        # if password:
        #     instance.set_password(password)

        # Save the user instance
        instance.save()

        # Update the associated Student instance if needed (if fields are passed in the data)
        student = instance.student
        student.save()

        return instance
