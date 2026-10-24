"""Command to create or reset the demo users and populate complete academic data for Ayush Deshmukh."""
import random
from datetime import date, timedelta, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from academics.models import Department, Course, Subject, Marks
from teachers.models import Teacher
from students.models import Student
from attendance.models import Attendance
from finance.models import FeeStructure, FeeInvoice, FeePayment
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamSchedule
from announcements.models import Announcement
from student_services.models import BookIssued, ClassSchedule, StudyMaterial


class Command(BaseCommand):
    help = "Instantly creates demo users (admin1, cse_fac_002, stu_cse1_002) and seeds complete live data for Ayush"

    def handle(self, *args, **options):
        self.stdout.write("Setting up demo users and complete live database records...")

        with transaction.atomic():
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

            # 3. Semester 1 Subjects (for Ayush)
            sub_c, _ = Subject.objects.update_or_create(
                code="CS101",
                defaults={"name": "Programming in C", "course": course, "semester": 1, "credits": 4}
            )
            sub_math, _ = Subject.objects.update_or_create(
                code="MAT101",
                defaults={"name": "Engineering Mathematics I", "course": course, "semester": 1, "credits": 4}
            )
            sub_phy, _ = Subject.objects.update_or_create(
                code="PHY101",
                defaults={"name": "Engineering Physics", "course": course, "semester": 1, "credits": 4}
            )

            # Higher semester subjects (for teacher)
            sub_dsa, _ = Subject.objects.update_or_create(
                code="CS301",
                defaults={"name": "Data Structures and Algorithms", "course": course, "semester": 3, "credits": 4}
            )
            sub_dbms, _ = Subject.objects.update_or_create(
                code="CS401",
                defaults={"name": "Database Management Systems", "course": course, "semester": 4, "credits": 4}
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
            t_meera.subjects.add(sub_dsa, sub_dbms)
            self.stdout.write(self.style.SUCCESS("[OK] Teacher: cse_fac_002 (Dr. Meera Kulkarni) / TeacherPass123!"))

            # Fallback teacher (teacher1)
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

            # Faculty teachers for Ayush's subjects
            patil_user, _ = User.objects.get_or_create(
                username="cse_fac_003",
                defaults={"email": "rahul.patil@example.com", "first_name": "Rahul", "last_name": "Patil", "role": "teacher", "phone": "9820010003"}
            )
            t_patil, _ = Teacher.objects.get_or_create(employee_id="CSE-FAC-003", defaults={"user": patil_user, "department": dept, "qualification": "Associate Professor", "phone": "9820010003"})
            t_patil.subjects.add(sub_c)

            raut_user, _ = User.objects.get_or_create(
                username="cse_fac_015",
                defaults={"email": "abhishek.raut@example.com", "first_name": "Abhishek", "last_name": "Raut", "role": "teacher", "phone": "9820010015"}
            )
            t_raut, _ = Teacher.objects.get_or_create(employee_id="CSE-FAC-015", defaults={"user": raut_user, "department": dept, "qualification": "Professor | Mathematics", "phone": "9820010015"})
            t_raut.subjects.add(sub_math)

            joshi_user, _ = User.objects.get_or_create(
                username="cse_fac_004",
                defaults={"email": "sneha.joshi@example.com", "first_name": "Sneha", "last_name": "Joshi", "role": "teacher", "phone": "9820010004"}
            )
            t_joshi, _ = Teacher.objects.get_or_create(employee_id="CSE-FAC-004", defaults={"user": joshi_user, "department": dept, "qualification": "Assistant Professor | Physics", "phone": "9820010004"})
            t_joshi.subjects.add(sub_phy)

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

            ayush = Student.objects.filter(user=ayush_user).first()
            if not ayush:
                ayush = Student.objects.filter(student_id="STU-CSE1-002").first()
            if not ayush:
                ayush = Student(student_id="STU-CSE1-002")
            ayush.user = ayush_user
            ayush.student_id = "STU-CSE1-002"
            ayush.first_name = "Ayush"
            ayush.last_name = "Deshmukh"
            ayush.email = "student002.cse1@example.com"
            ayush.phone = "9800000002"
            ayush.gender = "male"
            ayush.date_of_birth = date(2006, 3, 13)
            ayush.department = dept
            ayush.course = course
            ayush.semester = 1
            ayush.year = 1
            ayush.city = "Aurangabad"
            ayush.state = "Maharashtra"
            ayush.status = "active"
            ayush.admission_date = date(2026, 8, 1)
            ayush.save()
            self.stdout.write(self.style.SUCCESS("[OK] Student: stu_cse1_002 (Ayush Deshmukh) / StudentPass123!"))

            # Fallback student (student1)
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

            aarav = Student.objects.filter(user=student_user).first()
            if not aarav:
                aarav = Student.objects.filter(student_id="STU-2026-001").first()
            if not aarav:
                aarav = Student(student_id="STU-2026-001")
            aarav.user = student_user
            aarav.first_name = "Aarav"
            aarav.last_name = "Sharma"
            aarav.email = "aarav.sharma@nit.ac.in"
            aarav.phone = "9820011231"
            aarav.gender = "male"
            aarav.date_of_birth = date(2004, 5, 15)
            aarav.department = dept
            aarav.course = course
            aarav.semester = 4
            aarav.year = 2
            aarav.status = "active"
            aarav.admission_date = date(2022, 8, 1)
            aarav.save()
            self.stdout.write(self.style.SUCCESS("[OK] Student: student1 / TestPass123!"))

            # 7. Fee Structure, Invoices & Payment for Ayush
            self.stdout.write("Configuring Fee structures, invoice (INR 20,000 balance due), and payment...")
            FeeStructure.objects.get_or_create(course=course, fee_type="Tuition Fee", defaults={"period": "Semester", "amount": Decimal("55000.00"), "academic_session": "2026-2027"})
            FeeStructure.objects.get_or_create(course=course, fee_type="Examination & Lab Fee", defaults={"period": "Semester", "amount": Decimal("10000.00"), "academic_session": "2026-2027"})

            inv_no = "INV-2026-STU-CSE1-002"
            inv, _ = FeeInvoice.objects.update_or_create(
                invoice_no=inv_no,
                defaults={
                    "student": ayush,
                    "title": "Academic Year 2026-27 (Semester 1) Tuition & Examination Fee",
                    "due_date": date.today() + timedelta(days=22),
                    "total_amount": Decimal("65000.00"),
                    "paid_amount": Decimal("45000.00"),
                    "status": FeeInvoice.InvoiceStatus.PARTIAL,
                    "academic_session": "2026-2027"
                }
            )

            FeePayment.objects.filter(student=ayush).delete()
            FeePayment.objects.create(
                transaction_id=f"TXN2026{ayush.id:04d}01",
                invoice=inv,
                student=ayush,
                amount=Decimal("45000.00"),
                payment_method="Online Banking / UPI",
                receipt_no=f"REC-2026-{ayush.student_id}",
                notes="Semester 1 Academic fee installment received with receipt issued."
            )
            self.stdout.write(self.style.SUCCESS("[OK] Fees: INR 65,000 invoiced, INR 45,000 paid, INR 20,000 due."))

            # 8. Real Attendance for Ayush (Target ~90.1%)
            self.stdout.write("Generating 30 weekdays classroom attendance for Ayush (90.1% rate)...")
            weekdays = []
            cur_date = date.today() - timedelta(days=1)
            while len(weekdays) < 30:
                if cur_date.weekday() < 5:  # Mon to Fri
                    weekdays.append(cur_date)
                cur_date -= timedelta(days=1)

            # 30 days * 3 subjects = 90 total lecture sessions
            # 81 present + 7 absent + 2 leave = 90 (81/90 = 90.0%)
            ayush_subjects = [(sub_c, patil_user), (sub_math, raut_user), (sub_phy, joshi_user)]
            slot = 0
            for day in weekdays:
                for sub, t_u in ayush_subjects:
                    slot += 1
                    if slot in [14, 28, 42, 56, 70, 77, 84]:
                        st = "absent"
                        rem = "Absent from lecture"
                    elif slot in [35, 63]:
                        st = "leave"
                        rem = "Approved Medical Leave"
                    else:
                        st = "present"
                        rem = "Present in lecture"

                    Attendance.objects.update_or_create(
                        student=ayush,
                        subject=sub,
                        date=day,
                        defaults={
                            "status": st,
                            "teacher": t_u,
                            "remarks": rem,
                        }
                    )
            self.stdout.write(self.style.SUCCESS("[OK] Attendance: 90 classes recorded (90.0% attendance rate)."))

            # 9. Exactly 6 Coursework Assignments for Ayush (Semester 1)
            self.stdout.write("Setting up exactly 6 coursework assignments for Semester 1...")
            # Clean up old assignments for BT-CSE Sem 1 to ensure cleanly 6 assignments
            Assignment.objects.filter(subject__course=course, subject__semester=1).delete()

            ayush_assignments = [
                (sub_c, t_patil, "C Programming Lab 4: Dynamic Arrays & Pointer Arithmetic", "Implement dynamic array resizing and string manipulation without string.h", 5, 100),
                (sub_c, t_patil, "C Programming Lab 5: Structs, Linked Lists & File I/O", "Build an in-memory student record manager using singly linked list and file storage", 12, 100),
                (sub_math, t_raut, "Calculus Problem Set 3: Taylor Series & Partial Differentiation", "Solve problems 1-15 from Chapter 4 of Higher Engineering Mathematics", 8, 50),
                (sub_math, t_raut, "Linear Algebra Assignment 4: Matrix Diagonalization & Eigenvalues", "Determine eigenvalues and diagonalize symmetric matrices with verification steps", 15, 50),
                (sub_phy, t_joshi, "Optics & Laser Lab Manual: Numerical Aperture & Interference", "Complete lab observations and graphs for semiconductor laser experiment", 10, 50),
                (sub_phy, t_joshi, "Quantum Mechanics Set 2: Wave Equations & Tunneling Effect", "Derive 1D time-independent Schrodinger equation for finite potential well", 18, 50),
            ]

            for s, t, title, desc, due_offset, max_m in ayush_assignments:
                Assignment.objects.create(
                    title=title,
                    subject=s,
                    teacher=t,
                    description=desc,
                    due_date=timezone.now() + timedelta(days=due_offset),
                    max_marks=max_m
                )
            self.stdout.write(self.style.SUCCESS("[OK] Assignments: Exactly 6 active Semester 1 assignments created."))

            # 10. Upcoming Examinations & Schedules
            self.stdout.write("Scheduling End-Semester Theory Examinations (starting in 5 days)...")
            exam_term, _ = Exam.objects.update_or_create(
                title="End-Semester Theory Examinations - Winter 2026",
                academic_year="2026-2027",
                defaults={
                    "exam_type": Exam.ExamType.FINAL,
                    "start_date": date.today() + timedelta(days=5),
                    "end_date": date.today() + timedelta(days=26),
                    "is_published": True,
                    "instructions": (
                        "1. Candidates must arrive at the examination hall 15 minutes before scheduled commencement.\n"
                        "2. Electronic gadgets, smart watches, and mobile phones are strictly prohibited.\n"
                        "3. Hall ticket and institutional photo ID card are mandatory for entry."
                    )
                }
            )

            exam_schedule_data = [
                (sub_c, 5, time(10, 0), time(13, 0), "Audi Hall 201"),
                (sub_math, 9, time(10, 0), time(13, 0), "Examination Hall A"),
                (sub_phy, 14, time(10, 0), time(13, 0), "Science Block 102"),
            ]
            for s, d_off, st, et, rm in exam_schedule_data:
                ExamSchedule.objects.update_or_create(
                    exam=exam_term,
                    subject=s,
                    defaults={
                        "date": date.today() + timedelta(days=d_off),
                        "start_time": st,
                        "end_time": et,
                        "room_number": rm,
                        "max_marks": 100,
                        "passing_marks": 40
                    }
                )
            self.stdout.write(self.style.SUCCESS("[OK] Exams: Winter 2026 final exam schedule configured (next in 5 days)."))

            # 11. Library Books Issued to Ayush
            self.stdout.write("Issuing 2 academic reference books to Ayush...")
            BookIssued.objects.update_or_create(
                student=ayush,
                book_title="The C Programming Language (2nd Edition)",
                defaults={
                    "author": "Brian W. Kernighan & Dennis M. Ritchie",
                    "accession_no": "LIB-CSE-2026-084",
                    "issue_date": date.today() - timedelta(days=10),
                    "due_date": date.today() + timedelta(days=20),
                    "status": "issued",
                    "fine_amount": Decimal("0.00")
                }
            )
            BookIssued.objects.update_or_create(
                student=ayush,
                book_title="Higher Engineering Mathematics (44th Edition)",
                defaults={
                    "author": "Dr. B.S. Grewal",
                    "accession_no": "LIB-MATH-2026-112",
                    "issue_date": date.today() - timedelta(days=5),
                    "due_date": date.today() + timedelta(days=25),
                    "status": "issued",
                    "fine_amount": Decimal("0.00")
                }
            )
            self.stdout.write(self.style.SUCCESS("[OK] Library: 2 books actively issued."))

            # 12. Mid-Semester Academic Marks (CGPA ~7.95)
            self.stdout.write("Recording mid-semester performance marks for Ayush...")
            marks_data = [
                (sub_c, 26, 53, 79, "B+"),
                (sub_math, 28, 52, 80, "A"),
                (sub_phy, 27, 51, 78, "B+"),
            ]
            for s, in_m, ex_m, tot, grd in marks_data:
                Marks.objects.update_or_create(
                    student=ayush,
                    subject=s,
                    semester=1,
                    academic_year="2026-2027",
                    defaults={
                        "internal_marks": in_m,
                        "external_marks": ex_m,
                        "practical_marks": 0,
                        "total_marks": tot,
                        "grade": grd,
                        "created_by": patil_user
                    }
                )
            self.stdout.write(self.style.SUCCESS("[OK] Marks: Recorded mid-semester performance (avg 79.0, CGPA 7.95)."))

            # 13. Institutional Announcements
            announcements = [
                ("Winter 2026 End-Semester Examination Timetable Published", "The official theory and practical timetable for Winter 2026 examinations has been published. Hall tickets will be downloadable next week.", "exam", True),
                ("National Level Hackathon & Project Expo Registration Open", "Registrations are now open for the annual CSE Tech Expo. Submit project proposals via the department portal by Nov 10.", "event", True),
                ("Digital IEEE and Springer Library Access Extended", "Students can now access IEEE Xplore and Springer digital libraries from home using institutional LDAP credentials.", "academic", False),
                ("Academic Fee Semester Installment Notification", "Second installment of academic session fees is due by mid-November. Online receipts will reflect in the student finance portal immediately upon verification.", "general", False),
            ]
            for title, cnt, cat, pin in announcements:
                Announcement.objects.update_or_create(
                    title=title,
                    defaults={
                        "content": cnt,
                        "category": cat,
                        "is_pinned": pin,
                        "target_role": "all",
                        "created_by": admin_user
                    }
                )
            self.stdout.write(self.style.SUCCESS("[OK] Announcements: 4 official campus notices posted."))

            # 14. Weekly Class Schedule for Semester 1
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            schedule_plan = [
                (1, time(9, 30), time(10, 30), sub_c, t_patil, "Lab 101"),
                (2, time(10, 30), time(11, 30), sub_math, t_raut, "Classroom 204"),
                (3, time(11, 45), time(12, 45), sub_phy, t_joshi, "Physics Lab 2"),
            ]
            for d in days:
                for period_no, st, et, s, t, rm in schedule_plan:
                    ClassSchedule.objects.update_or_create(
                        day_of_week=d,
                        period_number=period_no,
                        subject=s,
                        defaults={
                            "start_time": st,
                            "end_time": et,
                            "teacher": t,
                            "room": rm
                        }
                    )
            self.stdout.write(self.style.SUCCESS("[OK] Timetable: 15 weekly class lecture sessions scheduled."))

        self.stdout.write(self.style.SUCCESS("\nDone! All demo users and Ayush's complete dynamic data are ready!"))
