from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
import pandas as pd
from django.conf import settings
import xlsxwriter
from django.contrib import messages
from .forms import *
from .models import *
from blog.models import Post
from blog.forms import PostForm
# security functions:


def role_check(user, role):
    for item in Profile.objects.filter(user=user):
        if item.role == role:
            return True
        else:
            return False
def get_user_role(request):
    if Profile.objects.filter(user=request.user):
        return Profile.objects.filter(user=request.user)[0].role
    else:
        return "superuser"
# These are code for admin of site
def register_user_admin(request):
    all_user = User.objects.all()
    all_profile = Profile.objects.all()
    form = UserCreationForm(request.POST or None)
    context = {
        "title": "افزودن کاربر",
        "users": all_user,
        "profiles": all_profile,
        "form": form,
        'role': get_user_role(request),
        'teachers': Teacher.objects.all(),
        "students": Student.objects.all()
    }
    if form.is_valid():
        username = request.POST['username']
        password = request.POST['password1']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
        if request.POST['role'] == "Teacher":
            for user in all_user:
                if user.username == username:
                    user_obj = user
            Profile.objects.create(user=user_obj, role="Teacher")
            return redirect(f'/account/register/teacher-class?user={user_obj}')
        elif request.POST['role'] == "Student":
            for user in all_user:
                if user.username == username:
                    user_obj = user
            Profile.objects.create(user=user_obj, role="Student")
            return redirect(f'/account/register/student-class?user={user_obj}')
    return render(request, 'LMS/register_user.html', context)

def SelectClassTeacher(request):
    unavailable_classes = []
    for teacher in Teacher.objects.all():
        class_subjects = teacher.class_subject.split(', ')
        for cls_sbjct in class_subjects:
            unavailable_classes.append(cls_sbjct)
    SUBJECTS = ['ریاضی', 'علوم', 'مطالعات اجتماعی', 'ادبیات فارسی', 'عربی', 'قرآن', 'پیام های آسمان', 'نگارش', 'تفکر و سبک زندگی', 'ورزش', 'فرهنگ و هنر', 'کار و فناوری', 'انگلیسی']
    classes = []
    for p in [7, 8, 9]:
        for c in ['a', 'b', 'c']:
            for subject in SUBJECTS:
                    cls_sbjct = f"{p}{c}_{subject}"
                    if cls_sbjct in unavailable_classes:
                        continue
                    classes.append(f"{p}{c}_{subject}")
    if request.method == "POST":
        teacher_classes = ''
        for key,obj in request.POST.items():
            if key == "csrfmiddlewaretoken":
                continue
            teacher_classes += f"{obj}, "
        teacher_classes = teacher_classes[:-2]
        teacher = User.objects.get(username=request.GET.get('user'))
        Teacher.objects.create(user=teacher, class_subject=teacher_classes)
        return redirect('/account/register/')
    context = {
        "title": "انتخاب کلاس و درس",
        "classes": classes
    }
    return render(request, 'LMS/teacher class.html', context)
def SelectClassStudent(request):
    for i in User.objects.all():
        if i.username == request.GET['user']:
            user = i
    if request.method == "POST":
        grade = request.POST['grade']
        clas = request.POST['class']
        Student.objects.create(user=user, grade=grade, clas=clas)
        return redirect('/account/register/')
    return render(request, 'LMS/student class.html', {"title": "انتخاب کلاس و درس", "user": user})

def manage_ticket_notification(request):
    context = {
        'title': 'مدیریت تیکت ها',
        'notifications': Notification.objects.all(),
        'support_tickets': SupportTicket.objects.all(),
        'form': NotifcationForm,
        'role': get_user_role(request),
    }
    if request.method == 'POST':
        for_users = request.POST.get('for')
        message = request.POST.get('message')
        Notification.objects.create(to=for_users, from_user=request.user, message=message)
        return redirect('/account/manage-tickets-notifs/')
    return render(request, 'LMS/manage tickets notifs.html', context)
