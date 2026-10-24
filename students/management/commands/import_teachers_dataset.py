"""Management command to import and configure the 20 CSE faculty members."""
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from academics.models import Department, Subject
from teachers.models import Teacher

FACULTY_DATA = [
    {
        "staff_id": "CSE-FAC-001",
        "name": "Dr. Anil Deshmukh",
        "designation": "Professor & HOD",
        "specialization": "Computer Science and Engineering",
        "responsibility": "Department administration; curriculum oversight",
        "assigned_year_role": "HOD / All Years",
        "email": "hod.cse@example.com",
        "phone": "9820010001",
        "subject_codes": ["ALL_CSE"],
    },
    {
        "staff_id": "CSE-FAC-002",
        "name": "Dr. Meera Kulkarni",
        "designation": "Professor",
        "specialization": "Data Structures and Algorithms",
        "responsibility": "DSA; Advanced Algorithms",
        "assigned_year_role": "Subject Teacher (Second Year, Third Year)",
        "email": "meera.kulkarni@example.com",
        "phone": "9820010002",
        "subject_codes": ["CS301", "CS503"],
    },
    {
        "staff_id": "CSE-FAC-003",
        "name": "Prof. Rahul Patil",
        "designation": "Associate Professor",
        "specialization": "Programming in C and C++",
        "responsibility": "Programming Fundamentals; OOP",
        "assigned_year_role": "Subject Teacher (First Year, Second Year)",
        "email": "rahul.patil@example.com",
        "phone": "9820010003",
        "subject_codes": ["CS101", "CS102"],
    },
    {
        "staff_id": "CSE-FAC-004",
        "name": "Prof. Sneha Joshi",
        "designation": "Assistant Professor",
        "specialization": "Python Programming",
        "responsibility": "Python; Full-Stack Development",
        "assigned_year_role": "Subject Teacher (First Year, Third Year)",
        "email": "sneha.joshi@example.com",
        "phone": "9820010004",
        "subject_codes": ["CS601", "CS101"],
    },
    {
        "staff_id": "CSE-FAC-005",
        "name": "Dr. Nikhil Shinde",
        "designation": "Associate Professor",
        "specialization": "Database Management Systems",
        "responsibility": "DBMS; SQL; Data Modeling",
        "assigned_year_role": "Subject Teacher (Second Year, Third Year)",
        "email": "nikhil.shinde@example.com",
        "phone": "9820010005",
        "subject_codes": ["CS401"],
    },
    {
        "staff_id": "CSE-FAC-006",
        "name": "Prof. Aditi Pawar",
        "designation": "Assistant Professor",
        "specialization": "Web Technologies",
        "responsibility": "HTML; CSS; JavaScript",
        "assigned_year_role": "Subject Teacher (Second Year, Third Year)",
        "email": "aditi.pawar@example.com",
        "phone": "9820010006",
        "subject_codes": ["CS601"],
    },
    {
        "staff_id": "CSE-FAC-007",
        "name": "Dr. Kunal Jadhav",
        "designation": "Associate Professor",
        "specialization": "Computer Networks",
        "responsibility": "Networking; Network Security",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "kunal.jadhav@example.com",
        "phone": "9820010007",
        "subject_codes": ["CS501", "CS702"],
    },
    {
        "staff_id": "CSE-FAC-008",
        "name": "Prof. Pooja More",
        "designation": "Assistant Professor",
        "specialization": "Operating Systems",
        "responsibility": "OS; Linux Fundamentals",
        "assigned_year_role": "Subject Teacher (Second Year, Third Year)",
        "email": "pooja.more@example.com",
        "phone": "9820010008",
        "subject_codes": ["CS402"],
    },
    {
        "staff_id": "CSE-FAC-009",
        "name": "Dr. Saurabh Kale",
        "designation": "Professor",
        "specialization": "Software Engineering",
        "responsibility": "Software Design; Testing; Agile",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "saurabh.kale@example.com",
        "phone": "9820010009",
        "subject_codes": ["CS502"],
    },
    {
        "staff_id": "CSE-FAC-010",
        "name": "Prof. Vaishnavi Borkar",
        "designation": "Assistant Professor",
        "specialization": "Artificial Intelligence",
        "responsibility": "AI; Machine Learning Fundamentals",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "vaishnavi.borkar@example.com",
        "phone": "9820010010",
        "subject_codes": ["CS602"],
    },
    {
        "staff_id": "CSE-FAC-011",
        "name": "Dr. Om Mahajan",
        "designation": "Associate Professor",
        "specialization": "Theory of Computation",
        "responsibility": "Automata; Formal Languages",
        "assigned_year_role": "Subject Teacher (Second Year, Third Year)",
        "email": "om.mahajan@example.com",
        "phone": "9820010011",
        "subject_codes": ["CS503"],
    },
    {
        "staff_id": "CSE-FAC-012",
        "name": "Prof. Riya Gaikwad",
        "designation": "Assistant Professor",
        "specialization": "Compiler Design",
        "responsibility": "Compiler Design; Language Processing",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "riya.gaikwad@example.com",
        "phone": "9820010012",
        "subject_codes": ["CS603"],
    },
    {
        "staff_id": "CSE-FAC-013",
        "name": "Dr. Tejas Wankhede",
        "designation": "Associate Professor",
        "specialization": "Cloud Computing",
        "responsibility": "Cloud Platforms; Distributed Systems",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "tejas.wankhede@example.com",
        "phone": "9820010013",
        "subject_codes": ["CS701", "CS703"],
    },
    {
        "staff_id": "CSE-FAC-014",
        "name": "Prof. Kavya Desai",
        "designation": "Assistant Professor",
        "specialization": "Cyber Security",
        "responsibility": "Information Security; Cryptography Basics",
        "assigned_year_role": "Subject Teacher (Second Year, Final Year)",
        "email": "kavya.desai@example.com",
        "phone": "9820010014",
        "subject_codes": ["CS702"],
    },
    {
        "staff_id": "CSE-FAC-015",
        "name": "Dr. Abhishek Raut",
        "designation": "Professor",
        "specialization": "Mathematics for Computing",
        "responsibility": "Discrete Mathematics; Probability",
        "assigned_year_role": "Subject Teacher (First Year, Second Year)",
        "email": "abhishek.raut@example.com",
        "phone": "9820010015",
        "subject_codes": ["MAT101", "MAT102", "CS303"],
    },
    {
        "staff_id": "CSE-FAC-016",
        "name": "Prof. Tanvi Chavan",
        "designation": "Assistant Professor",
        "specialization": "Data Science",
        "responsibility": "Data Analytics; Introductory ML",
        "assigned_year_role": "Subject Teacher (Third Year, Final Year)",
        "email": "tanvi.chavan@example.com",
        "phone": "9820010016",
        "subject_codes": ["CS602"],
    },
    {
        "staff_id": "CSE-FAC-017",
        "name": "Prof. Harsh Pawar",
        "designation": "Assistant Professor",
        "specialization": "Java Programming",
        "responsibility": "Java; Object-Oriented Programming",
        "assigned_year_role": "Subject Teacher (First Year, Second Year)",
        "email": "harsh.pawar@example.com",
        "phone": "9820010017",
        "subject_codes": ["CS102"],
    },
    {
        "staff_id": "CSE-FAC-018",
        "name": "Dr. Shruti Suryawanshi",
        "designation": "Associate Professor",
        "specialization": "Computer Architecture",
        "responsibility": "Digital Logic; Computer Organization",
        "assigned_year_role": "Subject Teacher (First Year, Second Year)",
        "email": "shruti.suryawanshi@example.com",
        "phone": "9820010018",
        "subject_codes": ["CS302", "CS403"],
    },
    {
        "staff_id": "CSE-FAC-019",
        "name": "Prof. Pranav Mankar",
        "designation": "Assistant Professor",
        "specialization": "Project and Research Guidance",
        "responsibility": "Mini Projects; Major Projects; Research Methods",
        "assigned_year_role": "Project Coordinator / Subject Teacher (Third Year, Final Year)",
        "email": "pranav.mankar@example.com",
        "phone": "9820010019",
        "subject_codes": ["CS801"],
    },
    {
        "staff_id": "CSE-FAC-020",
        "name": "Prof. Nandini Shaikh",
        "designation": "Assistant Professor & Class Teacher",
        "specialization": "Department Class Coordination",
        "responsibility": "First Year Class Teacher / Student Mentoring",
        "assigned_year_role": "Class Teacher (First Year — Sem 1 & Sem 2)",
        "email": "nandini.shaikh@example.com",
        "phone": "9820010020",
        "subject_codes": ["CS101", "CS102", "MAT101", "MAT102", "PHY101"],
    },
]


