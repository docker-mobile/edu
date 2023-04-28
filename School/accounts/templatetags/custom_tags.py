from django import template
from LMS.models import *
from blog.models import *
from blog.forms import *

register = template.Library()

@register.filter
def get_by_index(l, i):
    return l[i]
@register.filter
def plus(int, n):
    return int + n
@register.filter
def minus(int, n):
    return int - n
@register.filter
def is_bigger(first, second):
    if first > second:
        return True
    else:
        return False

@register.filter
def convert_to_persian(st):
    if st == 'semester1':
        return 'ترم اول پایانی'
    if st == 'semester1 mostamar':
        return 'ترم اول تکوینی'
    if st == 'semester1 exam':
        return 'ترم اول نوبت'
    if st == 'semester2':
        return 'ترم دوم پایانی'
    if st == 'semester2 mostamar':
        return 'ترم دوم تکوینی'
    if st == 'semester2 exam':
        return 'ترم دوم نوبت'
@register.filter
def get_exam_score(student, exam_id):
    exam = ExamScore.objects.filter(exam_id=exam_id, student__user=student)
    if exam:
        return exam[0].exam_score
    else:
        return 'ثبت نشده است.'