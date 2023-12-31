from django.shortcuts import render,HttpResponse,redirect,get_object_or_404,HttpResponseRedirect
import datetime,random,string,json
from bnmc_project.models import *
from django.views.generic import TemplateView
#from dal import autocomplete
from django.db.models import Q
from django.views.generic import ListView
import csv
from decimal import Decimal
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from .serializers import PostSerializer,sliderSerializer,Student_info,Education_info
from rest_framework import generics
from drf_multiple_model.views import FlatMultipleModelAPIView
from django.core.files.storage import FileSystemStorage
from dateutil.relativedelta import relativedelta
from django.views.generic import View
from django.utils import timezone
from .models import *
from .render import Render
from num2words import num2words
from django.utils.dateparse import parse_date
import datetime


from django.shortcuts import render_to_response
from django.template import RequestContext


from django.contrib import messages
from PIL import Image




from django.core import serializers
from django.http import HttpResponse




def dataUpdate(request):
    pwd = os.path.dirname(__file__)
    with open(pwd + '/bnc_rnm_info_.csv', encoding="ISO-8859-1") as f:
        reader = csv.DictReader(f, delimiter=',')
        i = 0
        diploma=Program.objects.get(id=18)
        bacelor=Program.objects.get(id=4)
        k=0
        for row in reader:



            entry_id = row['entry_id']
            course_type = row['course_type']
            dip='18032019102700'
            bsc='11032014131633'




            if course_type == dip:


                lic=license_receive.objects.filter(entry_id=entry_id)
                if lic:

                    lic=lic[0]

                    lic_h=LicenseHistory.objects.filter(license_receive_id=lic.id)[0]


                    k+=1
                    # print(course_type,lic_h.program,'doploma')
                    lic_h.program=diploma
                    lic_h.save()
                    print(lic_h,k)


            if course_type == bsc:
                lic = license_receive.objects.filter(entry_id=entry_id)
                if lic:

                    lic = lic[0]

                    lic_h = LicenseHistory.objects.filter(license_receive_id=lic.id)[0]



                    k += 1
                    # print(course_type, lic_h.program, 'bsc')
                    lic_h.program = bacelor
                    lic_h.save()
                    print(lic_h,k)
        print(k)
    return HttpResponse('llll')

def examination_result_add(request,main_subject):
    context={}
    if  not request.user.is_superuser:

        get_request_user=UserPermissionResult.objects.filter(user=request.user.id).last()
        exam_student_reg=ExaminationStudentRegistration.objects.filter(exam=get_request_user.final_exam,roll_number__range=(get_request_user.start_roll,get_request_user.end_roll))
        sub_main=ExamSubject.objects.get(id=main_subject)
        sub=SubSubject.objects.filter(exam_subject=sub_main.id)

        result_list=[]
        sort_list=[]
        start_zero=-1
        for k in exam_student_reg:
            if sub_main in k.subjects.all():
                sort_list.append(k)

        result_dimention_list=[[] for i in range(0, len(sort_list))]
        pass_status_dimention_list=[[] for i in range(0, len(sort_list))]

        status = ''
        for students in sort_list:
            start_zero+=1
            for user_subject in get_request_user.sub_subjects.all():
                filter_result_add = Examination_result_add.objects.filter(exam_id=students.id, subject=user_subject.id)
                print(filter_result_add)


                if filter_result_add:
                    result_dimention_list[start_zero].append(filter_result_add)

                else:

                    set_mark_and_id=str(user_subject.id)+'-'+str(user_subject.marks)
                    result_dimention_list[start_zero].append(set_mark_and_id)

                if filter_result_add:


                    if filter_result_add[0].mark > filter_result_add[0].subject.pass_marks or filter_result_add[0].mark == filter_result_add[0].subject.pass_marks:
                        status='Pass'
                        pass_status_dimention_list[start_zero].append(status)


                        if not 'Failed' in pass_status_dimention_list[start_zero]:

                            pass_status_dimention_list[start_zero]=[]

                            pass_status_dimention_list[start_zero].append('Pass')

                        elif 'Failed' in pass_status_dimention_list[start_zero]:
                            pass_status_dimention_list[start_zero] = []

                            pass_status_dimention_list[start_zero].append('Failed')


                    elif filter_result_add[0].mark < filter_result_add[0].subject.pass_marks:
                        status = 'Failed'
                        pass_status_dimention_list[start_zero].append(status)

                        if 'Failed' in pass_status_dimention_list[start_zero]:
                            pass_status_dimention_list[start_zero]=[]
                            pass_status_dimention_list[start_zero].append('Failed')


        context={'own_students':zip(sort_list,result_dimention_list,pass_status_dimention_list),
                 'sub_main':sub_main,
                 'get_request_user':get_request_user
                 }

    if request.method == 'POST':

        obtain_mark_list=request.POST.getlist('obtain[]')
        exam_student_list=request.POST.getlist('exam_registration[]')
        sub_subject_list=request.POST.getlist('sub_subject[]')


        for obtain,student_id,sub_subject_id in zip(obtain_mark_list,exam_student_list,sub_subject_list):
            print(obtain,student_id,sub_subject_id)
            result_filter=Examination_result_add.objects.filter(exam_id=student_id,subject=sub_subject_id)

            if result_filter:
                print('if',result_filter)
                result_filter.update(mark=float(obtain))

            else:
                print('else',result_filter)
                if obtain != '':

                    exam_student_filter=ExaminationStudentRegistration.objects.get(id=student_id)
                    get_sub_subject=SubSubject.objects.get(id=sub_subject_id)
                    get_user=User.objects.get(id=request.user.id)

                    result_create=Examination_result_add()
                    result_create.exam_id=exam_student_filter
                    result_create.subject=get_sub_subject
                    result_create.mark=float(obtain)

                    result_create.result_submitted_by=get_user
                    result_create.save()

        return redirect('/admin/add_result/'+str(sub_main.id))


    return render(request, 'admin/result_add.html',context)


def subject_list_result(request):
    get_request_user = UserPermissionResult.objects.filter(user=request.user.id).last()


    context={'subject':get_request_user.main_subjects.all()}

    return render(request, 'admin/subject_list.html',context)


def subject_text(request):


    subject_name=SubSubject.objects.get(id=request.GET['subs_id'])
    print(subject_name.exam_subject.name)
    subject_name_=[True,subject_name.exam_subject.name]
    data=json.dumps(subject_name_)


    return HttpResponse(data)

def program_text(request):


    e_year=ExamYear.objects.get(id=request.GET['year_id'])
    print(e_year,'kkkkkkkkkkkkkkkk')

    program_name=[True,e_year.program.title]
    data=json.dumps(program_name)


    return HttpResponse(data)


def division_wise_report(request):
    division=Division.objects.all()
    program=Program.objects.all()
    session=Session.objects.all()
    context={'division':division,
             'program':program,
             'session':session
             }

    if request.method == 'POST':
        division_id=request.POST['division']
        program_id=request.POST['program']
        session_id=request.POST['session']

        program=Program.objects.get(id=program_id)
        division=Division.objects.get(id=division_id)
        session=Session.objects.get(id=session_id)
        district_list=[]
        institution_list=[]


        districts=District.objects.filter(division=division)
        for i in districts:
            district_list.append(i.name)

        count_len=len(district_list)
        minus_one=-1
        zero=-1
        dimension_list = [[] for i in range(0, count_len)]
        student_total = [[] for i in range(0, count_len)]
        for n in district_list:
            minus_one+=1

            institutions = Institution.objects.filter(district__name=n)

            for ins in institutions:

                student_approve_total=Student_Registration.objects.filter(session=session,program_title=program,approved=True,institution__institution_name=ins).count()

                dimension_list[minus_one].append(ins)

                student_total[minus_one].append(student_approve_total)


                print(student_approve_total,'kkkkkkkkkkkkkk')

        try:
            if division !=0 and program !=0 and session !=0:

                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="exam_wise_report_for_bnmc.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Users')

                # Sheet header, first row
                row_num = 0
                no=0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Division', 'District', 'Institution', 'Total','total list',]

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()
                exam_='Exam Name: '
                prog_='Program Name: '
                ws._cell_overwrite_ok = True
                total_amount=''
                zero=-1
                total_list=[]
                kk=0



                for d in district_list:
                    kk+=1

                    zero+=1

                    print(sum(student_total[zero]),student_total[zero])
                    for p, total in zip(dimension_list[zero],student_total[zero]):
                        total_list.append(sum(student_total[zero]))
                        row_num += 1




                        ws.write(row_num, 0, division.name, font_style)
                        ws.write(row_num, 1, str(d), font_style)
                        ws.write(row_num, 2, str(p), font_style)
                        ws.write(row_num, 3, str(total), font_style)
                        ws.write(row_num, 4, d+' total students '+str(sum(student_total[zero])), font_style)







                ws.write(row_num, 5, 'llll', font_style)

                wb.save(response)
                return response
        except ValueError as e:
            print(e)






    return render(request,'admin/division_report.html',context)

def old(request):
    up=license_receive.objects.filter(is_old_data=True)
    up.update(status=Permission.objects.all().order_by('display_order').last())
    return HttpResponse('llll')


def new_end_date_implement(date_end_inc):
    if date_end_inc.day == 1:
        month=date_end_inc.month - 1
        if month < 8:
            if month % 2 == 1:
                new_end_date_implement = date(date_end_inc.year + 5, month, day=31)

            elif month % 2 == 0 and month == 2 and (date_end_inc.year+5) % 4 !=0:
                new_end_date_implement = date(date_end_inc.year + 5,month, day=28)

            elif month % 2 == 0 and month == 2 and (date_end_inc.year+5) % 4 == 0:
                new_end_date_implement = date(date_end_inc.year + 5,month, day=29)

            elif month % 2 == 0 and month !=0:
                new_end_date_implement = date(date_end_inc.year + 5, month, day=30)



            elif month == 0:

                new_end_date_implement = date(date_end_inc.year + 4,month=12, day=31)

        elif month > 7 and month < 12:
            if month % 2 == 1:
                new_end_date_implement = date(date_end_inc.year + 5, month, day=30)

            elif month % 2 == 0 and month !=0:
                new_end_date_implement = date(date_end_inc.year + 5, month, day=31)

    else:
        new_end_date_implement = date(date_end_inc.year + 5, date_end_inc.month, date_end_inc.day - 1)


    return new_end_date_implement
from django.db.models import Avg, Max, Min, Sum
def license_select(request):
    license_list=request.POST.getlist('list[]')
    reg_date=request.POST.get('reg_date')
    start_date=request.POST.get('start_date')


    date_end_inc=parse_date(start_date)
    new_end_date=new_end_date_implement(date_end_inc)


    license_rec_list=license_receive.objects.filter(id__in=license_list)
    for i in license_rec_list:
        print(i.id)
        search_licenseHis_q=LicenseHistory.objects.filter(license_receive_id=i)
        if len(search_licenseHis_q) == 1:
            search_licenseHis_q=search_licenseHis_q[0]
            if search_licenseHis_q.program and search_licenseHis_q.license_number == None:
                search_by_program=LicenseHistory.objects.filter(program=search_licenseHis_q.program.id).aggregate(Max('license_number'))
                max_number=search_by_program.get("license_number__max")
                search_licenseHis_q.license_registration_date=reg_date
                search_licenseHis_q.license_start_date=start_date
                search_licenseHis_q.license_end_date=new_end_date
                search_licenseHis_q.license_receive_id=i
                search_licenseHis_q.license_number=max_number+1
                search_licenseHis_q.save()
            print()
    data = json.dumps('llll')
    return HttpResponse(data)


def delete_():


    li=license_receive.objects.all()

    for i in li:
        s=Student.objects.filter(id=li.students.id)
        s.delete()
        print('delete done')
    LicenseHistory.objects.all().delete()
    li=license_receive.objects.all().delete()

def all_subjects(request, exam_id):
    exam_subs=ExamSubject.objects.all()
    json_models = serializers.serialize("json", exam_subs)
    return HttpResponse(json_models, content_type='application/json')



def get_sub_subject(request, subject_id):
    print(subject_id)
    sub_subs=SubSubject.objects.filter(exam_subject=subject_id)




    for i in sub_subs:
        print(i.id,i.subject_name)
    json_models = serializers.serialize("json", sub_subs)
    return HttpResponse(json_models, content_type='application/json')




def get_year_url(request, program_id):

    years=ExamYear.objects.filter(program=program_id)
    print(years)
    json_models = serializers.serialize("json", years)
    return HttpResponse(json_models, content_type='application/json')




def examination_result_add_u_p(request):
    if request.method == 'POST':

        institute=request.POST.getlist('ins[]')
        programs=request.POST.getlist('program[]')
        years=request.POST.getlist('year[]')
        exam=request.POST.getlist('exam[]')
        subjects=request.POST.getlist('sub[]')
        sub_subjects=request.POST.getlist('subs[]')
        user=request.POST.get('user')
        start_roll=request.POST.get('start')
        end_roll=request.POST.get('end')
        remove_ids=request.POST.get('remove_id')

        pure_subject_list=[]

        institutions_instances=Institution.objects.filter(id__in=institute)
        subjects_instances=ExamSubject.objects.filter(id__in=subjects)

        re_list=remove_ids.split(",")
        if re_list:
            for i in sub_subjects:
                if i in re_list:
                    pass

                else:
                    pure_subject_list.append(i)

        sub_subjects=SubSubject.objects.filter(id__in=pure_subject_list)
        if user != '0':
            user_instance = User.objects.get(id=user)
            user_permission=UserPermissionResult()

            user_permission.user=user_instance
            user_permission.start_roll=start_roll
            user_permission.end_roll=r=end_roll
            user_permission.save()
            print('pppppppppppppppppppppppp')


            user_permission.institutions.add(*institutions_instances)
            user_permission.main_subjects.add(*subjects_instances)
            user_permission.sub_subjects.add(*sub_subjects)
            user_permission.program.add(*programs)
            user_permission.exam_year.add(*years)



    con = {

           'institution': Institution.objects.all(),
          'exam':Final_exam.objects.all(),
          'exam_subject':ExamSubject.objects.all(),
          'user':User.objects.all(),
        'SubSubject':SubSubject.objects.all(),
        'program':Program.objects.all(),
        'year':ExamYear.objects.all()

           }
    return render(request, 'admin/html.html',con)

def edit_teacher_form(request,id):
    ins_p=IntuitionProfile.objects.get(id=id)
    if ins_p.is_nurse:
        student=Student.objects.get(id=ins_p.student.id)
        license_query = LicenseHistory.objects.filter(student_id=student)
        if license_query:

            list_of_collections = []

            current_date = datetime.datetime.now().date()

            for i in license_query:
                if i.license_end_date:
                    expire_date = parse_date(i.license_end_date)

                    if current_date > expire_date:
                        list_of_collections.append('Expired')

                    else:
                        list_of_collections.append('Renewed')

                else:
                    list_of_collections.append('None')

    else:
        student=IntuitionProfile.objects.get(id=id)

    con={'license_his':student,
        'nationality': Nationality.objects.all().exclude(id=student.nationality.id),

                    'institution': Institution.objects.all(),
                    'designation': Designation.objects.all(),
                    'program': Program.objects.all(),
                    'div': Division.objects.all().exclude(id=student.division.id),
                    'dis': District.objects.all().exclude(id=student.district.id),
                    'thn': Thana.objects.all().exclude(id=student.thana.id),
                    'qr': zip(license_query, list_of_collections)
         }
    return render(request, 'admin/teacher_form_edit.html',con)
# encoding: utf-8

