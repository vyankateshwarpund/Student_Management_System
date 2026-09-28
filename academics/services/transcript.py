"""Academic transcript and CGPA / SGPA calculation service."""
from academics.models import Marks

GRADE_POINTS = {
    'O': 10,
    'A+': 9,
    'A': 8,
    'B+': 7,
    'B': 6,
    'C': 5,
    'F': 0,
}


def calculate_student_transcript(student):
    """
    Computes semester-wise SGPA and overall CGPA for a student.
    Returns:
    {
        'student': student,
        'semesters': [
            {
                'semester': 1,
                'records': [...],
                'total_credits': 20,
                'earned_credits': 20,
                'total_points': 180,
                'sgpa': 9.0
            }
        ],
        'total_credits': 60,
        'earned_credits': 60,
        'cgpa': 8.85,
        'classification': 'First Class with Distinction'
    }
    """
    marks_records = Marks.objects.filter(student=student).select_related('subject')

    # Group by semester
    sem_dict = {}
    for m in marks_records:
        sem = m.semester
        if sem not in sem_dict:
            sem_dict[sem] = []
        sem_dict[sem].append(m)

    semesters_data = []
    cum_total_credits = 0
    cum_earned_credits = 0
    cum_points = 0

    for sem in sorted(sem_dict.keys()):
        records = sem_dict[sem]
        sem_credits = 0
        sem_earned_credits = 0
        sem_points = 0
        formatted_records = []

        for rec in records:
            credits = rec.subject.credits
            grade = rec.grade or 'F'
            point = GRADE_POINTS.get(grade, 0)
            score_points = point * credits

            sem_credits += credits
            if grade != 'F':
                sem_earned_credits += credits
            sem_points += score_points

            formatted_records.append({
                'subject_code': rec.subject.code,
                'subject_name': rec.subject.name,
                'credits': credits,
                'internal_marks': float(rec.internal_marks),
                'external_marks': float(rec.external_marks),
                'practical_marks': float(rec.practical_marks),
                'total_marks': float(rec.total_marks),
                'grade': grade,
                'grade_points': point,
                'credit_points': score_points,
            })

        sgpa = round(sem_points / sem_credits, 2) if sem_credits > 0 else 0.0

        cum_total_credits += sem_credits
        cum_earned_credits += sem_earned_credits
        cum_points += sem_points

        semesters_data.append({
            'semester': sem,
            'records': formatted_records,
            'total_credits': sem_credits,
            'earned_credits': sem_earned_credits,
            'sgpa': sgpa,
        })

    cgpa = round(cum_points / cum_total_credits, 2) if cum_total_credits > 0 else 0.0

    classification = "First Class with Distinction" if cgpa >= 8.0 else (
        "First Class" if cgpa >= 6.5 else (
            "Second Class" if cgpa >= 5.0 else "Pass Class"
        )
    )

    return {
        'student_id': student.student_id,
        'full_name': student.full_name,
        'department': student.department.name,
        'course': student.course.name,
        'admission_date': str(student.admission_date or ''),
        'semesters': semesters_data,
        'total_credits': cum_total_credits,
        'earned_credits': cum_earned_credits,
        'cgpa': cgpa,
        'classification': classification,
    }
