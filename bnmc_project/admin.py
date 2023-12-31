from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.admin import site
from django.core.exceptions import PermissionDenied
from django.contrib.admin.actions import delete_selected as delete_selected_
from django.views.generic import DeleteView
from django.db.models import Q,F
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import site
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.urls import path
from .render import Render
from django.core import serializers
import json
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django.forms.models import model_to_dict
from django.utils.functional import curry
from dateutil.relativedelta import relativedelta
import datetime
from django.utils.safestring import mark_safe
from django.contrib import admin
from bnmc_project.models import *
from easy_select2 import select2_modelform
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Sum
from functools import reduce

from django.http import QueryDict
from urllib.parse import parse_qs






class StudentFileProgramInline(admin.TabularInline):
    model = StudentFileProgram
    extra = 2
    readonly_fields = ('program_id',)


class Student_file_inline(admin.TabularInline):
    model= Student_file
    extra= 0
    readonly_fields = ('student_registration',)

    def get_formset(self, request, obj=None, **kwargs):
       initial = []
       if request.method == "GET":
           if request.GET.get('program_title', None):
               student_file = StudentFileProgram.objects.filter(program_id__id=request.GET.get('program_title', None))
               if student_file:
                   self.extra=len(student_file)
                   for file in student_file:
                       initial.append({
                           'student_file_program': file,
                            # 'education_type': qualification.education_type,
                            # 'board': qualification.board,
                            # 'roll': qualification.roll,
                            # 'cgpa': qualification.cgpa,
                            # 'year': qualification.year,
                            # 'duration': qualification.duration,
                            # 'country': qualification.country,
                            })
       formset = super(Student_file_inline, self).get_formset(request, obj,**kwargs)
       formset.__init__ = curry(formset.__init__, initial=initial)
       return formset

class qualificationInLine(admin.TabularInline):
    model = Qualification
    extra = 3

class Education_qualificationTabularInline(admin.TabularInline):
    model = EducationQualification
    extra = 0
    readonly_fields = ('students','student')


    def get_formset(self, request, obj=None, **kwargs):
       initial = []
       if request.method == "GET":
           if request.GET.get('program_title', None):
               qualifications=Qualification.objects.filter(program_set__id=request.GET.get('program_title', None))
               if qualifications:
                   self.extra=len(qualifications)+3
                   for qualification in qualifications:
                       initial.append({
                           'level_of_educations': qualification.id,
                            # 'education_type': qualification.education_type,
                            # 'board': qualification.board,
                            # 'roll': qualification.roll,
                            # 'cgpa': qualification.cgpa,
                            # 'year': qualification.year,
                            # 'duration': qualification.duration,
                            # 'country': qualification.country,
                            })
       formset = super(Education_qualificationTabularInline, self).get_formset(request, obj,**kwargs)
       formset.__init__ = curry(formset.__init__, initial=initial)
       return formset

    # def has_add_permission(self, request):
    #
    #     if request.user.is_superuser:
    #         return True
    #
    #     else:
    #         return False

class AdminListFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status_category'

    def lookups(self, request, model_admin):
        return
        (
            ('institutions', 'Approved'),
        )

    def queryset(self, request, queryset):
        return queryset






student_form = select2_modelform(Student_Registration, attrs={'width': '250px'})


class MaleFemaleFilter(admin.SimpleListFilter):
    title = 'sex'
    parameter_name = 'sex'

    def lookups(self, request, model_admin):
        return (
            ('', 'sex'),

        )

    def queryset(self, request, queryset):
        if request.GET.get('sex'):
            student_r=queryset.filter(sex=request.GET.get('sex'))

            return student_r