def apply_for_renew(request):
    if 'data' in request.POST:
        license_number = request.POST.get("license_number")
        program_id = request.POST.get("program_id_")
        license_his = LicenseHistory.objects.filter(license_number=license_number, program=program_id)
        if license_his:
            license_query = LicenseHistory.objects.filter(license_receive_id=license_his[0].license_receive_id)

            list_of_collections = []

            current_date = datetime.datetime.now().date()

            for i in license_query:
                print(i.program,i.license_number)
                if i.license_end_date:
                    expire_date = parse_date(i.license_end_date)

                    if current_date > expire_date:
                        req_re=RequestedLicense.objects.filter(program=i.program,license_number=i.license_number,name=i.license_receive_id.last_name)
                        if req_re:
                            list_of_collections.append('Already Applied')

                        else:
                            list_of_collections.append('Expired')

                    else:
                        list_of_collections.append('Renewed')

                else:
                    list_of_collections.append('No Status')

            context = {
                'f': 'true',
                'license_query':license_query,

                'license_his': license_his[0],

                'nationality': Nationality.objects.all()
                ,
                'institution': Institution.objects.all(),
                'designation': Designation.objects.all(),
                'program': Program.objects.all(),
                'div': Division.objects.all(),
                'dis': District.objects.all(),
                'thn': Thana.objects.all(),
                'qr': zip(license_query, list_of_collections)

            }

            return render(request, 'admin/apply_form.html', context)

        else:
            context = {'program': Program.objects.all(),'f':'f' }

            return render(request, 'admin/apply_form.html', context)


    elif 'data2' in request.POST:
        license_renew_ids = request.POST.getlist("n")
        I_am_satisfied=request.POST.get('I_am_satisfied')
        before_starting=request.POST.get('before_starting')
        I_own_my=request.POST.get('I_own_my')
        I_am_interested=request.POST.get('I_am_interested')
        I_am_aware=request.POST.get('I_am_aware')
        I_am_aware_of_prescribed=request.POST.get('I_am_aware_of_prescribed')
        In_Bangladesh_most=request.POST.get('In_Bangladesh_most')
        Every_day=request.POST.get('Every_day')
        I_always_try=request.POST.get('I_always_try')
        I_am_aware_of_functions=request.POST.get('I_am_aware_of_functions')
        I_always_wear_my_professional=request.POST.get('I_always_wear_my_professional')
        I_feel_the_present=request.POST.get('I_feel_the_present')
        I_feel_there_should_be=request.POST.get('I_feel_there_should_be')
        I_know_the_number=request.POST.get('I_know_the_number')
        urgent=request.POST.get('urgent')



        current_working_place=request.POST.get('current_working_place')
        current_position=request.POST.get('current_position')
        working_years=request.POST.get('working_years')
        traning=request.POST.get('traning')
        a_s=request.POST.get('a_s')
        s_o=request.POST.get('s_o')
        image=request.POST.get('image')


        if I_am_satisfied:
            I_am_satisfied=True

        else:
            I_am_satisfied=False

        if before_starting:
            before_starting = True

        else:
            before_starting = False

        if I_own_my:
            I_own_my = True

        else:
            I_own_my = False

        if I_am_interested:
            I_am_interested = True

        else:
            I_am_interested = False

        if I_am_aware:
            I_am_aware = True

        else:
            I_am_aware = False

        if I_am_aware_of_prescribed:
            I_am_aware_of_prescribed = True

        else:
            I_am_aware_of_prescribed = False

        if In_Bangladesh_most:
            In_Bangladesh_most = True

        else:
            In_Bangladesh_most = False

        if Every_day:
            Every_day = True

        else:
            Every_day = False

        if I_am_aware_of_functions:
            I_am_aware_of_functions = True

        else:
            I_am_aware_of_functions = False


        if I_always_wear_my_professional:
            I_always_wear_my_professional = True

        else:
            I_always_wear_my_professional = False

        if I_feel_the_present:
            I_feel_the_present = True

        else:
            I_feel_the_present = False


        if I_feel_there_should_be:
            I_feel_there_should_be = True

        else:
            I_feel_there_should_be = False


        if I_know_the_number:
            I_know_the_number = True

        else:
            I_know_the_number = False

        if I_always_try:
            I_always_try = True

        else:
            I_always_try = False

        if urgent:
            urgent=True
        else:
            urgent=False


        apply_save = ApplyLicense(I_am_satisfied=I_am_satisfied, before_starting=before_starting, I_own_my=I_own_my,
                                  I_am_interested=I_am_interested,
                                  I_am_aware=I_am_aware, I_am_aware_of_prescribed=I_am_aware_of_prescribed,
                                  Every_day=Every_day,
                                  In_Bangladesh_most=In_Bangladesh_most, I_always_try=I_always_try,
                                  I_am_aware_of_functions=I_am_aware_of_functions,
                                  I_always_wear_my_professional=I_always_wear_my_professional,
                                  I_feel_the_present=I_feel_the_present,
                                  I_feel_there_should_be=I_feel_there_should_be, I_know_the_number=I_know_the_number,urgent=urgent,
                                  currently_working_place=current_working_place,current_position=current_position,Working_years_as_a_registered=working_years,
                                  Training=traning,Attendance_in_Seminar=a_s,Research_skills=s_o,image=str('/media/'+image)

                                  )

        apply_save.save()

        if license_renew_ids:
            license_his = LicenseHistory.objects.filter(id__in=license_renew_ids)
            for i in license_his:
                req_renew = RequestedLicense()
                req_renew.program = i.program
                req_renew.name = i.license_receive_id.last_name
                req_renew.license_number = i.license_number
                req_renew.applyLicense = apply_save
                req_renew.save()

        context = {'program': Program.objects.all(),
                   'suc':'Your apply successful'
                   }

        return render(request, 'admin/apply_form.html', context)

    context = {'program': Program.objects.all(),}

    return render(request,'admin/apply_form.html',context)


def get_data(request):
    license_number=request.POST.get("registation_number")
    program_id=request.POST.get("program_id")
    license_his=LicenseHistory.objects.filter(license_number=license_number,program=program_id)
    license_find=LicenseHistory.objects.filter(license_receive_id=license_his[0].license_receive_id)

    qs_json = serializers.serialize('json', license_find)


    for js in license_find:
        print(js.institution.institution_name)
        js.institution=js.institution.institution_name
    # print(qs_json)
    return HttpResponse(qs_json, content_type='application/json')
    # if license_his:
    #     license_his=license_his[0]
    #     if license_his.license_receive_id.is_old_data:
    #         info=[True,license_his.license_number,license_his.license_receive_id.students.last_name,str(license_his.license_receive_id.students.date_of_birth),
    #               license_his.license_receive_id.students.fathers_name,license_his.license_receive_id.students.mothers_name,
    #               license_his.license_receive_id.students.sex,license_his.license_receive_id.students.marital_status,license_his.license_receive_id.students.nationality.id,
    #               license_his.license_receive_id.students.students_mobile_no,license_his.license_receive_id.students.email_address,license_his.license_receive_id.students.division.id,
    #               license_his.license_receive_id.students.district.id,license_his.license_receive_id.students.thana.id,license_his.license_receive_id.students.village,
    #               license_his.license_receive_id.students.postal_code,license_his.license_receive_id.students.post_office,license_his.institution.id,
    #               str(license_his.license_receive_id.image)
    #
    #
    #               ]

    # else:
    #     info=[False]
    # data = json.dumps(info)
    # return HttpResponse(data)

@login_required
def teacher_form(request):


    if request.method == 'POST':

        if 'get_data' in request.POST:
            license_number = request.POST.get("license_number")
            program_id = request.POST.get("program_id_")
            license_his = LicenseHistory.objects.filter(license_number=license_number, program=program_id)
            if license_his:
                license_query=LicenseHistory.objects.filter(license_receive_id=license_his[0].license_receive_id)

                list_of_collections = []

                current_date = datetime.datetime.now().date()

                for i in license_query:
                    if i.license_end_date:
                        expire_date = parse_date(i.license_end_date)

                        if current_date > expire_date:
                            list_of_collections.append('Expired')

                        else:
                            list_of_collections.append('Renewed')

                    else:
                        list_of_collections.append('None')

                context={
                    'f':'true',

                    'license_his':license_his[0],

                    'nationality': Nationality.objects.all()
                    ,
                    'institution': Institution.objects.all(),
                    'designation': Designation.objects.all(),
                    'program': Program.objects.all(),
                    'div': Division.objects.all(),
                    'dis': District.objects.all(),
                    'thn': Thana.objects.all(),
                    'qr':zip(license_query,list_of_collections)

                }


                return render(request, 'admin/teacher_form.html', context)

            else:
                context = {



                    'nationality': Nationality.objects.all()
                    ,
                    'institution': Institution.objects.all(),
                    'designation': Designation.objects.all(),
                    'program': Program.objects.all(),
                    'div': Division.objects.all(),
                    'dis': District.objects.all(),
                    'thn': Thana.objects.all(),
                    'not':'Not Found Please Give Correct Information'
                }

                return render(request, 'admin/teacher_form.html', context)

        elif 'submit' in request.POST:
            print('submit')
            is_nurse = request.POST.get('nurse')
            student_id = request.POST.get('student_id')
            license_number = request.POST.get('number')
            name = request.POST.get('name')
            date_birth = request.POST.get('date_birth')
            f_name = request.POST.get('f_name')
            m_name = request.POST.get('m_name')
            sex = request.POST.get('sex')
            matrtial = request.POST.get('matrtial')
            national = request.POST.get('national')
            no = request.POST.get('no')
            email = request.POST.get('email')
            division = request.POST.get('division')
            district = request.POST.get('district')
            thana = request.POST.get('thana')
            village = request.POST.get('village')
            post_code = request.POST.get('post_code')
            post_off = request.POST.get('post_off')
            ins = request.POST.get('ins')
            e_t = request.POST.get('e_t')
            designation = request.POST.get('designation')
            w_start_date = request.POST.get('w_start_date')
            f_id = request.POST.get('f_id')
            file = request.POST.get('file')

            if ins != '':
                institute = Institution.objects.get(id=ins)

            else:
                institute = None

            if division != '':
                division_obj = Division.objects.get(id=division)

            else:
                division_obj = None

            if district != '':
                district_obj = District.objects.get(id=district)

            else:
                district_obj = None

            if thana != '':
                thana_obj = Thana.objects.get(id=thana)

            else:
                thana_obj = None

            if national != '':
                national_obj = Nationality.objects.get(id=national)

            else:
                national_obj = None

            if designation != '':
                designation_obj = Designation.objects.get(id=designation)

            else:
                designation_obj = None
            if student_id:
                std_id=Student.objects.get(id=student_id)

            else:
                std_id = None


            if is_nurse or student_id:


                institute_save=IntuitionProfile(  is_nurse = True, full_name_english = None,
                father_name = None,
                mother_name = None,
                marital_status = None,
                sex = None,
                nationality = None,
                division = None,
                district = None,
                thana = None,
                village = None,
                email_address = None,
                post_office = None,
                postal_code = None,
                date_of_birth = None, license_number = None, students_mobile_no = None, institute_name = institute, employment_type = 1,
                work_starting_date = w_start_date, faculty_id = f_id, image = None, designation = designation_obj,student=std_id)

                institute_save.save()
                print('first step')
                # context = {'nationality': Nationality.objects.all()
                #     ,
                #            'institution': Institution.objects.all(),
                #            'designation': Designation.objects.all(),
                #            'program': Program.objects.all(),
                #            'div': Division.objects.all(),
                #            'dis': District.objects.all(),
                #            'thn': Thana.objects.all(),
                #            'sucsess': 'Your Registration Successful'
                #
                #            }

                # return render(request, 'admin/teacher_form.html', context)

                return redirect('/admin/bnmc_project/intuitionprofile/')



            else:
                print('not')
                if ins != '' and division != '' and district != '' and  thana != '' and national != '':
                    institute_save=IntuitionProfile(is_nurse=False,full_name_english=name,
                        father_name=f_name,
                        mother_name=m_name,
                        marital_status=matrtial,
                        sex=sex,
                        nationality=national_obj,
                        division=division_obj,
                        district=district_obj,
                        thana=thana_obj,
                        village=village,
                        email_address=email,
                        post_office=post_off,
                        postal_code=post_code,
                        date_of_birth=date_birth,students_mobile_no=no,institute_name=institute,employment_type=2,
                                                    license_number=license_number,
                        work_starting_date=w_start_date,faculty_id=f_id,image=str('/institute_profile/'+file),designation=designation_obj)

                    institute_save.save()


                    # context = {'nationality': Nationality.objects.all()
                    #     ,
                    #            'institution': Institution.objects.all(),
                    #            'designation': Designation.objects.all(),
                    #            'program': Program.objects.all(),
                    #            'div': Division.objects.all(),
                    #            'dis': District.objects.all(),
                    #            'thn': Thana.objects.all(),
                    #            'sucsess':'Your Registration Successful'
                    #
                    #            }

                    # return render(request, 'admin/teacher_form.html', context)

                    return redirect('/admin/bnmc_project/intuitionprofile/')
                    print('second step')
    context={ 'nationality':Nationality.objects.all()
              ,
              'institution':Institution.objects.all(),
              'designation':Designation.objects.all(),
              'program':Program.objects.all(),
              'div':Division.objects.all(),
              'dis':District.objects.all(),
              'thn':Thana.objects.all(),

              }

    return render(request,'admin/teacher_form.html',context)

def search_with_license_number(request):
    if request.method == 'POST':
        number=request.POST.get('number')
        program=request.POST.get('program')


        if number  and program:
            license_qr=LicenseHistory.objects.get(license_number=number,program=program)
            if license_qr:
                list_of_collections = []

                license_history_qr = LicenseHistory.objects.filter(license_receive_id=license_qr.license_receive_id)
                current_date = datetime.datetime.now().date()

                for i in license_history_qr:
                    if i.license_end_date:
                        expire_date=parse_date(i.license_end_date)

                        if current_date > expire_date:
                            list_of_collections.append('Expired')

                        else:
                            list_of_collections.append('Renewed')

                    else:
                        list_of_collections.append('None')


                context = {'qr': zip(license_history_qr,list_of_collections),
                           'info_student': license_history_qr[0],
                           'program_objs': Program.objects.all()}
                print(list_of_collections)
                return render(request, 'admin/license_number_search.html',
                              context)






    return render(request, 'admin/license_number_search.html', {'program_objs':Program.objects.all()})


def license_card_info(request,entry):
    qr_license=license_receive.objects.filter(entry_id__icontains=entry)[0]
    list_of_collections = []
    license_his_qr=LicenseHistory.objects.filter(license_receive_id=qr_license.id)

    current_date = datetime.datetime.now().date()

    for i in license_his_qr:
        expire_date = parse_date(i.license_end_date)

        if current_date > expire_date:
            list_of_collections.append('Expired')

        else:
            list_of_collections.append('Renewed')
    context = {'qr': zip(license_his_qr, list_of_collections),
               'info_student': license_his_qr[0],
    }

    return render(request,'admin/license_card_info.html',context)

def edit_final_center(request):
    center_id=request.POST.get('id_set')
    center_query=FinalExamCenterManage.objects.filter(id=center_id).first()
    if center_query:
        info = [True, center_query.id,center_query.exam.id,center_query.roll_start,center_query.roll_end,center_query.center.id]
        print(info)
    else:
        info=[False]
    data=json.dumps(info)
    return HttpResponse(data)

def report_of_center_for_final_exam(request,center_id):
    center=FinalExamCenterManage.objects.get(id=center_id)
    exam=ExaminationStudentRegistration.objects.filter(roll_number__range=(center.roll_start,center.roll_end),center=center.center,exam=center.exam).order_by('roll_number')
    get_program=ExaminationStudentRegistration.objects.filter(roll_number__range=(center.roll_start,center.roll_end),center=center.center,exam=center.exam).last()
    exam_subs=ExamSubject.objects.filter(program=get_program.program.id).order_by('id')
    double_calculation=len(exam_subs)
    context={

        'license':exam,
        'len':len(exam),
        'center':center,
        'range':range(double_calculation),
        'exam_subs':exam_subs,
        'max_len': double_calculation

    }
    return render(request, 'admin/center_report_for_final_exam.html',context)

