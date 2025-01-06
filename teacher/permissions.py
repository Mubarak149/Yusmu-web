from rest_framework.permissions import BasePermission

class isTeacher(BasePermission):
    """
    Custom permission to check if the user is a student.
    """
    def has_permission(self, request, view):
        # Example: Check if the user has a 'is_student' attribute or group
        
        return request.user.user_type == "2"

    def has_object_permission(self, request, view, obj):
        # Optional: Add object-level permission checks if needed
        print("the Has Object Permission")
        return True
