"""Command to populate real database records for all tables across all students."""
import random
from datetime import date, timedelta, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from academics.models import Department, Course, Subject, Marks
from students.models import Student
from teachers.models import Teacher
from attendance.models import Attendance
from finance.models import FeeStructure, FeeInvoice, FeePayment
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamSchedule
from announcements.models import Announcement
from student_services.models import BookIssued, ClassSchedule, StudyMaterial, Lesson


class Command(BaseCommand):
    help = "Populate authentic dynamic database records for attendance, fees, assignments, exams, library, and timetable"

    def handle(self, *args, **options):
        self.stdout.write("Starting complete database population for all academic modules...")

        with transaction.atomic():
            # 1. Academic Department & Course
            dept, _ = Department.objects.get_or_create(
                code="CSE",
                defaults={
                    "name": "Computer Science and Engineering",
                    "description": "Department of Computer Science and Engineering"
                }
            )

            course, _ = Course.objects.get_or_create(
                code="BT-CSE",
                defaults={
                    "name": "B.Tech Computer Science & Engineering",
                    "department": dept,
                    "duration": 4,
                    "status": "active"
                }
            )

            # Ensure essential faculty members exist
            primary_teacher = Teacher.objects.filter(department=dept).first()
            teacher_user = primary_teacher.user if primary_teacher else User.objects.filter(role="teacher").first()

            all_students = list(Student.objects.select_related('course', 'department').all())
            self.stdout.write(f"Targeting {len(all_students)} students across all batches...")

            # 2. Fee Structures
            fee_specs = [
                ("Tuition Fee", "Semester", Decimal("55000.00")),
                ("Examination & Assessment Fee", "Semester", Decimal("5000.00")),
                ("Library & Digital Lab Fee", "Semester", Decimal("5000.00")),
            ]
            for f_type, period, amt in fee_specs:
                FeeStructure.objects.get_or_create(
                    course=course,
                    fee_type=f_type,
                    defaults={"period": period, "amount": amt, "academic_session": "2026-2027"}
                )

            # 3. Create Fee Invoices & Payment Receipts for all students
            self.stdout.write("Generating authentic Fee Invoices and Payment records...")
            invoice_count = 0
            for student in all_students:
                inv_no = f"INV-2026-{student.student_id}"
                sem = student.semester or 1
                total_amt = Decimal("65000.00")

                # If student is Ayush Deshmukh, create a partial invoice (Due: ₹20,000)
                if student.student_id == "STU-CSE1-002" or student.first_name == "Ayush":
                    paid_amt = Decimal("45000.00")
                    inv_status = FeeInvoice.InvoiceStatus.PARTIAL
                else:
                    # Randomize between full paid and partial
                    if random.random() < 0.65:
                        paid_amt = total_amt
                        inv_status = FeeInvoice.InvoiceStatus.PAID
                    else:
                        paid_amt = Decimal("45000.00")
                        inv_status = FeeInvoice.InvoiceStatus.PARTIAL

                inv, created = FeeInvoice.objects.update_or_create(
                    invoice_no=inv_no,
                    defaults={
                        "student": student,
                        "title": f"Academic Year 2026-27 (Semester {sem}) Tuition & Examination Fee",
                        "due_date": date.today() + timedelta(days=22),
                        "total_amount": total_amt,
                        "paid_amount": paid_amt,
                        "status": inv_status,
                        "academic_session": "2026-2027"
                    }
                )

                # Payment receipt
                if paid_amt > Decimal("0.00"):
                    txn_id = f"TXN2026{student.id:04d}01"
                    rec_no = f"REC-2026-{student.student_id}"
                    FeePayment.objects.update_or_create(
                        transaction_id=txn_id,
                        defaults={
                            "invoice": inv,
                            "student": student,
                            "amount": paid_amt,
                            "payment_method": "Online Banking / UPI",
                            "receipt_no": rec_no,
                            "notes": f"Semester {sem} Academic installment received."
                        }
                    )
                invoice_count += 1

            self.stdout.write(self.style.SUCCESS(f"Logged {invoice_count} student fee invoices with verified ledger records."))

            # 4. Generate Realistic Attendance for past 30 weekdays
            self.stdout.write("Generating classroom attendance records across subjects...")
            weekdays = []
            cur_date = date.today() - timedelta(days=1)
            while len(weekdays) < 30:
                if cur_date.weekday() < 5:  # Mon to Fri
                    weekdays.append(cur_date)
                cur_date -= timedelta(days=1)

            att_records = 0
            for student in all_students:
                subs = list(Subject.objects.filter(course=student.course, semester=student.semester))
                if not subs:
                    subs = list(Subject.objects.filter(course=student.course)[:3])

                is_ayush = (student.student_id == "STU-CSE1-002" or student.first_name == "Ayush")
                # Target attendance ~90.1% for Ayush, 85-94% for others
                target_present_rate = 0.901 if is_ayush else random.uniform(0.85, 0.94)

                for sub in subs:
                    # Pick teacher
                    sub_teacher = sub.teachers.first() or primary_teacher
                    teacher_u = sub_teacher.user if sub_teacher else teacher_user

                    for day in weekdays:
                        # Determine status
                        roll = random.random()
                        if roll < target_present_rate:
                            status = "present"
                            remark = "Present in lecture"
                        elif roll < (target_present_rate + 0.06):
                            status = "absent"
                            remark = "Absent"
                        else:
                            status = "leave"
                            remark = "Approved Medical/Institutional Leave"

                        _, c = Attendance.objects.update_or_create(
                            student=student,
                            subject=sub,
                            date=day,
                            defaults={
                                "status": status,
                                "teacher": teacher_u,
                                "remarks": remark,
                            }
                        )
                        if c:
                            att_records += 1

            self.stdout.write(self.style.SUCCESS(f"Populated {att_records} attendance records."))

            # 5. Coursework Assignments & Submissions
            self.stdout.write("Generating coursework assignments and submissions...")
            assignment_specs = [
                # Semester 1 (6 assignments for Ayush & Batch)
                ("CS101", "C Programming Lab 4: Dynamic Arrays & Pointer Arithmetic", "Implement dynamic array resizing and string manipulation without string.h", 5, 100),
                ("CS101", "C Programming Lab 5: Structs, Linked Lists & File I/O", "Build an in-memory student record manager using singly linked list and file storage", 12, 100),
                ("MAT101", "Calculus Problem Set 3: Taylor Series & Partial Differentiation", "Solve problems 1-15 from Chapter 4 of Higher Engineering Mathematics", 8, 50),
                ("MAT101", "Linear Algebra Assignment 4: Matrix Diagonalization & Eigenvalues", "Determine eigenvalues and diagonalize symmetric matrices with verification steps", 15, 50),
                ("PHY101", "Optics & Laser Lab Manual: Numerical Aperture & Interference", "Complete lab observations and graphs for semiconductor laser experiment", 10, 50),
                ("PHY101", "Quantum Mechanics Set 2: Wave Equations & Tunneling Effect", "Derive 1D time-independent Schrodinger equation for finite potential well", 18, 50),
                # Semester 3
                ("CS301", "DSA Problem Set: Binary Search Trees & AVL Rotations", "Implement AVL tree insertion and verify height balancing factor", 6, 100),
                ("CS302", "Digital Logic Design: 4-Bit Synchronous Up/Down Counter", "Design and simulate using Logisim circuit simulator", -5, 50),
                # Semester 4
                ("CS401", "DBMS Mini Project: Relational Schema & BCNF Normalization", "Design normalized schema for college management database", 7, 100),
                ("CS402", "Operating Systems Lab: CPU Scheduling Algorithms Simulation", "Implement FCFS, SJF, and Round Robin in C/Python", 11, 100),
                # Semester 5
                ("CS501", "Networks Socket Programming: Client-Server Chat Architecture", "Implement TCP multi-threaded socket chat in Python", 6, 100),
                ("CS502", "Software Engineering SRS Document: Microservices Architecture", "Prepare complete IEEE 830 compliant SRS", 12, 100),
                # Semester 6
                ("CS601", "Web Tech Full Stack: REST API with Django & Bootstrap", "Build authenticated REST API with token verification", 9, 100),
                ("CS602", "Machine Learning: Classification Models on Real Dataset", "Train and evaluate Logistic Regression, SVM, and Random Forest", -4, 100),
                # Semester 7
                ("CS701", "Cloud DevOps: Docker Containerization & CI/CD Pipeline", "Create Dockerfile, docker-compose, and GitHub Actions workflow", 8, 100),
                ("CS702", "Cybersecurity Lab: RSA Encryption & Digital Signatures", "Implement 2048-bit RSA key generation and signing in Python", 14, 100),
            ]

            created_assignments = {}
            for s_code, title, desc, days_offset, max_m in assignment_specs:
                sub = Subject.objects.filter(code=s_code).first()
                if sub:
                    sub_t = sub.teachers.first() or primary_teacher
                    due_dt = timezone.now() + timedelta(days=days_offset)
                    assign, _ = Assignment.objects.update_or_create(
                        title=title,
                        subject=sub,
                        defaults={
                            "description": desc,
                            "teacher": sub_t,
                            "due_date": due_dt,
                            "max_marks": max_m
                        }
                    )
                    created_assignments[s_code] = assign

            # Add submissions for past assignments for Ayush and other students
            for student in all_students:
                for s_code, assign in created_assignments.items():
                    if assign.subject.course == student.course and assign.subject.semester == student.semester:
                        # If assignment due date is past, create submission
                        if assign.due_date < timezone.now():
                            AssignmentSubmission.objects.update_or_create(
                                assignment=assign,
                                student=student,
                                defaults={
                                    "status": AssignmentSubmission.SubmissionStatus.GRADED,
                                    "marks_obtained": float(random.randint(42, int(assign.max_marks))),
                                    "feedback": "Well written solution. Clean code and accurate derivations.",
                                    "submission_text": "Completed and verified on lab machines."
                                }
                            )

            self.stdout.write(self.style.SUCCESS(f"Configured assignments with live pending dues and graded submissions."))

            # 6. Examinations & Exam Schedules (Upcoming Winter 2026)
            self.stdout.write("Scheduling authentic institutional examinations...")
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

            # Schedule dates for subjects across Sem 1 to 8
            schedule_offsets = {
                # Sem 1
                "CS101": (5, time(9, 30), time(12, 30), "Auditorium Hall A"),
                "MAT101": (8, time(9, 30), time(12, 30), "Hall 201 (Block B)"),
                "PHY101": (12, time(14, 0), time(17, 0), "Hall 104 (Block A)"),
                # Sem 2
                "CS102": (6, time(9, 30), time(12, 30), "Hall 202 (Block B)"),
                "MAT102": (9, time(9, 30), time(12, 30), "Hall 203 (Block B)"),
                # Sem 3
                "CS301": (5, time(9, 30), time(12, 30), "Hall 301 (Block C)"),
                "CS302": (8, time(14, 0), time(17, 0), "Hall 302 (Block C)"),
                "CS303": (12, time(9, 30), time(12, 30), "Hall 301 (Block C)"),
                # Sem 4
                "CS401": (6, time(9, 30), time(12, 30), "Hall 401 (Block D)"),
                "CS402": (10, time(9, 30), time(12, 30), "Hall 402 (Block D)"),
                "CS403": (14, time(14, 0), time(17, 0), "Hall 401 (Block D)"),
                # Sem 5
                "CS501": (5, time(9, 30), time(12, 30), "Exam Centre Main"),
                "CS502": (9, time(9, 30), time(12, 30), "Exam Centre Main"),
                "CS503": (13, time(14, 0), time(17, 0), "Exam Centre Main"),
                # Sem 6
                "CS601": (6, time(9, 30), time(12, 30), "Lab Complex East"),
                "CS602": (10, time(9, 30), time(12, 30), "Lab Complex East"),
                "CS603": (14, time(14, 0), time(17, 0), "Lab Complex East"),
                # Sem 7
                "CS701": (5, time(9, 30), time(12, 30), "Seminar Hall 1"),
                "CS702": (9, time(14, 0), time(17, 0), "Seminar Hall 1"),
                "CS703": (13, time(9, 30), time(12, 30), "Seminar Hall 1"),
                # Sem 8
                "CS801": (7, time(10, 0), time(16, 0), "Board Room 3"),
            }

            sched_count = 0
            for code, (day_off, st, et, room) in schedule_offsets.items():
                subj = Subject.objects.filter(code=code).first()
                if subj:
                    ExamSchedule.objects.update_or_create(
                        exam=exam_term,
                        subject=subj,
                        defaults={
                            "date": date.today() + timedelta(days=day_off),
                            "start_time": st,
                            "end_time": et,
                            "room_number": room,
                            "max_marks": 100,
                        }
                    )
                    sched_count += 1

            self.stdout.write(self.style.SUCCESS(f"Published {sched_count} live exam schedules for upcoming Winter term."))

            # 7. Library Books Issued
            self.stdout.write("Issuing curriculum library books to students...")
            library_books = [
                ("Programming in ANSI C (8th Edition)", "E. Balagurusamy", "LIB-CS-101"),
                ("Higher Engineering Mathematics", "Dr. B.S. Grewal", "LIB-MAT-042"),
                ("Concepts of Modern Physics", "Arthur Beiser", "LIB-PHY-098"),
                ("Data Structures Using C and C++", "Tanenbaum & Langsam", "LIB-CS-301"),
                ("Database System Concepts (7th Edition)", "Silberschatz, Korth & Sudarshan", "LIB-CS-401"),
                ("Operating System Concepts", "Abraham Silberschatz & Peter Galvin", "LIB-CS-402"),
            ]

            for student in all_students:
                if not student.books_issued.exists():
                    # Pick 2 books
                    sample_b = random.sample(library_books, 2)
                    for title, author, acc in sample_b:
                        BookIssued.objects.create(
                            student=student,
                            book_title=title,
                            author=author,
                            accession_no=f"{acc}-{student.id:03d}",
                            issue_date=date.today() - timedelta(days=random.randint(10, 20)),
                            due_date=date.today() + timedelta(days=random.randint(10, 25)),
                            status=BookIssued.BookStatus.ISSUED,
                            fine_amount=Decimal("0.00")
                        )

            # 8. College Announcements & Noticeboard
            announcement_specs = [
                ("Winter 2026 End-Semester Examination Timetable Announced",
                 "The official examination schedule for all undergraduate degree programs (Semesters 1 through 8) has been published. Hall tickets will be available for download 7 days prior to commencement.",
                 Announcement.Category.EXAM, True),
                ("Smart India Hackathon 2026 — Institutional Round Registrations Open",
                 "All B.Tech students are invited to register in teams of 6 for the internal hackathon. Shortlisted teams will represent the institute at the National Finals.",
                 Announcement.Category.EVENT, True),
                ("Central Digital Library & IEEE Xplore Remote Access Guidelines",
                 "Students and faculty can access IEEE Xplore, ScienceDirect, and ACM Digital Library off-campus using their institutional credentials.",
                 Announcement.Category.ACADEMIC, False),
                ("Semester Fee Payment Deadline Notice",
                 "Students are advised to clear pending academic dues by 15 November 2026 to ensure uninterrupted access to exam admit cards and portal services.",
                 Announcement.Category.URGENT, False),
            ]
            for title, content, cat, pinned in announcement_specs:
                Announcement.objects.get_or_create(
                    title=title,
                    defaults={
                        "content": content,
                        "category": cat,
                        "is_pinned": pinned,
                        "target_role": Announcement.TargetRole.ALL,
                        "created_by": teacher_user
                    }
                )

            # 9. Class Timetable Schedule
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            cse_subs = list(Subject.objects.filter(course=course))
            for day in days:
                for p_num in range(1, 5):
                    sub_idx = (days.index(day) + p_num) % len(cse_subs)
                    sub = cse_subs[sub_idx]
                    t = sub.teachers.first() or primary_teacher
                    ClassSchedule.objects.get_or_create(
                        day_of_week=day,
                        period_number=p_num,
                        subject=sub,
                        defaults={
                            "start_time": time(9 + p_num, 0),
                            "end_time": time(9 + p_num, 50),
                            "teacher": t,
                            "room": f"Room {200 + p_num}"
                        }
                    )

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Entire system populated with realistic dynamic database records!"))