def set_center(request):
    if request.POST:
        exam=request.POST.get("exam",None)
        start_role=request.POST.get("role_ranger_first",None)
        end_role=request.POST.get("role_ranger_snd",None)
        center=request.POST.get("center",None)
        hidden_id=request.POST.get("hidden_id",None)




        if exam and start_role and end_role and center:
            exam_students=ExaminationStudentRegistration.objects.filter(roll_number__range=(start_role,end_role),approved=True,exam__id=exam)
            for student in exam_students:
                student.center=Institution.objects.get(pk=center)
                student.save()

            final_exam_center= FinalExamCenterManage()

            final_exam_center.exam=Final_exam.objects.get(pk=exam)
            final_exam_center.center=Institution.objects.get(pk=center)
            final_exam_center.roll_start=start_role
            final_exam_center.roll_end=end_role
            final_exam_center.save()

        #
        #
        # if hidden_id:
        #     license_update_roll=license_registrations.objects.filter(rool_number__range=(start_role,end_role),approved=True,exam_title__id=exam)
        #     update_query=license_update_roll.update(centre=center,hall_name=hall,room_name=room_no)
        #     query = CenterManagement.objects.filter(id=hidden_id)
        #     update = query.update(exam=exam, roll_start=start_role, roll_end=end_role, center=center, hall_name=hall,
        #                           room_name=room_no)
        #
        #
        #

    var=FinalExamCenterManage.objects.all()
    revarse=var.order_by('-id')
    paginator = Paginator(revarse, 100)
    page = request.GET.get('page')
    paginate = paginator.get_page(page)
    centers_institution=Institution.objects.all()


    context={"institution_name":centers_institution,"exams":Final_exam.objects.all(),
             'var':paginate,



             }

    return render(request,'admin/set_center.html',context)

def changeStatus_exam(request):
    student_id = request.POST.get("stdId")
    permission_id = int(request.POST.get("permissionId").strip())
    # prmsn_id = Permission.objects.filter(id_no=permission_id)
    # permission_ids =Permission.objects.filter(id=id_no)re_id
    program_short_name = {'DCN': 600001,
                          'JM': 800001, 'CP': 900001, }
    student_reg = ExaminationStudentRegistration.objects.get(id=student_id)
    reg_no = 1

    permission_info = Permission.objects.get(id=permission_id)
    student_reg.status = permission_info
    last_permission = Permission.objects.order_by('display_order').last()
    is_valid = False

    if last_permission.id == permission_id and student_reg.approved == False:
        if program_short_name[student_reg.program.code]:
            reg_no = program_short_name[student_reg.program.code]
            print(type(reg_no))
        # student_reg.approve_by = request.user

        student_reg.approved = True
        while is_valid == False:
            # search_reg_no=student_reg.institution.institution_code+str(student_reg.session)+student_reg.program_title.code+str(reg_no)+DNSM
            auto_reg_no = ExaminationStudentRegistration.objects.filter(program__code=student_reg.program.code,
                                                                        roll_number=reg_no)

            if auto_reg_no:
                reg_no += 1

            else:
                is_valid = True
        student_reg_no = reg_no
        print(student_reg_no)
        # user = request.user.id



        student_reg.roll_number = student_reg_no
    student_reg.save()

    return HttpResponse(json.dumps(request.POST.get("stdId")))

def final_exam_wise_report(request):
    exam=Final_exam.objects.all()
    program=Program.objects.all()
    context={'exam':exam,
             'program':program
             }

    if request.method == 'POST':
        exam_id=request.POST['exam']
        program_id=request.POST['program']
        prog=Program.objects.get(id=program_id)
        ex=Final_exam.objects.get(id=exam_id)
        try:
            if exam_id !=0 and program !=0:
                exam_students=ExaminationStudentRegistration.objects.filter(exam=exam_id,program=program_id)
                if exam_students:

                    total=0
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Final_exam_wise_report_for_bnmc.xls"'

                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet('Users')

                    # Sheet header, first row
                    row_num = 0
                    no=0

                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True

                    columns = ['Student id', 'Student Name', 'Fathers name ','Institution name','Roll number']
                    subs=[]

                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)

                    # Sheet body, remaining rows
                    font_style = xlwt.XFStyle()
                    exam_='Exam Name: ',ex.name
                    prog_='Program Name: ',prog.title
                    ws._cell_overwrite_ok = True
                    subject_count=ExamSubject.objects.filter(program=program_id)
                    subjects=ExamSubject.objects.filter(program=program_id)



                    count_len = len(subject_count)
                    for i in subject_count:
                        subs.append(i)

                    start_five=5
                    for sub_col in subs:
                        start_five+=1
                        ws.write(0, start_five, 'subjects', font_style)
                    headers = [[] for i in range(0, count_len)]
                    all_subs=0

                    for i in exam_students:


                            o=0
                            l=0
                            all_subs+=len(i.subjects.all())
                            list_implement = -1
                            for subject_s in subjects:
                                list_implement += 1
                                is_stop = True
                                while is_stop:


                                    if subject_s in i.subjects.all():
                                        o += 1
                                        headers[list_implement].append(subject_s)
                                        is_stop = False
                                        break

                                    else:
                                        headers[list_implement].append('')
                                        is_stop = False
                                        break







                            row_num+=1
                            ws.write(row_num, 0, i.student_id, font_style)
                            ws.write(row_num, 1, i.last_name, font_style)
                            ws.write(row_num, 2, i.fathers_name, font_style)
                            ws.write(row_num, 3, i.institute.institution_name, font_style)
                            ws.write(row_num, 4, i.roll_number, font_style)
                    start_zero=-1
                    four=5
                    zero=0

                    for p in range(0,len(headers)):

                        start_zero+=1
                        four+=1
                        number_of_loop=0

                        for i in headers[start_zero]:


                            number_of_loop+=1
                            zero+=1


                            if i != '':

                                    ws.write(number_of_loop, four, str(i), font_style)
                            else:

                                ws.write(number_of_loop, four, '', font_style)






                    row_num+=1
                    ws.write(row_num, 5, exam_, font_style)
                    ws.write(row_num, 6, prog_, font_style)
                    # ws.write(row_num, 2, total_amount, font_style)
                    wb.save(response)
                    return response
        except ValueError as e:
            print(e)






    return render(request,'admin/final_exam_rep.html',context)


def signature_upload_principal(request):
    request_user_institution=request.user.staff_institute.values_list('id',flat=True)[0]
    institute_update=Institution.objects.get(id=request_user_institution)


    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
           myfile = request.FILES['file']
           fs = FileSystemStorage('media/pricipal_signature/')
           filename = fs.save(myfile.name, myfile)
           institute=request.user.staff_institute.values_list('id',flat=True)[0]
           institute_update=Institution.objects.get(id=institute)
           institute_update.principal_signature=filename
           institute_update.save()

    print(institute_update.principal_signature)
    return render (request,'admin/principal_signature.html',{'img':institute_update})

def unlock_history(request,id_history):
    if not request.user.is_superuser:
        lic_his_id = LicenseHistory.objects.get(id=id_history)
        license_receive_id = license_receive.objects.get(id=lic_his_id.license_receive_id.id)
        if lic_his_id:
            lic_his_id.lock=False

            lic_his_id.save()

        return redirect('/admin/bnmc_project/license_receive/' + '' + str(license_receive_id.id) + '' + '/change/',)

    else:
        lic_his_id = LicenseHistory.objects.get(id=id_history)
        license_receive_id = license_receive.objects.get(id=lic_his_id.license_receive_id.id)
        return redirect('/admin/bnmc_project/license_receive/' + '' + str(license_receive_id.id) + '' + '/change/', )

def print_license_card(request,license_history_card):
    lic_his_id=LicenseHistory.objects.get(id=license_history_card)
    if lic_his_id.lock == False:
        # re_history=re_new_history.objects.get(id=lic_his_id.renew_history.id)
        license_receive_id=license_receive.objects.get(id=lic_his_id.license_receive_id.id)
        lic_his_id.lock=False
        lic_his_id.save()
        if lic_his_id.card_serial is None or lic_his_id.card_serial == 0 or lic_his_id.card_serial== '':
            code={'BSCB':13002437,'DNSM':11012914,'DIM':12002131}
            is_found=False
            for key, value in code.items():

                if key == lic_his_id.program.code:
                    print(key, value)
                    card_no=value
                    while is_found == False:
                        last_no=LicenseHistory.objects.filter(card_serial=card_no,program__code=lic_his_id.program.code)
                        if last_no:
                            card_no+=1

                        else:
                            is_found = True

                    lic_his_id.card_serial=card_no
                    lic_his_id.save()
        full_license_registration_date=None
        if lic_his_id.license_registration_date:
            li_reg_date = parse_date(lic_his_id.license_registration_date)
            li_reg_year=str(li_reg_date.year)
            li_reg_month=str(li_reg_date.month)
            li_reg_day = str(li_reg_date.day)

            if len(li_reg_month) == 1:
                zero_month = '0'
            else:
                zero_month=''

            if len(li_reg_day) == 1:
                zero = '0'
            else:
                zero=''

            full_license_registration_date=zero+li_reg_day+'-'+zero_month+li_reg_month+'-'+li_reg_year
        full_license_start_date=None
        if lic_his_id.license_start_date:
            li_start_date = parse_date(lic_his_id.license_start_date)

            li_sta_year=str(li_start_date.year)
            li_sta_month=str(li_start_date.month)
            li_sta_day=str(li_start_date.day)

            if len(li_sta_month) == 1:
                zero_month = '0'

            else:
                zero_month=''

            if len(li_sta_day) == 1:
                zero = '0'

            else:
                zero=''
            full_license_start_date=zero+li_sta_day+'-'+zero_month+li_sta_month+'-'+li_sta_year

        full_license_end_date=None
        if lic_his_id.license_end_date:
            li_end_date = parse_date(lic_his_id.license_end_date)
            li_end_year = str(li_end_date.year)
            li_end_month = str(li_end_date.month)
            li_end_day = str(li_end_date.day)

            if len(li_end_month) == 1:
                zero_month = '0'
            else:
                zero_month=''

            if len(li_end_day) == 1:
                zero = '0'
            else:
                zero=''
            full_license_end_date=zero+li_end_day+'-'+zero_month+li_end_month+'-'+li_end_year
        print(lic_his_id.program.code,'code')
        context = {"licenses": lic_his_id,
                   'license_receive':license_receive_id,
                   'full_license_registration_date':full_license_registration_date,
                   'full_license_start_date':full_license_start_date,
                   'full_license_end_date':full_license_end_date
                   }
        return render(request, 'admin/regCard.html', context)

    else:
        license_receive_id = license_receive.objects.get(id=lic_his_id.license_receive_id.id)


        return redirect('/admin/bnmc_project/license_receive/'+''+str(license_receive_id.id)+''+'/change/',messages.error(request, "Error!"))



