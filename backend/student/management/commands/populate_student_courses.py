from django.core.management.base import BaseCommand
from student.models import StudentCourses

class Command(BaseCommand):
    help = 'Populate the StudentCourses table with initial data'

    def handle(self, *args, **kwargs):
        # Define the initial data
        initial_courses = [
            {
                'course_title': 'Ethical Hacking/Web Penetration Testing',
                'course_desc': 'An advanced course focusing on cybersecurity and penetration testing methodologies.',
                'course_price': 35_000,
            },
            {
                'course_title': 'Python Programming',
                'course_desc': 'An in-depth exploration of Python programming, including syntax, libraries, and practical projects.',
                'course_price': 20_000,
            },
            {
                'course_title': 'Scratch Programming',
                'course_desc': 'An introductory course designed for young learners to understand programming concepts through Scratch.',
                'course_price': 20_000,
            },
            {
                'course_title': 'Computer Fundamentals',
                'course_desc': 'A foundational course on computer operations, hardware, and software basics.',
                'course_price': 20_000,
            },
            {
                'course_title': 'Web Development(Front-End)',
                'course_desc': 'A comprehensive course on front-end development, including HTML, CSS, and JavaScript.',
                'course_price': 30_000,
            },
            {
                'course_title': 'Web Development(Back-End)',
                'course_desc': 'Covers back-end technologies such as server-side scripting, databases, and API integration.',
                'course_price': 40_000,
            },
            {
                'course_title': 'IOT/Robotic',
                'course_desc': 'An advanced course on IoT systems, robotics programming, and automation.',
                'course_price': 45_000,
            },
        ]

        # Add the data to the database
        for course in initial_courses:
            StudentCourses.objects.get_or_create(
                course_title=course['course_title'],
                defaults={
                    'course_desc': course['course_desc'],
                    'course_price': course['course_price'],
                }
            )

        # Print success message
        self.stdout.write(self.style.SUCCESS('Successfully populated StudentCourses table with initial data.'))