def answer_support_ticket(request, id):
    context = {
        'title': f'پاسخ تیکت: {id}',
        'ticket_id': id,
        'role': get_user_role(request),
    }
    if SupportTicket.objects.filter(id=id)[0].status:
        context['last_answer'] = SupportTicket.objects.filter(id=id)[0].reply
    if request.method == "POST":
        answer = request.POST.get('answer')
        SupportTicket.objects.filter(id=id).update(status=True, reply=answer)
        return redirect('/account/manage-tickets-notifs/')
    return render(request, 'LMS/answer ticket.html', context)

def edit_notification(request, id):
    # a form for notification with persian label
    obj = get_object_or_404(Notification, id=id)
    form = NotifcationForm(request.POST or None, instance=obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('/account/manage-tickets-notifs')
    context = {
        'title': 'ویرایش اعلامیه',
        'id': id,
        'form': form,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/edit notif.html', context)
# Teacher view are here
def manage_score(request):
    if not role_check(request.user, 'Teacher'):
        return redirect('/account/scores/')
    class_choices2 = []
    context = {
        'title': 'مدیریت نمرات',
        'users': User.objects.all(),
        'scores': Score.objects.all(),
        'role': get_user_role(request),
    }
    teacher_info = Teacher.objects.filter(user=request.user) or False
    if teacher_info:
        class_choices1 = teacher_info[0].class_subject.split(', ')
        for choice in class_choices1:
            class_choices2.append(choice.replace("_", ' '))
        context['class_choices'] = class_choices2
        if request.GET.get('class_subject_choice'):
            class_subject_choice = request.GET.get('class_subject_choice')
            clas = class_subject_choice[:2]
            subject = class_subject_choice[3:]
            students_list = Student.objects.filter(grade=clas[0], clas=clas.upper()[1])
            context['teacher_subject'] = subject
            context['teacher_class'] = subject
            context['students_list'] = students_list
    else:
        class_choices2 = False
    return render(request, "LMS/manage score.html", context)

def teacher_update_scores(request, student, subject):
    student_obj = get_object_or_404(Student, user__username=student)
    if request.method == "POST":
        title = int(request.POST.get('title'))
        score = request.POST.get('score')
        # add or update scores in Score model
        score_obj = Score.objects.get_or_create(user=student_obj, subject=subject)[0]
        if title == 1:
            score_obj.semester1 = score
        elif title == 2:
            score_obj.semester1_t = score
        elif title == 3:
            score_obj.semester1_e = score
        elif title == 4:
            score_obj.semester2 = score
        elif title == 5:
            score_obj.semester2_t = score
        elif title == 6:
            score_obj.semester2_e = score
        # 1 -> sm1 2 -> sm1t 3 -> sm1e ...
        score_obj.save()

    context = {
        'title': 'ویرایش',
        'fullname': User.objects.filter(username=student)[0].get_full_name(),
        'rl_scores': Score.objects.filter(user=student_obj, subject=subject),
        'role': get_user_role(request),
    }
    return render(request, 'LMS/edit score.html', context)
# student scores
def student_score(request):
    context = {
        'title': 'نمرات',
        'fullname': User.objects.filter(username=request.user)[0].get_full_name(),
        'scores': Score.objects.filter(user=Student.objects.filter(user=request.user)[0]),
        'role': get_user_role(request),
    }
    return render(request, 'LMS/score.html', context)

# manage homework from teacher:
def manage_homework(request):
    # functions
    def homework_exist(grade, subject):
        for homework in Homework.objects.all():
            # print(f"{grade} == {homework.class_grade} / {subject} == {homework.subject}")
            if grade == homework.class_grade and subject == homework.subject:
                return True
            else:
                return False
    # make subject and class looks better
    class_subjects = Teacher.objects.get(user=request.user).class_subject.split(', ')

    context = {
        'title': 'مدیریت تکالیف',
        'homeworks': Homework.objects.filter(teacher__user=request.user),
        'class_subject': class_subjects,
        'role': get_user_role(request),
    }
    # get teacher's object
    if request.method == "POST":
        grade = request.POST.get('class')[:2]
        subject = str(request.POST.get('class')[3:])
        homework = request.POST.get('homework')
        check_date = request.POST.get('check_date')
        if homework_exist(grade, subject.replace('-', ' ')):
            Homework.objects.filter(teacher=Teacher.objects.filter(user=request.user)[0], class_grade=grade, subject=subject.replace('-', ' ')).update(homework=homework, check_date=check_date)
            return redirect('/account/manage-homeworks/')
        else:
            Homework.objects.create(teacher=Teacher.objects.filter(user=request.user)[0], class_grade=grade, subject=subject.replace('-', ' '), homework=homework, check_date=check_date)
            return redirect('/account/manage-homeworks/')

    return render(request, 'LMS/manage homework.html', context)
# delete homework
def delete_homework(request, id):
    if not role_check(request.user, 'Teacher'):
        return redirect('/account/')
    Homework.objects.filter(id=id).delete()
    return redirect('/account/manage-homeworks')
# student's homework
def student_homework(request):
    # get all homeworks for student's class
    homeworks = Homework.objects.filter(class_grade=f"{Student.objects.filter(user=request.user)[0].grade}{Student.objects.filter(user=request.user)[0].clas.lower()}")
    context = {
        'title': 'تکالیف',
        'homeworks': homeworks,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/homeworks.html', context)

# teacher's manage exams
def manage_exam(request):
    teacherClasses = Teacher.objects.get(user=request.user).class_subject.split(', ')
    if request.method == "POST":
        teacher = request.user
        class_grade = request.POST.get('class_subject')[:2]
        subject = request.POST.get('class_subject')[3:]
        descriptions = request.POST.get('description')
        date = request.POST.get('date')
        Exam.objects.create(teacher=teacher, class_grade=class_grade, subject=subject, descriptions=descriptions, date=date, status=False)
        return redirect('/account/manage-exams/')
    context = {
        'title': 'مدیریت امتحانات',
        'all_exam': Exam.objects.all() or False,
        'teacher_classes': teacherClasses,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/manage exams.html', context)
def delete_exam(request, id):
    Exam.objects.filter(id=id).delete()
    return redirect('/account/manage-exams/')
def edit_exam(request, id):
    if request.method == "POST":
        description = request.POST.get('description')
        date = request.POST.get('date')
        status = request.POST.get('status')
        Exam.objects.filter(id=id).update(descriptions=description, date=date, status=status)
        return redirect('/account/manage-exams/')
    context = {
        'title': f'ویرایش امتحان{id}',
        'description_value': Exam.objects.filter(id=id)[0].descriptions,
        'date_value': Exam.objects.filter(id=id)[0].date,
        'id': id,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/edit exam.html', context)

# Manage student's exam score (in class)
def edit_examScore(request, id):
    grade = Exam.objects.filter(id=id)[0].class_grade[:1]
    clas = Exam.objects.filter(id=id)[0].class_grade[1:2].upper()
    student_list = Student.objects.filter(grade=grade, clas=clas)
    context = {
        'title': 'ثبت نمرات دانش آموزان',
        'student_list': student_list,
        'users': User.objects.all(),
        'role': get_user_role(request),
        'exam': id
    }
    return render(request, 'LMS/edit examscore.html', context)
def change_student_examscore(request, id, student_id):
    context = {
        'title': 'ویرایش نمره',
        'exam_id': id,
        'student_id': student_id,
        'role': get_user_role(request),
    }
    for exam_score in ExamScore.objects.all():
        if int(exam_score.exam_id.id) == int(id) and int(exam_score.student.user_id) == int(student_id):
            context['last_score'] = exam_score.exam_score
            
    if request.method == "POST":
        student = Student.objects.get(user=student_id)
        exam = ExamScore.objects.get_or_create(exam_id_id=id, student=student)[0]
        exam.exam_score = request.POST.get('score')
        exam.save()

        return redirect(f'/account/manage-exams/{id}/scores')
    return render(request, 'LMS/change student examscore.html', context)

# student see his scores
def student_exam(request):
    class_grade = f"{Student.objects.filter(user=request.user)[0].grade}{Student.objects.filter(user=request.user)[0].clas.lower()}"
    exam_schecdule = Exam.objects.filter(class_grade=class_grade)
    context = {
        'title': 'امتحانات',
        'exam_schedule': exam_schecdule,
        'exam_scores': ExamScore.objects.all(),
        'role': get_user_role(request),
    }
    return render(request, 'LMS/exams.html', context)
# make a ticekt for students and teachers
def make_ticket(request):
    role = get_user_role(request)
    context = {
        'title': 'تیکت ها',
        'private_tickets': PrivateTicket.objects.filter(from_user=request.user),
        'support_tickets': SupportTicket.objects.filter(from_user=request.user),
        'role': get_user_role(request),
    }
    if role == "Student":
        teachers = []
        for teacher in Teacher.objects.all():
            if teacher.class_subject[:2] == f"{Student.objects.filter(user=request.user)[0].grade}{Student.objects.filter(user=request.user)[0].clas.lower()}":
                teachers.append(teacher)
        context['teachers'] = teachers
    if request.method == "POST":
        for_user = request.POST.get('for')
        message = request.POST.get('message')
        if for_user == "support":
            SupportTicket.objects.create(from_user=request.user, message=message, status=False)
            return redirect('/account/tickets/')
        else:
            PrivateTicket.objects.create(from_user=request.user, to_user=Teacher.objects.filter(user__last_name=for_user)[0], message=message, status=False)
            return redirect('/account/tickets/')
    # if the user is a teacher -> he/she can also answer Private tickets
    if role == "Teacher":
        teacher_tickets = PrivateTicket.objects.filter(to_user__user=request.user)
        context['teacher_tickets'] = teacher_tickets
    return render(request, 'LMS/tickets.html', context)

def answer_ticket(request, id):
    context = {
        'title': f'پاسخ تیکت: {id}',
        'ticket_id': id,
        'role': get_user_role(request),
    }
    if SupportTicket.objects.filter(id=id)[0].status:
        context['last_answer'] = SupportTicket.objects.filter(id=id)[0].reply
    if request.method == "POST":
        answer = request.POST.get('answer')
        PrivateTicket.objects.filter(id=id).update(status=True, reply=answer)
        return redirect('/account/tickets/')
    return render(request, 'LMS/answer ticket.html', context)

# manage Sample exams for teachers
def manage_sample_exams(request):
    own_sample_exams = SampleExam.objects.filter(teacher__user=request.user)
    form = SampleExamForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.teacher = Teacher.objects.get(user=request.user)
        obj.save()
        return redirect('/account/manage-sample-exams')
    context = {
        'title': 'مدیریت نمونه سوال ها',
        'own_sample_exams': own_sample_exams,
        'form': form,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/manage sample exam.html', context)

def delete_sample_exam(request, id):
    if not role_check(request.user, 'Teacher'):
        return redirect('/account/')
    SampleExam.objects.filter(id=id).delete()
    return redirect('/account/manage-sample-exams/')

# get exam scores
def sample_exams(request):
    context = {
        'title': 'نمونه سوال ها',
        'sample_exams': SampleExam.objects.all(),
        'role': get_user_role(request),
    }
    return render(request, 'LMS/smaple exams.html', context)

# students festivals:
def festivals(request):
    registered = []
    for r in Request.objects.filter(user=request.user):
        if r.title.rfind('جشنواره') != -1:
            v = int(r.title.rfind('جشنواره') + 8)
            registered.append(r.title[v:r.title.rfind('،')])
    #? Note: hardest problem I've ever solve
            
    context = {
        'title': 'جشنواره ها',
        'role': get_user_role(request),
        'festivals': Festival.objects.all(),
        'registered': registered,
    }
    return render(request, 'LMS/festivals.html', context)
def festival_parts(request, id):
    parts = Festival.objects.filter(id=id)[0].parts.split('، ')
    context = {
        'title': 'جشنواره ها',
        'parts': parts,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/festival parts.html', context)
def participate_in_festival(request, id, part):
    festival = Festival.objects.filter(id=id)[0].title
    Request.objects.create(user=request.user, title=f'با سلام. کاربر {request.user} با نام {request.user.first_name} و نام خانوادگی {request.user.last_name} میخواهد در جشنواره {festival} در محور {part}، شرکت کند.')
    messages.success(request, 'شما با موفقیت ثبت نام شدید.')
    return redirect('/account/')
# admin manage festivals
def manage_festivals(request):
    context = {
        'title': 'مدیریت جشنواره ها',
        'role': get_user_role(request),
        'festivals': Festival.objects.all(),
    }
    if request.method == "POST":
        title = request.POST.get('title')
        until_date = request.POST.get('until_date')
        parts = request.POST.get('parts')
        if title and until_date and parts:
            Festival.objects.create(title=title, until_date=until_date, parts=parts)
            redirect('/account/manage-festivals/')
    return render(request, 'LMS/manage festivals.html', context)
def delete_festival(request, id):
    Festival.objects.filter(id=id).delete()
    return redirect('/account/manage-festivals/')
# admin requests
def requests(request):
    request_qs = Request.objects.all()
    context = {
        'title': 'درخواست ها',
        'requests': request_qs,
        'role': get_user_role(request),
    }
    return render(request, 'LMS/requests.html', context)

def answer_request(request, id):
    if Request.objects.filter(id=id)[0].feedback:
        feedback = Request.objects.filter(id=id)[0].feedback
    else:
        feedback = ''
    if not feedback:
        if request.method == 'POST':
            Request.objects.filter(id=id).update(feedback=request.POST.get('feedback'))
            messages.success(request, 'با موفقیت ثبت شد.')
            return redirect('/account/')
    context = {
        'title': 'درخواست ها',
        'role': get_user_role(request),
        'feedback': feedback,
    }
    return render(request, 'LMS/answer request.html', context)

def student_request(request, festival_part):
    feedback = Request.objects.filter(title=f"با سلام. کاربر {request.user} با نام {request.user.first_name} و نام خانوادگی {request.user.last_name} میخواهد در جشنواره {festival_part}، شرکت کند.")
    context = {
        'title': 'وضعیت',
        'feedback': feedback,
        "role": get_user_role(request),
    }
    return render(request, 'LMS/festival feedback.html', context)

# admin makes gallery image
def admin_manage_gallery(request):
    if not request.user.is_superuser:
        return redirect('/access-denied/')
    form = ImageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/account/manage-gallery')
    context = {
        'title': 'مدیریت عکس ها',
        'form': form,
        'gallery_pic': GalleryImage.objects.all(),
    }
    return render(request, 'LMS/manage gallery.html', context)
def delete_gallery_image(request, id):
    GalleryImage.objects.filter(id=id).delete()
    return redirect('/account/manage-gallery')
# manage news
def manage_news(request):
    if not request.user.is_superuser:
        return redirect('/account/')
    form = NewForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.slug = request.POST.get('title').replace(' ', '-')
        obj.save()
        return redirect('/account/manage-news')
    context = {
        'title': 'مدیریت اخبار',
        'form': form,
        'news': New.objects.all()
    }
    return render(request, 'LMS/manage news.html', context)
def delete_new(request, id):
    New.objects.filter(id=id).delete()
    return redirect('/aaccount/manage-news')
def edit_new(request, slug):
    form = NewForm(request.POST or None, instance=get_object_or_404(New, slug=slug))
    if form.is_valid():
        form.save()
        return redirect('/account/manage-news/')
    context = {
        'title': 'ویرایش خبر',
        'form': form,
    }
    return render(request, 'LMS/edit new.html', context)

def manage_blog(request):
    posts = Post.objects.all()
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.slug = request.POST.get('title').replace(' ', '-')
        new_post.save()
        return redirect('/account/manage-blog')
    context = {
        'title': 'مدیریت وبلاگ',
        'blog_posts': posts,
        'form': form,
    }
    return render(request, 'LMS/manage blog.html', context)
def edit_blog_post(request, slug):
    obj = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        post = form.save(commit=False)
        post.slug = request.POST.get('title').replace(' ', '-')
        post.save()
        return redirect('/account/manage-blog/')

    context = {
        'title': 'ویرایش نوشته',
        'form': form
    }
    return render(request, 'LMS/edit blogpost.html', context)

def delete_blog_post(request, slug):
    obj = get_object_or_404(Post, slug=slug)
    obj.delete()
    return redirect('/account/manage-blog/')

# Get student scores for admin
def get_reportsheets(request):
    context = {
        'title': 'کارنامه دانش آموزان',
        'students': Student.objects.all()
    }
    if request.GET.get('q'):
        query = request.GET.get('q')
        students = []
        all_student = Student.objects.all()
        for student in all_student:
            if query in student.get_fullname():
                students.append(student)
            elif query in student.user.username:
                students.append(student)
            elif query in student.which_class():
                students.append(student)

        context['students'] = students
    return render(request, 'LMS/get_reportsheet.html', context)
def get_semester_score(request, student):
    context = {
        'title': 'نمرات ترم',
        'scores': Score.objects.filter(user__user__username=student),
        'student': student
    }

    return render(request, 'LMS/get semester score.html', context)
def get_semester_score_excel(request, student):
    sobj = Score.objects.filter(user__user__username=student)
    scores = {'نام درس': [s.subject for s in sobj], 'ترم اول تکوینی': [s.semester1_t for s in sobj], 'ترم اول نوبت': [s.semester1_e for s in sobj], 'ترم اول پایانی': [s.semester1 for s in sobj], 'ترم دوم تکوینی': [s.semester2_t for s in sobj], 'ترم دوم نوبت': [s.semester2_e for s in sobj], 'ترم دوم پایانی': [s.semester2 for s in sobj]}
    sum_score = 0
    n_of_operation = 0
    for score in sobj:
        sum_score += float(score.semester1)
        sum_score += float(score.semester2)
        n_of_operation += 2
    sum_ = sum_score / n_of_operation

    df = pd.DataFrame(scores)
    df.loc[len(df.index)] = [f'معدل: {sum_}', '', '', '', '', '', '']
    df.reset_index(drop=True, inplace=True)
    writer = pd.ExcelWriter(settings.STATICFILES_DIRS[0] / 'reportsheet.xlsx', engine='xlsxwriter')
    workbook = writer.book
    font = workbook.add_format({'font_name': 'vazir'})
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(0, len(df.columns) - 1, 15, font)
    writer._save()
    file = 'reportsheet.xlsx'

    context = {
        'title': 'دریافت اکسل',
        'file': file,
        'table': df.to_html(index=False, classes='table')
    }

    return render(request, 'LMS/get_semester_student_excel.html', context)

def get_classscore_score(request, student):
    context = {
        'title': 'نمرات کلاسی',
        'exam_scores': ExamScore.objects.filter(student__user__username=student),
    }
    return render(request, 'LMS/get classcore.html', context)
def get_classscore_score_excel(request, student):
    all_score = ExamScore.objects.filter(student__user__username=student)
    scores = {"نمرات": {}}
    SUBJECTS = ['ریاضی', 'علوم', 'مطالعات اجتماعی', 'ادبیات فارسی', 'عربی', 'قرآن', 'پیام های آسمان', 'نگارش', 'تفکر و سبک زندگی', 'ورزش', 'فرهنگ و هنر', 'کار و فناوری', 'انگلیسی']
    for subject in SUBJECTS:
        score_list = []
        for score in all_score:
            if score.exam_id.subject == subject:
               score_list.append(str(score.exam_score))
        scores['نمرات'][subject] = ', '.join(score_list)
    df = pd.DataFrame(scores)
    writer = pd.ExcelWriter(settings.STATICFILES_DIRS[0] / 'نمرات کلاسی.xlsx', engine='xlsxwriter')
    workbook = writer.book
    font = workbook.add_format({'font_name': 'vazir', 'align': 'center'})
    df.to_excel(writer, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(0, 1, 13, font)
    worksheet.set_column(1, len(df.columns), 10, font)
    writer._save()
    context = {
        'title': 'نمرات کلاسی',
        'file': 'نمرات کلاسی.xlsx',
        'score_html': df.to_html(classes='table')
    }
    return render(request, 'LMS/get classscore excel.html', context)