def institute_code_add(request):
    if request.method == "POST":
        pwd = os.path.dirname('')
        with open(pwd + 'bnmc_project/add_institute_code.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            list_=[]
            empty=[]
            for row in reader:
                code=row['subposition'].strip()
                second_code=row['pos_id'].strip()

                institute_find=Institution.objects.filter(institution_code=code)

                if institute_find:
                    list_.append(institute_find)
                    try:

                        institute_find.update(institution_second_code=second_code)

                    except:
                        pass



            print('student_reg',len(list_))
    return render(request,'admin/import_license_data.html')


def rnm_data(request):
    if request.POST:
        pwd = os.path.dirname(__file__)
        with open(pwd + '/bnc_rnm_info_.csv',encoding="ISO-8859-1") as f:
            reader = csv.DictReader(f, delimiter=',')
            i=0

            for row in reader:
                i+=1
                print(i)
                entry_id=row['entry_id']
                student_id=row['student_id']
                rnm_reg_no=row['rnm_reg_no']
                license_registration_date=row['rnm_reg_date']
                license_registration_fee=row['rnm_reg_fee']
                payment_method_name = row['payment_method'].strip()
                bank_draft_date=row['bankdraft_date']
                bank_draft_no=row['bankdraft_no']
                license_end_date=row['rnm_expire_date']
                employer_type=row['type_employer']
                employer_country=row['employer_country']
                institution_code=row['institute_name']
                course_type=row['course_type']
                admission_date=row['admission_date']
                course_start_date=row['course_start_date']
                course_completion_date=row['course_completion_date']
                registration_fee=row['registration_fee']
                first_name = ''
                last_name = row['full_name'].strip()
                registation_date = row['registration_date'].strip()
                fathers_name = row['father_name'].strip()
                mothers_name = row['mother_name'].strip()
                guardians_name = row['guardian_name'].strip()
                relation_with_guardians = row['guardian_relation'].strip()
                quotas_name = row['quota'].strip()
                nationality_name = row['natinality'].strip()
                date_of_birth = row['birth_date'].strip()
                choice_sex = row['sex'].strip()
                religions_name = row['religion'].strip()
                marital_status_name = row['marital_status'].strip()
                national_ID_No = row['national_id'].strip()
                passport_no = row['passport_no'].strip()
                students_mobile_no = row['mobile'].strip()
                email_address = row['email'].strip()
                division_name = row['per_division'].strip()
                district_name = row['per_district'].strip()
                thana_name = row['per_thana'].strip()
                village = row['per_village'].strip()
                post_office = row['per_postoffice'].strip()
                postal_code = row['per_postalcode'].strip()
                division_snd_name = row['pre_division'].strip()
                district_snd_name = row['pre_district'].strip()
                thana_snd_name = row['pre_thana'].strip()
                village_snd = row['pre_village'].strip()
                post_office_snd = row['pre_postoffice'].strip()
                postal_code_snd = row['pre_postalcode'].strip()
                institution_name = row['institute_name'].strip()
                create_on=row['added_on']
                card_serial=row['card_serial']
                month_info=row['month_info']
                image_location = "media/" + str(row['filename'].strip())
                signature = "signature_student/" + str(row['signature'].strip())

                date_of_registration = row['admission_date'].strip()
                program_starting_date = row['course_start_date'].strip()
                program_title = row['course_type'].strip()

                registration_fees = row['registration_fee'].strip()
                program_completion_date = row['course_completion_date'].strip()
                session_value = row['session'].strip()
                program_code = row['course_code'].strip()
                institution_code = row['college_code'].strip()
                catagory = row['gcode'].strip()
                type = row['type_code'].strip()
                program_length = row['course_length'].strip()
                program_fee = row['registration_fee'].strip()
                program_category_name = row['cgcode'].strip()

                # ssc_edutype = row['ssc_edutype'].strip()
                # hsc_edutype = row['hsc_edutype'].strip()
                # diploma_edutype = row['diploma_edutype'].strip()
                # bsc_edutype = row['bsc_edutype'].strip()
                # msc_edutype = row['msc_edutype'].strip()
                # doc_edutype = row['doc_edutype'].strip()
                bank_draft_no = row['bankdraft_no'].strip()
                bank_draft_date_str = row['bankdraft_date'].strip()
                approved = False
                student_permission = Permission.objects.order_by('display_order').last()
                institute=None
                if institution_name:
                    ins = Institution.objects.filter(institution_second_code=institution_name)
                    if ins:
                        institute = ins[0]



                program=None
                if course_type:
                    pro = Program.objects.filter(second_code=course_type)
                    if pro:
                        program=pro[0]




                quota = None
                if quotas_name:
                    quota = Quota.objects.filter(quota_name__icontains=quotas_name)

                    if quota:
                        quota = quota[0]
                    else:
                        quota = Quota(quota_name=quotas_name)
                        quota.save()

                nationality = Nationality.objects.filter(nationality_name__icontains=nationality_name)
                if nationality:
                    nationality = nationality[0]
                else:
                    nationality = Nationality(nationality_name=nationality_name)
                    nationality.save()

                relation_to_guardian = Relation_to_guardians.objects.filter(
                    relation__icontains=relation_with_guardians)
                if relation_to_guardian:
                    relation_to_guardian = relation_to_guardian[0]
                else:
                    relation_to_guardian = Relation_to_guardians(relation=relation_with_guardians)
                    relation_to_guardian.save()
                sex = ""
                religion = ""
                marital_status = ""
                payment_method = ""
                employer_type=''
                if employer_type == 'Private':
                    employer_type='1'
                if employer_type == 'Public':
                    employer_type='2'

                if choice_sex == 'FEMALE':
                    sex = '2'
                if choice_sex == 'MALE':
                    sex = '1'
                try:
                    date_of_birth = str(date_of_birth.replace('/','-'))
                except ValueError as e:
                    # print("error in date of birth " + registation_no + " error is " + str(e))
                    date_of_birth = 0


                # try:
                #     license_registration_date.replace('/', '-')
                # except ValueError as e:
                #     # print("error in date of registration "+registation_no+" error is "+str(e))
                #
                #     license_registration_date.replace('/','-')
                #     print(license_registration_date, 'dddddd')

                try:
                    bank_draft_date = datetime.datetime.strptime(bank_draft_date, "%d-%m-%Y").date()
                except ValueError as e:
                    # print("error in program starting date "+registation_no+" error is "+str(e))
                    bank_draft_date = None

                # try:
                #     license_end_date.replace('/', '-')license_registration_date.replace('/', '-')
                # except ValueError as e:
                #     # print("program completion date "+registation_no+" error is "+str(e))
                #
                #     license_end_date.replace('/','-')
                #     print(license_end_date,'eeee')

                try:
                    admission_date = datetime.datetime.strptime(admission_date, "%d-%m-%Y").date()
                except:
                    admission_date = None


                try:
                    course_start_date = datetime.datetime.strptime(course_start_date, "%d-%m-%Y").date()
                except:
                    course_start_date = None

                try:
                    course_completion_date = datetime.datetime.strptime(course_completion_date, "%d-%m-%Y").date()
                except:
                    course_completion_date = None


                try:
                    create_on = datetime.datetime.strptime(create_on, "%d-%m-%Y").date()
                except:
                    create_on = None


                try:
                    registation_date = datetime.datetime.strptime(registation_date, "%d-%m-%Y").date()
                except:
                    registation_date = None

                try:
                    month_info = datetime.datetime.strptime(month_info, "%d-%m-%Y").date()
                except:
                    month_info = None


                if religions_name == "Islam":
                    religion = '1'
                if religions_name == "Hindu":
                    religion = '2'
                if religions_name == "Buddhist":
                    religion = '3'
                if religions_name == "Christian":
                    religion = '4'
                if religions_name == "Others":
                    religion = '5'

                if marital_status_name == "Single":
                    marital_status = '1'
                if marital_status_name == "Married":
                    marital_status = '2'
                if marital_status_name == "Widow":
                    marital_status = '3'
                if marital_status_name == "Divorced":
                    marital_status = '4'
                if marital_status_name == "Seperated":
                    marital_status = '5'

                if payment_method_name == "Cash":
                    payment_method = '2'
                if payment_method_name == "Bank Draft":
                    payment_method = '1'

                division = Division.objects.filter(name__icontains=division_name)
                if not division:



                    division=Division(name=str(division_name))
                    division.save()

                else:
                    division = division[0]

                district = District.objects.filter(name__icontains=district_name)
                if not district:
                    district=District(name=district_name,division=division)
                    district.save()
                else:
                    district = district[0]

                thana = Thana.objects.filter(name__icontains=thana_name)
                if not thana:
                    thana=Thana(name=thana_name,district=district)
                    thana.save()
                    # if not thana_name:
                    #     thana = test_thana
                        # print("test thana has created in "+str(registation_no)+" and thana name is "+thana_name)

                else:
                    thana = thana[0]

                division_snd = Division.objects.filter(name__icontains=division_snd_name)
                if not division_snd:
                    division_snd=division_snd(name=division_snd_name)
                    division_snd.save()
                else:
                    division_snd = division_snd[0]

                district_snd = District.objects.filter(name__icontains=district_snd_name)
                if not district_snd:
                    district_snd=District(name=district_snd_name,division=division_snd)
                    district_snd.save()
                else:
                    district_snd = district_snd[0]

                thana_snd = Thana.objects.filter(name__icontains=thana_snd_name)
                if not thana_snd:
                    # if not thana_snd_name:
                    #     thana_snd = test_thana
                    #     # print("2ND test thana has created in "+str(registation_no)+" and thana name is "+thana_snd_name)
                    # else:
                    #     thana_snd = Thana(name=thana_snd_name, district=district_snd)
                    #     thana_snd.save()
                    thana_snd=Thana(name=thana_snd_name,district=district_snd)

                    thana_snd.save()

                else:
                    thana_snd = thana_snd[0]



                    try:

                        try:

                            end_date = str(license_end_date.replace('/', '-'))
                            start_date = str(license_registration_date.replace('/', '-'))

                            final_start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
                            final_end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

                            print(final_start_date, final_end_date)

                        except:
                            final_start_date = 0
                            final_end_date = 0

                        stu=Student(last_name=str(last_name),nationality=nationality,date_of_birth=date_of_birth,national_ID_No=national_ID_No,
                                                  division=division,district=district,thana=thana,village=village,post_office=post_office,postal_code=postal_code,
                                                  sex=sex,fathers_name=fathers_name,mothers_name=mothers_name,
                                                  guardians_name=guardians_name,relation_to_guardians=relation_to_guardian,religions=religions_name,marital_status=marital_status,
                                                  passport_no=passport_no,students_mobile_no=students_mobile_no,email_address=email_address,division_snd=division_snd,district_snd=district_snd,
                                                  thana_snd=thana_snd,village_snd=village_snd,postal_code_snd=postal_code_snd,post_office_snd=post_office_snd,quota=quota,
                                                  institution=institute,
                                                 )
                        stu.save()
                        if stu:


                            lic=license_receive(last_name=last_name,nationality=nationality,date_of_birth=date_of_birth,national_ID_No=national_ID_No,
                                                      division=division,district=district,thana=thana,village=village,post_office=post_office,postal_code=postal_code,
                                                      approved=True,status=student_permission,
                                                      is_old_data=True,license_registration_fee=license_registration_fee,
                                                      payment_method=payment_method,bank_draft_no=bank_draft_no,registration_fee=registration_fee,bank_draft_date=bank_draft_date,
                                                      employer_type=employer_type,employer_country=employer_country,sex=sex,fathers_name=fathers_name,mothers_name=mothers_name,
                                                      guardians_name=guardians_name,relation_to_guardians=relation_to_guardian,religions=religion,marital_status=marital_status,
                                                      passport_no=passport_no,students_mobile_no=students_mobile_no,email_address=email_address,division_snd=division_snd,district_snd=district_snd,
                                                      thana_snd=thana_snd,village_snd=village_snd,postal_code_snd=postal_code_snd,post_office_snd=post_office_snd,quota=quota,
                                                      image=image_location,create_on=create_on,month_info=month_info,signature=signature,students=stu,program=program,institution=institute,entry_id=entry_id




                                                      )
                            lic.save()
                            print(lic.program)





                            if lic:

                                license_history=LicenseHistory(program=program,institution=institute,student_id=stu,license_number=float(rnm_reg_no),registration_no=0,license_registration_date=final_start_date,
                                                               license_start_date=final_start_date,
                                                               license_end_date=final_end_date,license_receive_id=lic,lock=False,card_serial=card_serial
                                                               )

                                license_history.save()



                    except Exception as E:
                        print(E)







    return render(request,'admin/import_license_data.html')




import xlwt





def get_info_moneyrecipte(request):
    number=request.POST.get('num')
    pro=request.POST.get('prog')

    if number !=0 and pro !=0:
        student_reg=Student_Registration.objects.filter(program_title_id=pro,registration_no=number)
        print('aaaa','student_reg')
        if student_reg:
            student_reg=student_reg[0]
            if student_reg:
                student_=Student.objects.get(id=student_reg.students.id)
                student_data=[True,student_.id,student_.last_name,student_.fathers_name]

            else:
                student_data=[False]
            data=json.dumps(student_data)
            return HttpResponse(data)


def get_info_moneyrecipte_li(request):
    number=request.POST.get('num')
    pro=request.POST.get('prog')

    if number !=0 and pro !=0:
        lic_reg=license_registrations.objects.filter(program_id=pro,rool_number=number)
        if lic_reg:
            lic_reg=lic_reg[0]
            if lic_reg:
                student_=Student_Registration.objects.get(id=lic_reg.student_registration.id)
                if student_:
                    stu=Student.objects.get(id=student_.students.id)
                    print('ff',stu)
                    if stu:
                        student_data=[True,stu.id,stu.last_name,stu.fathers_name]
                        data=json.dumps(student_data)
                        return HttpResponse(data)



def exam_wise_report(request):
    exam=Exam.objects.all()
    program=Program.objects.all()
    context={'exam':exam,
             'program':program
             }

    if request.method == 'POST':
        exam_id=request.POST['exam']
        program_id=request.POST['program']
        prog=Program.objects.get(id=program_id)
        ex=Exam.objects.get(id=exam_id)
        try:
            if exam_id !=0 and program !=0:
                license_queryset=license_registrations.objects.filter(exam_title=exam_id,program=program_id)
                institition=Institution.objects.all()
                if institition:
                    institution_list=[]
                    number_of_student__for_institution=[]
                    total=0
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="exam_wise_report_for_bnmc.xls"'

                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet('Users')

                    # Sheet header, first row
                    row_num = 0
                    no=0

                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True

                    columns = ['SN', 'Collage Name', 'Examinee']

                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)

                    # Sheet body, remaining rows
                    font_style = xlwt.XFStyle()
                    exam_='Exam Name: ',ex.exam_name
                    prog_='Program Name: ',prog.title
                    ws._cell_overwrite_ok = True
                    for i in institition:
                        institution_wise_examinee=license_queryset.filter(institution=i.id)
                        total_student=len(institution_wise_examinee)
                        if institution_wise_examinee:
                            institution_list.append(i.institution_name)
                            number_of_student__for_institution.append(total_student)


                    for i,total_number in zip(institution_list,number_of_student__for_institution):
                        row_num += 1
                        no+=1
                        total+=total_number

                        ws.write(row_num, 1, i, font_style)
                        ws.write(row_num, 0, no, font_style)
                        ws.write(row_num, 2, total_number, font_style)
                    row_num+=1
                    total_amount='Total:',str(total)
                    ws.write(row_num, 3, exam_, font_style)
                    ws.write(row_num, 4, prog_, font_style)
                    ws.write(row_num, 2, total_amount, font_style)
                    wb.save(response)
                    return response
        except ValueError as e:
            print(e)






    return render(request,'admin/examWiseReport.html',context)


def report_of_center(request,center_id):
    center=CenterManagement.objects.get(id=center_id)
    print(center.roll_start)
    license=license_registrations.objects.filter(rool_number__range=(center.roll_start,center.roll_end),centre=center.center,exam_title=center.exam).order_by('rool_number')
    print(license)

    context={

        'license':license,
        'len':len(license),
        'center':center

    }
    return render(request, 'admin/center_report.html',context)

def bad_request(request):
    response = render_to_response(
        '400.html',
        context_instance=RequestContext(request)
        )


    response.status_code = 400

    return response


def get_license_rec_stu(request,licenserec_id):
    license_id=license_registrations.objects.get(pk=licenserec_id)
    stu_status=Student_Registration.objects.get(id=license_id.student_registration.id)
    education_qulification=EducationQualification.objects.filter(students=stu_status.students.id)
    print(stu_status.id)
    context={'license_id':stu_status,
             'education_qulification':education_qulification,
             'reg':license_id
             }
    return render(request,'admin/license_form.html',context)


#def get_license_rec_stu(request,licenserec_id):
#    license_id=license_receive.objects.get(pk=licenserec_id)
#    print(license_id.license_registrations_refference,"refferences")
#    education_qulification=EducationQualification.objects.filter(student=license_id.license_registrations_refference.student_registration)
#    context={'license_id':license_id.license_registrations_refference.student_registration,
#             'education_qulification':education_qulification
#             }
    #return render(request,'admin/license_form.html',context)


class rest(FlatMultipleModelAPIView):
    querylist = [
        {'queryset': Student_Registration.objects.filter(id=4000), 'serializer_class': Student_info},

        {'queryset': EducationQualification.objects.filter(id=4000), 'serializer_class': Education_info},
    ]






class get_parameter(generics.ListAPIView):
    serializer_class = PostSerializer
    def get_queryset(self):
        queryset = Post.objects.all()
        post_id = self.request.query_params.get('post_id', None)
        if post_id is not None:
            queryset = queryset.filter(id=post_id)
        return queryset

class get_slide(generics.ListAPIView):
    serializer_class = sliderSerializer

    def get_queryset(self):
        queryset = Slider.objects.all()
        return queryset


class get_all_post(generics.ListAPIView):
    serializer_class = PostSerializer
    def get_queryset(self):
        posts=Post.objects.all()

        return posts




def license_exam_data(request):
    form_submit=request.GET.get('submit')

    if form_submit:
        reg_no=request.GET.get('registration_no')

        if reg_no:
            queryset=Student_Registration.objects.filter(registration_no=reg_no)

            print(queryset)
        queryset

    return HttpResponse("hi")

def print_license(request,license_id):
    std_license= license_registrations.objects.get(pk=license_id)
    return render(request,'admin/print_admit_card.html',{"std_license":std_license})


def log(request):
    log_list = LogEntry.objects.all()
    form_submit=request.GET.get('submit')

    if form_submit:
        user_name=request.GET.get('user_name')
        start_date=request.GET.get('start_date')
        end_date=request.GET.get('end_date')

        if user_name:
            queryset=log_list.filter(user_id=user_name)
        if start_date and end_date:
            queryset=log_list.filter(action_time__range=(start_date,end_date))
        queryset
        print(queryset)



        paginator = Paginator(queryset, 20)
        page = request.GET.get('page')
        contacts = paginator.get_page(page)


    else:
        log_list = LogEntry.objects.all()
        paginator = Paginator(log_list, 25)
        page = request.GET.get('page')
        contacts = paginator.get_page(page)


    cotext = {'contacts': contacts,
              'acivity_users': User.objects.all()
              }

    return render(request,'admin/activity_log.html',cotext)

def approve_student(request):

    return render(request,'admin/approve_student.html')

def changeExamStatus(request):
    student_id = request.POST.get("stdId")
    permission_id = request.POST.get("permissionId")

    license_rec=license_receive.objects.get(id=student_id)
    per=Permission.objects.get(id=permission_id)
    license_rec.status=per
    last_per=Permission.objects.order_by('display_order').last()
    is_run=False
    license_no=20

    if last_per.id == int(permission_id) and license_rec.approved == False:
        print('last')

        license_rec.approved=True

        while is_run == False:
            license_number_set=license_receive.objects.filter(license_number=license_no)
            if license_number_set:
                license_no+=1
            else:
                is_run = True
        lic_no=license_no
        license_rec.license_number=lic_no
    license_rec.save()
    print(student_id,permission_id)
    return HttpResponse (json.dumps(request.POST.get("stdId")))



