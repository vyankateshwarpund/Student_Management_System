"""Command to create or reset the three demo users immediately."""
from datetime import date
from django.core.management.base import BaseCommand
from accounts.models import User
from academics.models import Department, Course, Subject
from teachers.models import Teacher
from students.models import Student


class Command(BaseCommand):
    help = "Instantly creates or resets the 3 demo users (admin1, teacher1, student1)"

    def handle(self, *args, **options):
        self.stdout.write("Setting up demo users and essential structures...")

        # 1. Department
        dept, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={
                "name": "Computer Science and Engineering",
                "description": "Focuses on computer architecture, software systems, and AI."
            }
        )

        # 2. Course
        course, _ = Course.objects.get_or_create(
            code="BT-CSE",
            defaults={
                "name": "B.Tech Computer Science & Engineering",
                "department": dept,
                "duration": 4,
                "status": "active"
            }
        )

        # 3. Subject
        subject, _ = Subject.objects.get_or_create(
            code="CS401",
            defaults={
                "name": "Database Management Systems",
                "course": course,
                "semester": 4,
                "credits": 4
            }
        )

        # 4. Admin User
        admin_user, _ = User.objects.get_or_create(
            username="admin1",
            defaults={
                "email": "admin@test.com",
                "first_name": "System",
                "last_name": "Administrator",
                "role": "admin",
            }
        )
        admin_user.set_password("TestPass123!")
        admin_user.role = "admin"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("[OK] Admin: admin1 / TestPass123!"))

        # 5. Teacher User & Profile
        teacher_user, _ = User.objects.get_or_create(
            username="teacher1",
            defaults={
                "email": "teacher1@school.edu",
                "first_name": "Suresh",
                "last_name": "Rao",
                "role": "teacher",
                "phone": "9820011230",
            }
        )
        teacher_user.set_password("TeacherPass123!")
        teacher_user.role = "teacher"
        teacher_user.is_active = True
        teacher_user.save()

        t_prof, _ = Teacher.objects.get_or_create(
            user=teacher_user,
            defaults={
                "employee_id": "TCH001",
                "department": dept,
                "qualification": "M.Tech in Computer Science",
                "phone": "9820011230",
            }
        )
        t_prof.subjects.add(subject)
        self.stdout.write(self.style.SUCCESS("[OK] Teacher: teacher1 / TeacherPass123!"))

        # 6. Student User & Profile
        student_user, _ = User.objects.get_or_create(
            username="student1",
            defaults={
                "email": "aarav.sharma@nit.ac.in",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "role": "student",
                "phone": "9820011231",
            }
        )
        student_user.set_password("TestPass123!")
        student_user.role = "student"
        student_user.is_active = True
        student_user.save()

        Student.objects.get_or_create(
            user=student_user,
            defaults={
                "roll_number": "2026CSE001",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "email": "aarav.sharma@nit.ac.in",
                "phone": "9820011231",
                "gender": "male",
                "date_of_birth": date(2004, 5, 15),
                "department": dept,
                "course": course,
                "semester": 4,
                "year": 2026,
                "status": "active",
                "admission_date": date(2022, 8, 1),
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Student: student1 / TestPass123!"))

        self.stdout.write(self.style.SUCCESS("\nDone! All demo users are ready for login."))