class RegisterAdmin(admin.ModelAdmin):
    inlines = [Education_qualificationTabularInline,Student_file_inline]
    # readonly_fields = ('image_tag','new_institute','old_institute','approve_by','created_user')
    actions = ['Published','select_print','final_print','approve_to_draft','Unlock']
    list_display = ['get_last_name','fathers_name', 'image_tag','registration_no','status','locked','printed_by','institution','session','program_title']
    fields = ('image_tag','image','first_name', 'registration_no','last_name','date_of_birth','fathers_name','sex','mothers_name',
              'religions','guardians_name','passport_no','relation_to_guardians','quota','nationality',
              'marital_status','national_ID_No','students_mobile_no','division','email_address','district','village',
              'thana','post_office','postal_code','same_address','division_snd','village_snd','district_snd','post_office_snd','thana_snd','postal_code_snd','institution','program_title',
              'program_starting_date','date_of_registration','program_completion_date','payment_method','session','registration_fees','bank_draft_no','bank_draft_date','approved',
              'migration','migration_approval_bnmc','created_by','new_institute','old_institute','migration_date','student_id','approve_by','created_user','locked',
              )
    search_fields = ['registration_no']
    list_per_page = 20
    list_filter = (
        ('institution', RelatedDropdownFilter),
        ('program_title', RelatedDropdownFilter),
        ('status', RelatedDropdownFilter),
        ('institution__catagory', RelatedDropdownFilter),
        ('program_title__category', RelatedDropdownFilter),
        ('institution__type', RelatedDropdownFilter),
        ('session', RelatedDropdownFilter),
        AdminListFilter,MaleFemaleFilter
    )
    # form = student_form

    #list_display_links = ('get_last_name',)


    def get_form(self, request, obj=None, **kwargs):
        self.instance = obj
        return super(RegisterAdmin, self).get_form(request, obj=obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "session" and self.instance:
            kwargs["queryset"] = Session.objects.filter(id=self.instance.session.id)

        if db_field.name == 'session' and not self.instance:
            kwargs["queryset"] = Session.objects.filter(is_active=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_last_name(self,obj):
        if obj.students:
            return mark_safe('<a href="/admin/bnmc_project/student_registration/%s/change/">%s</a>' % (obj.id, obj.students.last_name))

        else:
            return mark_safe('<a href="/admin/bnmc_project/student_registration/%s/change/">%s</a>' % (obj.id, obj.last_name))

    get_last_name.short_description = 'last name'



    def get_result(self,obj):
        if obj.id:
            final_exam_reg=ExaminationStudentRegistration.objects.filter(student_registration=obj.id)
            for fin in final_exam_reg:
                if fin.student_registration:
                    final_exam_result=ExamResultDetails.objects.filter(examStudentInfo=int(fin.id))
                    if final_exam_result:
                        for i in final_exam_result:
                            if i.marks and i.subject.passMarks:
                                if int(i.marks) >= int(i.subject.passMarks):
                                    return 'Pass'

                                else:
                                    return 'Fail'
        return None


    def get_readonly_fields(self, request, obj=None):
        if obj:
            general='General'
            if general != obj.program_title.category.name:
                return ['image_tag','new_institute','old_institute','approve_by','created_user','passport_no','national_ID_No','fathers_name','division',
                        'first_name','last_name','mothers_name','guardians_name','relation_to_guardians','quota',
                        'nationality','date_of_birth','sex','religions','marital_status','students_mobile_no','email_address','district','thana',
                        'village','post_office','postal_code','division_snd','district_snd','thana_snd','village_snd','post_office_snd','postal_code_snd'


                        ]
            else:
                return ['image_tag','new_institute','created_user','old_institute','approve_by']


        else:
            return ['image_tag', 'new_institute', 'created_user','old_institute', 'approve_by']

    # def get_readonly_fields(self, request, obj=None):
    #     is_migration=request.GET.get('migration', None)
    #     if not is_migration:
    #         return ('institution',)
    #     else:
    #         return super(RegisterAdmin, self).get_readonly_fields(request, obj)



    def add_view(self, request, form_url='', extra_context=None):
        program_id= None
        if request.GET.get("program_title"):
            program_id=request.GET.get("program_title")
        else:
            encoded_url= QueryDict(request.GET.urlencode())
            change_list_value=parse_qs(encoded_url.get("_changelist_filters"))
            if change_list_value:
                program_title_param=change_list_value.get("program_title")
                if program_title_param:
                    program_id=program_title_param[0].replace("?","")
        if program_id:
            print(program_id)
            pro_q=Program.objects.get(id=int(program_id))
            extra_context = {
                'var': pro_q.category.name
            }
            if request.GET.get('source', None):
                if int(request.GET.get('source', None)) > 0:
                    license_rec=license_receive.objects.get(id=request.GET.get('source', None))
                    if license_rec.is_old_data == False:
                        license_reg=license_registrations.objects.get(id=license_rec.license_registrations_refference.id)
                        if license_reg:
                            student_reg=Student_Registration.objects.get(id=license_reg.student_registration.id)
                            if student_reg:
                                student_data=Student.objects.get(id=student_reg.students.id)
                                if student_data:
                                    request.GET._mutable=True
                                    request.GET['first_name'] = student_data.first_name
                                    request.GET['last_name'] = student_data.last_name
                                    request.GET['nationality'] = student_data.nationality
                                    request.GET['national_ID_No'] = student_data.national_ID_No
                                    request.GET['division'] = student_data.division
                                    request.GET['district'] = student_data.district
                                    request.GET['thana'] = student_data.thana
                                    request.GET['village'] = student_data.village
                                    request.GET['post_office'] = student_data.post_office
                                    request.GET['postal_code'] = student_data.postal_code
                                    request.GET['institution'] = request.GET.get('institution')
                                    request.GET['program_title'] = request.GET.get("program_title")
                                    request.GET['registration_no'] = student_data.registration_no
                                    request.GET['fathers_name'] = student_data.fathers_name
                                    request.GET['mothers_name'] = student_data.mothers_name
                                    request.GET['sex'] = student_data.sex
                                    request.GET['religions'] = student_data.religions
                                    request.GET['religions'] = student_data.religions
                                    request.GET['students_mobile_no'] = student_data.students_mobile_no
                                    request.GET['division_snd'] = student_data.division_snd
                                    request.GET['district_snd'] = student_data.district_snd
                                    request.GET['thana_snd'] = student_data.thana_snd
                                    request.GET['village_snd'] = student_data.village_snd
                                    request.GET['post_office_snd'] = student_data.post_office_snd
                                    request.GET['postal_code_snd'] = student_data.postal_code_snd



                    elif license_rec.is_old_data:
                        request.GET._mutable = True
                        request.GET['first_name'] = license_rec.students.first_name
                        request.GET['last_name'] = license_rec.students.last_name
                        request.GET['nationality'] = license_rec.students.nationality
                        request.GET['national_ID_No'] = license_rec.students.national_ID_No
                        request.GET['division'] = license_rec.students.division
                        request.GET['district'] = license_rec.students.district
                        request.GET['thana'] = license_rec.students.thana
                        request.GET['village'] = license_rec.students.village
                        request.GET['post_office'] = license_rec.students.post_office
                        request.GET['postal_code'] = license_rec.students.postal_code
                        request.GET['institution'] = request.GET.get('institution')
                        request.GET['program_title'] = request.GET.get("program_title")
                        request.GET['registration_no'] = license_rec.students.registration_no
                        request.GET['fathers_name'] = license_rec.students.fathers_name
                        request.GET['mothers_name'] = license_rec.students.mothers_name
                        request.GET['sex'] = license_rec.students.sex
                        request.GET['religions'] = license_rec.students.religions
                        request.GET['religions'] = license_rec.students.religions
                        request.GET['students_mobile_no'] = license_rec.students.students_mobile_no
                        request.GET['division_snd'] = license_rec.students.division_snd
                        request.GET['district_snd'] = license_rec.students.district_snd
                        request.GET['thana_snd'] = license_rec.students.thana_snd
                        request.GET['village_snd'] = license_rec.students.village_snd
                        request.GET['post_office_snd'] = license_rec.students.post_office_snd
                        request.GET['postal_code_snd'] = license_rec.students.postal_code_snd


        return super(RegisterAdmin, self).add_view(request, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            my_id=request.user.id
            if not None == obj:
                if my_id == obj.created_user.id and obj.approved== False:
                    return True
                elif obj.approved==True:
                    return False

        elif request.user.is_superuser:
            return True




    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):


        extra_context = extra_context or {}
        last_permission = Permission.objects.order_by('display_order').last()

        if object_id is not None:
            student=Student_Registration.objects.get(id=object_id)
            if student.status == last_permission and request.user.can_modify_after_approved== False:
                extra_context['show_save_and_continue'] = False
                extra_context['show_save'] = False


            elif student.status != last_permission:
                extra_context['show_save_and_continue'] = True
                extra_context['show_save'] = True


            elif student.status==last_permission and request.user.can_modify_after_approved == True and request.user.is_superuser==False:
                  extra_context['show_save_and_continue'] = True
                  extra_context['show_save'] = True


            elif request.user.is_superuser:
                extra_context['show_save_and_continue'] = True
                extra_context['show_save'] = True





            #
            # if student:
            #
            #     exit_student_data=Student.objects.get(id=student.students.id)
            #
            #     if exit_student_data:
            #         Student_Registration.first_name=exit_student_data.first_name
            #         Student_Registration.last_name=exit_student_data.last_name
            #         Student_Registration.fathers_name=exit_student_data.fathers_name
            #         Student_Registration.mothers_name=exit_student_data.mothers_name
            #         print(exit_student_data.fathers_name)
                    # (self.fields['first_name'].widget).initial_value = "something"
        return super(RegisterAdmin, self).changeform_view(request, object_id, extra_context=extra_context)



    def changelist_view(self, request, extra_context=None):
        if request.GET.get("approved"):
            self.list_display= ['get_last_name', 'image_tag','registration_no','institution','session','program_title','exam_link']
            self.list_display_links=('',)

        elif request.GET.get('pending'):
            self.list_display = ['get_last_name', 'image_tag', 'registration_no','status', 'institution', 'session', 'program_title']

        elif request.GET.get('license_use'):
            self.list_display=['get_last_name', 'get_result','image_tag','registration_no','institution','session','program_title','Apply_license_exam']

        else:
            self.list_display = ['get_last_name','fathers_name', 'image_tag','registration_no','status','locked','printed_by','institution','session','program_title']


        #if request.GET.get('license_use',None):
            #self.list_display_links=('',)


        extra_context = {
            'progrm_cat': ProgramCatagory.objects.all(),
            'program':Program.objects.all(),
            'InstituteCatagory': InstituteCatagory.objects.all(),
            'Session': Session.objects.all(),
            'InstituteType': InstituteType.objects.all(),
            'ins_name':Institution.objects.all(),
            'status':Permission.objects.all(),
        }
        return super(RegisterAdmin, self).changelist_view(request, extra_context=extra_context)

    template_name = 'admin/student_registration/change_form.html'



    def post(self, request):
        if request.method.POST:
            name = request.POST.get("name")
            url = request.POST.get("imgURL")
            caption = request.POST.get("caption")
            print(name)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)


    def approve_to_draft(self,request,queryset):
        first_permission = Permission.objects.order_by('display_order').first()
        queryset.update(approve_by="",approved=False,registration_no="",status=first_permission)
    approve_to_draft.short_description='Approve to draft'


                 
    def Published(self, request, queryset):
        permission_query_set = Permission.objects.all().order_by('display_order')
        premissions = list(permission_query_set)
        program_short_name = {'DNSM': 71912, 'BSCB': 16476, 'DIM': 4632, 'CSBA': 12350, 'DCN': 1750, 'DPN': 1634,
                              'BNPB': 15502, 'JM': 3064, 'FWB': 8130, 'CP': 4453, 'BSCPHN': 15464}
                                
        for reg_std in queryset:
            if reg_std.status and reg_std.status != permission_query_set.last():
                current_index = premissions.index(reg_std.status)
                if len(premissions) > current_index - 1:
                    reg_std.status = premissions[current_index + 1]
                    if reg_std.status == permission_query_set.last() and reg_std.approved == False:
                        reg_no = 1
                        if program_short_name.get(reg_std.program_title.code, None):
                            reg_no = Student_Registration.objects.filter(program_title__code=reg_std.program_title.code,
                                                                    approved=True).extra(
                                    {'registration_no_int': "CAST(registration_no as INTEGER)"}).order_by(
                                    'registration_no_int').last()
                            if reg_no and  reg_no.registration_no.strip()!="":
                                reg_no=int(reg_no.registration_no)+1
                            else:
                                reg_no=1


                        reg_std.approve_by = request.user
                        reg_std.approved = True
                        is_valid = False
                        while is_valid == False:
                            auto_reg_no = Student_Registration.objects.filter(
                                program_title__code=reg_std.program_title.code, registration_no=reg_no, approved=True)
                            if auto_reg_no:
                                reg_no += 1
                            else:
                                is_valid = True
                        reg_std.registration_no = reg_no
                        reg_std.save()

                        # if reg_std.students:
                        #     if not reg_std.students.has_student_id:
                        #         student_id = int(Student.objects.filter(has_student_id=True).extra(
                        #             {'student_id_int': "CAST(registration_no as INTEGER)"}).order_by(
                        #             'student_id_int').last().registration_no) + 1
                        #         end_loop = False
                        #         while end_loop == False:
                        #             search_student = Student.objects.filter(registration_no=str(student_id))
                        #             if search_student:
                        #                 student_id += 1
                        #             else:
                        #                 end_loop = True
                        #         reg_std.students.registration_no = str(student_id)
                        #         reg_std.students.has_student_id = True
                        #         reg_std.students.save()

    Published.short_description = 'Submit'
    def same_ins(self,request):
        print(request.get.user.staff_institute.institution_name)

    def select_print(self,request,queryset):
        student_query = []
        for i in queryset:
            if i.students:
                student_query.extend(list(Student.objects.filter(id=i.students.id)))
                edu=EducationQualification.objects.filter(student=i.id)
                print(edu,'edu')


        context = {'students': zip(student_query, queryset),
                   'edu':edu
                   }

        return  render(request,'admin/student_info_view_1.html',context)

    select_print.short_description  = 'Print'


    def final_print(self,request,queryset):
            approved_queryset = queryset.filter(approved=True,locked=False)
            locked=queryset.filter(approved=False,locked=False)
            if locked:
                message_bit = "Something wrong"
                return self.message_user(request, "%s " % message_bit)
            if not approved_queryset:
                message_bit = "Locked"
                return self.message_user(request, "%s " % message_bit)

            if approved_queryset:
                queryset.update(locked=True)
                student_query = []
                for i in approved_queryset:
                    if i.students:
                        student_query.extend(list(Student.objects.filter(id=i.students.id)))
                context = {'students': zip(student_query,approved_queryset)
                           }
                return render(request, 'admin/form_2nd.html', context)







                # queryset.update(locked=True,printed_by=request.user)
                # for i in approved_queryset:
                #     print(i)
                    # if q.students:
                    #
                    #     student_id=Student.objects.filter(id=q.students.id)

    final_print.short_description  = 'Student Registration card'


    def Unlock(self,request,queryset):
        queryset_lock=queryset.filter(locked=True)
        if queryset_lock:
            queryset.update(locked=False)

    Unlock.short_description='Unlock forms'



    def response_add(self, request, obj, post_url_continue=None):
       edu=EducationQualification.objects.filter(student=obj.id)

       context={'p':obj,
                'edu':edu

                }

       return render(request,'admin/student_info_view.html',context)









    # def print(self,request,queryset):
    #
    #     approved_queryset=queryset.filter(approved=True)
    #     if not approved_queryset:
    #         return HttpResponseRedirect("Approved student not found")
    #
    #     # data = serializers.serialize('json', approved_queryset, fields=('id','first_name','last_name'))
    #     reg_ids=[]
    #     for reg in approved_queryset:
    #         reg_ids.append(reg.id)
    #
    #     request.session['query_set']=reg_ids
    #
    #     context={'students':approved_queryset}
    #     # request.session["queryset"]=queryset
    #     return  HttpResponseRedirect('/render/pdf/')



    def get_actions(self, request):
        actions = super(RegisterAdmin, self).get_actions(request)
        if not request.user.is_superuser | request.user.can_print_registration_form:
            del actions['final_print']
        if not request.user.is_superuser:
            del actions['approve_to_draft']

        if not request.user.is_superuser:
            del actions['Unlock']

        if not request.user.is_superuser | request.user.is_bnmc_user:
            del actions['Published']

        return actions


    class Meta:
        model=Student_Registration

    def get_queryset(self, request):
        if request.user.is_superuser :
            if request.POST:
                # last_permission = Permission.objects.order_by('display_order').last()
                student_registations=Student_Registration.objects.filter(status__id__in=request.user.show_permission.values_list('id'))
                if request.POST.get('ins_type') and int( request.POST.get('ins_type'))> 0:
                    ins_type=request.POST.get('ins_type')
                    student_registations=student_registations.filter(institution__type__id=ins_type)
                    print(student_registations)
                    # return Student_Registration.objects.filter(Q(institution=ins_type))
                if request.POST.get('progmType') and int(request.POST.get('progmType'))>0:
                    progmType=request.POST.get('progmType')
                    student_registations=student_registations.filter(program_title=progmType)
                if request.POST.get('session') and int(request.POST.get('session'))>0:
                    session = request.POST.get('session')
                    student_registations = student_registations.filter(session=session)
                if request.POST.get('ins_cat') and int(request.POST.get('ins_cat'))>0:
                    ins_cat = request.POST.get('ins_cat')
                    student_registations = student_registations.filter(institution__catagory=ins_cat)
                if request.POST.get('program_category') and int(request.POST.get('program_category')) > 0:
                    program_category = request.POST.get('program_category')
                    student_registations = student_registations.filter(program_title__category=program_category)
                if request.POST.get('ins_name') and int(request.POST.get('ins_name')) > 0:
                    ins_name = request.POST.get('ins_name')
                    student_registations = student_registations.filter(institution=ins_name)

                if request.POST.get('reg_no'):
                    reg_no = request.POST.get('reg_no')
                    student_registations = student_registations.filter(registration_no=reg_no.strip())
                return student_registations

        if request.user.is_staff and request.user.show_permission and request.user.staff_institute:
            if request.POST:
                student_registations = Student_Registration.objects.filter(institution__id__in=request.user.staff_institute.values_list('id'),status__id__in=request.user.show_permission.values_list('id'))
                if request.POST.get('ins_type') and int(request.POST.get('ins_type')) > 0:
                    ins_type = request.POST.get('ins_type')
                    student_registations = student_registations.filter(institution__type=ins_type)
                    print(student_registations)
                    # return Student_Registration.objects.filter(Q(institution=ins_type))
                if request.POST.get('progmType') and int(request.POST.get('progmType')) > 0:
                    progmType = request.POST.get('progmType')
                    student_registations = student_registations.filter(program_title=progmType)
                if request.POST.get('session') and int(request.POST.get('session')) > 0:
                    session = request.POST.get('session')
                    student_registations = student_registations.filter(session=session)
                    print("session" + str(student_registations))
                if request.POST.get('ins_cat') and int(request.POST.get('ins_cat')) > 0:
                    ins_cat = request.POST.get('ins_cat')
                    student_registations = student_registations.filter(institution__catagory=ins_cat)
                    print("ins_cat" + str(student_registations))

                if request.POST.get('program_category') and int(request.POST.get('program_category')) > 0:
                    program_category = request.POST.get('program_category')
                    student_registations = student_registations.filter(program_title__category__id=program_category)
                    print("prog_cat" + str(student_registations))

                if request.POST.get('ins_name') and int(request.POST.get('ins_name')) > 0:
                    ins_name = request.POST.get('ins_name')
                    student_registations = student_registations.filter(institution=ins_name)
                    print("insname" + str(student_registations))

                if request.POST.get('reg_no'):
                    reg_no = request.POST.get('reg_no')
                    student_registations = student_registations.filter(registration_no=reg_no)
                    print("reg" + str(student_registations))
                return student_registations


        #
        # if request.POST.get('ins_name'):
        #     ins_name=request.POST.get('ins_name')
        #     print(ins_name)
        #     return Student_Registration.objects.filter(Q(institution=ins_name))


        qs = super(RegisterAdmin, self).get_queryset(request)


        if request.user.is_superuser:
            print('ccc')
            last_permission = Permission.objects.order_by('display_order').last()
            return Student_Registration.objects.filter(status__id__in=request.user.show_permission.values_list('id'))

        elif request.user.is_staff and request.user.show_permission and request.user.staff_institute and request.GET.get("license_use",None):

            return Student_Registration.objects.filter(institution__id__in=request.user.staff_institute.values_list('id'),approved=True)

        elif request.user.is_staff and request.user.show_permission and request.user.staff_institute and request.GET.get(
                "approved", None):

            return Student_Registration.objects.filter(
                institution__id__in=request.user.staff_institute.values_list('id'), approved=True)

        elif request.user.show_permission and request.user.staff_institute:
            return Student_Registration.objects.filter(status__id__in=request.user.show_permission.values_list('id') , institution__id__in=request.user.staff_institute.values_list('id'))





class Job_history_inline_in_license_receive(admin.TabularInline):
    model = Job_History
    extra = 1
    readonly_fields = ('create_on','edit_on',)
    list_display = ('current_hospital', 'is_running_job','job_starting_date','job_ending_date',)
    exclude = ('student','license_registration_reference')

class Job_history_inline_in_license_registration(admin.TabularInline):
    model = Job_History
    extra = 1
    readonly_fields = ('create_on','edit_on',)
    list_display = ('current_hospital', 'is_running_job','job_starting_date','job_ending_date',)
    exclude = ('student','license_receive_reference',)

class student_admin(admin.ModelAdmin):
    inlines = [Education_qualificationTabularInline, ]
    readonly_fields = ('image_tag',)
    fields = (
    'image_tag', 'image', 'first_name', 'registration_no', 'has_student_id','last_name', 'date_of_birth', 'fathers_name', 'sex','mothers_name',
     'religions', 'guardians_name', 'passport_no', 'relation_to_guardians', 'quota', 'nationality','marital_status',
    'national_ID_No', 'students_mobile_no', 'division', 'email_address', 'district', 'village','thana', 'post_office',
     'postal_code','division_snd','village_snd','district_snd','post_office_snd','thana_snd','postal_code_snd',
    )

    class Meta:
        model=Student

user_form = select2_modelform(User, attrs={'width': '250px'})
class user_search(admin.ModelAdmin):
    search_fields = ('username',)
    fields = ('username','password','is_staff','is_active','is_superuser','is_bnmc_user','allow_for_old_license_add','is_result','can_print_registration_form','can_modify_after_approved','first_name','last_name','email','staff_institute','show_permission','staff_status','result_for_program','result_institute','groups')

    form = user_form
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(user_search, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class license_receive_inline(admin.TabularInline):
    model = re_new_history
    extra = 0
    readonly_fields = ('license','created_on','renew_by','previous_start_date','previous_end_date','new_start_date','new_end_date','license_number','program')

class license_history_admin_inline(admin.TabularInline):
    model = LicenseHistory
    extra = 1
    exclude = ('license_registration_id', 'student_registration_id', 'student_id','renew_history','money_recipte_id',)
    template = 'admin/bnmc_project/license_receive/edit_inline/tabular.html'
    readonly_fields = ('lock','card_serial',)

class InstituteFilter(admin.SimpleListFilter):
    title = 'institute_id'
    parameter_name = 'institute_id'

    def lookups(self, request, model_admin):
        return (
            ('', 'institute_id'),

        )

    def queryset(self, request, queryset):
        if request.GET.get('institute_id') and not request.GET.get('programreal_id') and not request.GET.get('no'):
            print('prooooooooooooo')

            li = LicenseHistory.objects.filter(institution=request.GET.get('institute_id'))

            value_list = li.values_list('license_receive_id', flat=True)
            print(value_list)

            return license_receive.objects.filter(id__in=value_list)

        elif request.GET.get('institute_id') and request.GET.get('programreal_id'):
            li = LicenseHistory.objects.filter(institution=request.GET.get('institute_id'),program=request.GET.get('programreal_id'))

            value_list = li.values_list('license_receive_id', flat=True)
            print(value_list)

            return license_receive.objects.filter(id__in=value_list)

class program_id(admin.SimpleListFilter):
    title = 'programreal_id'
    parameter_name = 'programreal_id'

    def lookups(self, request, model_admin):
        return (
            ('', 'programreal_id'),

        )

    def queryset(self, request, queryset):
        if request.GET.get('programreal_id') and not request.GET.get('no'):



            print('pro')

            li=LicenseHistory.objects.filter(program=request.GET.get('programreal_id'))

            value_list = li.values_list('license_receive_id', flat=True)
            print(value_list)







            return license_receive.objects.filter(id__in=value_list)





class License_number_filter(admin.SimpleListFilter):
    title = 'no'
    parameter_name = 'no'

    def lookups(self, request, model_admin):
        return (
            ('', 'no'),

        )

    def queryset(self, request, queryset):

        if request.GET.get('programreal_id') and request.GET.get('no'):



            print('two')
            li = LicenseHistory.objects.filter(license_number=request.GET.get('no'),program=request.GET.get('programreal_id'))



            value_list = li.values_list('license_receive_id', flat=True)

            return license_receive.objects.filter(id__in=value_list)



        elif request.GET.get('no') and request.GET.get('institute_id'):
            print('lllllllllllllllllllllll')



            li = LicenseHistory.objects.filter(license_number=request.GET.get('no'), institution = request.GET.get('institute_id'))

            value_list = li.values_list('license_receive_id', flat=True)

            return license_receive.objects.filter(id__in=value_list)

        elif request.GET.get('no') and request.GET.get('institute_id') and request.GET.get('programreal_id'):

            li = LicenseHistory.objects.filter(license_number=request.GET.get('no'),
                                               institution=request.GET.get('institute_id'),
                                               program=request.GET.get('programreal_id'))

            value_list = li.values_list('license_receive_id', flat=True)

            return license_receive.objects.filter(id__in=value_list)

        elif  request.GET.get('no'):
            print('nooooooooooooo')
            list_of_items=[]
            license_history=LicenseHistory.objects.filter(license_number=request.GET.get('no'))
            for i in license_history:
                list_of_items.append(i.license_receive_id.id)


            for o in license_receive.objects.filter(id__in=list_of_items):
                print(o.status)
            return license_receive.objects.filter(id__in=list_of_items)

class working_inline(admin.TabularInline):
    model= WorkingDetails
    extra= 1

class t_admin(admin.TabularInline):
    model= TrainingDetails
    extra= 1

class license_receive_admin(admin.ModelAdmin):
    search_fields = ['first_name',]
    inlines = [license_receive_inline,license_history_admin_inline,working_inline,t_admin]
    exclude = ('renew_history','job_history_reffer')
    list_display = ('last_name','institution','fathers_name','program','get_license_number','start_date','end_date')
    fields = ('image_tag','image','first_name','last_name','fathers_name','mothers_name','date_of_birth','sex','religions','marital_status','nationality',
              'quota','national_ID_No','guardians_name','relation_to_guardians','passport_no','students_mobile_no','email_address','permanent','division','village','district','post_office','thana',
              'postal_code','exam_name','registration_no','license_registration_fee','payment_method','bank_draft_no','registration_fee','same_address',
              'present','division_snd','village_snd','district_snd','post_office_snd','thana_snd','postal_code_snd','bank_draft_date','month_info','is_old_data','students','sig','signature'
              ,'program','institution','late','license_registrations_refference'


              )

    def get_readonly_fields(self, request, obj=None):

        if request.GET.get("id") and obj is None:
            return ('image_tag', 'students', 'is_old_data', 'permanent', 'present','sig')

        elif obj is not None and obj.is_old_data == True:
            return ('image_tag', 'students', 'is_old_data', 'permanent', 'present','sig')



        elif request.user.allow_for_old_license_add and obj is None:
            return ('image_tag','students','permanent','present','sig')

        else:
            return ('image_tag', 'students','is_old_data','permanent','present','sig')



    def get_license_number(self,obj):
        if obj is not None:
            lic_his=LicenseHistory.objects.filter(license_receive_id=obj.id)
            if lic_his:
                return [i.license_number for i in lic_his]

    def start_date(self,obj):
        if obj is not None:
            lic_his = LicenseHistory.objects.filter(license_receive_id=obj.id)
            if lic_his:
                lic_his = lic_his[0]
                return lic_his.license_start_date

    def end_date(self,obj):
        if obj is not None:
            lic_his = LicenseHistory.objects.filter(license_receive_id=obj.id)
            if lic_his:
                lic_his = lic_his[0]
                return lic_his.license_end_date


    def program(self,obj):
        if obj is not None:
            lic_his = LicenseHistory.objects.filter(license_receive_id=obj.id)
            if lic_his:

                lic_his = lic_his[0]
                return lic_his.program

    actions=['print_license','Approved']
    raw_id_fields = ['license_registrations_refference','students']
    list_filter = (
        ('institution', RelatedDropdownFilter),
        ('license_registrations_refference__exam_title', RelatedDropdownFilter),
        ('license_registrations_refference__status', RelatedDropdownFilter),
        ('institution__catagory', RelatedDropdownFilter),
        ('license_registrations_refference__centre', RelatedDropdownFilter),
        ('institution__type', RelatedDropdownFilter),
        ('program__category', RelatedDropdownFilter),
        ('license_registrations_refference__session', RelatedDropdownFilter),
        ('license_registrations_refference__session', RelatedDropdownFilter),
        ('license_registrations_refference__session', RelatedDropdownFilter),
       License_number_filter,program_id,InstituteFilter
    )

    def get_queryset(self, request):
        qs = super(license_receive_admin, self).get_queryset(request)

        if request.user.is_superuser:
            return license_receive.objects.all()

        if request.user.is_staff and request.user.show_permission and request.user.staff_institute and not request.user.is_superuser:



            return license_receive.objects.filter(status__id__in=request.user.show_permission.values_list('id'),

                                       institution__id__in=request.user.staff_institute.values_list('id'))

    def response_add(self, request, obj, post_url_continue=None):
       if request.GET.get("id"):
            license_id = license_registrations.objects.get(id=request.GET.get("id"))
            if license_id:
                stu_status = Student_Registration.objects.get(id=license_id.student_registration.id)
                education_qulification = EducationQualification.objects.filter(students=stu_status.students.id)
                works=WorkingDetails.objects.filter(license=obj.id).last()
                context = {'license_id': stu_status,
                           'education_qulification': education_qulification,
                           'reg': license_id,
                           'works':works
                           }
            return render(request, 'admin/license_form.html',context)

       else:
           return HttpResponseRedirect('/admin/bnmc_project/license_receive/')

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            'progrm_cat': ProgramCatagory.objects.all(),
            'program':Program.objects.all(),
            'InstituteCatagory': InstituteCatagory.objects.all(),
            'Session': Session.objects.all(),
            'InstituteType': InstituteType.objects.all(),
            'ins_name':Institution.objects.all(),
            'status':Permission.objects.all(),
        }
        return super(license_receive_admin, self).changelist_view(request, extra_context=extra_context)

    def Approved(self,request,queryset):
        for record in queryset:
            reg_number= record.license_registrations_receive_id
            if not reg_number:
                reg_number=0
            validate=False
            while not validate:
                print(record)
                exist_record=license_receive.objects.filter(license_registrations_receive_id=reg_number)
                if exist_record:
                    reg_number+=1
                else:
                    validate=True
                    record.license_registrations_receive_id=reg_number
                    record.save()
                    print("got "+str(reg_number)+"  "+str(record))

    def add_view(self, request, form_url='', extra_context=None):
        if request.GET.get("id",None):
            if not request.GET._mutable:
                request.GET._mutable = True
            license_reg = license_registrations.objects.get(pk=request.GET.get("id"))
            student_reg=Student.objects.get(pk=license_reg.student_registration.students.id)
            request.GET['first_name']=license_reg.first_name
            request.GET['religions']=license_reg.religions
            request.GET['registration_no']=license_reg.registration_no
            request.GET['last_name']=license_reg.last_name
            request.GET['fathers_name']=student_reg.fathers_name
            request.GET['mothers_name']=student_reg.mothers_name
            request.GET['sex']=student_reg.sex
            request.GET['marital_status']=student_reg.marital_status
            request.GET['quota']=student_reg.quota
            request.GET['guardians_name']=student_reg.guardians_name
            request.GET['relation_to_guardians']=student_reg.relation_to_guardians
            request.GET['passport_no']=student_reg.passport_no
            request.GET['email_address']=student_reg.email_address
            request.GET['nationality']=student_reg.nationality
            request.GET['date_of_birth']=student_reg.date_of_birth
            request.GET['national_ID_No']=student_reg.national_ID_No
            request.GET['division']=student_reg.division
            request.GET['district']=student_reg.district
            request.GET['thana']=student_reg.thana
            request.GET['village']=student_reg.village
            request.GET['post_office']=student_reg.post_office
            request.GET['postal_code']=student_reg.postal_code

            request.GET['division_snd'] = student_reg.division
            request.GET['district_snd'] = student_reg.district
            request.GET['thana_snd'] = student_reg.thana
            request.GET['village_snd'] = student_reg.village
            request.GET['post_office_snd'] = student_reg.post_office
            request.GET['postal_code_snd'] = student_reg.postal_code

            request.GET['program']=license_reg.program
            request.GET['institution']=license_reg.institution
            request.GET['exam_name']=license_reg.exam_title
            request.GET['license_registrations_id']=request.GET.get("id")
            request.GET['license_registrations_refference']=license_reg
            if license_reg.student_id:
                request.GET['student_id'] = license_reg.student_id



            
            #print(str(request.GET['license_registrations_id'])+" dfgdtg")
        return super(license_receive_admin, self).add_view(request, form_url, extra_context)

    def print_license(self,request,queryset):
        for obj_id in queryset:
            get_re_new=re_new_history.objects.filter(license=obj_id.id).last()
        context={"licenses":queryset,
                 "get_re_new":get_re_new,
                 }
        return render(request,'admin/regCard.html',context)


class rendom_filter(admin.SimpleListFilter):
    title = 'rendom'
    parameter_name = 'rendom'

    def lookups(self, request, model_admin):
        return
        (
            ('rendom', 'rendo'),
        )

    def queryset(self, request, queryset):
        return queryset

class license(admin.ModelAdmin):
    inlines = [Job_history_inline_in_license_registration, ]
    readonly_fields = ('image_li','image_tag_li','image_tag_lis','image_second')

    fields=('centre','image_field','image_li','image_second','image','image_sec','session', 'registration_no','exam_title','date_of_passing_on', 'last_name', 'sex', 'fathers_name','religions',
     'mothers_name','nationality', 'students_mobile_no','institution','text_field', 'division','village', 'district','post_office', 'thana','received_filter',
     'postal_code','pass_mark','approved','hall_name','rool_number','room_name','image_tag_li','image_tag_lis','signature_first','program','student_registration')
    search_fields = ('first_name', 'registration_no','rool_number')
    actions=['admit_card','Published','print_license','approve_to_draft']
    list_display = ['get_last_name','image_li','image_tag_li','registration_no','institution','rool_number','status','print_licence','license_receive_link','exam_title','program']
    raw_id_fields = ["student_registration",'program']
    #list_editable = ('status',)
    list_filter = (
        ('institution', RelatedDropdownFilter),
        ('exam_title', RelatedDropdownFilter),
        ('status', RelatedDropdownFilter),
        ('institution__catagory', RelatedDropdownFilter),
        ('centre', RelatedDropdownFilter),
        ('institution__type', RelatedDropdownFilter),
        ('program__category', RelatedDropdownFilter),
        ('program', RelatedDropdownFilter),
        ('session', RelatedDropdownFilter),AdminListFilter,rendom_filter
    )
    list_per_page = 10


    def approve_to_draft(self,request,queryset):
        first_permission = Permission.objects.order_by('display_order').first()
        queryset.update(approve_by="",approved=False,registration_no="",status=first_permission)
    approve_to_draft.short_description='Approve to draft'



    def get_last_name(self,obj):
        if obj.student_registration:
            student_id=Student_Registration.objects.get(id=obj.student_registration.id)
            if student_id.students:
                query_student=Student.objects.get(id=student_id.students.id)
                if query_student.last_name:
                    return mark_safe('<a href="/admin/bnmc_project/license_registrations/%s/change/">%s</a>' % (obj.id, query_student.last_name))
                else:
                    return None
            else:
                return None
        else:
            return None
    get_last_name.short_description = 'last name'



    def changelist_view(self, request, extra_context=None):

        if request.GET.get('received_filter',None):
            self.list_display_links = ('',)

        extra_context = {
            'progrm_cat': ProgramCatagory.objects.all(),
            'program':Program.objects.all(),
            'InstituteCatagory': InstituteCatagory.objects.all(),
            'Session': Session.objects.all(),
            'InstituteType': InstituteType.objects.all(),
            'ins_name':Institution.objects.all(),
            'status':Permission.objects.all(),
            'exam':Exam.objects.all(),
        }
        return super(license, self).changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        if request.GET.get("registration_no", None):
            reg_number = request.GET.get("registration_no")
            if not request.GET._mutable:
                request.GET._mutable = True
            program_id = 0
            try:
                program_id = int(request.GET.get("program_title"))
            except:
                program_id = 0
            student_infos = Student_Registration.objects.filter(registration_no=reg_number,program_title__id=program_id)
            get_exam=Exam.objects.filter(date_active=True).first()
            if student_infos:
                student_infos = student_infos[0]
                request.GET['first_name'] = student_infos.first_name
                request.GET['last_name'] = student_infos.last_name
                request.GET['nationality'] = student_infos.nationality
                request.GET['national_ID_No'] = student_infos.national_ID_No
                request.GET['division'] = student_infos.division
                request.GET['district'] = student_infos.district
                request.GET['thana'] = student_infos.thana
                request.GET['village'] = student_infos.village
                request.GET['post_office'] = student_infos.post_office
                request.GET['postal_code'] = student_infos.postal_code
                request.GET['program'] = student_infos.program_title
                request.GET['institution'] = student_infos.institution
                request.GET['program_title'] = request.GET.get("program_title")
                request.GET['created_at'] = datetime.datetime.now()
                request.GET['registration_no'] = student_infos.registration_no
                request.GET['session'] = student_infos.session
                request.GET['fathers_name'] = student_infos.fathers_name
                request.GET['mothers_name'] = student_infos.mothers_name
                request.GET['sex'] = student_infos.sex
                request.GET['religions'] = student_infos.religions
                request.GET['religions'] = student_infos.religions
                request.GET['students_mobile_no'] = student_infos.students_mobile_no
                request.GET['received_filter'] = 1
                request.GET['image_field'] = (student_infos.image)
                request.GET['student_registration'] = student_infos
                request.GET['exam_title']= get_exam
                if student_infos.students:
                    request.GET['student_id'] = student_infos.students.id
             
        return super(license, self).add_view(request, form_url, extra_context)


    def Published(self,request,queryset):
        permission_query_set=Permission.objects.all().order_by('display_order')
        premissions=list( permission_query_set)
        program_short_name = {
                                'DNSM':100001 ,'DIM':200001 ,'BSCB':300001,
                                'BNPB':400001,'DPN':500001,'DCN':600001,
                                'FWV':700001,'JM':800001,'CP':900001,'CSBA':110001
                             }
        for reg_std in queryset:
            if reg_std.status and reg_std.status!=permission_query_set.last():
               current_index= premissions.index(reg_std.status)
               if len(premissions) >current_index-1:
                   reg_std.status=premissions[current_index+1]
                   if reg_std.status==permission_query_set.last() and reg_std.approved==False:
                           reg_no = 1
                           if program_short_name.get(reg_std.program.code,None):
                               reg_no=program_short_name[reg_std.program.code]

                           if program_short_name.get(reg_std.program.code, None):
                               reg_no = license_registrations.objects.filter(
                                   program__code=reg_std.program.code,
                                   approved=True).extra(
                                   {'rool_number_int': "CAST(rool_number as INTEGER)"}).order_by(
                                   'rool_number_int').last()
                               if reg_no and reg_no.rool_number != "":
                                   reg_no = int(reg_no.rool_number) + 1
                               else:
                                   reg_no = 1


                           reg_std.approve_by=request.user
                           reg_std.approved = True
                           is_valid=False
                           while  is_valid==False:
                               auto_reg_no = license_registrations.objects.filter(program__code=reg_std.program.code,rool_number=reg_no)
                               if auto_reg_no:
                                   reg_no+=1
                               else:
                                   is_valid=True
                           reg_std.rool_number=reg_no
                   reg_std.save()

    def get_queryset(self, request):
        #return license_registrations.objects.filter( program_title__pass_mark__gte = F('pass_mark'))
        print(self.list_display,"------------------------------------")
        licence_regs= license_registrations.objects.all()
        

        if request.GET.get('rendom',None):
            print('rendom')
            last_permission = Permission.objects.order_by('display_order').first()
            return license_registrations.objects.filter(program=request.GET.get('program__id__exact',None),status=last_permission,institution__id__in=request.user.staff_institute.values_list('id')).order_by('?')



        if request.user.is_superuser and request.GET.get("received_filter",None):
            licence_regs=licence_regs.filter(exam_title__pass_mark__lte = F('pass_mark'),approved=True)
            return licence_regs
            print('super pere')

        if request.user.is_staff and request.GET.get("received_filter", None) and not request.user.is_superuser:
            licence_regs = licence_regs.filter(exam_title__pass_mark__lte=F('pass_mark'),approved=True,institution__id__in=request.user.staff_institute.values_list('id').all())
            print('ooo')
            return licence_regs

        if request.user.is_superuser and request.user.show_permission and request.user.staff_institute:
            print('jjj')
            last_permission = Permission.objects.order_by('display_order').last()

            return license_registrations.objects.all()

            print('super')
        if request.user.is_staff and request.user.show_permission and request.user.staff_institute:
            print('kk')
            last_permission = Permission.objects.order_by('display_order').last()
            print("form admin",licence_regs.filter(status__id__in=request.user.show_permission.values_list('id')).all())
            return licence_regs.filter(status__id__in=request.user.show_permission.values_list('id'),
                                       institution__id__in=request.user.staff_institute.values_list('id')).all()


    def admit_card(self,request,queryset):
        context = {'students': queryset}
        return  render(request,'admin/admit_card_.html',context)
    admit_card.short_description  = 'admit'

    # def first_print_form(self,request,queryset):
    #     for p in queryset:
    #         var=p.registration_no
    #         student_info=Student_Registration.objects.filter(registration_no=var)
    #         print("ssss"+str(student_info))
    #         context={'student_info':student_info}
    #     return render(request,'admin/first.html',context)
    #
    # first_print_form.short_description = 'print forms'


    def get_actions(self, request):
        actions = super(license, self).get_actions(request)
     
        if not request.user.is_superuser and not request.user.is_bnmc_user:
            del actions['admit_card']

        if not request.user.is_superuser and not request.user.is_bnmc_user:
            del actions['Published']



        if not request.user.is_superuser | request.user.is_bnmc_user:
            del actions['approve_to_draft']

        return actions


    def response_add(self, request, obj, post_url_continue=None):
            context = {'p': obj
                   }
            return render(request, 'admin/comprehenshive_exam_form.html', context)

class DistrictListFilter(admin.SimpleListFilter):
    title = 'name'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        return
        (
            ('name', 'division'),
        )

    def queryset(self, request, queryset):
        return queryset

class ExaminationRegistrationFilter(admin.SimpleListFilter):
    title="create_on"
    parameter_name = 'create_on'
    def lookups(self, request, model_admin):
        return
        (
            ('exam', 'subjects'),
        )
    def queryset(self, request, queryset):
        return queryset



class AmountHistoryFilter(admin.SimpleListFilter):
    title="create_on"
    parameter_name = 'create_on'
    def lookups(self, request, model_admin):
        return
        (
            ('account', 'historyType'),
        )
    def queryset(self, request, queryset):
        return queryset


class District_admin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = (
        ('division', RelatedDropdownFilter),
        DistrictListFilter
    )
                    
class Thana_admin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = (
        ('district', RelatedDropdownFilter),
        #('district__division', RelatedDropdownFilter),
        DistrictListFilter
    )

class Program_admin(admin.ModelAdmin):
    search_fields = ('title',)
    inlines = [qualificationInLine,StudentFileProgramInline]
    list_display = ['title','second_code','code']
                
class Institution_admin(admin.ModelAdmin):
    search_fields = ('institution_name',)
    actions = ['delete_selected']

    def delete_selected(self, request, obj):
        for o in obj.all():
            User.objects.update(staff_institute='')
            o.delete()

    delete_selected.short_description = 'test'

    def delete_view(self, request, object_id, extra_context=None):
        self.template_name  = 'confirm_delete_someitems.html'
        return super(Institution_admin, self).delete_view(request, object_id, extra_context)

    def delete_model(self, request, obj):
        for modelb_obj in obj.institution_name.all():
            User.objects.update(staff_institute='')
            modelb_obj.delete()
        return super(Institution_admin, self).delete_model(request, obj)

class EducationQualification_admin(admin.ModelAdmin):
    search_fields = ('education_type','level_of_education')
    readonly_fields = ('student','students','institution_name')

class Job_History_Admin(admin.ModelAdmin):
    readonly_fields = ('student','create_on','edit_on')

class ExamResultDetailsInline(admin.TabularInline):
    model = ExamResultDetails
    extra = 0
    readonly_fields = ('create_on','subject','passMarks','get_grad','get_grad_point')
    fields = ('subject','passMarks','marks', 'create_on','get_grad','get_grad_point')

subjects_form = select2_modelform(ExamSubject, attrs={'width': '250px'})


class SubSubject_inline(admin.TabularInline):
    model = SubSubject

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            sub = SubSubjectName.objects.all().last()
            if sub:

                initial.append({
                    'subject_name': sub,
                    # 'education_type': qualification.education_type,
                    # 'board': qualification.board,
                    # 'roll': qualification.roll,
                    # 'cgpa': qualification.cgpa,
                    # 'year': qualification.year,
                    # 'duration': qualification.duration,
                    # 'country': qualification.country,
                })
        formset = super(SubSubject_inline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

class ExamSubject_admin(admin.ModelAdmin):
    readonly_fields = ['create_on',]
    list_display = ['name','isMainSubject','passMarks','fullMarks','year','program']
    form = subjects_form
    inlines = [SubSubject_inline]
    fields = ('program','year','name','fullMarks','passMarks','code','discription','create_on','is_active',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id is not None:
            self.object_id = object_id
        return self.changeform_view(request, object_id, form_url, extra_context)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "SubSubjects":
            kwargs["queryset"] = ExamSubject.objects.filter(isMainSubject=False,SubSubjects=None)
        return super().formfield_for_manytomany(db_field, request, **kwargs)



    # def formfield_for_foreignkey(self,db_field, request, **kwargs):
    # 
    # 
    #     if self.object_id and db_field.name == "year":
    #         exam_sub=ExamSubject.objects.get(id=self.object_id)
    #         kwargs["queryset"] = ExamYear.objects.filter(program=exam_sub.program)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)




class BalanceHistoryChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super(BalanceHistoryChangeList, self).get_results(*args, **kwargs)
        q = self.result_list.aggregate(values=Sum('amount'))
        print(self.result_list)
        self.values_count = q['values']
        print(self.values_count)



class reg_no_filter(admin.SimpleListFilter):
    title = 'Registration_no'
    parameter_name = 'Registration_no'

    def lookups(self, request, model_admin):
        return (
            ('', 'reg_no'),
        )



    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student_reg__registration_no=self.value())


class reg_no_filter_ex(admin.SimpleListFilter):
    title = 'Registration_no'
    parameter_name = 'Registration_no'

    def lookups(self, request, model_admin):
        return (
            ('', 'reg_no'),


        )



    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student_registration__registration_no=self.value())


class exam_student(admin.SimpleListFilter):

    title = 'exam'
    parameter_name = 'exam'
    def lookups(self, request, model_admin):
        return
        (
            ('subjects','program','exam',),
        )

    def queryset(self, request, queryset):
        return queryset

from django.db import models

from django.forms import CheckboxSelectMultiple

class ExaminationRegistrationAdmin(admin.ModelAdmin):
    inlines = []
    raw_id_fields = ["student_registration"]
    list_display = ['exam','student_id','image_tag','student_registration','program','institute','roll_number']
    list_filter = (
                ('program', RelatedDropdownFilter),
                ('institute', RelatedDropdownFilter),
                ( 'exam', RelatedDropdownFilter), reg_no_filter_ex
    )
    readonly_fields = ['edit_on','create_on','image_tag','center']
    actions = ['Published', 'admit_card', ]
    fields = ['program','exam','year','student_id','subjects','last_name','fathers_name','mothers_name','students_mobile_no','division',
              'district','thana','village','post_office','publish_result','institute','create_on','edit_on','image_tag','roll_number','student_registration'
              ]

    # checkbox---------
    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    # }

    # filter_horizontal=('subjects',)
    #def save_formset(self, request, forms, formset, change):
    #    formset.save()
    #    print(forms,"is self dddd")
    # def get_readonly_fields(self, request, obj=None):
    #
    #     if request.user.is_staff and request.user.is_superuser== False:
    #         return ('create_on','edit_on','last_name','fathers_name','mothers_name','nationality','sex','religions','status','division',
    #                    'district','thana','village','post_office','postal_code','publish_result')
    #
    #
    #     elif request.user.is_superuser:
    #         return (
    #         'create_on', 'edit_on', 'last_name', 'fathers_name', 'mothers_name', 'nationality', 'sex', 'religions',
    #         'status', 'division',
    #         'district', 'thana', 'village', 'post_office', 'postal_code',)
    #
    #     elif request.user.is_result:
    #
    #         return (
    #             'create_on', 'edit_on', 'last_name', 'fathers_name', 'mothers_name', 'nationality', 'sex', 'religions',
    #             'status', 'division',
    #             'district', 'thana', 'village', 'post_office', 'postal_code',)




    def admit_card(self,request,queryset):
        headers = [[] for i in range(0, len(queryset))]
        minus=-1
        for i in queryset:
            subject_count = ExamSubject.objects.filter(program=i.program).order_by('id')


            minus += 1
            headers[minus].append(subject_count)


        context = {'students': zip(queryset,headers),
                   'subs': subject_count,
                   'sports':headers,
                   'empty':''}
        return  render(request,'admin/finalexamadmit.html',context)
    admit_card.short_description  = 'admit'

    def Published(self, request, queryset):
        permission_query_set = Permission.objects.all().order_by('display_order')
        premissions = list(permission_query_set)
        program_short_name = {'DCN': 600001,
                          'JM': 800001, 'CP': 900001,'CSBA':1100001}

        for reg_std in queryset:
            if reg_std.status and reg_std.status != permission_query_set.last():
                current_index = premissions.index(reg_std.status)
                if len(premissions) > current_index - 1:
                    reg_std.status = premissions[current_index + 1]
                    if reg_std.status == permission_query_set.last() and reg_std.approved == False:
                        reg_no = 1
                        if program_short_name.get(reg_std.program.code, None):
                            reg_no = ExaminationStudentRegistration.objects.filter(program__code=reg_std.program.code,
                                                                         approved=True).extra(
                                {'roll_number_int': "CAST(roll_number as INTEGER)"}).order_by(
                                'roll_number_int').last()
                            if reg_no and reg_no.roll_number != "":
                                reg_no = int(reg_no.roll_number) + 1
                            else:
                                reg_no = 1

                        # reg_std.approve_by = request.user
                        reg_std.approved = True
                        is_valid = False
                        while is_valid == False:
                            auto_reg_no = ExaminationStudentRegistration.objects.filter(
                                program__code=reg_std.program.code, roll_number=reg_no, approved=True)
                            if auto_reg_no:
                                reg_no += 1
                            else:
                                is_valid = True
                        reg_std.roll_number = reg_no
                        reg_std.save()


    Published.short_description = 'Submit'
    def response_add(self, request, obj, post_url_continue=None):
            context = {'p': obj,
                       'sub':obj.subjects.all()
                   }
            return render(request, 'admin/comprehenshive_exam_form.html', context)

    def get_queryset(self, request):
        qs = super(ExaminationRegistrationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return ExaminationStudentRegistration.objects.all()

        elif request.user.is_staff and request.user.result_institute and request.user.result_for_program and request.user.is_result:
            return ExaminationStudentRegistration.objects.filter(institute__id__in=request.user.result_institute.values_list('id'),program__id__in=request.user.result_for_program.values_list('id'))


        elif request.user.is_staff and request.user.staff_institute:
            return ExaminationStudentRegistration.objects.filter(institute__id__in=request.user.staff_institute.values_list('id'))


    def changelist_view(self, request, extra_context=None):








        extra_context = {
        'exam':Final_exam.objects.all(),
        'sub':ExamSubject.objects.all(),
        'program':Program.objects.all(),
        'institute':Institution.objects.all(),
        }
        return super(ExaminationRegistrationAdmin, self).changelist_view(request, extra_context=extra_context)

    # def get_queryset(self, request):
    #
    #     return None

    def change_view(self, request, object_id, extra_content=None):
        if request.user.is_result or request.user.is_superuser:
            self.inlines=[ExamResultDetailsInline,]



        return super(ExaminationRegistrationAdmin, self).change_view(request, object_id)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []

        if request.GET.get("student_registration",None):
            student_reg=Student_Registration.objects.get(id=request.GET.get("student_registration",None))
            if student_reg:
                student_id=Student.objects.get(id=student_reg.students.id)
                if student_id:
                    request.GET._mutable=True
                    request.GET['last_name'] = student_id.last_name
                    request.GET['fathers_name'] = student_id.fathers_name
                    request.GET['sex'] = student_id.sex
                    request.GET['mothers_name'] = student_id.mothers_name
                    request.GET['marital_status'] = student_id.marital_status
                    request.GET['division'] = student_id.division
                    request.GET['district'] = student_id.district
                    request.GET['thana'] = student_id.thana
                    request.GET['village'] = student_id.village
                    request.GET['post_office'] = student_id.post_office
                    request.GET['postal_code'] = student_id.postal_code
                    request.GET['nationality'] = student_id.nationality
                    request.GET['student_id'] = student_reg.registration_no




        return super(ExaminationRegistrationAdmin, self).add_view(request, form_url='', extra_context=None)
    #
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #
    #     if request.GET.get("year",None) and db_field.name == "exam":
    #         kwargs["queryset"] = Final_exam.objects.filter(year=request.GET.get("year",None))
    #
    #
    #     if not request.GET.get("year",None) and db_field.name == "exam":
    #         kwargs["queryset"] = Final_exam.objects.filter(year=None)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
    #
    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if request.GET.get("exam", None) and db_field.name == "subjects":
    #         exam_search = Final_exam.objects.get(id=request.GET.get("exam", None))
    #         if exam_search:
    #             kwargs["queryset"] = exam_search.subjects.all()
    #
    #     if not request.GET.get ("exam", None) and db_field.name == "subjects":
    #         kwargs["queryset"] = Final_exam.objects.filter(subjects=None)
    #
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

class ExamResultDetailsAdmin(admin.ModelAdmin):
    readonly_fields = ['create_on',"passMarks","get_grad","get_grad_point"]
    list_display = ['subject','passMarks','get_grad','get_grad_point']

class AccountsAdmin(admin.ModelAdmin):
    readonly_fields = ['create_on',"edit_on"]
    list_display = ['accountNumber','bank_raffer','edit_on',]



class BalanceHistory_filter(admin.SimpleListFilter):
    title = 'historyType'
    parameter_name = 'historyType'

    def lookups(self, request, model_admin):
        return (
            ('Add_balance', 'Add balance'),
            ('Remove_balance', 'Remove balance'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Add_balance':
            return queryset.filter(historyType=BalanceHistory.add)
        if self.value() == 'Remove_balance':
            return queryset.filter(historyType=BalanceHistory.remove)

BalanceHistory_form = select2_modelform(BalanceHistory, attrs={'width': '250px'})

class BalanceHistoryAdmin(admin.ModelAdmin):    
    readonly_fields = ['create_on',"edit_on",'getTransfarLocation','amount','IsApproved','approvedBy','approvDate','get_add_or_remove']
    list_display = ['account','IsApproved','amount','getTransfarLocation','get_add_or_remove','total']
    form = BalanceHistory_form
    fields=('account','student_reg','instituition','historyType','BalanceIncomes','amount','Note','create_on','edit_on'
            ,'IsApproved','approvedBy','approvDate','bankBranch','bankIssueDate','id_no','number_of_item','total')
    form = BalanceHistory_form

    raw_id_fields = ["student_reg","instituition"]
    def get_changelist(self, request):
        return BalanceHistoryChangeList
    list_filter = (
        ('account', RelatedDropdownFilter)
        ,BalanceHistory_filter,reg_no_filter
    )

    def changelist_view(self, request, extra_context=None):

        banances=BalanceHistory.objects.all().filter(IsApproved=True)
        removedBalances = banances.filter(historyType='2')
        addedBalances=banances.filter(historyType='1')
        addedAmounts=0
        removedAmounts=0

        if removedBalances:
            removedAmounts=reduce(lambda x, y: x+y, removedBalances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True))

        if addedBalances:
            addedAmountsObjects= addedBalances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True)
            if addedAmountsObjects:
                addedAmounts=reduce(lambda x, y: x+y, addedBalances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True))

        totalAmounts=addedAmounts-removedAmounts

        # #removedBalances=banances.filter(historyType='2')
        # balanceAmounts=addedBalances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True)
        # totalAmounts=banances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True)
        # totalRequesedtAmount=0
        # totalApprovedAmounts=0
        #
        # if totalAmounts:
        #     totalRequesedtAmount= reduce(lambda x, y: x+y, totalAmounts)
        #
        # if balanceAmounts:
        #     totalApprovedAmounts= reduce(lambda x, y: x+y, balanceAmounts)

        #totalRemoved=reduce(lambda x, y: x+y, removedBalances.filter(amount__isnull= False,amount__gt=1).all().values_list('amount', flat=True))  
        extra_context = {
            # 'totalAmounts':totalRequesedtAmount,
            # #'addedBalanceTimes':len(addedBalances),
            # #'removedBalanceTimes': len(removedBalances),
            # 'totalApprovedAmounts': totalApprovedAmounts,
            #'totalRemoved': totalRemoved,
            'totalAmounts':totalAmounts,
            'addedAmounts':addedAmounts,
            'removedAmounts':removedAmounts,


            'ins': Institution.objects.all(),
            'Accounts': Accounts.objects.all(),
            'program': Program.objects.all()
        }
        return super(BalanceHistoryAdmin, self).changelist_view(request, extra_context=extra_context)


#def save_formset(self, request, forms, formset, change):
#    formset.save_m2m()


class TransfarBalanceAdmin(admin.ModelAdmin):
    readonly_fields = ['create_on',"edit_on"]
    list_display = ['FromAccount','ToAccount','amount','Note',]





class institition_profile_filter(admin.SimpleListFilter):

    title = 'institute'
    parameter_name = 'institute'
    def lookups(self, request, model_admin):
        return
        (
            ('institute_name'),
        )

    def queryset(self, request, queryset):
        return queryset



class nurse_type_filter(admin.SimpleListFilter):
    title = 'nurse_type'
    parameter_name = 'nurse_type'

    def lookups(self, request, model_admin):
        return (
            ('nurse', 'Nurse'),
            ('non_nurse', 'Non-Nurse'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'nurse':
            return queryset.filter(employment_type=1)
        if self.value() == 'non_nurse':
            return queryset.filter(employment_type=2)


ins_form = select2_modelform(IntuitionProfile, attrs={'width': '250px'})
class institute_profile_admin(admin.ModelAdmin):
    fields = ['Image_View','is_nurse','student','license_number','image','institute_name','employment_type','designation','faculty_id','date_of_joining','work_starting_date','full_name_english','father_name'
              ,'mother_name','sex','date_of_birth','marital_status','students_mobile_no','email_address','division','district','thana','village','post_office','postal_code','nationality'
              ]
    raw_id_fields = ['student',]
    list_display = ['get_full_name','institute_name','designation','license_number']
    form = ins_form
    list_filter =  (
        ('institute_name', RelatedDropdownFilter),
        ('division', RelatedDropdownFilter)

        ,institition_profile_filter,nurse_type_filter)

    def get_full_name(self,obj):
        if obj.student:
            return obj.student.last_name

        elif obj.student==None:
            return obj.full_name_english

    get_full_name.short_description = 'Full Name'

    def changelist_view(self, request, extra_context=None):
        extra_context = {

            'ins': Institution.objects.all(),
            'division': Division.objects.all(),
        }
        return super(institute_profile_admin, self).changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        if request.GET.get("registration_no", None):
            if not request.GET._mutable:
                request.GET._mutable = True
            license_history_found=LicenseHistory.objects.filter(license_number=request.GET.get("registration_no"))[0]
            if license_history_found.license_receive_id.is_old_data:
                request.GET['full_name_english'] = license_history_found.license_receive_id.students.last_name
                request.GET['father_name'] = license_history_found.license_receive_id.students.fathers_name
                request.GET['sex'] = license_history_found.license_receive_id.students.sex
                request.GET['mother_name'] = license_history_found.license_receive_id.students.mothers_name
                request.GET['date_of_birth'] = license_history_found.license_receive_id.students.date_of_birth
                request.GET['marital_status'] = license_history_found.license_receive_id.students.marital_status
                request.GET['national_ID_No'] = license_history_found.license_receive_id.students.national_ID_No
                request.GET['email_address'] = license_history_found.license_receive_id.students.email_address
                request.GET['division'] = license_history_found.license_receive_id.students.division
                request.GET['district'] = license_history_found.license_receive_id.students.district
                request.GET['thana'] = license_history_found.license_receive_id.students.thana
                request.GET['village'] = license_history_found.license_receive_id.students.village
                request.GET['post_office'] = license_history_found.license_receive_id.students.post_office
                request.GET['postal_code'] = license_history_found.license_receive_id.students.postal_code
                request.GET['nationality'] = license_history_found.license_receive_id.students.nationality
                request.GET['student'] = license_history_found.license_receive_id.students
                request.GET['is_nurse'] = True
                request.GET['employment_type'] = 1
                request.GET['license_number'] = request.GET.get("registration_no")

            else:

                if license_history_found:
                    license_reg_id=license_registrations.objects.get(id=license_history_found.license_registration_id.id)
                    if license_reg_id:
                        student_reg=Student_Registration.objects.get(id=license_reg_id.student_registration.id)
                        if student_reg:
                            student=Student.objects.get(id=student_reg.students.id)
                            if student:
                                request.GET['full_name_english'] = student.first_name
                                request.GET['father_name'] = student.fathers_name
                                request.GET['sex'] = student.sex
                                request.GET['mother_name'] = student.mothers_name
                                request.GET['date_of_birth'] = student.date_of_birth
                                request.GET['marital_status'] = student.marital_status
                                request.GET['national_ID_No'] = student.national_ID_No
                                request.GET['email_address'] = student.email_address
                                request.GET['division'] = student.division
                                request.GET['district'] = student.district
                                request.GET['thana'] = student.thana
                                request.GET['village'] = student.village
                                request.GET['post_office'] = student.post_office
                                request.GET['postal_code'] = student.postal_code
                                request.GET['nationality'] = student.nationality
                                request.GET['student'] = student
                                request.GET['is_nurse'] = True
            # request.GET['registration_no'] = license_reg.registration_no
            # request.GET['last_name'] = license_reg.last_name
            # request.GET['nationality'] = license_reg.nationality
            # # request.GET['date_of_birth']=license_reg.
            # # request.GET['national_ID_No']=license_reg.
            # request.GET['division'] = license_reg.division
            # request.GET['district'] = license_reg.district
            # request.GET['thana'] = license_reg.thana
            # request.GET['village'] = license_reg.village
            # request.GET['post_office'] = license_reg.post_office
            # request.GET['postal_code'] = license_reg.postal_code
            # request.GET['program'] = license_reg.program
            # request.GET['institution'] = license_reg.institution
            # request.GET['license_start_date'] = datetime.date.today()
            # request.GET['license_end_date'] = datetime.date.today() + relativedelta(years=5)
            # request.GET['exam_name'] = license_reg.exam_title
            # request.GET['student_id'] = license_reg.student_id
            # request.GET['license_registrations_id'] = request.GET.get("id")
            # request.GET['license_registrations_refference'] = license_reg




            # print(str(request.GET['license_registrations_id'])+" dfgdtg")
        return super(institute_profile_admin, self).add_view(request, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['is_nurse','Image_View']
        else:
            return ['Image_View']


    def get_queryset(self, request):
        if request.user.is_staff:
            return IntuitionProfile.objects.filter(institute_name__id__in=request.user.staff_institute.values_list('id'))

        elif request.user.is_superuser:
            return IntuitionProfile.objects.all()

class Student_file_admin(admin.ModelAdmin):
    readonly_fields = ('student_registration',)


liceense_his = select2_modelform(LicenseHistory, attrs={'width': '250px'})
class license_history_admin(admin.ModelAdmin):
    raw_id_fields = ['license_registration_id','student_registration_id','student_id','license_receive_id','money_recipte_id',]
    exclude = ['renew_history']
    readonly_fields = ('lock',)
    form = liceense_his

class balanceIncomeAdmin(admin.ModelAdmin):
   list_display = ['head_no','name','amount']

class requested_inline(admin.TabularInline):
    model = RequestedLicense
    extra = 0

class applyLicense_admin(admin.ModelAdmin):
    readonly_fields = ['license_id']
    inlines = [requested_inline]

class exam_result(admin.ModelAdmin):

    raw_id_fields = ['exam_id']

admin.site.register(Job_History,Job_History_Admin)
admin.site.register(Institution,Institution_admin)
admin.site.register(ProgramCatagory)
admin.site.register(Program,Program_admin)
admin.site.register(User,user_search)
admin.site.register(InstituteCatagory)
admin.site.register(Student_Registration,RegisterAdmin)
admin.site.register(Student,student_admin)
admin.site.register(Division)
admin.site.register(District,District_admin)
admin.site.register(Thana,Thana_admin)
admin.site.register(Permission)
admin.site.register(Session)
admin.site.register(ProgramDuration)
admin.site.register(Qualification)
admin.site.register(InstituteType)
admin.site.register(Exam)
admin.site.register(Quota)
admin.site.register(Nationality)
admin.site.register(Relation_to_guardians)
admin.site.register(EducationQualification,EducationQualification_admin)
admin.site.register(license_registrations,license)
admin.site.register(ExamCenter)
admin.site.register(license_receive,license_receive_admin)
admin.site.register(Post)
admin.site.register(Slider)
admin.site.register(re_new_history)
admin.site.register(Register_image)
admin.site.register(SeatCapacity)
admin.site.register(Hospital)
admin.site.register(ExamSubject,ExamSubject_admin)
admin.site.register(ExaminationStudentRegistration,ExaminationRegistrationAdmin)
admin.site.register(ExamResultDetails,ExamResultDetailsAdmin)
admin.site.register(Bank)
admin.site.register(Accounts,AccountsAdmin)
admin.site.register(BalanceHistory,BalanceHistoryAdmin)
admin.site.register(TransfarBalance,TransfarBalanceAdmin)
admin.site.register(BalanceIncome,balanceIncomeAdmin)
admin.site.register(CenterManagement)
admin.site.register(Student_file,Student_file_admin)
admin.site.register(IntuitionProfile,institute_profile_admin)
admin.site.register(ExamYear)
admin.site.register(Final_exam)
admin.site.register(LicenseHistory,license_history_admin)
admin.site.register(SubSubject)
admin.site.register(SubSubjectName)
admin.site.register(TrainingDetails)
admin.site.register(WorkingDetails)
admin.site.register(ApplyLicense,applyLicense_admin)
admin.site.register(RequestedLicense)
admin.site.register(Designation)
admin.site.register(UserPermissionResult)
admin.site.register(Examination_result_add,exam_result)