def registration_step(request):
    student_id=request.POST.get("stdId")
    permission_id=int(request.POST.get("permissionId").strip())
    # prmsn_id = Permission.objects.filter(id_no=permission_id)
    # permission_ids =Permission.objects.filter(id=id_no)re_id
    program_short_name={'DNSM':71912,'BSCB':16476,'DIM':4632,'CSBA':12350,'DCN':1750,'DPN':1634,'BNPB':15502,'JM':3064,'FWB':8130,'CP':4453,'BSCPHN':15464}
    student_reg=Student_Registration.objects.get(id=student_id)
    reg_no = 1

    permission_info=Permission.objects.get(id=permission_id)
    student_reg.status=permission_info
    last_permission=Permission.objects.order_by('display_order').last()
    is_valid=False

    print(str(last_permission.id )+" "+str(permission_id))
    if last_permission.id ==permission_id and student_reg.approved==False:
        print("last permission")
        if program_short_name[student_reg.program_title.code]:
            reg_no=program_short_name[student_reg.program_title.code]
        student_reg.approve_by=request.user

        student_reg.approved = True
        while  is_valid==False:
            print("curent reg no is "+str(reg_no))
            #search_reg_no=student_reg.institution.institution_code+str(student_reg.session)+student_reg.program_title.code+str(reg_no)+DNSM
            auto_reg_no = Student_Registration.objects.filter(program_title__code=student_reg.program_title.code,registration_no=reg_no)
            
            if auto_reg_no:
                print(str(reg_no)+" exist")
                reg_no+=1

            else:
                is_valid=True
        student_reg_no=reg_no
        user=request.user.id
        if student_reg.students:
            student_id=1
            if not student_reg.students.has_student_id:
                end_loop=False
                while end_loop == False:
                    search_student=Student.objects.filter(registration_no=str(student_id))
                    if search_student:
                        student_id+=1
                    else:
                        end_loop=True
                student_reg.students.registration_no=str(student_id)
                student_reg.students.has_student_id=True
                student_reg.students.save()
            student_reg.students.registration_no=reg_no
        student_reg.registration_no=student_reg_no
    student_reg.save()


    return HttpResponse(json.dumps(request.POST.get("stdId")))



def registration_step_li(request):
    student_id=request.POST.get("stdId")
    permission_id=int(request.POST.get("permissionId").strip())
    program_start_code={'DNSM':100001 ,'DIM':200001 ,'BSCB':300001,
                        'BNPB':400001,'DPN':500001,'DCN':600001,
                        'FWV':700001,'JM':800001,'CP':900001,'CSBA':110001
                        }
    student_reg=license_registrations.objects.get(id=student_id)
    reg_no = student_reg.registration_no
    student_reg_no=0
    permission_info=Permission.objects.get(id=permission_id)
    student_reg.status=permission_info
    last_permission=Permission.objects.order_by('display_order').last()
    is_valid=False
    if last_permission.id ==permission_id and student_reg.approved==False:
        if program_start_code.get(student_reg.program.code,None):
            student_reg_no=program_start_code[student_reg.program.code]
        student_reg.approved=True
        while  is_valid==False:
            auto_reg_no = license_registrations.objects.filter(program__code=student_reg.program.code,rool_number=student_reg_no)
            if auto_reg_no:
                student_reg_no+=1
            else:
                is_valid=True

    student_reg.rool_number=student_reg_no
    student_reg.save()
    return HttpResponse(json.dumps(request.POST.get("stdId")))

def registation_panel(request):
    query_str=request.GET.get('type')
    context={"type":query_str}
    return render(request, "admin/program_reg_link.html",context)

# def callablefunction():
#     no = Student_Registration.objects.count()
#     return no + 1


def upload_file(request):
    context={"exams":Exam.objects.filter(date_active=True),

             'exam':Exam.objects.all(),
             }

    if request.method == 'POST':
        if request.POST['exams'] and  request.FILES['file']:
            print(request.POST['exams'])
            upload_file=request.FILES['file']
            exam_id=request.POST['exams']
            fs = FileSystemStorage()
            filename = fs.save(upload_file.name, upload_file)
            uploaded_file_url = fs.url(filename)
            pwd = os.path.dirname('')
            changes_datas=[]
            with open(pwd + 'bnmc_project/'+uploaded_file_url, encoding="utf8") as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    registration= row['no'].strip()
                    pass_mark= row['pass_mark'].strip()
                    try:
                        reg_no = license_registrations.objects.filter(rool_number=int(registration),exam_title__id=exam_id)
                        if reg_no:
                            pass_mark_update=reg_no.update(pass_mark = pass_mark)
                            changes_datas.append(reg_no[0])
                        else:
                            pass
                    except:
                        print('Non-numeric data found in the file.')
                context["data_lists"]= changes_datas
                print(changes_datas)
    return render(request,'admin/upload_file.html',context)

# def uploaded_file_save(file, filename):
#     if not os.path.exists('upload/'):
#         os.mkdir('upload/')
#
#     with open('upload/' + filename, 'wb+') as destination:
#         pwd = os.path.dirname('upload/')
#         with open(pwd + '/'+filename, encoding="utf8") as f:
#             reader = csv.DictReader(f, delimiter=',')
#             for p in reader:
#                 print(p)



def program_show(request):
    query=request.GET.get('program_text')
    context={"name":query}
    return render(request, "admin/bnmc_project/student_registration/change_list.html",context)

def get_registation_student_info(request):
    license_number=request.POST.get("registation_number")
    program_id=request.POST.get("program_id")
    license_info=LicenseHistory.objects.filter(license_number=license_number,program=int(program_id))
    if license_info:
        info=[True,license_info[0].license_receive_id.id]

    else:
        info=[False]
    data = json.dumps(info)
    return HttpResponse(data)



def get_registation_student_license(request):
    registation_number=request.POST.get("registation_number")
    student_info=Student_Registration.objects.filter(registration_no=registation_number).first()
    if student_info:
        info = [True,student_info.registration_no, student_info.last_name,student_info.fathers_name,student_info.mothers_name,student_info.students_mobile_no,
                student_info.sex,student_info.religions,student_info.nationality.id,student_info.division.id,student_info.district.id,student_info.thana.id,
                student_info.village,student_info.post_office,student_info.postal_code,str(student_info.image),str(student_info.image)
            ]


    else:
        info=[False]
    data = json.dumps(info)
    return HttpResponse(data)

def address(request):
    parmanent_address = request.POST.get("boolian")
    present_address = Student.objects.filter(same_address=parmanent_address).first()
    if present_address:
        address=[True,present_address.division]

    else:
        address=[False]

    data = json.dumps(address)
    return HttpResponse ("sucsess");



def all_student(request):
    is_submited = request.GET.get("search_filter_stu")
    
    # selected_institute = request.user.staff_institute.values_list('id')
    if is_submited:
        students = Student_Registration.objects.filter(institution__id__in=request.user.staff_institute.values_list('id'))
        prog_cat = request.GET.get("program_category")
        reg_no = request.GET.get("registationNo")
        ins_type = request.GET.get("ins_type")
        prog_type = request.GET.get("progmType")
        ins_cat = request.GET.get("ins_cat")
        session = request.GET.get("session")
        ins_name = request.GET.get("ins_name")
        if prog_cat and  prog_cat !="0":
            print("prog_cat "+prog_cat)
            students=students.filter(program_title__category__id=int(prog_cat))
            print(students)
        if ins_type and ins_type !="0":
            students=students.filter(institution__type__id=int(ins_type))

        if prog_type and prog_type !="0":
            students=students.filter(program_title__id=int(prog_type))
        if ins_cat and ins_cat !="0":
            students=students.filter(institution__catagory__id=int(ins_cat))
        if session and session !="0":
            print("session" +session)
            students=students.filter(session__id=int(session))

        if reg_no and reg_no.strip():
            print("reg" + reg_no)
            students=students.filter(registration_no=reg_no)
        if ins_name and ins_name !="0":
            print("ins_name" + ins_name)
            students=students.filter(institution__id=ins_name)
        paginator = Paginator(students, 20)
        page = request.GET.get('page')
        contacts = paginator.get_page(page)





    else:
        print(request.user.staff_institute.values_list('id'))
        students=Student_Registration.objects.filter(institution__id__in=request.user.staff_institute.values_list('id'))
        paginator = Paginator(students, 20)
        page = request.GET.get('page')
        contacts = paginator.get_page(page)

    context={'contacts':contacts,
             'progrm_cat':ProgramCatagory.objects.all(),
             'program':Program.objects.all(),
             'InstituteCatagory':InstituteCatagory.objects.all(),
             'Session':Session.objects.all(),
             'InstituteType':InstituteType.objects.all(),
             'ins_name':Institution.objects.all()
             }

    return render(request,'admin/search_list.html',context)
# def pegination(request):
#     student_list = Student_Registration.objects.all()
#     page = request.GET.get('page', 1)
#
#     paginator = Paginator(student_list, 10)
#     try:
#         users = paginator.page(page)
#     except PageNotAnInteger:
#         users = paginator.page(1)
#     except EmptyPage:
#         users = paginator.page(paginator.num_pages)
#
#     return render(request, 'admin/search_list.html', { 'users': users })


def info(request,student_id):
    student = Student_Registration.objects.filter(pk=student_id)
    education_qu=EducationQualification.objects.filter(student=student[0])
    context = {'student_registration': student,
               'education_qu':education_qu
               }
    return render(request,'admin/student_info.html',context)

def sort_info(request):
    students = Student_Registration.objects.all()
    context = {'student_registration': students,
               }
    return render(request,'admin/student_info_view.html',context)

def search_village(request):
    search_key=request.POST.get("search_key").strip()
    village_list=[]
    print(search_key)
    villages= Student.objects.filter(village__icontains=search_key).distinct("village")
    if villages:
        for v in villages:
            village_list.append(v.village)
    data = json.dumps(village_list)
    print(data)
    return HttpResponse (data)



def search_place(request):
    search_key=request.POST.get("search_key").strip()
    place_list=[]
    places= WorkingDetails.objects.filter(place__icontains=search_key).distinct("place")
    if places:
        for p in places:
            place_list.append(p.place)
    data = json.dumps(place_list)
    print(data)
    return HttpResponse (data)


def search_traning(request):
    search_key=request.POST.get("search_key").strip()
    place_list_=[]
    places= TrainingDetails.objects.filter(training_place__icontains=search_key).distinct("training_place")
    if places:
        for p in places:
            place_list_.append(p.training_place)
    data = json.dumps(place_list_)
    print(data)
    return HttpResponse (data)


def search_post_office(request):
    search_key=request.POST.get("search_key").strip()
    Post_office_list=[]
    print(search_key)
    post_offices= Student.objects.filter(post_office__icontains=search_key).distinct("post_office")
    if post_offices:
        for v in post_offices:
            Post_office_list.append(v.post_office)
    data = json.dumps(Post_office_list)
    return HttpResponse (data)

def search_snd_village(request):
    search_key=request.POST.get("search_key").strip()
    snd_village_list=[]
    snd_villages= Student.objects.filter(village_snd__icontains=search_key).distinct("village_snd")
    if snd_villages:
        for v in snd_villages:
            snd_village_list.append(v.village_snd)
    data = json.dumps(snd_village_list)
    return HttpResponse (data)

def search_snd_post_office(request):
    search_key=request.POST.get("search_key").strip()
    snd_Post_office_list=[]
    snd_post_offices= Student.objects.filter(post_office_snd__icontains=search_key).distinct("post_office_snd")
    if snd_post_offices:
        for v in snd_post_offices:
            snd_Post_office_list.append(v.post_office_snd)
    data = json.dumps(snd_Post_office_list)
    print(data)
    return HttpResponse (data)

def get_program_info(request):
    program_id=request.GET.get("program")
    context = [False]
    if program_id:
        program = Program.objects.filter(id=program_id)
        if program:
            context=[True,program[0].session.session,float(program[0].duration.duration)]
    data = json.dumps(context)
    return HttpResponse(data)

def Search_student(request):
    all_stu= Student_Registration.objects.all()
    RequestConfig(request, paginate={'per_page': 25}).configure(table)
    prog_cat=request.GET.get("program_category")
    reg_no = request.GET.get("registationNo")
    ins_type=request.GET.get("ins_type")
    prog_type=request.GET.get("progmType")
    ins_cat=request.GET.get("ins_cat")
    session=request.GET.get("session")
    ins_name=request.GET.get("ins_name")
    print(query)
    data=False
    if query:
        data=True
        all_student = all_stu.objects.filter(
            # Q(institution__institution_name__icontains=query)|
            Q(registration_no__icontains=query)
        )

        context={'data':data,
                 'all_stu':all_student

                 }
    return context

def education_qualification(request):
    context={'education':EducationQualification.objects.all()}
    return  render(request,'admin/student_registration/change_form.html',context)

def send_notification(request):
    return render(request,'admin/bnmc.html')




months = ['JAN', 'JANUARY', 'FEB', 'FEBRUARY', 'MAR', 'MARCH', 'APRIL', 'MAY', 'JUN', 'JUNE', 'JUL', 'JULY', 'AUG',
          'AUGUST', 'SEPT', 'SEP', 'SEPTEMBER', 'OCT', 'OCTOBER', 'NOV', 'NOVEMBER', 'DEC', 'DECEMBER']
change_month = ['01', '01', '02', '02', '03', '03', '04', '05', '06', '06', '07', '07', '08', '08', '09', '09', '09',
                '10', '10', '11', '11', '12', '12']

years = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006',
         '2005', '2004', '2003', '2002', '2001', '2000', '16', '15', '14', '13']
change_year = ['19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '09', '08', '07', '06', '05', '04', '03',
               '02', '01', '00', '16', '15', '14', '13']