def clean_name(raw_name):
    # Remove titles like Dr., Prof.
    tokens = raw_name.split()
    clean_tokens = [t for t in tokens if t.lower() not in ["dr.", "dr", "prof.", "prof", "mr.", "ms.", "mrs."]]
    if len(clean_tokens) == 1:
        return clean_tokens[0], ""
    return clean_tokens[0], " ".join(clean_tokens[1:])


class Command(BaseCommand):
    help = "Imports 20 CSE faculty members with Subject Teacher and Class Teacher privileges"

    def handle(self, *args, **options):
        self.stdout.write("Starting import of 20 CSE faculty members...")

        dept, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={
                "name": "Computer Science and Engineering",
                "description": "Department of Computer Science and Engineering"
            }
        )

        all_cse_subjects = list(Subject.objects.filter(course__department=dept))
        subject_dict = {s.code: s for s in all_cse_subjects}

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for item in FACULTY_DATA:
                staff_id = item["staff_id"]
                raw_name = item["name"]
                first_name, last_name = clean_name(raw_name)
                email = item["email"].lower()
                phone = item["phone"]
                designation = item["designation"]
                role_desc = f"{designation} | {item['specialization']} | {item['assigned_year_role']}"

                # Username e.g. fac_cse_001
                username = staff_id.lower().replace("-", "_")

                # Create or update User
                user, u_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "teacher",
                        "phone": phone,
                        "is_active": True,
                    }
                )
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.role = "teacher"
                user.phone = phone
                user.is_active = True
                user.set_password("TeacherPass123!")
                user.save()

                # Create or update Teacher Profile
                teacher, t_created = Teacher.objects.update_or_create(
                    employee_id=staff_id,
                    defaults={
                        "user": user,
                        "department": dept,
                        "phone": phone,
                        "qualification": role_desc,
                    }
                )

                # Assign subjects according to role
                codes = item["subject_codes"]
                if "ALL_CSE" in codes:
                    # HOD has access to all subjects
                    teacher.subjects.set(all_cse_subjects)
                else:
                    assigned_subs = [subject_dict[c] for c in codes if c in subject_dict]
                    teacher.subjects.set(assigned_subs)

                if t_created:
                    created_count += 1
                else:
                    updated_count += 1

                subs_assigned_names = ", ".join([s.code for s in teacher.subjects.all()])
                self.stdout.write(self.style.SUCCESS(
                    f"[{staff_id}] {raw_name} ({item['assigned_year_role']}) -> Subjects: {subs_assigned_names or 'None'}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Processed 20 faculty records (Created: {created_count}, Updated: {updated_count})."
        ))
