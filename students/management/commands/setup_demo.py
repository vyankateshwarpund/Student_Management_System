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

        # 5. Teacher User & Profile (Dr. Meera Kulkarni)
        meera_user, _ = User.objects.get_or_create(
            username="cse_fac_002",
            defaults={
                "email": "meera.kulkarni@example.com",
                "first_name": "Meera",
                "last_name": "Kulkarni",
                "role": "teacher",
                "phone": "9820010002",
            }
        )
        meera_user.first_name = "Meera"
        meera_user.last_name = "Kulkarni"
        meera_user.set_password("TeacherPass123!")
        meera_user.role = "teacher"
        meera_user.is_active = True
        meera_user.save()

        t_meera, _ = Teacher.objects.get_or_create(
            employee_id="CSE-FAC-002",
            defaults={
                "user": meera_user,
                "department": dept,
                "qualification": "Professor | Data Structures and Algorithms",
                "phone": "9820010002",
            }
        )
        t_meera.user = meera_user
        t_meera.save()
        t_meera.subjects.add(subject)
        self.stdout.write(self.style.SUCCESS("[OK] Teacher: cse_fac_002 (Dr. Meera Kulkarni) / TeacherPass123!"))

        # Teacher fallback (teacher1)
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

        # 6. Student User & Profile (Ayush Deshmukh)
        ayush_user, _ = User.objects.get_or_create(
            username="stu_cse1_002",
            defaults={
                "email": "student002.cse1@example.com",
                "first_name": "Ayush",
                "last_name": "Deshmukh",
                "role": "student",
                "phone": "9800000002",
            }
        )
        ayush_user.first_name = "Ayush"
        ayush_user.last_name = "Deshmukh"
        ayush_user.set_password("StudentPass123!")
        ayush_user.role = "student"
        ayush_user.is_active = True
        ayush_user.save()

        Student.objects.update_or_create(
            student_id="STU-CSE1-002",
            defaults={
                "user": ayush_user,
                "first_name": "Ayush",
                "last_name": "Deshmukh",
                "email": "student002.cse1@example.com",
                "phone": "9800000002",
                "gender": "male",
                "date_of_birth": date(2006, 3, 13),
                "department": dept,
                "course": course,
                "semester": 1,
                "year": 1,
                "city": "Aurangabad",
                "state": "Maharashtra",
                "status": "active",
                "admission_date": date(2026, 8, 1),
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Student: stu_cse1_002 (Ayush Deshmukh) / StudentPass123!"))

        # Student fallback (student1)
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
