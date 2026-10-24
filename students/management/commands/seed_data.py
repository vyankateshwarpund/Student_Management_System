"""Management command to seed realistic institution-scale mock data."""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from accounts.models import User
from academics.models import Department, Course, Subject, Marks
from students.models import Student
from teachers.models import Teacher
from attendance.models import Attendance


class Command(BaseCommand):
    help = "Seeds database with realistic institution scale mock data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=80,
            help='Number of students to generate (default: 80)',
        )

    def handle(self, *args, **options):
        student_target = options['students']
        self.stdout.write(self.style.NOTICE(f"Seeding realistic institution data with target {student_target} students..."))

        with transaction.atomic():
            # 1. Departments
            dept_specs = [
                ("Computer Science and Engineering", "CSE", "Focuses on computer architecture, software systems, and artificial intelligence."),
                ("Electronics and Communication", "ECE", "Focuses on telecommunications, embedded systems, microprocessors, and IoT."),
                ("Mechanical Engineering", "ME", "Focuses on thermodynamics, fluid mechanics, CAD design, and robotics."),
                ("Civil Engineering", "CE", "Focuses on structural engineering, environmental infrastructure, and geotechnical systems."),
                ("Management Studies", "MBA", "Focuses on organizational leadership, financial management, and business strategy."),
            ]

            departments = {}
            for name, code, desc in dept_specs:
                dept, _ = Department.objects.get_or_create(code=code, defaults={'name': name, 'description': desc})
                departments[code] = dept
            self.stdout.write(self.style.SUCCESS(f"Verified {len(departments)} academic departments."))

            # 2. Courses
            course_specs = [
                ("B.Tech Computer Science & Engineering", "BT-CSE", departments["CSE"], 4),
                ("B.Tech AI & Data Science", "BT-AIDS", departments["CSE"], 4),
                ("B.Tech Electronics & Communication", "BT-ECE", departments["ECE"], 4),
                ("B.Tech Mechanical Engineering", "BT-ME", departments["ME"], 4),
                ("B.Tech Civil Engineering", "BT-CE", departments["CE"], 4),
                ("Master of Business Administration", "MBA-GEN", departments["MBA"], 2),
            ]

            courses = {}
            for name, code, dept, dur in course_specs:
                course, _ = Course.objects.get_or_create(code=code, defaults={
                    'name': name,
                    'department': dept,
                    'duration': dur,
                    'status': 'active'
                })
                courses[code] = course
            self.stdout.write(self.style.SUCCESS(f"Verified {len(courses)} degree programs."))

            # 3. Subjects Catalog (across Semesters 1 to 8)
            subject_specs = [
                # CSE Sem 1 & 2
                ("Engineering Mathematics I", "MAT101", "BT-CSE", 1, 4),
                ("Engineering Physics", "PHY101", "BT-CSE", 1, 3),
                ("Programming in C", "CS101", "BT-CSE", 1, 4),
                ("Engineering Mathematics II", "MAT102", "BT-CSE", 2, 4),
                ("Object Oriented Programming with Java", "CS102", "BT-CSE", 2, 4),
                # CSE Sem 3 & 4
                ("Data Structures & Algorithms", "CS301", "BT-CSE", 3, 4),
                ("Digital Electronics & Logic Design", "CS302", "BT-CSE", 3, 3),
                ("Discrete Mathematics", "CS303", "BT-CSE", 3, 3),
                ("Database Management Systems", "CS401", "BT-CSE", 4, 4),
                ("Operating Systems Architecture", "CS402", "BT-CSE", 4, 4),
                ("Computer Organization", "CS403", "BT-CSE", 4, 3),
                # CSE Sem 5 & 6
                ("Computer Networks", "CS501", "BT-CSE", 5, 4),
                ("Software Engineering Principles", "CS502", "BT-CSE", 5, 3),
                ("Theory of Computation", "CS503", "BT-CSE", 5, 3),
                ("Web Technologies & Full Stack", "CS601", "BT-CSE", 6, 4),
                ("Machine Learning Foundations", "CS602", "BT-CSE", 6, 4),
                ("Compiler Design", "CS603", "BT-CSE", 6, 3),
                # CSE Sem 7 & 8
                ("Cloud Computing & DevOps", "CS701", "BT-CSE", 7, 4),
                ("Cybersecurity & Cryptography", "CS702", "BT-CSE", 7, 3),
                ("Distributed Systems", "CS703", "BT-CSE", 7, 3),
                ("Major Capstone Project", "CS801", "BT-CSE", 8, 8),

                # ECE Subjects
                ("Network Analysis & Synthesis", "EC301", "BT-ECE", 3, 4),
                ("Signals and Systems", "EC302", "BT-ECE", 3, 4),
                ("Analog Circuits & Devices", "EC401", "BT-ECE", 4, 4),
                ("Electromagnetic Field Theory", "EC402", "BT-ECE", 4, 3),
                ("Digital Signal Processing", "EC501", "BT-ECE", 5, 4),
                ("Microprocessors & Microcontrollers", "EC502", "BT-ECE", 5, 4),

                # ME Subjects
                ("Thermodynamics & Heat Transfer", "ME301", "BT-ME", 3, 4),
                ("Fluid Mechanics & Machinery", "ME302", "BT-ME", 3, 4),
                ("Manufacturing Technology", "ME401", "BT-ME", 4, 3),
                ("Machine Design & CAD", "ME501", "BT-ME", 5, 4),

                # CE Subjects
                ("Fluid Mechanics & Hydraulics", "CE301", "BT-CE", 3, 4),
                ("Structural Analysis & Design", "CE401", "BT-CE", 4, 4),
                ("Geotechnical Engineering", "CE501", "BT-CE", 5, 3),

                # MBA Subjects
                ("Financial Accounting & Analysis", "MB101", "MBA-GEN", 1, 3),
                ("Marketing Management", "MB102", "MBA-GEN", 1, 3),
                ("Organizational Behavior", "MB201", "MBA-GEN", 2, 3),
                ("Corporate Financial Strategy", "MB301", "MBA-GEN", 3, 3),
            ]

            subjects = []
            for s_name, s_code, c_code, sem, credits in subject_specs:
                course = courses.get(c_code)
                if course:
                    subj, _ = Subject.objects.get_or_create(code=s_code, defaults={
                        'name': s_name,
                        'course': course,
                        'semester': sem,
                        'credits': credits
                    })
                    subjects.append(subj)
            self.stdout.write(self.style.SUCCESS(f"Verified {len(subjects)} subjects."))

            # 4. Faculty Members (Teachers)
            # Core Admin & Demo Accounts
            admin_user, _ = User.objects.get_or_create(
                username="admin1",
                defaults={
                    "email": "admin@test.com",
                    "first_name": "System",
                    "last_name": "Administrator",
                    "role": "admin",
                    "is_staff": True,
                    "is_superuser": True,
                }
            )
            admin_user.set_password("TestPass123!")
            admin_user.role = "admin"
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

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
            teacher_user.save()

            cse_dept = departments["CSE"]
            t_prof1, _ = Teacher.objects.get_or_create(
                user=teacher_user,
                defaults={
                    "employee_id": "TCH001",
                    "department": cse_dept,
                    "qualification": "M.Tech in Computer Science",
                    "phone": "9820011230",
                }
            )

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
                    "department": cse_dept,
                    "course": courses["BT-CSE"],
                    "semester": 4,
                    "year": 2026,
                    "status": "active",
                    "address": "Flat 204, Green Valley Heights",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001",
                    "admission_date": date(2022, 8, 1),
                }
            )

            teacher_specs = [
                ("dr_sharma", "dr_sharma@school.edu", "Ramesh", "Sharma", "CSE", "FAC101", "Ph.D. in Computer Science (IIT Bombay)", "9820011221"),
                ("dr_patel", "dr_patel@school.edu", "Sunita", "Patel", "CSE", "FAC102", "Ph.D. in AI & Robotics (IISc)", "9820011222"),
                ("prof_verma", "prof_verma@school.edu", "Arun", "Verma", "ECE", "FAC103", "M.Tech in VLSI Systems", "9820011223"),
                ("prof_kulkarni", "prof_kulkarni@school.edu", "Neha", "Kulkarni", "ME", "FAC104", "M.Tech in Thermal Engineering", "9820011224"),
                ("prof_iyer", "prof_iyer@school.edu", "Venkatesh", "Iyer", "CE", "FAC105", "Ph.D. in Structural Dynamics", "9820011225"),
                ("dr_deshmukh", "dr_deshmukh@school.edu", "Pooja", "Deshmukh", "MBA", "FAC106", "Ph.D. in Financial Economics", "9820011226"),
            ]

            teachers = list(Teacher.objects.all())
            for uname, email, fname, lname, dcode, empid, qual, ph in teacher_specs:
                user, created = User.objects.get_or_create(username=uname, defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'teacher',
                    'phone': ph
                })
                if created:
                    user.set_password("TeacherPass123!")
                    user.save()

                dept = departments[dcode]
                t_prof = Teacher.objects.filter(user=user).first()
                if not t_prof:
                    # Check if employee_id already taken
                    if Teacher.objects.filter(employee_id=empid).exists():
                        empid = f"{empid}_{random.randint(100, 999)}"
                    t_prof = Teacher.objects.create(
                        user=user,
                        employee_id=empid,
                        department=dept,
                        qualification=qual,
                        phone=ph
                    )

                # Assign subjects matching department
                dept_subjects = [s for s in subjects if s.course.department == dept]
                if dept_subjects:
                    t_prof.subjects.set(dept_subjects[:3])
                if t_prof not in teachers:
                    teachers.append(t_prof)

            self.stdout.write(self.style.SUCCESS(f"Verified {len(teachers)} faculty profiles."))

            # 5. Realistic Student Pool Generation
            first_names_male = ["Aarav", "Rohan", "Vikram", "Aditya", "Amit", "Rahul", "Karan", "Sanjay", "Arjun", "Deepak", "Nikhil", "Pranav", "Varun", "Kunal", "Harsh", "Sameer", "Gaurav", "Manish"]
            first_names_female = ["Priya", "Ananya", "Neha", "Sneha", "Pooja", "Meera", "Divya", "Rhea", "Isha", "Shreya", "Kavya", "Tanvi", "Aditi", "Pallavi", "Swati", "Nandini", "Simran", "Alka"]
            last_names = ["Sharma", "Verma", "Patil", "Rao", "Kumar", "Singh", "Gupta", "Joshi", "Nair", "Kulkarni", "Mehta", "Reddy", "Choudhury", "Bose", "Menon", "Deshmukh", "Agarwal", "Bhat"]
            cities = [
                ("Mumbai", "Maharashtra", "400001"),
                ("Pune", "Maharashtra", "411001"),
                ("Bengaluru", "Karnataka", "560001"),
                ("Hyderabad", "Telangana", "500001"),
                ("New Delhi", "Delhi", "110001"),
                ("Ahmedabad", "Gujarat", "380001"),
                ("Chennai", "Tamil Nadu", "600001"),
                ("Kolkata", "West Bengal", "700001"),
                ("Jaipur", "Rajasthan", "302001"),
                ("Indore", "Madhya Pradesh", "452001"),
            ]

            created_students_count = 0
            student_records = []
            registered_students = list(Student.objects.all())

            # Generate students until we reach desired total count
            current_total = len(registered_students)
            needed = max(0, student_target - current_total)

            course_list = list(courses.values())
            for i in range(needed):
                idx = current_total + i + 1
                is_female = random.choice([True, False])
                fname = random.choice(first_names_female) if is_female else random.choice(first_names_male)
                lname = random.choice(last_names)
                gender = 'female' if is_female else 'male'

                course = random.choice(course_list)
                dept = course.department
                sem = random.randint(1, course.duration * 2)

                # Format student ID: e.g. 2024CSE021
                batch_year = 2026 - (sem // 2)
                stu_id = f"{batch_year}{dept.code}{idx:03d}"

                uname = f"stu_{stu_id.lower()}"
                email = f"{fname.lower()}.{lname.lower()}{idx}@student.edu"
                city_info = random.choice(cities)

                # User account
                user, _ = User.objects.get_or_create(username=uname, defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'student',
                    'phone': f"98{random.randint(10000000, 99999999)}"
                })
                user.set_password("StudentPass123!")
                user.save()

                # Student Profile
                student, s_created = Student.objects.get_or_create(student_id=stu_id, defaults={
                    'user': user,
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'phone': user.phone,
                    'gender': gender,
                    'date_of_birth': date(2003, random.randint(1, 12), random.randint(1, 28)),
                    'department': dept,
                    'course': course,
                    'semester': sem,
                    'year': 2026,
                    'status': 'active',
                    'address': f"Flat {random.randint(101, 804)}, Green Valley Heights",
                    'city': city_info[0],
                    'state': city_info[1],
                    'pincode': city_info[2],
                    'admission_date': date(batch_year, 8, 1)
                })

                if s_created:
                    student_records.append(student)
                    created_students_count += 1

            self.stdout.write(self.style.SUCCESS(f"Generated {created_students_count} new student profiles (Total: {Student.objects.count()})."))

            # 6. Historical Attendance Generation (Past 20 weekdays)
            self.stdout.write("Generating realistic classroom attendance logs for active semesters...")
            all_students = list(Student.objects.select_related('course', 'department').all())
            primary_teacher_user = teachers[0].user if teachers else None

            # Collect dates for the last 20 weekdays
            dates = []
            curr_d = date.today() - timedelta(days=1)
            while len(dates) < 20:
                if curr_d.weekday() < 5:  # Mon to Fri
                    dates.append(curr_d)
                curr_d -= timedelta(days=1)

            att_created = 0
            for student in all_students:
                # Find subjects matching student's course and semester
                enrolled_subs = [s for s in subjects if s.course == student.course and s.semester == student.semester]
                if not enrolled_subs:
                    # fallback to any subject for this course
                    enrolled_subs = [s for s in subjects if s.course == student.course][:2]

                for subj in enrolled_subs:
                    for d in dates:
                        # 88% chance present, 8% absent, 4% leave
                        roll = random.random()
                        status = 'present' if roll < 0.88 else ('absent' if roll < 0.96 else 'leave')

                        _, c = Attendance.objects.get_or_create(
                            student=student,
                            subject=subj,
                            date=d,
                            defaults={
                                'status': status,
                                'teacher': primary_teacher_user,
                                'remarks': 'Regular Session' if status == 'present' else ('Absent' if status == 'absent' else 'Medical leave')
                            }
                        )
                        if c:
                            att_created += 1

            self.stdout.write(self.style.SUCCESS(f"Logged {att_created} attendance records across past 20 days."))

            # 7. Examination Marks & Grades Generation
            self.stdout.write("Generating examination marks and grades...")
            marks_created = 0
            for student in all_students:
                enrolled_subs = [s for s in subjects if s.course == student.course and s.semester == student.semester]
                for subj in enrolled_subs:
                    # Realistic grade distribution (mostly B+ to A+)
                    internal = round(random.uniform(18.0, 24.5), 1)
                    external = round(random.uniform(42.0, 64.0), 1)
                    practical = round(random.uniform(7.0, 10.0), 1)

                    _, m_created = Marks.objects.get_or_create(
                        student=student,
                        subject=subj,
                        semester=student.semester,
                        academic_year="2025-2026",
                        defaults={
                            'internal_marks': internal,
                            'external_marks': external,
                            'practical_marks': practical,
                            'created_by': primary_teacher_user
                        }
                    )
                    if m_created:
                        marks_created += 1

            self.stdout.write(self.style.SUCCESS(f"Recorded {marks_created} examination marksheets."))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Institution dataset seeded with authentic academic scale!"))