def add_student_info(request):
    if request.POST:
        pwd = os.path.dirname(__file__)
        with open(pwd + '/missing_student_list.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            view_row = 0
            saved_row = 0
            exist_student = 0

            approved_permission = Permission.objects.filter(permission_name="Approved BNMC")
            if approved_permission:
                approved_permission = approved_permission[0]
            else:
                approved_permission = Permission(permission_name="Approved BNMC", id_no=5, display_order=4)
                approved_permission.save()

            draft_permissio = Permission.objects.filter(permission_name="Draft")
            if draft_permissio:
                draft_permissio = draft_permissio[0]
            else:
                draft_permissio = Permission(permission_name="Draft", id_no=1, display_order=0)
                draft_permissio.save()

            test_qualification = Qualification.objects.filter(minimum_qualification="Test qulification")
            if test_qualification:
                test_qualification = test_qualification[0]
            else:
                test_qualification = Qualification(minimum_qualification="Test qulification")
                test_qualification.save()

            test_divisions = Division.objects.filter(name="Test Division")
            if test_divisions:
                test_divisions = test_divisions[0]
            else:
                test_divisions = Division(name="Test Division")
                test_divisions.save()

            test_district = District.objects.filter(name="Test District")
            if test_district:
                test_district = test_district[0]
            else:
                test_district = District(name="Test District", division=test_divisions)
                test_district.save()

            test_thana = Thana.objects.filter(name="Test Thana")
            if test_thana:
                test_thana = test_thana[0]
            else:
                test_thana = Thana(name="Test Thana", district=test_district)
                test_thana.save()

                # is_student_exist=Student_Registration.objects.filter(registration_no=registation_no)
                # if  is_student_exist:
                #    exist_student=exist_student+1
                #    print(registation_no+" has exist and exist student number is"+str(exist_student))
                # if not is_student_exist:

            for row in reader:
                view_row = view_row + 1
                id = row['id'].strip()
                registation_no = row['student_id'].strip()
                # This registation id is student ID
                student_id = row['student_id'].strip()

                try:
                    # first_name = row['name_bangla'].strip()
                    first_name = ''
                    last_name = row['full_name'].strip()
                    registation_date = row['registration_date'].strip()
                    fathers_name = row['father_name'].strip()
                    mothers_name = row['mother_name'].strip()
                    guardians_name = row['guardian_name'].strip()
                    relation_with_guardians = row['guardian_relation'].strip()
                    quotas_name = row['quota'].strip()
                    nationality_name = row['natinality'].strip()
                    date_of_birth = row['birth_date'].strip()
                    choice_sex = row['sex'].strip()
                    religions_name = row['religion'].strip()
                    marital_status_name = row['marital_status'].strip()
                    national_ID_No = row['national_id'].strip()
                    passport_no = row['passport_no'].strip()
                    students_mobile_no = row['mobile'].strip()
                    email_address = row['email'].strip()
                    division_name = row['per_division'].strip()
                    district_name = row['per_district'].strip()
                    thana_name = row['per_thana'].strip()
                    village = row['per_village'].strip()
                    post_office = row['per_postoffice'].strip()
                    postal_code = row['per_postalcode'].strip()
                    division_snd_name = row['pre_division'].strip()
                    district_snd_name = row['pre_district'].strip()
                    thana_snd_name = row['pre_thana'].strip()
                    village_snd = row['pre_village'].strip()
                    post_office_snd = row['pre_postoffice'].strip()
                    postal_code_snd = row['pre_postalcode'].strip()
                    institution_name = row['institute_name'].strip()
                    date_of_registration = row['admission_date'].strip()
                    program_starting_date = row['course_start_date'].strip()
                    program_title = row['course_type'].strip()
                    payment_method_name = row['payment_method'].strip()
                    registration_fees = row['registration_fee'].strip()
                    program_completion_date = row['course_completion_date'].strip()
                    session_value = row['session'].strip()
                    image_location = "media/" + str(row['filename'].strip())
                    program_code = row['course_code'].strip()
                    institution_code = row['college_code'].strip()
                    catagory = row['gcode'].strip()
                    type = row['type_code'].strip()
                    program_length = row['course_length'].strip()
                    program_fee = row['registration_fee'].strip()
                    program_category_name = row['cgcode'].strip()

                    ssc_edutype = row['ssc_edutype'].strip()
                    hsc_edutype = row['hsc_edutype'].strip()
                    diploma_edutype = row['diploma_edutype'].strip()
                    bsc_edutype = row['bsc_edutype'].strip()
                    msc_edutype = row['msc_edutype'].strip()
                    doc_edutype = row['doc_edutype'].strip()
                    bank_draft_no = row['bankdraft_no'].strip()
                    bank_draft_date_str = row['bankdraft_date'].strip()
                    approved = False
                    student_permission = Permission.objects.order_by('display_order').last()

                    quota = None
                    if quotas_name:
                        quota = Quota.objects.filter(quota_name__icontains=quotas_name)
                        if quota:
                            quota = quota[0]
                        else:
                            quota = Quota(quota_name=quotas_name)
                            quota.save()

                    nationality = Nationality.objects.filter(nationality_name__icontains=nationality_name)
                    if nationality:
                        nationality = nationality[0]
                    else:
                        nationality = Nationality(nationality_name=nationality_name)
                        nationality.save()

                    sex = ""
                    religion = ""
                    marital_status = ""
                    payment_method = ""

                    if choice_sex == 'FEMALE':
                        sex = '2'
                    if choice_sex == 'MALE':
                        sex = '2'
                    try:
                        date_of_birth = datetime.datetime.strptime(date_of_birth, "%d-%m-%Y").date()
                    except ValueError as e:
                        # print("error in date of birth " + registation_no + " error is " + str(e))
                        date_of_birth = datetime.datetime.strptime(str(datetime.datetime.now().date()),
                                                                   "%Y-%m-%d").date()

                    try:
                        date_of_registration = datetime.datetime.strptime(date_of_registration, "%d-%m-%Y").date()
                    except ValueError as e:
                        # print("error in date of registration "+registation_no+" error is "+str(e))
                        date_of_registration = None

                    try:
                        program_starting_date = datetime.datetime.strptime(program_starting_date, "%d-%m-%Y").date()
                    except ValueError as e:
                        # print("error in program starting date "+registation_no+" error is "+str(e))
                        program_starting_date = None

                    try:
                        program_completion_date = datetime.datetime.strptime(program_completion_date, "%d-%m-%Y").date()
                    except ValueError as e:
                        # print("program completion date "+registation_no+" error is "+str(e))
                        program_completion_date = None

                    try:
                        bank_draft_date = datetime.datetime.strptime(bank_draft_date_str, "%d-%m-%Y").date()
                    except:
                        bank_draft_date = None

                    if religions_name == "Islam":
                        religion = '1'
                    if religions_name == "Hindu":
                        religion = '2'
                    if religions_name == "Buddhist":
                        religion = '3'
                    if religions_name == "Christian":
                        religion = '4'
                    if religions_name == "Others":
                        religion = '5'

                    if marital_status_name == "Single":
                        marital_status = '1'
                    if marital_status_name == "Married":
                        marital_status = '2'
                    if marital_status_name == "Widow":
                        marital_status = '3'
                    if marital_status_name == "Divorced":
                        marital_status = '4'
                    if marital_status_name == "Seperated":
                        marital_status = '5'

                    if payment_method_name == "Cash":
                        payment_method = '2'
                    if payment_method_name == "Bank Draft":
                        payment_method = '1'

                    division = Division.objects.filter(name__icontains=division_name)
                    if not division:
                        division = Division(name=division_name)
                        division.save()
                    else:
                        division = division[0]

                    district = District.objects.filter(name__icontains=district_name)
                    if not district:
                        district = District(name=district_name, division=division)
                        district.save()
                    else:
                        district = district[0]

                    thana = Thana.objects.filter(name__icontains=thana_name)
                    if not thana:
                        if not thana_name:
                            thana = test_thana
                            # print("test thana has created in "+str(registation_no)+" and thana name is "+thana_name)
                        else:
                            thana = Thana(name=thana_name, district=district)
                            thana.save()
                    else:
                        thana = thana[0]

                    division_snd = Division.objects.filter(name__icontains=division_snd_name)
                    if not division_snd:
                        division_snd = Division(name=division_snd_name)
                        division_snd.save()
                    else:
                        division_snd = division_snd[0]

                    district_snd = District.objects.filter(name__icontains=district_snd_name)
                    if not district_snd:
                        district_snd = District(name=district_snd_name, division=division_snd)
                        district_snd.save()
                    else:
                        district_snd = district_snd[0]

                    thana_snd = Thana.objects.filter(name__icontains=thana_snd_name)
                    if not thana_snd:
                        if not thana_snd_name:
                            thana_snd = test_thana
                            # print("2ND test thana has created in "+str(registation_no)+" and thana name is "+thana_snd_name)
                        else:
                            thana_snd = Thana(name=thana_snd_name, district=district_snd)
                            thana_snd.save()

                    else:
                        thana_snd = thana_snd[0]

                    relation_to_guardian = Relation_to_guardians.objects.filter(relation__icontains=relation_with_guardians)
                    if relation_to_guardian:
                        relation_to_guardian = relation_to_guardian[0]
                    else:
                        relation_to_guardian = Relation_to_guardians(relation=relation_with_guardians)
                        relation_to_guardian.save()

                    program_duration = ProgramDuration.objects.filter(duration=(program_length))
                    if program_duration:
                        program_duration = program_duration[0]
                    else:
                        program_duration = ProgramDuration(duration=Decimal(program_length))
                        program_duration.save()

                    program_category = ProgramCatagory.objects.filter(name__icontains=program_category_name)
                    if program_category:
                        program_category = program_category[0]
                    else:
                        program_category = ProgramCatagory(name=program_category_name)
                        program_category.save()

                        # region seasson

                    if session_value:
                        session_value, start_date, end_date = get_month_year(session_value)

                        # end region

                        session = Session.objects.filter(session=session_value)
                        if session:
                            session = session[0]
                        else:
                            # session_value,start_date,end_date = get_month_year(session_value)
                            session = Session(session=session_value, session_start_date=start_date,
                                              session_end_date=end_date)
                            session.save()

                    program = Program.objects.filter(code=program_code)
                    if program:
                        program = program[0]
                    else:
                        program = Program(category=program_category, title=program_title, code=program_code,
                                          duration=program_duration, program_fee=program_fee, session=session,
                                          )
                        program.save()

                    ins_category = InstituteCatagory.objects.filter(status__icontains=catagory)
                    if ins_category:
                        ins_category = ins_category[0]
                    else:
                        ins_category = InstituteCatagory(status=catagory)
                        ins_category.save()

                    ins_type = InstituteType.objects.filter(institute_type__icontains=type)
                    if ins_type:
                        ins_type = ins_type[0]
                    else:
                        ins_type = InstituteType(institute_type=type)
                        ins_type.save()

                    institution = Institution.objects.filter(institution_name__icontains=institution_name)
                    if institution:
                        institution = institution[0]
                    else:
                        institution = Institution(institution_name=institution_name, institution_code=institution_code,
                                                  catagory=ins_category, type=ins_type, division=test_divisions,
                                                  district=test_district, thana=test_thana, village=" ",
                                                  post_office=" ", is_exam_center=False)
                        institution.save()

                    student_permission = None
                    is_2018_batch = session_value.find("2018")

                    if is_2018_batch >= 0:
                        student_permission = draft_permissio
                        student_id = ""

                    else:
                        student_permission = approved_permission
                        approved = True
                        reg_no = 1
                        is_valid = False
                        # while is_valid == False:
                        #     search_reg_no = institution.institution_code + str(session) + program.code + str(reg_no)
                        #     auto_reg_no = Student_Registration.objects.filter(session=session,
                        #                                                       registration_no=search_reg_no)
                        #     if auto_reg_no:
                        #         reg_no += 1
                        #     else:
                        #         is_valid = True
                        # student_id = institution.institution_code + str(session) + program.code + str(reg_no)

                    student_registration = Student_Registration(image=image_location, student_id="",
                                                                registration_no=student_id,
                                                                first_name=first_name, last_name=last_name,
                                                                fathers_name=fathers_name, mothers_name=mothers_name,
                                                                sex=sex, date_of_birth=date_of_birth,
                                                                national_ID_No=national_ID_No, passport_no=passport_no,
                                                                guardians_name=guardians_name,
                                                                relation_to_guardians=relation_to_guardian, quota=quota,
                                                                nationality=nationality, religions=religion,
                                                                marital_status=marital_status,
                                                                email_address=email_address,
                                                                students_mobile_no=students_mobile_no,
                                                                division=division, district=district,
                                                                thana=thana, institution=institution, village=village,
                                                                post_office=post_office, postal_code=postal_code,
                                                                division_snd=division_snd, district_snd=district_snd,
                                                                thana_snd=thana_snd, village_snd=village_snd,
                                                                post_office_snd=post_office_snd,
                                                                postal_code_snd=postal_code_snd, same_address=False,
                                                                date_of_registration=date_of_registration,
                                                                program_starting_date=program_starting_date,
                                                                program_title=program, payment_method=payment_method,
                                                                registration_fees=registration_fees,
                                                                program_completion_date=program_completion_date,
                                                                session=session, status=student_permission,
                                                                bank_draft_no=bank_draft_no,
                                                                bank_draft_date=bank_draft_date, approved=True)

                    student_registration.save()
                    if ssc_edutype:
                        ssc_roll = row['ssc_roll'].strip()
                        ssc_college = row['ssc_college'].strip()
                        ssc_class = row['ssc_class'].strip()
                        ssc_year = row['ssc_year'].strip()
                        try:
                            ssc_year = int(ssc_year)
                        except:
                            ssc_year = 0

                        ssc_duration = row['ssc_duration'].strip()
                        ssc_country = row['ssc_country'].strip()
                        ssc_gpa = row['ssc_class'].strip()

                        ssc_education_qualification = EducationQualification(student=student_registration,
                                                                             level_of_education=ssc_edutype,
                                                                             education_type=" ", board=ssc_college,
                                                                             roll=ssc_roll, cgpa=float(ssc_gpa),
                                                                             year=ssc_year,
                                                                             duration=change_education_year_into_chose_field(
                                                                                 ssc_duration),
                                                                             country=change_country_into_choice_field(
                                                                                 ssc_country))
                        ssc_education_qualification.save()

                    if hsc_edutype:
                        hsc_roll = row['hsc_roll'].strip()
                        hsc_college = row['hsc_college'].strip()
                        hsc_year = row['hsc_year'].strip()
                        try:
                            hsc_year = int(hsc_year)
                        except:
                            hsc_year = 0

                        hsc_duration = row['hsc_duration'].strip()
                        hsc_country = row['hsc_country'].strip()
                        hsc_gpa = row['hsc_class'].strip()
                        hsc_education_qualification = EducationQualification(student=student_registration,
                                                                             level_of_education=ssc_edutype,
                                                                             education_type=" ", board=hsc_college,
                                                                             roll=hsc_roll, cgpa=hsc_gpa, year=hsc_year,
                                                                             duration=change_education_year_into_chose_field(
                                                                                 hsc_duration),
                                                                             country=change_country_into_choice_field(
                                                                                 hsc_country))
                        hsc_education_qualification.save()

                    if diploma_edutype:
                        diploma_roll = row['diploma_roll'].strip()
                        diploma_college = row['diploma_college'].strip()
                        diploma_year = row['diploma_year'].strip()
                        try:
                            diploma_year = int(diploma_year)
                        except:
                            diploma_year = 0

                        diploma_duration = row['diploma_duration'].strip()
                        diploma_country = row['diploma_country'].strip()
                        diploma_gpa = row['diploma_class'].strip()

                        diploma_education_qualification = EducationQualification(student=student_registration,
                                                                                 level_of_education=diploma_edutype,
                                                                                 education_type=" ",
                                                                                 board=diploma_college,
                                                                                 roll=diploma_roll,
                                                                                 cgpa=float(diploma_gpa),
                                                                                 year=diploma_year,
                                                                                 duration=change_education_year_into_chose_field(
                                                                                     diploma_duration),
                                                                                 country=change_country_into_choice_field(
                                                                                     diploma_country))
                        diploma_education_qualification.save()

                    if bsc_edutype:
                        bsc_roll = row['bsc_roll'].strip()
                        bsc_college = row['bsc_college'].strip()
                        bsc_year = row['bsc_year'].strip()
                        try:
                            bsc_year = int(bsc_year)
                        except:
                            bsc_year = 0

                        bsc_duration = row['bsc_duration'].strip()
                        bsc_country = row['bsc_country'].strip()
                        bsc_gpa = row['bsc_class'].strip()
                        if bsc_gpa == 'Pass':
                            bsc_gpa = 0.00

                            bsc_education_qualification = EducationQualification(student=student_registration,
                                                                                 level_of_education=bsc_edutype,
                                                                                 education_type=" ", board=bsc_college,
                                                                                 roll=bsc_roll, cgpa=bsc_gpa,
                                                                                 year=bsc_year,
                                                                                 duration=change_education_year_into_chose_field(
                                                                                     bsc_duration),
                                                                                 country=change_country_into_choice_field(
                                                                                     bsc_country))
                            bsc_education_qualification.save()
                        else:
                            bsc_education_qualification = EducationQualification(student=student_registration,
                                                                                 level_of_education=bsc_edutype,
                                                                                 education_type=" ", board=bsc_college,
                                                                                 roll=bsc_roll, cgpa=bsc_gpa,
                                                                                 year=bsc_year,
                                                                                 duration=change_education_year_into_chose_field(
                                                                                     bsc_duration),
                                                                                 country=change_country_into_choice_field(
                                                                                     bsc_country))
                            bsc_education_qualification.save()

                    if msc_edutype:
                        msc_roll = row['msc_roll'].strip()
                        msc_college = row['msc_college'].strip()
                        msc_year = row['msc_year'].strip()
                        try:
                            msc_year = int(msc_year)
                        except:
                            msc_year = 0

                        msc_duration = row['msc_duration'].strip()
                        msc_country = row['msc_country'].strip()
                        msc_gpa = row['msc_class'].strip()

                        msc_education_qualification = EducationQualification(student=student_registration,
                                                                             level_of_education=msc_edutype,
                                                                             education_type=" ", board=msc_college,
                                                                             roll=msc_roll, cgpa=msc_gpa, year=msc_year,
                                                                             duration=change_education_year_into_chose_field(
                                                                                 msc_duration),
                                                                             country=change_country_into_choice_field(
                                                                                 msc_country))
                        msc_education_qualification.save()

                    if doc_edutype:
                        doc_roll = row['doc_roll'].strip()
                        doc_college = row['doc_college'].strip()
                        doc_year = row['doc_year'].strip()
                        try:
                            doc_year = int(doc_year)
                        except:
                            doc_year = 0

                        doc_duration = row['doc_duration'].strip()
                        doc_country = row['doc_country'].strip()
                        doc_gpa = row['doc_class'].strip()

                        doc_education_qualification = EducationQualification(student=student_registration,
                                                                             level_of_education=doc_edutype,
                                                                             education_type=" ", board=doc_college,
                                                                             roll=doc_roll, cgpa=doc_gpa, year=doc_year,
                                                                             duration=change_education_year_into_chose_field(
                                                                                 doc_duration),
                                                                             country=change_country_into_choice_field(
                                                                                 doc_country))
                        doc_education_qualification.save()

                    saved_row = saved_row + 1
                except ValueError as e:
                    print(e)
        print("viewd rows " + str(view_row) + " saved row " + str(saved_row))

    return render(request, "bnmc_project/form_up.html")

def get_month_year(month_year_str):
    month_year_str = month_year_str.strip().upper()
    month_year_str = month_year_str.replace(",", "")
    month_year_str = month_year_str.replace("'", "")

    start_month = "01"
    start_year = None

    end_month = '01'
    end_year = None
    if month_year_str.find("~"):
        month_year_str = month_year_str.replace('~', '-')

    if month_year_str.find("-"):
        hyphens = month_year_str.count('-')
        if hyphens == 1:
            start_season = month_year_str.split('-')[0]

            if any(x in start_season for x in months):
                match_month = next((x for x in months if x in start_season), False)
                start_month = change_month[months.index(match_month)]

            if any(x in start_season for x in years):
                match_year = next((x for x in years if x in start_season), False)
                start_year = change_year[years.index(match_year)]

            end_season = month_year_str.split('-')[1]

            if any(x in end_season for x in months):
                match_end_month = next((x for x in months if x in end_season), False)
                end_month = change_month[months.index(match_end_month)]

            if any(x in end_season for x in years):
                match_end_year = next((x for x in years if x in end_season), False)
                end_year = change_year[years.index(match_end_year)]

            if start_year == None:
                start_year = end_year
            if end_year == None:
                end_year = start_year

        if hyphens == 2:

            common_year = None
            start_season = month_year_str.split('-')[0]

            if any(x in start_season for x in months):
                match_month = next((x for x in months if x in start_season), False)
                start_month = change_month[months.index(match_month)]

            if any(x in start_season for x in years):
                match_year = next((x for x in years if x in start_season), False)
                # start_year=change_year[years.index(match_year)]

            end_season = month_year_str.split('-')[1]

            if any(x in end_season for x in months):
                match_end_month = next((x for x in months if x in end_season), False)
                end_month = change_month[months.index(match_end_month)]

            if any(x in end_season for x in years):
                match_end_year = next((x for x in years if x in end_season), False)
                # end_year=change_year[years.index(match_end_year)]
            end_season = month_year_str.split('-')[2]
            if any(x in end_season for x in years):
                match_end_year = next((x for x in years if x in end_season), False)
                # end_year=change_year[years.index(match_end_year)]
                common_year = change_year[years.index(match_end_year)]
                start_year = end_year = common_year

    start_date = datetime.date(int("20" + str(start_year)), int(start_month), 1)
    end_date = datetime.date(int("20" + str(end_year)), int(end_month), 1)

    return month_year_str, start_date, end_date


def change_country_into_choice_field(country):
    choice_country = ''
    if country == 'Bangladesh':
        choice_country = '1'
    if country == 'Barbados':
        choice_country = '9'
    if country == 'Belarus':
        choice_country = '10'
    if country == 'Nepal':
        choice_country = '11'
    if country == 'Bahamas':
        choice_country = '5'
    if country == 'Malaysia':
        choice_country = '12'
    if country == 'India':
        choice_country = '13'

    return choice_country


def change_education_year_into_chose_field(durations):
    choice_key = ' '
    durations = durations.upper()
    if durations == '1 YEAR':
        choice_key = '1'
    if durations == '2 YEARS':
        choice_key = '2'
    if durations == '3 YEARS':
        choice_key = '3'
    if durations == '4 YEARS':
        choice_key = '4'
    if durations == '5 YEARS':
        choice_key = '5'
    return choice_key

@login_required(login_url='/admin/login/')
def add_instatuited(request):
    if request.POST:
        pwd = os.path.dirname(__file__)
        with open(pwd + '/accc.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            count = 0

            test_divisions = Division.objects.filter(name="Test Division")
            if test_divisions:
                test_divisions = test_divisions[0]
            else:
                test_divisions = Division(name="Test Division")
                test_divisions.save()

            test_district = District.objects.filter(name="Test District")
            if test_district:
                test_district = test_district[0]
            else:
                test_district = District(name="Test District", division=test_divisions)
                test_district.save()

            test_thana = Thana.objects.filter(name="Test Thana")
            if test_thana:
                test_thana = test_thana[0]
            else:
                test_thana = Thana(name="Test Thana", district=test_district)
                test_thana.save()

            for row in reader:
                institution_name = row['institute_name'].strip()
                institution_code = row['college_code'].strip()
                catagory = row['gcode'].strip()
                type = row['type_code'].strip()
                division_name = row['pre_division'].strip()
                district_name = row['pre_district'].strip()
                thana_name = row['per_thana'].strip()
                village = row['pre_village'].strip()
                post_office = row['pre_postoffice'].strip()
                program_title = row['course_type'].strip()
                program_code = row['course_code'].strip()
                program_category_name = row['cgcode'].strip()
                program_length = row['course_length'].strip()
                program_fee = row['registration_fee'].strip()
                session_value = row['session'].strip()

                institution = Institution.objects.filter(institution_name=institution_name)

                if not institution:
                    ins_category = InstituteCatagory.objects.filter(status=catagory)
                    if ins_category:
                        ins_category = ins_category[0]
                    else:
                        ins_category = InstituteCatagory(status=catagory)
                        ins_category.save()

                    ins_type = InstituteType.objects.filter(institute_type=type)
                    if ins_type:
                        ins_type = ins_type[0]
                    else:
                        ins_type = InstituteType(institute_type=type)
                        ins_type.save()

                    program_category = ProgramCatagory.objects.filter(name=program_category_name)
                    if program_category:
                        program_category = program_category[0]
                    else:
                        program_category = ProgramCatagory(name=program_category_name)
                        program_category.save()

                    program_duration = ProgramDuration.objects.filter(duration=(program_length))
                    if program_duration:
                        program_duration = program_duration[0]
                    else:
                        program_duration = ProgramDuration(duration=Decimal(program_length))
                        program_duration.save()

                    if session_value:
                        session_value, session_start, sesson_end = get_month_year(session_value)
                        session = Session.objects.filter(session=session_value)
                        if session:
                            session = session[0]
                        else:
                            session = Session(session=session_value, session_start_date=session_start,
                                              session_end_date=sesson_end)
                            session.save()

                    program = Program.objects.filter(code=program_code)
                    if program:
                        program = program[0]
                    else:
                        program = Program(category=program_category, title=program_title, code=program_code,
                                          duration=program_duration, program_fee=program_fee, session=session,
                                          minimum_grade=0.0)
                        program.save()

                        # created_institution=Institution(institution_name=institution_name,institution_code=institution_code,catagory=ins_category,type=ins_type,is_exam_center=False)
                    created_institution = Institution(institution_name=institution_name,
                                                      institution_code=institution_code, catagory=ins_category,
                                                      type=ins_type, division=test_divisions, district=test_district,
                                                      thana=test_thana, village=" ", post_office=" ",
                                                      is_exam_center=False)
                    created_institution.save()
                    created_institution.program_ins.add(program)
        return render(request, "bnmc_project/add_ins.html")

    return render(request, "bnmc_project/add_ins.html")


def add_distric(request):
    if request.POST:
        pwd = os.path.dirname(__file__)
        with open(pwd + '/area_info_dis.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            count = 0
            for row in reader:
                name = row['position_name'].strip()
                divission_name = row['subposition'].strip()
                if not name:
                    continue
                if not divission_name:
                    continue
                district = District.objects.filter(name=name)
                if not district:
                    divisions = Division.objects.filter(name=divission_name)
                    if divisions:
                        divisions = divisions[0]
                    else:
                        divisions = Division(name=divission_name)
                        divisions.save()
                    created_district = District(name=name, division=divisions)
                    created_district.save()
                count = count + 1
                print(count)
    return render(request, "bnmc_project/add_distric.html")


def add_thana(request):
    if request.POST:
        pwd = os.path.dirname(__file__)
        with open(pwd + '/area_info_thana.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            count = 0
            for row in reader:
                name = row['position_name'].strip()
                district_name = row['subposition'].strip()
                if not name:
                    continue
                thana = Thana.objects.filter(name=name)
                if not thana:
                    district = District.objects.filter(name=district_name)
                    if district:
                        district = district[0]
                    else:
                        district = District(name=district_name)
                        district.save()
                    created_thana = Thana(name=name, district=district)
                    created_thana.save()
                count = count + 1
                print(count)
    return render(request, "bnmc_project/add_thana.html")

def get_view(request):
    today = timezone.now()
    registation_list=Student_Registration.objects.filter(pk__in=(request.session.get('query_set')))

    params = {
        'today': today,
        'request': request,
        'query_set':registation_list
    }
    return Render.render('admin/approve_student.html', params)

def test(request):
    return render(request,'admin/approve_student_1.html')

def clear_reg_number_by_programs(request):
    sttt=""
    count=0
    reg_students= Student_Registration.objects.filter(institution__id=350)
    for std in reg_students.all():
        std.approve_by=None
        std.approved=False
        std.registration_no=""
        std.status=Permission.objects.all().order_by('display_order').first()
        std.save()
        count+=1
        sttt+=str(std.id)+"</br>"
    return HttpResponse("<h1>"+sttt +"</br> Total "+str(count)+"</h1>")


def process_licnese(request):
    if request.POST:
        exam=request.POST.get("exam",None)
        start_role=request.POST.get("role_ranger_first",None)
        end_role=request.POST.get("role_ranger_snd",None)
        center=request.POST.get("center",None)
        hall=request.POST.get("hall_name",None)
        room_no=request.POST.get("room_no",None)
        hidden_id=request.POST.get("hidden_id",None)




        if exam and start_role and end_role and center and hall and room_no and not hidden_id:
            license_students=license_registrations.objects.filter(rool_number__range=(start_role,end_role),approved=True,exam_title__id=exam)
            for student in license_students:
                student.centre=ExamCenter.objects.get(pk=center)
                student.hall_name=hall
                student.room_name=room_no
                student.save()

            create = CenterManagement.objects.create(exam_id=exam, roll_start=start_role, roll_end=end_role,
                                                     center_id=center, hall_name=hall, room_name=room_no)
            create.save()



        if hidden_id:
            license_update_roll=license_registrations.objects.filter(rool_number__range=(start_role,end_role),approved=True,exam_title__id=exam)
            update_query=license_update_roll.update(centre=center,hall_name=hall,room_name=room_no)
            query = CenterManagement.objects.filter(id=hidden_id)
            update = query.update(exam=exam, roll_start=start_role, roll_end=end_role, center=center, hall_name=hall,
                                  room_name=room_no)




    var=CenterManagement.objects.all()
    revarse=var.order_by('-id')
    paginator = Paginator(revarse, 100)
    page = request.GET.get('page')
    paginate = paginator.get_page(page)

    centers= ExamCenter.objects.all()
    context={"centers":centers,"exams":Exam.objects.filter(date_active=True).all(),
             'var':paginate

             }

    return render(request,'admin/process_licnese.html',context)


def renew_licence(request,license_id):
    license_history=LicenseHistory.objects.get(pk=license_id)


    date_end_inc=parse_date(license_history.license_end_date)
    new_end_date=new_end_date_implement(date_end_inc)


    renew=re_new_history(license=license_history.license_receive_id,created_on=datetime.datetime.now(),previous_start_date=license_history.license_start_date,
                         previous_end_date=license_history.license_end_date,new_start_date=license_history.license_end_date,new_end_date=new_end_date,renew_by=request.user,
                         license_number=license_history.license_number,program=license_history.program

                         )

    renew.save()
    license_history.license_start_date=license_history.license_end_date
    license_history.license_end_date=new_end_date
    license_history.renew_history.add(renew.pk)
    license_history.save()



    return redirect("/admin/bnmc_project/license_receive/"+str(license_history.license_receive_id.id)+"/change/")



def print_exam_mark_sheet(request,id):
    reg_details=ExaminationStudentRegistration.objects.get(id=id)
    result_details= ExamResultDetails.objects.filter(examStudentInfo=reg_details)
    if not result_details:
        return HttpResponse("aa")                                        
    for _subject in reg_details.subjects.all():
        subject_marks=result_details.filter(subject=_subject)
        if subject_marks:
            _subject.marks=subject_marks[0].marks
            _subject.point=subject_marks[0].get_grad_point()
            _subject.grad=subject_marks[0].get_grad()
            if _subject.isMainSubject and _subject.SubSubjects:                
                for subSubject in _subject.SubSubjects.all():
                    sub_subject_marks=result_details.filter(subject=subSubject)
                    if sub_subject_marks:
                        subSubject.marks=sub_subject_marks[0].marks                                                                                                                                                    
    return HttpResponse("aaaa")


def update_exam(request):
    exam_id=Exam.objects.get(id=1)
    license_reg=license_registrations.objects.all()
    license_reg.update(exam_title=1,date_of_passing_on=exam_id.exam_date)

    return HttpResponse('work')

def get_approve(request):
    self_id=request.POST.get('self_id')
    if self_id:
        query_srch=BalanceHistory.objects.filter(id=self_id)
        last_query=query_srch[0]
        if last_query.IsApproved==False:
            update=query_srch.update(IsApproved=True,approvedBy=request.user.id,approvDate=datetime.datetime.now())
    return HttpResponse(json.dumps(request.POST.get("self_id")))



def student_money_recept(request):
    if request.POST:
        request_type=request.POST.get("rq_type")
        print(request_type)
        if request_type:
            Incomes= request.POST.getlist("Incomes[]")
            defaultAccounts=Accounts.objects.filter(IsDefaultAccount=True)
            if defaultAccounts:      
                if request_type=='reg':                             
                    reg_no=request.POST.get("reg_no")
                    reg_program=request.POST.get("reg_program")
                    note=request.POST.get("note")
                    student_registration=Student_Registration.objects.filter(registration_no=reg_no,program_title__id=reg_program)
                    if student_registration:
                        balance = BalanceHistory(account=defaultAccounts[0],historyType='1',Note=note,student_reg=student_registration[0])
                        balance.save()
                        total_amount=0
                        for income in Incomes:
                            income_rec=BalanceIncome.objects.get(id=int(income))
                            if income_rec.amount:
                                total_amount+=income_rec.amount
                            balance.BalanceIncomes.add(income)

                        get_date = str(balance.bankIssueDate)
                        # get_date = get_date[5:10]
                        static_date = '11-03'
                        recept_number=1
                        records =BalanceHistory.objects.filter(create_on__year=datetime.datetime.now().year)
                        if records:
                            recept_number=len(records)+1
                        balance.amount=total_amount
                        balance.id_no=recept_number
                        balance.save()

                        stu_reg=Student_Registration.objects.filter(id=balance.student_reg.id)
                        stu_reg=stu_reg[0]
                        total_income = balance.BalanceIncomes.all()
                        get_number=num2words(balance.amount)##pip install num2words
                        contaxt = {'p': balance,
                                   'stu_reg': stu_reg,
                                   'total_income': total_income,
                                   'get_number':get_number

                                   }
                        return render(request, 'admin/money_recipte.html', contaxt)



                elif request_type=='license_reg':
                    print("license_reg")
                    license_reg_no=request.POST.get("li_reg_no")
                    license_program=request.POST.get("license_program")
                    print(license_reg_no,license_program)
                    license_history= LicenseHistory.objects.filter(license_number=license_reg_no,program=license_program)
                    print()
                    note=request.POST.get("note")
                    balance=None
                    if license_history:
                        license_history=license_history[0]
                        if license_history.student_registration_id:
                            if license_history.student_registration_id:
                                balance = BalanceHistory(account=defaultAccounts[0],historyType='1',Note=note,student_reg=license_history.student_registration_id)
                                balance.save()
                                total_amount=0
                                for income in Incomes:
                                    income_rec=BalanceIncome.objects.get(id=int(income))
                                    if income_rec.amount:
                                        total_amount+=income_rec.amount
                                    balance.BalanceIncomes.add(income)
                                balance.amount=total_amount
                                recept_number = 1
                                records = BalanceHistory.objects.filter(create_on__year=datetime.datetime.now().year)
                                if records:
                                    recept_number = len(records) + 1
                                balance.id_no = recept_number
                                balance.save()

                                stu_reg = Student_Registration.objects.filter(id=balance.student_reg.id)
                                stu_reg = stu_reg[0]
                                total_income = balance.BalanceIncomes.all()
                                get_number = num2words(balance.amount)


                                print(stu_reg,total_income,get_number)
                                contaxt = {'p': balance,
                                           'stu_reg': stu_reg,
                                           'total_income': total_income,
                                           'get_number': get_number,
                                           'license_history': license_history,
                                           }
                                return render(request, 'admin/money_recipte_2.html', contaxt)


                        elif license_history.license_receive_id.is_old_data == True:
                            balance = BalanceHistory(account=defaultAccounts[0], historyType='1', Note=note,
                                                     )
                            balance.save()
                            total_amount = 0
                            for income in Incomes:
                                income_rec = BalanceIncome.objects.get(id=int(income))
                                if income_rec.amount:
                                    total_amount += income_rec.amount
                                balance.BalanceIncomes.add(income)
                            balance.amount = total_amount
                            recept_number = 1
                            records = BalanceHistory.objects.filter(create_on__year=datetime.datetime.now().year)
                            if records:
                                recept_number = len(records) + 1
                            balance.id_no = recept_number
                            balance.save()

                            student_id = Student.objects.filter(id=license_history.student_id.id)
                            student_id = student_id[0]
                            total_income = balance.BalanceIncomes.all()
                            get_number = num2words(balance.amount)

                            contaxt = {'p': balance,
                                       'stu_reg': student_id,
                                       'total_income': total_income,
                                       'license_history':license_history,
                                       'get_number': get_number
                                       }
                            return render(request, 'admin/money_recipte_2.html', contaxt)


                elif request_type=='ins':
                    institution=request.POST.get("institution")
                    note=request.POST.get("note")
                    item_list=[]

                    number_of_items = request.POST.getlist('number_of_item[]')
                    for i in number_of_items:
                        if i != '':
                            item_list.append(i)


                    # print(number_of_items)
                    # print(Incomes)
                    total_amount=0
                    list_of=[]


                    balance = BalanceHistory(account=defaultAccounts[0],historyType='1',Note=note,instituition=Institution.objects.get(id=institution))
                    text_list=[]
                    item_text=[]

                    for item_number, income_id in zip(item_list, Incomes):

                        income_receive = BalanceIncome.objects.get(id=int(income_id))
                        if income_receive.amount and item_number:
                            varr = income_receive.amount * int(item_number)
                            list_of.append(varr)
                            total_amount+=varr
                            item_text.append(int(item_number))
                            text_list.append(int(income_receive.amount))


                    balance.amount = total_amount
                    balance.save()



                    print('iii',text_list)
                    for income in Incomes:
                        balance.BalanceIncomes.add(income)
                    balance.save()
                    balance.number_of_item=number_of_items
                    recept_number = 1
                    records = BalanceHistory.objects.filter(create_on__year=datetime.datetime.now().year)
                    if records:
                        recept_number = len(records) + 1
                    balance.id_no = recept_number
                    balance.save()
                    total_income = balance.BalanceIncomes.all().order_by('head_no')
                    get_number = num2words(balance.amount)  ##pip install num2words
                    for i_taka in list_of:
                        pass

                    if balance and item_list:


                        contaxt={'p':balance,
                                 'total_income': zip(total_income,list_of,text_list,item_text),
                                 'total':zip(total_income,list_of,text_list,item_text),
                                 'to':zip(total_income,list_of,text_list,item_text),
                                 'get_number': get_number,
                                 }
                        return render(request, 'admin/money_recipte_1.html', contaxt)


    context={'institution':Institution.objects.all(),'Incomes':BalanceIncome.objects.all().order_by('head_no'),'programs':Program.objects.all()}
    return render(request,'admin/student_money_recept.html',context)

    
# def institute_receipt(request):
#     if request.POST.get()
#     institute_id=request.POST.get()
#     return HttpResponse('ffff')
#


def license_card(request):
    return render(request,'admin/regCard.html')




def re_store_data(request):
    id_list = [259]
    students=Student_Registration.objects.filter(institution__id__in = id_list)
    main_ins = Institution.objects.get(id=260)
    html="";

    for std in students:
        html+="<h1> institution is"+ str(std.institution)+" id is "+str(std.id)+" student name is "+std.last_name +"</h1>"
    update_student=students.update(institution=main_ins)
    print(students)
    return HttpResponse (html)



def re_store_session(request):
    id_list=[63189, 63200, 63201, 63203, 63207, 63224, 63229, 63250, 63258, 63271, 63287, 63296, 63300, 63303, 63307, 63308, 63309, 63310, 63311, 63314, 63315, 63316, 63318, 63319, 63320, 63321, 63322, 63323, 63324, 63325, 63326, 63327, 63329 ]
    students=Student_Registration.objects.filter(id__in=id_list)
    session_id=39
    html="";


    for std in students:
        html+="<h1> session is"+ str(std.session)+" id is "+str(std.id)+" student name is "+std.last_name +"</h1>"
    update_student=students.update(session=session_id)
    return HttpResponse (html)


def re_store_stid (request):
    id_list=[82455]
    students=Student_Registration.objects.filter(id__in=id_list)
    registration_no=23484
    html="";


    for std in students:
        html+="<h1> id is "+str(std.id)+" student name is "+std.last_name +"</h1>"
    update_student=students.update(registration_no=registration_no)
    return HttpResponse (html)



def get_division(request):

    division_id=request.POST.get('division_id')
    print(division_id)
    district_list=[]

    if division_id:
        districts=District.objects.filter(division__id=division_id)
        if districts:
            for p in districts:
                var=district_list.append(p.id)
                data=json.dumps(district_list)
        return HttpResponse(data)



def get_district(request):

    district_id=request.POST.get('district_id')
    thana_list=[]

    if district_id:
        thanas=Thana.objects.filter(district__id=district_id)
        print(thanas)
        if thanas:
            for p in thanas:
                var=thana_list.append(p.id)
                data=json.dumps(thana_list)
                print(p.name)
        return HttpResponse(data)


def get_division_fisrt(request):

    division_id=request.POST.get('division_id')
    print(division_id)
    district_list=[]

    if division_id:
        districts=District.objects.filter(division__id=division_id)
        if districts:
            for p in districts:
                var=district_list.append(p.id)
                data=json.dumps(district_list)
        return HttpResponse(data)



def get_district_first(request):

    district_id=request.POST.get('district_id')
    thana_list=[]

    if district_id:
        thanas=Thana.objects.filter(district__id=district_id)
        print(thanas)
        if thanas:
            for p in thanas:
                var=thana_list.append(p.id)
                data=json.dumps(thana_list)
                print(p.name)
        return HttpResponse(data)

def get_years(request):

    program_id=request.POST.get('program_id')
    print(program_id)
    year_list=[]

    if program_id:
        years=ExamYear.objects.filter(program=program_id)
        if years:
            for p in years:
                year_list.append(p.id)
                data=json.dumps(year_list)

        else:
            year_list.append('false')
            data=json.dumps(year_list)
    return HttpResponse(data)

def get_sub(request):
    year_id=request.POST.get('year_id')
    print(year_id)
    subjects_list=[]

    if year_id:
        sub=ExamSubject.objects.filter(year=year_id)
        if sub:
            for p in sub:
                print(p)
                subjects_list.append(p.id)
            data=json.dumps(subjects_list)

        else:
            subjects_list.append('false')
            data=json.dumps(subjects_list)

    else:
        subjects_list.append('false')
        data = json.dumps(subjects_list)
    return HttpResponse(data)


def edit_center(request):
    center_id=request.POST.get('id_set')
    center_query=CenterManagement.objects.filter(id=center_id).first()
    if center_query:
        info = [True, center_query.id,center_query.exam.id,center_query.roll_start,center_query.roll_end,center_query.center.id,center_query.hall_name,center_query.room_name]
        print(info)
    else:
        info=[False]
    data=json.dumps(info)
    return HttpResponse(data)

def import_user(request):

    if request.method == "POST":
        pwd = os.path.dirname(__file__)
        with open(pwd + '/copy.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                username = row['username'].strip()
                password = row['password'].strip()
                full_name = row['full_name'].strip()
                email = row['email'].strip()
                address = row['address'].strip()


                try:
                    last=Permission.objects.order_by('display_order').first()
                    create_user=User.objects.create(username=username,password=password,is_staff=True,is_active=True)





                except:
                    pass

    return render(request,'admin/import_user.html')


def license_data(request):
    if request.method == "POST":
        pwd = os.path.dirname(__file__)

        with open(pwd + '/license_data.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            list_=[]
            for row in reader:
                reg=row['registration_number'].strip()
                program_code=row['program_code'].strip()
                if reg != '' and program_code !='':
                    studentReg=Student_Registration.objects.filter(registration_no=reg,program_title__code=program_code)
                    if studentReg:
                        for i in studentReg:

                            license_reg=license_registrations()
                            license_reg.student_registration=i
                            license_reg.program=i.program_title
                            license_reg.institution=i.institution
                            license_reg.registration_no=reg
                            license_reg.status=Permission.objects.all().order_by('display_order').first()
                            license_reg.session=i.session
                            license_reg.image=i.image
                            license_reg.image_sec=i.image
                            license_reg.students_mobile_no=i.students_mobile_no
                            license_reg.save()


            print('student_reg',len(list_))
    return render(request,'admin/import_license_data.html')






def license_data_import(request):
    if request.method == "POST":
        pwd = os.path.dirname(__file__)

        with open(pwd + '/missing_student_list.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            list_=[]
            nu = []
            parmission=Permission.objects.all().order_by('display_order').first()
            for row in reader:
                try:
                    reg=row['student_id'].strip()
                    program_code=row['course_code'].strip()
                    file_signature = "signature_student/" + str(row['signature'].strip())
                    exam_id = Exam.objects.get(id=1)
                    if reg !='' and program_code !='':
                        student_reg=Student_Registration.objects.filter(registration_no=reg,program_title__code=program_code)
                        if student_reg:
                            for i in student_reg:
                                license=license_registrations(student_registration=i,program=i.program_title,status=parmission,session=i.session,image=i.image,image_sec=i.image
                                                              ,students_mobile_no=i.students_mobile_no,signature_first=file_signature,exam_title=exam_id,date_of_passing_on=exam_id.exam_date
                                                              ,institution=i.institution,registration_no=i.registration_no
                                                              )

                                license.save()
                                print(license)
                except ValueError as e:
                    print(e)



    return render(request, 'admin/import_license_data.html')



def signature_upload(request):
    if request.method == "POST":
        pwd = os.path.dirname(__file__)

        with open(pwd + '/signature.csv', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=',')
            list_=[]
            empty=[]
            for row in reader:
                reg=row['Student_Id'].strip()
                program_code=row['Course_type'].strip()
                file_signature=row['Signatue_Name'].strip()
                file_signature="signature_student/" + str(row['Signatue_Name'].strip())
                if reg != '' and program_code !='':
                    studentReg=license_registrations.objects.filter(registration_no=reg,program__code=program_code)

                    if studentReg:
                        list_.append(studentReg)
                        try:

                            studentReg.update(signature_first=file_signature)

                        except:
                            pass

                    else:
                        empty.append(reg)

            print('student_reg',len(list_))
            print('empty',len(empty))
    return render(request,'admin/import_license_data.html')


from django.core.exceptions import ValidationError
import base64
from django.contrib.auth.hashers import check_password
import base64
def change_password(request):





    get_user=request.user.id

    query_filter=User.objects.filter(id=get_user)
    query_filter=query_filter[0]
    pas_word=query_filter.password



    if request.method == "POST":
        old_pass=request.GET.get('old_pass')
    return render(request,'admin/change_password.html')


# def home_view(request):
#     return render(request,'admin/home_page.html')

def get_info_moneyrecipte(request):
    number=request.POST.get('num')
    pro=request.POST.get('prog')

    if number !=0 and pro !=0:
        student_reg=Student_Registration.objects.filter(program_title_id=pro,registration_no=number)
        print('aaaa','student_reg')
        if student_reg:
            student_reg=student_reg[0]
            if student_reg:
                student_=Student.objects.get(id=student_reg.students.id)
                student_data=[True,student_.id,student_.last_name,student_.fathers_name]
                data=json.dumps(student_data)
                return HttpResponse(data)


def get_info_moneyrecipte_li(request):
    number=request.POST.get('num')
    pro=request.POST.get('prog')

    if number !=0 and pro !=0:
        lic_reg=license_registrations.objects.filter(program_id=pro,rool_number=number)
        if lic_reg:
            lic_reg=lic_reg[0]
            if lic_reg:
                student_=Student_Registration.objects.get(id=lic_reg.student_registration.id)
                if student_:
                    stu=Student.objects.get(id=student_.students.id)
                    print('ff',stu)
                    if stu:
                        student_data=[True,stu.id,stu.last_name,stu.fathers_name]
                        data=json.dumps(student_data)
                        return HttpResponse(data)


def found_pass(request):
    filte=EducationQualification.objects.filter(cgpa=type())
    if filte:
        html=''
        for i in filte:
            html+='name '+str(i.student.last_name)+'  '+'program '+str(i.student.program_title)+'  '+'reg '+str(i.student.registration_no)+'<br>'



    # filte.update(cgpa=6.00)
    return HttpResponse(html)

def remove_cgpa(request):
    li=['1','2','3','4','5','6','8','9','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','33','34'
        , '35','36','37','38','39','40','41','42','43','44','46','47','48','49','50','51','52','53','54','55','56','57','58','59','60','61','62','63','64','65'
        , '66','67','68','69','70','71','72','73','74','75','76','77','78'
        ]

    stu=Student_Registration.objects.filter(session__id__in=li)
    html = ''
    for i in stu:
        edu=EducationQualification.objects.filter(student=i.id)


        html += 'name ' + str(i.student) + '  ' + 'session ' + str(i.student.session) + '  ' + 'reg '+ '<br>'
        edu.update(cgpa=0.00)

    return HttpResponse(html)


