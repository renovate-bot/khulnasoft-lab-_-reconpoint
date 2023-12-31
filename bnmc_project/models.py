# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User,_user_get_all_permissions
from django.db import models
from django.contrib.postgres.fields import ArrayField
import os
# import uuid
# from river.models.fields.state import StateField
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
# Create your models here.
from smart_selects.db_fields import ChainedForeignKey
from django.conf import settings
from django.utils.safestring import mark_safe
from ckeditor.fields import RichTextField
from django.db import transaction
import unicodedata
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.widgets import CKEditorWidget

from django.urls import reverse
from django.core.exceptions import ValidationError
import datetime
from django.contrib.contenttypes.models import ContentType
import itertools

#django-appconf-1.0.2 django-imagekit-4.0.2 pilkit-2.0
# rich_text5.6.1

class Register_image(models.Model):
    registrar_name=models.CharField(max_length=200,blank=True)
    signature=models.ImageField(upload_to="media/",blank=True,null=True)
    current_signature=models.BooleanField(blank=True,default=False)

    def __str__(self):
        return self.registrar_name


class Post(models.Model):
    title=models.CharField(max_length=300,blank=True,null=True)
    description=RichTextField(blank=True,null=True)
    image=models.ImageField(upload_to="media/",blank=True,null=True)
    time=models.DateField(blank=True,null=True)

    def __str__(self):
     return self.title

class Slider(models.Model):
    image=models.ImageField(upload_to="media/",blank=True,null=True)

class Division(models.Model):
    name = models.CharField(verbose_name='Division Name',max_length=255)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'DIVISION'
        verbose_name_plural = 'DIVISION'

class District(models.Model):
    division = models.ForeignKey(Division,verbose_name='Division Name', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='District Name',max_length=255)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'DISTRICT'
        verbose_name_plural = 'DISTRICT'

class Thana(models.Model):
    district=models.ForeignKey(District,verbose_name='District Name', on_delete=models.CASCADE)
    name=models.CharField(verbose_name='Police Station Name',max_length=120)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'THANA'
        verbose_name_plural = 'THANA'


class Session(models.Model):
    session = models.CharField(max_length=120, blank=False)
    is_active= models.BooleanField(blank=True,default=False)
    session_start_date=models.DateField(blank=False,null=True)
    session_end_date=models.DateField(blank=False,null=True)


    #def save(self, *args, **kwargs):
    #    start_month=str(self.session_start_date.month)
    #    end_month=str(self.session_end_date.month)
    #    if int(self.session_start_date.month)<10:
    #        start_month="0"+str(self.session_start_date.month)

    #    if int(self.session_end_date.month)<10:
    #        end_month="0"+str(self.session_end_date.month)
    #    start_str=start_month+str(self.session_start_date.year).replace("20","")
    #    end_str=end_month+str(self.session_end_date.year).replace("20","")
    #    self.session=start_str+end_str
    #    print(start_str+end_str)
    #    super(Session, self).save(*args,**kwargs)

    def __str__(self):
        ## months = [ 'JANUARY',  'FEBRUARY', 'MARCH', 'APRIL', 'MAY',  'JUNE',  'JULY',
        ##           'AUGUST', 'SEPTEMBER', 'OCTOBER','NOVEMBER',  'DECEMBER']
        #months = [ 'JAN',  'FEB', 'MAR', 'APR', 'MAY',  'JUN',  'JUL',
        #          'AUG', 'SEP', 'OCT','NOV',  'DEC']
        #try:
        #    start_month=months[int(self.session[:2].strip())-1]
        #    ending_month=months[(int(self.session[4:6]))-1]
        #    return start_month+",20"+self.session[2:4]+"-"+ending_month+",20"+self.session[6:8]
        #except :
        return str(self.session)

    class Meta:
        verbose_name = 'SESSION'
        verbose_name_plural = 'SESSIONS'

class ProgramDuration(models.Model): 
    duration = models.DecimalField(verbose_name='Program Duration',max_digits=10,decimal_places=2)

    def __str__(self):
        return str(self.duration)


    class Meta:
        verbose_name = 'PROGRAM DURATION'
        verbose_name_plural = 'PROGRAM DURATIONS'

class ProgramCatagory(models.Model):
    name=models.CharField(verbose_name='Program Catagory Name',max_length=120,blank=False)
    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'PROGRAM CATEGORY'
        verbose_name_plural = 'PROGRAM CATEGORIES'

class Program(models.Model):
    category = models.ForeignKey(ProgramCatagory,verbose_name='Program Catagory ',on_delete=models.CASCADE)
    title=models.CharField(verbose_name='Program Name',max_length=100)
    code=models.CharField(verbose_name='Program Code',max_length=100,blank=True,null=True)
    second_code=models.CharField(max_length=100,blank=True,null=True)
    duration=models.ForeignKey(ProgramDuration,verbose_name='Program Duration',on_delete=models.CASCADE)
    program_fee = models.CharField(verbose_name='Program Fee',max_length=10, blank=True, null=True)
    session = models.ForeignKey(Session, blank=True, null=True, on_delete=models.CASCADE)
    total=models.FloatField(max_length=120,blank=True,null=True)
    count_total=models.FloatField(max_length=120,blank=True,null=True)

    def __str__(self):
        return str(self.title)


    class Meta:
        verbose_name = 'PROGRAM '
        verbose_name_plural = 'PROGRAMS'

    def save(self, *args, **kwargs):
        if  not  self._state.adding:
             qualification=Qualification.objects.filter(program_set__id=int(self.id)).values_list('minimum_grade', flat=True)
             if qualification:
                 total=sum(qualification)
                 self.total=total
        super(Program, self).save(*args, **kwargs)

class Qualification(models.Model):
    minimum_qualification = models.CharField(verbose_name='Minimum Qualification',max_length=100)
    minimum_grade = models.FloatField(verbose_name='Minimum Grade',max_length=120,blank=True,null=True)
    program_set= models.ForeignKey(Program,blank=True,null=True,on_delete=models.CASCADE,verbose_name='program set')

    def __str__(self):
        return str(self.minimum_qualification)

    class Meta:
        verbose_name = 'QUALIFICATIION'
        verbose_name_plural = 'QUALIFICATIIONS'

class Qualification(models.Model):
    minimum_qualification = models.CharField(verbose_name='Minimum Qualification',max_length=100)
    minimum_grade = models.FloatField(verbose_name='Minimum Grade',max_length=120,blank=True,null=True)
    program_set= models.ForeignKey(Program,blank=True,null=True,on_delete=models.CASCADE,verbose_name='program set')



    def __str__(self):
        return str(self.minimum_qualification)

    class Meta:
        verbose_name = 'QUALIFICATIION'
        verbose_name_plural = 'QUALIFICATIIONS'

class InstituteCatagory(models.Model):
    status=models.CharField(verbose_name='Institution Catagory Name',max_length=120)

    def __str__(self):
     return str(self.status)


    class Meta:
        verbose_name = 'INSTITUTE CATEGORY'
        verbose_name_plural = 'INSTITUTE CATEGORIES'

class InstituteType(models.Model):
    institute_type=models.CharField(verbose_name='Institution Type',max_length=120)

    def __str__(self):
        return str(self.institute_type)

    class Meta:
        verbose_name = 'INSTITUTE TYPE'
        verbose_name_plural = 'INSTITUTE TYPES'

class Exam(models.Model):
    exam_name=models.CharField(verbose_name='Exam Name',max_length=120)
    exam_code = models.CharField(verbose_name='Exam Code', max_length=50,blank=True,null=True)
    pass_mark =  models.IntegerField(verbose_name='Pass Mark',blank=True,null=True)
    exam_date=models.DateField(blank=True,null=True)
    date_active=models.BooleanField(blank=True,default=False)

    def __str__(self):
        return str(self.exam_name)

    class Meta:
        verbose_name = 'EXAM'
        verbose_name_plural = 'EXAMS'

class Institution (models.Model):
    institution_name=models.CharField(verbose_name='Institution Name',max_length=200,)
    institution_code = models.CharField(verbose_name='Institution Code',max_length=100)
    institution_second_code = models.CharField(max_length=100,blank=True,null=True)
    catagory=models.ForeignKey(InstituteCatagory,verbose_name='Institution Catagory ',on_delete=models.CASCADE)
    type=models.ForeignKey(InstituteType,verbose_name='Institution Type ',on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    thana = models.ForeignKey(Thana, on_delete=models.CASCADE)

    village = models.CharField(max_length=200)
    post_office=models.CharField(max_length=100,blank=True)
    program_ins=models.ManyToManyField('Program',verbose_name='Program',blank=True)
    exam_ins=models.ManyToManyField('Exam',verbose_name='Exam',blank=True)
    is_exam_center=models.BooleanField(verbose_name='Is Exam Center')
    principal_signature=models.FileField(verbose_name='Upload photo', upload_to="media/",null=True, blank=True)
    def __str__(self):
        return str(self.institution_name)

    class Meta:
        verbose_name = 'INSTITUTION '
        verbose_name_plural = 'INSTITUTIONS'

    def save(self, *args, **kwargs):
        if self.is_exam_center==True:
            super(Institution, self).save(*args, **kwargs)
            center = ExamCenter(institution_name=self.institution_name,institution_code=self.institution_code,catagory=self.catagory,type=self.type,
                                division=self.division,district=self.district,thana=self.thana,village=self.village,post_office=self.post_office,)
            center.save()
        if self.is_exam_center == False:
         super(Institution, self).save(*args, **kwargs)




class ExamCenter(models.Model):
    institution_name = models.CharField(verbose_name='Center Name', max_length=200, )
    institution_code = models.CharField(verbose_name='Center Code', max_length=100)
    catagory = models.ForeignKey(InstituteCatagory, verbose_name='Center Catagory ', on_delete=models.CASCADE)
    type = models.ForeignKey(InstituteType, verbose_name='Center Type ', on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    district = ChainedForeignKey(
        'District',
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True
    )
    thana = ChainedForeignKey(
        'Thana',
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True
    )

    village = models.CharField(max_length=200)
    post_office = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.institution_name)

class Permission(models.Model):
    id_no=models.PositiveIntegerField(blank=True,null=True)
    permission_name=models.CharField(max_length=120,blank=True,)
    display_order = models.IntegerField(null=True, default=0)

    def __str__(self):
        return str(self.permission_name)

    class Meta:
        verbose_name = 'PERMISSION'
        verbose_name_plural = 'PERMISSIONS'

class User(AbstractUser):
    result_for_program=models.ManyToManyField(Program,blank=True)
    result_institute=models.ManyToManyField(Institution,blank=True)
    staff_institute = models.ManyToManyField(Institution,blank=True,related_name='head_of')
    show_permission = models.ManyToManyField(Permission,blank=False,related_name='show_permission_permissions')
    staff_status=models.ManyToManyField(Permission,blank=False,related_name='staff_status_permissions')
    can_print_registration_form=models.BooleanField(blank=False,default=False)
    can_modify_after_approved=models.BooleanField(blank=False,default=False)
    is_result=models.NullBooleanField(blank=True)
    is_bnmc_user=models.BooleanField(blank=True,default=False)
    allow_for_old_license_add=models.BooleanField(blank=True,default=False)
    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = 'STAFF'
        verbose_name_plural = 'STAFFS'

    def delete(self):

        super(User, self).delete()
        print("User delete")

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.set_password(self.password)

        if not self._state.adding:
            user=User.objects.get(id=self.id)
            if self.password !=user.password:
                print("password has changed")
                self.set_password(self.password)
        super(User, self).save(*args, **kwargs)

class SeatCapacity(models.Model):
    name=models.CharField(max_length=200,blank=True)
    institiution=models.ForeignKey(Institution,on_delete=models.CASCADE,blank=True,null=True)
    program=models.ForeignKey(Program,on_delete=models.CASCADE,blank=True,null=True)
    seat=models.IntegerField(blank=True,null=True)

    def __str__(self):
        return str(self.name)

    def clean(self):
        if self._state.adding:
            queryset=SeatCapacity.objects.filter(institiution__id=self.institiution.id,session__id=self.session.id,program__id=self.program.id)
            if queryset:
                raise ValidationError("already created")

            else:
                return True

class Nationality(models.Model):
    nationality_name=models.CharField(max_length=120)

    def __str__(self):
        return str(self.nationality_name)

    class Meta:
        verbose_name = 'NATIONALITY'
        verbose_name_plural = 'NATIONALITYS'

class Quota(models.Model):
    quota_name=models.CharField(max_length=120,null=True)



    def __str__(self):
        return str(self.quota_name)

    class Meta:
        verbose_name = 'QUOTA'
        verbose_name_plural = 'QUOTAS'

class Relation_to_guardians(models.Model):
    relation=models.CharField(max_length=120)
    def __str__(self):
        return str(self.relation)


    class Meta:
        verbose_name = 'RELATION TO GUARDIANS'
        verbose_name_plural = 'RELATION TO GUARDIANS'

class Student(models.Model):
    def image_tag(self):
        return mark_safe('<img  class="bc_img"  src="/media/%s" width="130" height="130"/>' % (self.image))
    image_tag.short_description = 'Image'
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(verbose_name='Upload photo', upload_to="media/", blank=True)
    registration_no = models.CharField(null=True, blank=True, default=0,max_length=120)
    has_student_id=models.BooleanField(blank=True,default=False)
    first_name=models.CharField(max_length=300,null=True,blank=True)
    last_name = models.CharField(max_length=300,null=True)
    fathers_name=models.CharField(max_length=300,null=True)
    mothers_name = models.CharField(max_length=300,null=True)
    choice_sex=(('1', 'Male'),('2', 'Female'),('3', 'Others'))
    sex=models.CharField(max_length=12, choices=choice_sex,null=True)
    date_of_birth=models.CharField(max_length=300,null=True,blank=True)
    national_ID_No = models.CharField(max_length=128,blank=True,null=True)
    passport_no= models.CharField(max_length=128,blank=True,null=True)
    guardians_name=models.CharField(max_length=300,blank=True,null=True)
    relation_to_guardians = models.ForeignKey(Relation_to_guardians,blank=True,null=True, on_delete=models.CASCADE)
    quota = models.ForeignKey(Quota, on_delete=models.CASCADE,null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE,null=True)
    choice_religion=(('1', 'Islam'),('2', 'Hindu'),('3', 'Buddhist'),('4', 'Christian'),('5', 'Others'))
    religions=models.CharField(max_length=120, choices=choice_religion,null=True)
    choice_status = (
        ('1', 'Single'),('2', 'Married'),('3', 'Widow'),('4', 'Divorce'),('5', 'Separated'))
    marital_status = models.CharField(max_length=120, choices=choice_status,null=True)
    email_address=models.EmailField(max_length=128,blank=True,null=True)
    students_mobile_no=models.CharField(max_length=200,blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE,null=True)
    district = ChainedForeignKey(
        'District',
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        null=True
    )
    thana = ChainedForeignKey(
        'Thana',
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True,
        null=True
    )
    institution= models.ForeignKey(Institution,on_delete=models.CASCADE,blank=True,null=True)
    union=models.CharField(max_length=300,blank=True)
    village=models.CharField(max_length=300,blank=True)
    post_office = models.CharField(max_length=300, blank=True)
    postal_code = models.CharField(max_length=300, blank=True,null=True)
    division_snd = models.ForeignKey(Division, related_name='dIviSiOn', on_delete=models.CASCADE, null=True,
                                     verbose_name='Division')
    district_snd = ChainedForeignKey(
        'District',
        chained_field="division", related_name='dIsItRiCt', chained_model_field="division", show_all=False,
        auto_choose=True, null=True, verbose_name='District')
    thana_snd = ChainedForeignKey(
        'Thana', null=True,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True,
        related_name='tHaNa',
        verbose_name='Thana'

    )
    village_snd = models.CharField(max_length=300, verbose_name='Village')
    post_office_snd = models.CharField(max_length=300, verbose_name='Post office')
    postal_code_snd = models.CharField(max_length=300, blank=True, verbose_name='Postal code',null=True)


    def __str__(self):
        return str(self.last_name)




class CharMaxlength25Field(models.Field):
    def db_type(self, connection):
        return 'char(25)'


    class Meta:
        verbose_name = 'STUDENT'
        verbose_name_plural = 'STUDENT'

class Student_Registration(models.Model):
    students = models.ForeignKey(Student,on_delete=models.CASCADE,blank=True,null=True)
    def image_tag(self):
        return mark_safe('<img name="img" class="bc_im" src="/media/%s" width="130" height="130"/>' % (self.image))
    image_tag.short_description = 'Image'
    created_at = models.DateTimeField(auto_now_add=True)
    image=models.ImageField(verbose_name='Upload photo',upload_to="media/", blank=True)                                    
    registration_no = models.CharField( null=True, blank=True,default=0,max_length=120)
    first_name = models.CharField(verbose_name='Full name (Bangla)',max_length=300,null=True,blank=True)
    last_name = models.CharField(verbose_name='Full name (English)',max_length=300,null=True)
    fathers_name = models.CharField(max_length=300,null=True)
    mothers_name = models.CharField(max_length=300,null=True)
    guardians_name = models.CharField(max_length=300, blank=True,null=True)
    relation_to_guardians = models.ForeignKey(Relation_to_guardians, on_delete=models.CASCADE,null=True,blank=True)
    quota = models.ForeignKey(Quota, on_delete=models.CASCADE,null=True,blank=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE,null=True)
    date_of_birth = models.DateField(null=True)
    choice_sex = (('1', 'Male'), ('2', 'Female'), ('3', 'Others'))
    sex = models.CharField(max_length=12, choices=choice_sex,null=True)
    choice_religion = (('1', 'Islam'), ('2', 'Hindu'), ('3', 'Buddhist'), ('4', 'Christian'), ('5', 'Others'))
    choice_status = (('1', 'Single'), ('2', 'Married'), ('3', 'Widow'), ('4', 'Divorce'), ('5', 'Separated'))
    religions = models.CharField(max_length=120, choices=choice_religion,null=True)
    marital_status = models.CharField(max_length=120, choices=choice_status,null=True)
    national_ID_No = models.CharField(max_length=128, blank=True,null=True)
    passport_no = models.CharField(max_length=128, blank=True,null=True)
    students_mobile_no = models.CharField(max_length=200,null=True)
    email_address = models.EmailField(max_length=128, blank=True,null=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True)
    district = ChainedForeignKey(
        'District',
        chained_field="division", chained_model_field="division", show_all=False, auto_choose=True, null=True)
    thana = ChainedForeignKey(
        'Thana', null=True,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True
    )
    village = models.CharField(max_length=300,null=True)
    post_office = models.CharField(max_length=300,null=True)
    postal_code = models.CharField(max_length=300, blank=True,null=True)

    same_address= models.BooleanField(blank=True)

    division_snd = models.ForeignKey(Division,related_name='Division', on_delete=models.CASCADE, null=True,verbose_name = 'Division')
    district_snd = models.ForeignKey(District,related_name='District', on_delete=models.CASCADE, null=True,verbose_name = 'District')
    thana_snd = models.ForeignKey(Thana,related_name='Thana', on_delete=models.CASCADE, null=True,verbose_name = 'Thana')
    village_snd = models.CharField(max_length=300,verbose_name = 'Village',null=True)
    post_office_snd = models.CharField(max_length=300,verbose_name = 'Post office',null=True)
    postal_code_snd = models.CharField(max_length=300, blank=True,verbose_name = 'Postal code',null=True)

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    # add to
    date_of_registration = models.DateField(verbose_name='Date of Admission',max_length=120, blank=True,null=True)
    program_starting_date = models.DateField(blank=True, null=True)
    program_title = models.ForeignKey(Program,max_length=120, on_delete=models.CASCADE)
    choice_method = (('1', 'Bank Draft'), ('2', 'Cash'), ('3', 'Cheque'))
    payment_method = models.CharField(max_length=120, choices=choice_method)
    registration_fees = models.CharField(max_length=120, blank=True)
    bank_draft_no = models.CharField(verbose_name='Bank Draft No. ',max_length=300, blank=True,null=True)
    bank_draft_date = models.DateField(verbose_name='Bank Draft Date ', max_length=300, blank=True,null=True)
    program_completion_date = models.DateField(blank=True, null=True)
    session = models.ForeignKey(Session, max_length=120, on_delete=models.CASCADE)
    status = models.ForeignKey(Permission, blank=True, null=True, on_delete=models.CASCADE)
    view_type = models.IntegerField(default=1,blank=True)
    re_id= models.CharField(max_length=120,null=True,blank=True)
    approved= models.BooleanField(blank=True,default=False)
    created_by=models.CharField(blank=True,null=True,max_length=200)
    created_user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    migration=models.BooleanField(blank=True,default=False,verbose_name='migrateable')
    migration_approval_bnmc=models.BooleanField(blank=True,default=False)
    new_institute=models.ForeignKey(Institution,on_delete=models.CASCADE,related_name='new_institution',blank=True,null=True)
    old_institute=models.ForeignKey(Institution,on_delete=models.CASCADE,related_name='old_intitution',blank=True,null=True)
    migration_date=models.DateField(blank=True,null=True)
    student_id=models.CharField(max_length=120,blank=True)
    approve_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name='approve_by')
    locked=models.BooleanField(default=False,blank=True)
    printed_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name='printed_by')
    pending=models.BooleanField(blank=True,default=False)
    license_use=models.BooleanField(blank=True,default=False)
    
    def exam_link(self):
        if self.approved:
            return mark_safe('<a href="/admin/bnmc_project/examinationstudentregistration/add/?student_registration=%d&program=%d&institute=%d">Attend In Exam<a/>' % (self.id,self.program_title.id,self.institution.id))
        else:
            return ""



    def Apply_license_exam(self):
        if self.approved:
            return mark_safe('<a href="/admin/bnmc_project/license_registrations/add?student_registration=%d&program_title=%d&registration_no=%s">Apply License Exam<a/>' % (self.id,self.program_title.id,self.registration_no))

        else:
            return ''






    def __init__(self, *args, **kwargs):
        super(Student_Registration, self).__init__(*args, **kwargs)
        if self.students:
            exit_student_data = Student.objects.get(id=self.students.id)
            if exit_student_data:
                print(exit_student_data.post_office)
                self.first_name = exit_student_data.first_name
                self.last_name = exit_student_data.last_name
                self.fathers_name = exit_student_data.fathers_name
                self.mothers_name = exit_student_data.mothers_name
                self.passport_no = exit_student_data.passport_no
                self.date_of_birth = exit_student_data.date_of_birth
                self.sex = exit_student_data.sex
                self.religions = exit_student_data.religions
                self.guardians_name= exit_student_data.guardians_name
                self.relation_to_guardians = exit_student_data.relation_to_guardians
                self.quota = exit_student_data.quota
                self.nationality = exit_student_data.nationality
                self.marital_status = exit_student_data.marital_status
                self.national_ID_No = exit_student_data.national_ID_No
                self.students_mobile_no = exit_student_data.students_mobile_no
                self.division = exit_student_data.division
                self.district = exit_student_data.district
                self.thana = exit_student_data.thana
                self.post_office = exit_student_data.post_office
                self.postal_code = exit_student_data.postal_code
                self.village = exit_student_data.village
                self.division_snd = exit_student_data.division_snd
                self.district_snd = exit_student_data.district_snd
                self.thana_snd = exit_student_data.thana_snd
                self.village_snd = exit_student_data.village_snd
                self.postal_code_snd = exit_student_data.postal_code_snd
                self.post_office_snd = exit_student_data.post_office_snd




    def save(self, *args, **kwargs):
        print("___________________________________________________")
        print("save hoyse")
        if self._state.adding:
            student=None
            if not self.status:
                self.status=Permission.objects.all().order_by('display_order').first()
            self.re_id=0
            if self.created_by and self.created_by!=0:
                created_user= User.objects.filter(id=self.created_by)
                if created_user:
                    self.created_user = created_user[0]

            if self.student_id:
                student = Student.objects.filter(id=self.student_id)
                if student:
                    student=student[0]
                    self.students=student
                    self.first_name=None
                    self.passport_no=None
                    self.registration_no=None
                    self.national_ID_No=None
                    self.fathers_name=None
                    self.marital_status=None
                    self.mothers_name=None
                    self.relation_to_guardians=None
                    self.guardians_name=None
                    self.quota=None
                    self.nationality=None
                    self.sex=None
                    self.students_mobile_no=None
                    self.division=None
                    self.district=None
                    self.thana=None
                    self.village=None
                    self.post_office=None
                    self.postal_code=None
                    self.division_snd=None
                    self.district_snd=None
                    self.thana_snd=None
                    self.village_snd=None
                    self.post_office_snd=None
                    self.postal_code_snd=None
                    self.email_address=None
                    self.date_of_birth=None
                    self.religions=None



                else:
                    student = Student(registration_no=self.student_id,image=self.image, first_name=self.first_name, last_name=self.last_name,
                                fathers_name=self.fathers_name, mothers_name=self.mothers_name,
                                sex=self.sex, date_of_birth=self.date_of_birth, national_ID_No=self.national_ID_No,
                                passport_no=self.passport_no, guardians_name=self.guardians_name,
                                relation_to_guardians=self.relation_to_guardians
                                , quota=self.quota, nationality=self.nationality, religions=self.religions,
                                marital_status=self.marital_status
                                , email_address=self.email_address, students_mobile_no=self.students_mobile_no,
                                division=self.division, district=self.district, institution=self.institution
                                , thana=self.thana, post_office=self.post_office, village=self.village,
                                division_snd=self.division_snd,district_snd=self.district_snd,thana_snd=self.thana_snd,village_snd=self.village_snd,postal_code=self.postal_code,
                                post_office_snd=self.post_office_snd,postal_code_snd=self.postal_code_snd,has_student_id=False)
                    student.save()
                    self.students=student



            else:



                if self.student_id:
                    self.first_name = None
                    self.passport_no = None
                    self.registration_no = None
                    self.national_ID_No = None
                    self.fathers_name = None
                    self.marital_status = None
                    self.mothers_name = None
                    self.relation_to_guardians = None
                    self.guardians_name = None
                    self.quota = None
                    self.nationality = None
                    self.sex = None
                    self.students_mobile_no = None
                    self.division = None
                    self.district = None
                    self.thana = None
                    self.village = None
                    self.post_office = None
                    self.postal_code = None
                    self.division_snd = None
                    self.district_snd = None
                    self.thana_snd = None
                    self.village_snd = None
                    self.post_office_snd = None
                    self.postal_code_snd = None
                    self.email_address = None
                    self.date_of_birth = None
                    self.religions = None

                student = Student(registration_no="",image=self.image, first_name=self.first_name, last_name=self.last_name,
                                fathers_name=self.fathers_name, mothers_name=self.mothers_name,
                                sex=self.sex, date_of_birth=self.date_of_birth, national_ID_No=self.national_ID_No,
                                passport_no=self.passport_no, guardians_name=self.guardians_name,
                                relation_to_guardians=self.relation_to_guardians
                                , quota=self.quota, nationality=self.nationality, religions=self.religions,
                                marital_status=self.marital_status
                                , email_address=self.email_address, students_mobile_no=self.students_mobile_no,
                                division=self.division, district=self.district, institution=self.institution
                                , thana=self.thana, post_office=self.post_office, village=self.village,
                                division_snd=self.division_snd,district_snd=self.district_snd,thana_snd=self.thana_snd,village_snd=self.village_snd,
                                post_office_snd=self.post_office_snd,postal_code_snd=self.postal_code_snd,has_student_id=False,postal_code=self.postal_code)
                student.save()
                self.students=student




        else:
            old_session=Student_Registration.objects.get(id=self.id).session
            if self.migration and self.migration_approval_bnmc==True:
                Old_institute=Student_Registration.objects.get(id=self.id).institution
                if not Old_institute==self.institution:
                    self.old_institute=Old_institute
                    self.new_institute=self.institution
                    self.migration_date=self.migration_date
                    self.migration=False
                    self.migration_approval_bnmc=False


            if self.students:
                General='General'
                general_program_edit=self.program_title.category.name
                if General == general_program_edit:
                    print('only edit general')
                    self.students.image=self.image
                    self.students.first_name=self.first_name
                    self.students.last_name=self.last_name
                    self.students.fathers_name=self.fathers_name
                    self.students.mothers_name=self.mothers_name
                    self.students.sex=self.sex
                    self.students.date_of_birth=self.date_of_birth
                    self.students.national_ID_No=self.national_ID_No
                    self.students.passport_no=self.passport_no
                    self.students.guardians_name=self.guardians_name
                    self.students.relation_to_guardians=self.relation_to_guardians
                    self.students.quota=self.quota
                    self.students.nationality=self.nationality
                    self.students.religions=self.religions
                    self.students.marital_status=self.marital_status
                    self.students.email_address=self.email_address
                    self.students.students_mobile_no=self.students_mobile_no
                    self.students.division=self.division
                    self.students.district=self.district
                    self.students.institution=self.institution
                    self.students.thana=self.thana
                    self.students.post_office=self.post_office
                    self.students.postal_code=self.postal_code
                    self.students.village=self.village
                    self.students.division_snd=self.division_snd
                    self.students.district_snd=self.district_snd
                    self.students.thana_snd=self.thana_snd
                    self.students.village_snd=self.village_snd
                    self.students.post_office_snd=self.post_office_snd
                    self.students.postal_code_snd=self.postal_code_snd
                    self.students.save()
        if self.students==None:
            print("student is none"+str(self.registration_no)+" "+str(self.student_id))
        super(Student_Registration, self).save(*args, **kwargs)




    def clean(self):

        if self.session and self.program_title and self.institution:
            filter_for_seat = SeatCapacity.objects.filter(institiution__id=int(self.institution.id),
                                                          program__id=int(self.program_title.id))

            if filter_for_seat:
                filter_for_seat = filter_for_seat[0]

                student_count_objects = Student_Registration.objects.filter(session__id=int(self.session.id),
                                                                            institution__id=int(
                                                                                self.institution.id),
                                                                            program_title__id=int(
                                                                                self.program_title.id)).count()

                if (student_count_objects > filter_for_seat.seat) or student_count_objects == filter_for_seat.seat:
                    raise ValidationError("Seat is full .")






    def __unicode__(self):
        return str(self.program_title)

    def __unicode__(self):
        return str(self.created_user)

    def __str__(self):
        return str(self.last_name)

    class Meta:
        verbose_name = 'STUDENT REGISTRATIONS'
        verbose_name_plural = 'STUDENT REGISTRATIONS'

class EducationQualification(models.Model):
    student=models.ForeignKey(Student_Registration, on_delete=models.CASCADE , null=True,verbose_name='Level Of Education',)

    level_of_education=models.CharField(null=True,blank=True,max_length=300)
    level_of_educations=models.ForeignKey(Qualification,null=True,blank=True,on_delete=models.CASCADE)

    # (max_length=120,verbose_name='Level Of Education',  blank=True,null=True)
    education_type_choice = (('1', 'Science'), ('2', 'Comerce'), ('3', 'Arts'),('4', 'Enginnering'),('5', 'Nursing'),('6', 'Doctorate'),('7', 'Professional'),('8', 'Technical'))
    education_type=models.CharField(verbose_name='Education Type',max_length=120,choices=education_type_choice)
    board=models.CharField(max_length=120,verbose_name='University/Board',   blank=True,null=True)
    roll=models.CharField (verbose_name='Roll',max_length=120, blank=True,null=True)
    cgpa=models.DecimalField(verbose_name='CGPA',max_digits=10, decimal_places=2,null=True)
    year=models.IntegerField(verbose_name='Ýear', blank=True,null=True)
    duration_choice = (('1', '1 year'), ('2', '2 years'), ('3', '3 years'),('4', '4years'))
    duration=models.CharField(verbose_name='Duration',max_length=120,choices=duration_choice, blank=True,null=True)
    country_choice=(('1','Bangladesh'),('2','Pakistan'),('3','India'),('4','Nepal'),('5','Sri Lanka'),('6','Bhutan'),('7','Maldives'),('8','Afghanistan'))
    country=models.CharField(verbose_name='Country',max_length=120,choices=country_choice, blank=True,null=True)
    students=models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True)
    registration_number=models.IntegerField(blank=True,null=True)
    institution_name=models.ForeignKey(Institution,on_delete=None,blank=True,null=True)



    # def clean(self):
    #     selected_program=self.level_of_educations
    #     if selected_program:
    #         total_qualification_main=Qualification.objects.filter(program_set__id=selected_program.program_set.id)
    #         program=Program.objects.filter(id=selected_program.program_set.id)
    #         program=program[0]
    #         var=total_qualification_main.filter(minimum_qualification=self.level_of_educations)
    #         require_qu = var[0]
    #         i=0
    #
    #         program_cgpa = self.cgpa
    #         if program_cgpa:
    #
    #             if require_qu.minimum_grade>program_cgpa:
    #                 raise ValidationError("low cgpa")
    #
    #
    #             # elif require_qu.minimum_grade <program_cgpa:
    #             #     raise ValidationError ("over cgpa")
    #             #
    #             # elif require_qu.minimum_grade==program_cgpa:
    #             #     raise ValidationError("equal cgpa")
    #
    #
    #         elif not self.cgpa:
    #
    #             raise ValidationError ("No cgpa")

    def __str__(self):
        return str(self.level_of_education)

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.student:
                if self.student.students:
                    self.students=self.student.students
        super(EducationQualification, self).save(*args, **kwargs)

class license_registrations(models.Model):
    pass_mark = models.IntegerField(blank=True, null=True)
    grade = models.CharField(max_length=300, blank=True, null=True)
    students = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)

    def image_li(self):
        return mark_safe('<img name="img" class="bc_im" src="/media/%s" width="130" height="130"/>' % (self.image))

    image_li.short_description = 'Image 1'
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(verbose_name='Upload photo', upload_to="media/", blank=True, null=True)

    def image_second(self):
        return mark_safe(
            '<img name="img" class="bc_im_sec" src="/media/%s" width="130" height="130"/>' % (self.image_sec))

    image_second.short_description = 'Image 2'
    created_at = models.DateTimeField(auto_now_add=True)
    image_sec = models.ImageField(verbose_name='Upload photo', upload_to="media/", null=True, blank=False)
    rool_number = models.IntegerField(verbose_name='roll number', null=True, blank=True, default=0)
    session = models.ForeignKey(Session, max_length=120, on_delete=models.CASCADE, null=True)
    date_of_passing_on = models.CharField(max_length=120, blank=False, null=True)
    centre = models.ForeignKey(ExamCenter, on_delete=models.CASCADE, related_name='center', null=True, blank=True)
    registration_no = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(verbose_name='Full name (Bangla)', max_length=300, null=True)
    last_name = models.CharField(verbose_name='Full name (English)', max_length=300, blank=True, null=True)
    fathers_name = models.CharField(max_length=300, blank=True, null=True)
    mothers_name = models.CharField(max_length=300, blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, blank=True, null=True)
    choice_sex = (('1', 'Male'), ('2', 'Female'), ('3', 'Others'))
    sex = models.CharField(max_length=12, choices=choice_sex, blank=True, null=True)
    choice_religion = (('1', 'Islam'), ('2', 'Hindu'), ('3', 'Buddhist'), ('4', 'Christian'), ('5', 'Others'))
    religions = models.CharField(max_length=120, choices=choice_religion, blank=True, null=True)
    students_mobile_no = models.CharField(max_length=200, blank=False)
    status = models.ForeignKey(Permission, blank=True, null=True, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, null=True, on_delete=models.CASCADE, blank=True)
    thana = models.ForeignKey(Thana, null=True, on_delete=models.CASCADE, blank=True)
    village = models.CharField(max_length=300, blank=True, null=True)
    post_office = models.CharField(max_length=300, blank=True, null=True)
    postal_code = models.CharField(max_length=300, blank=True, null=True)
    exam_title = models.ForeignKey(Exam, max_length=120, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='institution', blank=True,
                                    null=True, )
    received_filter = models.IntegerField(null=False, blank=True, default=0)
    student_id = models.IntegerField(null=True, blank=True, default=0)
    program = models.ForeignKey('Program', verbose_name='Program', blank=True, on_delete=models.CASCADE, null=True)
    student_registration = models.ForeignKey(Student_Registration, verbose_name='registration', blank=False,
                                             on_delete=None, null=True)
    text_field = models.BooleanField(blank=True, default=False)

    def image_tag_li(self):
        return mark_safe('<img class="bnc_s1" src="/media/%s" width="130" height="130"/>' % (self.signature_first))

    image_tag_li.short_description = 'Image'
    created_at = models.DateTimeField(auto_now_add=True)
    signature_first = models.ImageField(verbose_name='Upload photo', upload_to="signature_student/", blank=True,
                                        null=True)

    def image_tag_lis(self):
        if self.institution:
            if self.institution.principal_signature:
                return mark_safe('<img width="143px" height="23px" src="%s"' % self.institution.principal_signature.url)
        return None

    image_tag_lis.short_description = 'Image'
    created_at = models.DateTimeField(auto_now_add=True)
    signature_sec = models.ImageField(verbose_name='up photo', upload_to="media/", blank=True, null=True)
    approved = models.BooleanField(blank=True, default=False, )
    image_field = models.CharField(blank=True, null=True, max_length=200)
    hall_name = models.CharField(blank=True, null=True, max_length=300)
    room_name = models.CharField(blank=True, null=True, max_length=300)


    def print_licence(self):
        if self.approved:
            return mark_safe('<a href="/print_license/%s"  target="_blank" >Print</a>'%(self.id))
        else:
            return ""


    def license_receive_link(self):
        return mark_safe('<a target="_blank" href="/admin/bnmc_project/license_receive/add/?id=%s">Registration for license</a>'%self.id)

    def print_licence_form(self):
        if self.approved:
            return mark_safe('<a href="admin/print_license_form/"  target="_blank" >forms</a>' % (self.id))
        else:
            return ""

    def __init__(self, *args, **kwargs):
        super(license_registrations, self).__init__(*args, **kwargs)
        if self.student_registration:
            search_student_in_student_reg=Student_Registration.objects.get(id=self.student_registration.id)
            if search_student_in_student_reg.students:
                query_student=Student.objects.get(id=search_student_in_student_reg.students.id)
                if query_student:
                    self.first_name=query_student.first_name
                    self.last_name=query_student.last_name
                    self.fathers_name=query_student.fathers_name
                    self.mothers_name=query_student.mothers_name
                    self.nationality=query_student.nationality
                    self.sex=query_student.sex
                    self.religions=query_student.religions
                    self.division=query_student.division
                    self.district=query_student.district
                    self.thana=query_student.thana
                    self.village=query_student.village
                    self.post_office=query_student.post_office
                    self.institution=search_student_in_student_reg.institution
        



    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.image_field:
                self.image=self.image_field
            self.status=Permission.objects.all().order_by('display_order').first()
            if self.student_registration:
                self.first_name=None
                self.last_name=None
                self.fathers_name=None
                self.mothers_name=None
                self.nationality=None
                self.sex=None
                self.religions=None
                self.district=None
                self.division=None
                self.thana=None
                self.postal_code=None
                self.post_office=None
                self.village=None
                self.postal_code=None


        else:
            if self.student_registration:
                self.first_name=None
                self.last_name=None
                self.fathers_name=None
                self.mothers_name=None
                self.nationality=None
                self.sex=None
                self.religions=None
                self.district=None
                self.division=None
                self.thana=None
                self.postal_code=None
                self.post_office=None
                self.village=None
                self.postal_code=None
        super(license_registrations, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.last_name)

    class Meta:
        verbose_name = 'LICENSE REGISTRATION'
        verbose_name_plural = 'LICENSE REGISTRATIONS'

class license_receive(models.Model):
    image = models.ImageField(verbose_name='Upload photo', upload_to="media/", blank=True, null=True)

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="130" height="130"/>' % (self.image))

    first_name = models.CharField(verbose_name='Full name (Bangla)', max_length=300, null=True, blank=True)

    last_name = models.CharField(verbose_name='Full name (English)', max_length=300, null=True)
    fathers_name = models.CharField(max_length=300, null=True)
    mothers_name = models.CharField(max_length=300, null=True)
    date_of_birth = models.CharField(max_length=129, blank=True, null=True)
    choice_sex = (('1', 'Male'), ('2', 'Female'), ('3', 'Others'))
    sex = models.CharField(max_length=12, choices=choice_sex, null=True)
    choice_religion = (('1', 'Islam'), ('2', 'Hindu'), ('3', 'Buddhist'), ('4', 'Christian'), ('5', 'Others'))
    choice_status = (('1', 'Single'), ('2', 'Married'), ('3', 'Widow'), ('4', 'Divorce'), ('5', 'Separated'))
    religions = models.CharField(max_length=120, choices=choice_religion, null=True)
    marital_status = models.CharField(max_length=120, choices=choice_status, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, null=True)
    national_ID_No = models.CharField(max_length=128, blank=True, null=True)
    guardians_name = models.CharField(max_length=300, blank=True, null=True)
    relation_to_guardians = models.ForeignKey(Relation_to_guardians, on_delete=models.CASCADE, null=True,
                                              blank=True)
    passport_no = models.CharField(max_length=128, blank=True, null=True)
    students_mobile_no = models.CharField(max_length=200, null=True)
    email_address = models.EmailField(max_length=128, blank=True, null=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True)
    village = models.CharField(max_length=300, null=True)
    district = models.ForeignKey(District, null=True, on_delete=models.CASCADE)
    post_office = models.CharField(max_length=300, null=True)
    thana = models.ForeignKey(Thana, null=True, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=300, blank=True, null=True)
    exam_name = models.ForeignKey(Exam, max_length=120, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.IntegerField(null=True, blank=True, default=0)
    renew_history = models.ManyToManyField('re_new_history', verbose_name='Renew History', blank=True)
    license_registrations_id = models.IntegerField(null=True, blank=True, default=0)
    license_registrations_refference = models.ForeignKey(license_registrations, max_length=120,
                                                         on_delete=models.CASCADE, null=True, blank=True)
    approved = models.BooleanField(blank=True, default=False)
    license_registrations_receive_id = models.IntegerField(null=True, blank=True, default=0)
    registration_no = models.IntegerField(null=True, blank=True, default=0)
    status = models.ForeignKey(Permission, blank=True, null=True, on_delete=models.CASCADE)

    license_registration_date = models.CharField(max_length=120, blank=True, null=True)
    license_registration_fee = models.CharField(max_length=128, blank=True, null=True)
    choice_method = (('1', 'Bank Draft'), ('2', 'Cash'), ('3', 'Cheque'))
    payment_method = models.CharField(max_length=120, choices=choice_method, null=True)
    bank_draft_no = models.CharField(max_length=128, blank=True, null=True)
    registration_fee = models.CharField(max_length=128, blank=True, null=True)
    bank_draft_date = models.CharField(max_length=120, blank=True, null=True)
    choice_type = (('1', 'Private'), ('2', 'Public'))
    employer_type = models.CharField(max_length=120, choices=choice_type, null=True)
    choice_country = (('1', 'Bangladesh'),)
    employer_country = models.CharField(max_length=120, choices=choice_country, null=True)

    division_snd = models.ForeignKey(Division, related_name='Division_per', on_delete=models.CASCADE, null=True,
                                     verbose_name='Division')
    district_snd = models.ForeignKey(District, related_name='District_per', on_delete=models.CASCADE, null=True,
                                     verbose_name='District')
    thana_snd = models.ForeignKey(Thana, related_name='Thana_per', on_delete=models.CASCADE, null=True,
                                  verbose_name='Thana')
    village_snd = models.CharField(max_length=300, verbose_name='Village', null=True)
    post_office_snd = models.CharField(max_length=300, verbose_name='Post office', null=True)
    postal_code_snd = models.CharField(max_length=300, blank=True, verbose_name='Postal code', null=True)
    quota = models.ForeignKey(Quota, on_delete=models.CASCADE, null=True, blank=True)

    signature = models.ImageField(verbose_name='signature', upload_to="signature_student/", blank=True, null=True)

    def sig(self):
        return mark_safe('<img  class="sig"  src="/media/%s" width="130" height="130"/>' % (self.signature))


    create_on = models.CharField(max_length=120, blank=True, null=True)
    month_info = models.CharField(max_length=120, blank=True, null=True)
    students = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(Program, max_length=120, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    is_old_data = models.BooleanField(blank=True, default=False)
    entry_id=models.CharField(max_length=120, blank=True, null=True)
    permanent=models.BooleanField(blank=True,default=False,verbose_name='Permanent Address')
    present=models.BooleanField(blank=True,default=False,verbose_name='Present Address')
    late=models.BooleanField(blank=True,default=False)
    same_address= models.BooleanField(blank=True,default=False)

    def __str__(self):
        return str(self.last_name)


    def __init__(self, *args, **kwargs):
        super(license_receive, self).__init__(*args, **kwargs)
        if self.license_registrations_refference:
            print('licccccccccccccccccccccccccccccccc')
            exit_license_reg = license_registrations.objects.get(id=self.license_registrations_refference.id)
            if exit_license_reg:
                exit_student_reg = Student_Registration.objects.get(id=exit_license_reg.student_registration.id)
                if exit_student_reg:
                    student_find = Student.objects.filter(id=exit_student_reg.students.id)
                    student_find = student_find[0]
                    if student_find:
                        print('lllllll')
                        self.image = self.image
                        self.first_name = student_find.first_name
                        self.last_name = student_find.last_name
                        self.fathers_name = student_find.fathers_name
                        self.mothers_name = student_find.mothers_name
                        self.sex = student_find.sex
                        self.date_of_birth = student_find.date_of_birth
                        self.national_ID_No = student_find.national_ID_No
                        self.passport_no = student_find.passport_no
                        self.guardians_name = student_find.guardians_name
                        self.relation_to_guardians = student_find.relation_to_guardians
                        self.quota = student_find.quota
                        self.nationality = student_find.nationality
                        self.religions = student_find.religions
                        self.marital_status = student_find.marital_status
                        self.email_address = student_find.email_address
                        self.students_mobile_no = student_find.students_mobile_no
                        self.division = student_find.division
                        self.district = student_find.district
                        self.institution = student_find.institution
                        self.thana = student_find.thana
                        self.post_office = student_find.post_office
                        self.village = student_find.village
                        self.postal_code = student_find.postal_code

                        self.division_snd = student_find.division_snd
                        self.district_snd = student_find.district_snd
                        self.thana_snd = student_find.thana_snd
                        self.post_office_snd = student_find.post_office_snd
                        self.village_snd = student_find.village_snd
                        self.postal_code_snd = student_find.postal_code_snd


        elif self.is_old_data:
            if self.students:

                student_qr = Student.objects.get(id=self.students.id)

                self.student_id = student_qr.registration_no
                self.image =  self.image
                self.first_name = student_qr.first_name
                self.last_name = student_qr.last_name
                self.fathers_name = student_qr.fathers_name
                self.mothers_name = student_qr.mothers_name
                self.sex = student_qr.sex
                self.date_of_birth = student_qr.date_of_birth
                self.national_ID_No = student_qr.national_ID_No
                self.passport_no = student_qr.passport_no
                self.guardians_name = student_qr.guardians_name
                self.relation_to_guardians = student_qr.relation_to_guardians
                self.quota = student_qr.quota
                self.nationality = student_qr.nationality
                self.religions = student_qr.religions
                self.marital_status = student_qr.marital_status
                self.email_address = student_qr.email_address
                self.students_mobile_no = student_qr.students_mobile_no
                self.division = student_qr.division
                self.district = student_qr.district
                self.institution = student_qr.institution
                self.thana = student_qr.thana
                self.post_office = student_qr.post_office
                self.village = student_qr.village
                self.postal_code=student_qr.postal_code

                self.division_snd = student_qr.division_snd
                self.district_snd = student_qr.district_snd
                self.thana_snd = student_qr.thana_snd
                self.post_office_snd = student_qr.post_office_snd
                self.village_snd = student_qr.village_snd
                self.postal_code_snd = student_qr.postal_code_snd

    def save(self, *args, **kwargs):
        print(self.is_old_data)
        is_adding = self._state.adding
        if self.license_registrations_id or self.license_registrations_id != 0:
            license_reg = license_registrations.objects.filter(id=self.license_registrations_id)
            print("found " + str(license_reg), license_reg)
            if license_reg:
                license_reg = license_reg[0]
                self.license_registrations_refference = license_reg
        # if self._state.adding:
        super(license_receive, self).save(*args, **kwargs)
        status_first = Permission.objects.all().order_by('display_order').first()
        print("allah is one")
        if is_adding:
            if self.is_old_data == True:
                students=Student(registration_no=self.student_id,image=self.image, first_name=self.first_name, last_name=self.last_name,
                                fathers_name=self.fathers_name, mothers_name=self.mothers_name,
                                sex=self.sex, date_of_birth=self.date_of_birth, national_ID_No=self.national_ID_No,
                                passport_no=self.passport_no, guardians_name=self.guardians_name,
                                relation_to_guardians=self.relation_to_guardians
                                , quota=self.quota, nationality=self.nationality, religions=self.religions,
                                marital_status=self.marital_status
                                , email_address=self.email_address, students_mobile_no=self.students_mobile_no,
                                division=self.division, district=self.district, institution=self.institution
                                , thana=self.thana, post_office=self.post_office, village=self.village,
                                division_snd=self.division_snd,district_snd=self.district_snd,thana_snd=self.thana_snd,village_snd=self.village_snd,
                                post_office_snd=self.post_office_snd,postal_code_snd=self.postal_code_snd,has_student_id=False)
                students.save()
                self.students=students

                self.status = Permission.objects.all().order_by('display_order').last()
                self.first_name = None
                self.last_name = None
                self.fathers_name = None
                self.mothers_name = None
                self.sex = None
                self.date_of_birth = None
                self.national_ID_No = None
                self.passport_no = None
                self.guardians_name = None
                self.relation_to_guardians = None
                self.quota = self.quota
                self.nationality = None
                self.religions = None
                self.marital_status = None
                self.email_address = None
                self.students_mobile_no = None
                self.division = None
                self.district = None
                self.institution = None
                self.thana = None
                self.post_office = None
                self.village = None

                self.division_snd = None
                self.district_snd = None
                self.thana_snd = None
                self.post_office_snd = None
                self.village_snd = None
                self.postal_code_snd = None


            else:


                self.status = status_first
                self.first_name = None
                self.last_name = None
                self.fathers_name = None
                self.mothers_name = None
                self.sex = None
                self.date_of_birth = None
                self.national_ID_No = None
                self.passport_no = None
                self.guardians_name = None
                self.relation_to_guardians = None
                self.quota = self.quota
                self.nationality = None
                self.religions = None
                self.marital_status = None
                self.email_address = None
                self.students_mobile_no = None
                self.division = None
                self.district = None
                self.institution = None
                self.thana = None
                self.post_office = None
                self.village = None

                self.division_snd = None
                self.district_snd = None
                self.thana_snd = None
                self.post_office_snd = None
                self.village_snd = None
                self.postal_code_snd = None

        else:
            if self.is_old_data == True:
                student_qr=Student.objects.get(id=self.students.id)
                student_qr.registration_no=self.student_id
                student_qr.image=self.image
                student_qr.first_name=self.first_name
                student_qr.last_name=self.last_name
                student_qr.fathers_name=self.fathers_name
                student_qr.mothers_name=self.mothers_name
                student_qr.sex=self.sex
                student_qr.date_of_birth=self.date_of_birth
                student_qr.national_ID_No=self.national_ID_No
                student_qr.passport_no=self.passport_no
                student_qr.guardians_name=self.guardians_name
                student_qr.relation_to_guardians=self.relation_to_guardians
                student_qr.quota=self.quota
                student_qr.nationality=self.nationality
                student_qr.religions=self.religions
                student_qr.marital_status=self.marital_status
                student_qr.email_address=self.email_address
                student_qr.students_mobile_no=self.students_mobile_no
                student_qr.division=self.division
                student_qr.district=self.district
                student_qr.institution=self.institution
                student_qr.thana=self.thana
                student_qr.post_office=self.post_office
                student_qr.village=self.village

                student_qr.division_snd = self.division
                student_qr.district_snd = self.district
                student_qr.thana_snd = self.thana
                student_qr.post_office_snd = self.post_office
                student_qr.village_snd = self.village
                student_qr.postal_code_snd=self.postal_code_snd
                student_qr.has_student_id=False

                student_qr.save()


            if self.license_registrations_refference:
                self.first_name = None
                self.last_name = None
                self.fathers_name = None
                self.mothers_name = None
                self.sex = None
                self.date_of_birth = None
                self.national_ID_No = None
                self.passport_no = None
                self.guardians_name = None
                self.relation_to_guardians = None
                self.quota = self.quota
                self.nationality = None
                self.religions = None
                self.marital_status = None
                self.email_address = None
                self.students_mobile_no = None
                self.division = None
                self.district = None
                self.institution = None
                self.thana = None
                self.post_office = None
                self.village = None

                self.division_snd = None
                self.district_snd = None
                self.thana_snd = None
                self.post_office_snd = None
                self.village_snd = None
                self.postal_code_snd = None

        super(license_receive, self).save(*args, **kwargs)

    def license_form_print(self):
        return mark_safe('<a target="_blank" href="/get_license_rec_stu/%s">print</a>' % (self.id))





class WorkingDetails(models.Model):
    license=models.ForeignKey(license_receive,on_delete=models.CASCADE)
    choice_type = (('1', 'Private'), ('2', 'Non-Private'), ('3', 'foreign'))
    type=models.CharField(choices=choice_type,max_length=120)
    join_date=models.DateField(blank=True,null=True)
    place=models.CharField(blank=True,null=True,max_length=300)
    training_type=models.CharField(blank=True,max_length=300,null=True)

class TrainingDetails(models.Model):
    license=models.ForeignKey(license_receive,on_delete=models.CASCADE)
    training_name=models.CharField(blank=True,max_length=300,null=True)
    training_place=models.CharField(blank=True,max_length=300,null=True)
    training_duration=models.CharField(blank=True,max_length=300,null=True)

class re_new_history(models.Model):
    license = models.ForeignKey(license_receive,on_delete=models.CASCADE)
    created_on=models.DateTimeField()
    renew_by=models.ForeignKey(User,on_delete=models.CASCADE)
    previous_start_date=models.DateField()
    previous_end_date=models.DateField()
    new_start_date=models.DateField()
    new_end_date=models.DateField()
    license_number=models.CharField(max_length=120,blank=True,null=True)
    program=models.ForeignKey(Program, max_length=120, on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return str(self.license)

    def delete(self, *args, **kwargs):


        license_history=LicenseHistory.objects.filter(renew_history__id=self.pk)[0]
        if license_history:
            re=re_new_history.objects.filter(id__in=[thing.id for thing in license_history.renew_history.all()]).exclude(id=self.pk).last()
            if re:

                license_history.license_start_date=re.new_start_date
                license_history.license_end_date=re.new_end_date
                license_history.save()

        super(re_new_history, self).delete(*args, **kwargs)

class Job_History(models.Model):
    student=models.ForeignKey(Student,null=True,blank=True,on_delete=models.CASCADE)
    license_receive_reference=models.ForeignKey("license_receive",null=True,blank=True,on_delete=models.CASCADE)
    license_registration_reference=models.ForeignKey("license_registrations",null=True,blank=True,on_delete=models.CASCADE)
                                         
    current_designation=models.CharField(max_length=50,blank=False,null=True)
    current_hospital=models.ForeignKey("Hospital",blank=False,null=True,on_delete=models.CASCADE)
    is_running_job=models.BooleanField(blank=False)
    job_starting_date=models.DateField(null=True,blank=True)
    job_ending_date=models.DateField(null=True,blank=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
        else:
            self.edit_on=datetime.datetime.now()
        super(Job_History, self).save(*args, **kwargs)

    def __str__(self):
        if(self.student):
            return self.student
        else:
            return self.current_designation

class Hospital (models.Model):
    name=models.CharField(max_length=300,blank=False)
    established_date=models.DateField(blank=True)
    code= models.CharField(max_length=50,blank=True)
    hospital_address=models.TextField(max_length=500,blank=False)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
        else:
            self.edit_on=datetime.datetime.now()
        super(Hospital, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.name)


class ExamYear(models.Model):
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    year = models.CharField(max_length=300, blank=False)


    def __str__(self):
        return "%s" % self.year



class ExamSubject(models.Model):
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    year=models.ForeignKey(ExamYear,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=300,blank=False)
    fullMarks=models.FloatField(null=True,blank=True,default=0.000)
    passMarks=models.FloatField(null=True,blank=True,default=0.000)
    code= models.CharField(max_length=300,blank=True)
    isMainSubject=models.BooleanField(blank=True,default=False)
    SubSubjects=models.ManyToManyField("ExamSubject",verbose_name='Sub Subjects',blank=True)
    discription=models.TextField(blank=True,null=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)
    is_active=models.BooleanField(blank=True,default=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
        else:
            self.edit_on=datetime.datetime.now()
        super(ExamSubject, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

class SubSubjectName(models.Model):
    name=models.CharField(max_length=300,blank=False)

    def __str__(self):
        return str(self.name)

class SubSubject(models.Model):
    subject_name=models.ForeignKey(SubSubjectName,on_delete=models.SET_NULL,null=True)
    marks=models.FloatField(null=True,blank=True,default=0.000)
    pass_marks=models.FloatField(null=True,blank=True,default=0.000)
    exam_subject=models.ForeignKey(ExamSubject,on_delete=models.SET_NULL,null=True)

    def __str__(self):
            return str(self.subject_name)


class Final_exam(models.Model):
    name=models.CharField(max_length=300,blank=False)
    is_active=models.BooleanField(blank=True)
    subjects=models.ManyToManyField(ExamSubject,blank=True)
    date=models.DateField(null=True,blank=True)

    def __str__(self):
        return "%s" % self.name




from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
class ExaminationStudentRegistration(models.Model):
    program = models.ForeignKey(Program, on_delete=None, blank=False)

    exam=models.ForeignKey(Final_exam,on_delete=models.CASCADE,null=False,blank=False)
    year = models.ForeignKey(ExamYear, on_delete=None, null=True)

    student_registration=models.ForeignKey(Student_Registration,on_delete=None,blank=False)
    student_id=models.CharField(max_length=300, blank=True, null=True)
    subjects = models.ManyToManyField(ExamSubject, blank=False)
    last_name = models.CharField(verbose_name='Full name (English)', max_length=300, blank=True, null=True)
    fathers_name = models.CharField(max_length=300, blank=True, null=True)
    mothers_name = models.CharField(max_length=300, blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, blank=True, null=True)
    choice_sex = (('1', 'Male'), ('2', 'Female'), ('3', 'Others'))
    sex = models.CharField(max_length=12, choices=choice_sex, blank=True, null=True)
    choice_religion = (('1', 'Islam'), ('2', 'Hindu'), ('3', 'Buddhist'), ('4', 'Christian'), ('5', 'Others'))
    religions = models.CharField(max_length=120, choices=choice_religion, blank=True, null=True)
    students_mobile_no = models.CharField(max_length=200, blank=False,null=True)
    status = models.ForeignKey(Permission, blank=True, null=True, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, null=True, on_delete=models.CASCADE, blank=True)
    thana = models.ForeignKey(Thana, null=True, on_delete=models.CASCADE, blank=True)
    village = models.CharField(max_length=300, blank=True, null=True)
    post_office = models.CharField(max_length=300, blank=True, null=True)
    postal_code = models.CharField(max_length=300, blank=True, null=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True)
    publish_result=models.BooleanField(blank=False,default=False)
    institute=models.ForeignKey(Institution,null=True,on_delete=None)
    student_signature=models.ImageField(verbose_name='Candidate Signature',upload_to="signature_student/", blank=True)
    approved = models.BooleanField(blank=True, default=False)
    roll_number = models.IntegerField(blank=True, null=True)
    start_role = models.CharField(max_length=300, blank=True, null=True)
    end_role = models.CharField(max_length=300, blank=True, null=True)
    center = models.ForeignKey(Institution, null=True, on_delete=None, related_name='Center')

    def image_tag(self):
        return mark_safe('<img  class="bc_img"  src="/media/%s" width="130" height="130"/>' % (self.student_signature))


    def __str__(self):
        return str(self.student_registration.last_name)


    def __init__(self, *args, **kwargs):
        super(ExaminationStudentRegistration, self).__init__(*args, **kwargs)
        try:

            if self.student_registration:
                exit_student = Student.objects.get(id=self.student_registration.students.id)
                if exit_student:
                    self.first_name = exit_student.first_name
                    self.last_name = exit_student.last_name
                    self.fathers_name=exit_student.fathers_name
                    self.mothers_name=exit_student.mothers_name

                    self.nationality = exit_student.nationality
                    self.sex= exit_student.sex
                    self.religions=exit_student.religions



                    self.division = exit_student.division
                    self.district = exit_student.district
                    self.thana = exit_student.thana
                    self.village = exit_student.village
                    self.post_office = exit_student.post_office
                    self.postal_code = exit_student.postal_code
                    self.student_id= self.student_registration.registration_no

        except Exception:
            pass

    def save(self, *args, **kwargs):
        status_first = Permission.objects.all().order_by('display_order').first()
        isPublishedResult= self.publish_result
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.status=status_first
        else:
            self.status = status_first
            self.edit_on=datetime.datetime.now()
        self.publish_result=False
        super(ExaminationStudentRegistration, self).save(*args, **kwargs)


class Examination_result_add(models.Model):
    exam_id=models.ForeignKey(ExaminationStudentRegistration,on_delete=models.CASCADE)
    subject=models.ForeignKey(SubSubject,on_delete=models.CASCADE)
    mark=models.FloatField(null=True,blank=True,default=0.00)
    create=models.DateTimeField(blank=True,null=True)
    result_submitted_by=models.ForeignKey(User,on_delete=None,blank=True,null=True)


class FinalExamCenterManage(models.Model):
    exam = models.ForeignKey(Final_exam, blank=True, on_delete=None, null=True)
    roll_start = models.CharField(blank=True, max_length=300, null=True)
    roll_end = models.CharField(blank=True, max_length=300, null=True)
    center = models.ForeignKey(Institution, on_delete=None, null=True)

    def __str__(self):
            return str(self.roll_start)

class ExamForm(ModelForm):
    class Meta:
        model = ExaminationStudentRegistration
        fields = ("subjects",)

    def __init__(self, *args, **kwargs):
        super(ExamForm, self).__init__(*args, **kwargs)

        self.fields["subjects"].widget = CheckboxSelectMultiple()
        self.fields["subjects"].queryset = ExamSubject.objects.all()


class ExamResultDetails(models.Model):
    examStudentInfo=models.ForeignKey(ExaminationStudentRegistration,on_delete=models.CASCADE,null=False,blank=False)
    subject=models.ForeignKey(ExamSubject,on_delete=models.CASCADE,null=False,blank=False)
    marks=models.FloatField(null=True,blank=True,default=0.000)
    #passMarks=models.DecimalField(null=True,blank=True,max_digits=6,decimal_places=3)
    create_on=models.DateTimeField(null=True,blank=True)
    def passMarks(self):
        return str(self.subject.passMarks)

    def get_grad(self):
        if self.subject.passMarks and self.marks:

            if self.subject.passMarks>self.marks:
                    return mark_safe("<span style='color:red'><b>F</b></span>")
            if self.subject.isMainSubject:    
                if self.subject.SubSubjects:
                    subjectIds=[item['id'] for item in   self.subject.SubSubjects.all().values("id")]
                    subsubjects=ExamResultDetails.objects.filter(examStudentInfo=self.examStudentInfo,subject__pk__in=subjectIds)
                    for subject in subsubjects:
                        if not subject.marks:
                            subject.marks=0.00
                        if subject.subject.passMarks>subject.marks:
                            return mark_safe("<span style='color:red'><b>F</b></span>")

                print((80/100)*self.subject.fullMarks,self.marks)
                if (80/100)*self.subject.fullMarks<=self.marks:
                    return "A+"
                elif (70/100)*self.subject.fullMarks<=self.marks:
                    return "A"
                elif (60/100)*self.subject.fullMarks<=self.marks:
                    return "A-"
                elif (50/100)*self.subject.fullMarks<=self.marks:
                    return "B"
                elif (40/100)*self.subject.fullMarks<=self.marks:
                    return "C"

            return "";
    def get_grad_point(self):
        if self.subject.passMarks and self.marks:
            if self.subject.passMarks>self.marks:
                return 0.00;
            if self.subject.isMainSubject:
                if (80/100)*self.subject.fullMarks<=self.marks:
                    return 5.00
                elif (70/100)*self.subject.fullMarks<=self.marks:
                    return 4.00
                elif (60/100)*self.subject.fullMarks<=self.marks:
                    return 3.00
                elif (50/100)*self.subject.fullMarks<=self.marks:
                    return 2.00
                elif (40/100)*self.subject.fullMarks<=self.marks:
                    return 1.00
        return "";
    def __str__(self):
        return str(self.examStudentInfo)+" ("+str(self.subject.name)+" )"

class Bank(models.Model):
    name=models.CharField(max_length=300,blank=False)
    address=models.TextField(max_length=500,blank=False)
    bank_accounts=models.ManyToManyField("Accounts",blank=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.edit_on=None
        else:
            self.edit_on=datetime.datetime.now()
        super(Bank, self).save(*args, **kwargs)

class Accounts(models.Model):
    accountNumber=models.CharField(max_length=300,blank=False)
    bank_raffer=models.ForeignKey(Bank,null=False,blank=False, on_delete=None)
    IsDefaultAccount=models.BooleanField(default=False,blank=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)

    def __str__(self):
        return str(str(self.bank_raffer)+" "+self.accountNumber)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.edit_on=None
        else:
            self.edit_on=datetime.datetime.now()
        super(Accounts, self).save(*args, **kwargs)
from datetime import date
class BalanceHistory(models.Model):
    account=models.ForeignKey(Accounts,null=False,blank=False, on_delete=None)
    choice_historyType = (("1", 'Add balance'),("2", 'Remove balance'))
    historyType = models.CharField(choices=choice_historyType,blank=False,max_length=200)
    amount=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    Note=models.TextField(max_length=500,blank=False)
    IsTransfardBalance=models.BooleanField(blank=True,default=False)
    TransfarRaffer=models.ForeignKey("TransfarBalance",on_delete=None,blank=True,null=True)
    create_on=models.DateField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)
    BalanceIncomes=models.ManyToManyField("BalanceIncome",blank=True)
    student_reg=models.ForeignKey(Student_Registration,on_delete=None,blank=True,null=True)
    instituition=models.ForeignKey(Institution,on_delete=None,blank=True,null=True)
    IsApproved=models.BooleanField(default=False,blank=True)
    approvedBy=models.ForeignKey(User,on_delete=None,null=True,blank=True)
    approvDate=models.DateTimeField(null=True,blank=True)
    bankBranch=models.CharField(max_length=300,blank=True)
    bankIssueDate=models.DateField(("Date"),null=True,blank=True,default=date.today)
    add=1
    remove=2
    id_no=models.IntegerField(blank=True,null=True,default=0)
    number_of_item=models.CharField(max_length=300,blank=True,null=True)
    total=models.CharField(max_length=300,blank=True,null=True)

    def __str__(self):
        return str(str(self.account)+" "+str(self.amount))

    def getTransfarLocation(self):
        if self.IsTransfardBalance:
            if self.TransfarRaffer:
                return mark_safe("<a href='/admin/bnmc_project/transfarbalance/"+str(self.TransfarRaffer.id)+"/change/'>"+str(self.TransfarRaffer)+"</a>")
        return ""


    def get_add_or_remove(self):
        if self.historyType== "1":
            return mark_safe("<span style='width: 10px;height: 10px;background-color: green;border-radius: 100%;content: "";display: block;margin-left: 36px;'></span>")

        if self.historyType == "2":
            return mark_safe("<span style='width: 10px;height: 10px;background-color: red;border-radius: 100%;content: "";display: block;margin-left: 36px;'></span>")
        return ""

    def save(self,commit=True, *args, **kwargs):
        print(self.amount,"from main")
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.edit_on=None
        else:
            self.edit_on=datetime.datetime.now()
        super(BalanceHistory, self).save(*args, **kwargs)

        # amount=0
        # if commit:
        #     if self.BalanceIncomes:
        #         for incomeAmount in self.BalanceIncomes.all():
        #             amount+=incomeAmount.amount
        #         self.amount=amount
        #         self.save(False)


class LicenseHistory(models.Model):
    main_id=models.IntegerField(blank=True,null=True)
    license_number = models.IntegerField(blank=True, null=True)
    program = models.ForeignKey(Program, max_length=120, on_delete=models.CASCADE, null=True,blank=True)
    registration_no = models.CharField(null=True, blank=True, max_length=300,verbose_name='Student id')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True,blank=True)
    license_registration_date = models.CharField(max_length=120, blank=True, null=True)
    license_start_date = models.CharField(max_length=120, blank=True, null=True)
    license_end_date = models.CharField(max_length=120, blank=True, null=True)
    money_recipte_id=models.ForeignKey('BalanceHistory',on_delete=models.CASCADE, null=True,blank=True)
    date_of_passing=models.CharField(max_length=120, blank=True, null=True)
    license_receive_id=models.ForeignKey("license_receive",null=True,blank=True,on_delete=models.CASCADE)
    student_id=models.ForeignKey('Student',null=True,blank=True,on_delete=models.CASCADE)
    student_registration_id=models.ForeignKey('Student_Registration',null=True,blank=True,on_delete=models.CASCADE)
    license_registration_id=models.ForeignKey('license_registrations',null=True,blank=True,on_delete=models.CASCADE)
    renew_history = models.ManyToManyField('re_new_history', verbose_name='Renew History',blank=True)
    lock=models.BooleanField(blank=True,default=False)
    card_serial = models.IntegerField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self._state.adding:
            emplty=0
            obj=LicenseHistory.objects.all().last()
            if obj:
              self.main_id=int(obj.id+1)

            else:
                self.main_id=emplty+1


        else:
            self.main_id=self.id

        super(LicenseHistory, self).save(*args, **kwargs)

class TransfarBalance(models.Model):
    FromAccount=models.ForeignKey(Accounts,null=False,blank=False, on_delete=None,related_name='FromAccount')
    ToAccount=models.ForeignKey(Accounts,null=False,blank=False, on_delete=None,related_name='ToAccount')
    amount=models.DecimalField(max_digits=10, decimal_places=5)
    Note=models.TextField(max_length=500,blank=True,null=True)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)

    def __str__(self):
        return str(str(self.FromAccount)+"---->> "+str(self.ToAccount))
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.edit_on=None
        else:
            self.edit_on=datetime.datetime.now()
        super(TransfarBalance, self).save(*args, **kwargs)
        removeBalance=BalanceHistory(account=self.FromAccount,historyType=2,amount=self.amount,Note="Transfar Id id "+str(self.id),IsTransfardBalance=True,TransfarRaffer=self,IsApproved=True)
        removeBalance.save(commit=False)
        addBalance= BalanceHistory(account=self.ToAccount,historyType=1,amount=self.amount,Note="Transfar Id id "+str(self.id),IsTransfardBalance=True,TransfarRaffer=self,IsApproved=True)
        addBalance.save(commit=False)

class BalanceIncome(models.Model):
    name=models.CharField(max_length=200,blank=False)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)
    head_no=models.IntegerField(blank=True,null=True)
    change_amount=models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.create_on=datetime.datetime.now()
            self.edit_on=None
        else:
            self.edit_on=datetime.datetime.now()
        super(BalanceIncome, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    def save(self, new_image=False, *args, **kwargs):

        super(BalanceIncome, self).save(*args, **kwargs)



class BalanceIncome_institute(models.Model):
    name=models.CharField(max_length=200,blank=False)
    create_on=models.DateTimeField(null=True,blank=True)
    edit_on=models.DateTimeField(null=True,blank=True,auto_now=True)
    head_no=models.IntegerField(blank=True,null=True)
    change_amount=models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2)



class CenterManagement(models.Model):
    exam=models.ForeignKey(Exam,blank=True, on_delete=None,null=True)
    roll_start=models.CharField(blank=True,max_length=300,null=True)
    roll_end=models.CharField(blank=True,max_length=300,null=True)
    center=models.ForeignKey(ExamCenter,on_delete=None,null=True)
    hall_name=models.CharField(blank=True,max_length=300,null=True)
    room_name=models.CharField(blank=True,max_length=300,null=True)

    def __str__(self):
        return str(self.exam)



class StudentFileProgram(models.Model):
    program_id = models.ForeignKey(Program, blank=True, null=True,on_delete=models.CASCADE)
    caption = models.CharField(max_length=300, blank=False)

    def __str__(self):
        return str(self.caption)

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class Student_file(models.Model):
    student_file_program=models.ForeignKey(StudentFileProgram,on_delete=models.CASCADE,null=True)
    student_registration=models.ForeignKey(Student_Registration,blank=True,null=True,on_delete=models.CASCADE)
    file=models.FileField(upload_to='student_file/',blank=False)




    def save(self, *args, **kwargs):
        if self._state.adding:
            print('kkk')
            if self.file:
                print('kkk')
                imageTemproary = Image.open(self.file)
                outputIoStream = BytesIO()
                imageTemproaryResized = imageTemproary.resize((1020, 573))
                imageTemproaryResized.save(outputIoStream, format='JPEG', quality=30)
                outputIoStream.seek(0)
                self.file = InMemoryUploadedFile(outputIoStream, 'ImageField',
                                                  "%s.jpg" % self.file.name.split('.')[0], 'image/jpeg',
                                                  sys.getsizeof(outputIoStream), None)
        else:
            print('llll')
            if self.file:

                imageTemproary = Image.open(self.file)
                outputIoStream = BytesIO()
                imageTemproaryResized = imageTemproary.resize((1020, 573))
                imageTemproaryResized.save(outputIoStream, format='JPEG', quality=30)
                outputIoStream.seek(0)
                self.file = InMemoryUploadedFile(outputIoStream, 'ImageField',
                                                 "%s.jpg" % self.file.name.split('.')[0], 'image/jpeg',
                                                 sys.getsizeof(outputIoStream), None)
        super(Student_file,self).save(*args, **kwargs)
    class Meta:
        verbose_name = "Student Educational Document"

    def __str__(self):
        return str(self.student_file_program)



class Designation(models.Model):
    designation_name=models.CharField(max_length=300,blank=True)


    def __str__(self):
        return str(self.designation_name)


class IntuitionProfile(models.Model):
    is_nurse=models.BooleanField(blank=True)
    license_number=models.IntegerField(blank=True,null=True)
    image=models.ImageField(upload_to='institute_profile/')

    def Image_View(self):
        return mark_safe('<img  class="cb_img"  src="/media/%s" width="130" height="130"/>' % (self.image))
    institute_name=models.ForeignKey(Institution,on_delete=None,null=True)
    type_choices = (('1', 'Nurse'), ('2', 'Non-Nurse'))
    employment_type=models.CharField(max_length=300,blank=True,null=True,choices=type_choices,default=2)
    designation=models.ForeignKey(Designation,on_delete=None,null=True,blank=True)
    faculty_id=models.CharField(max_length=300,blank=True)
    date_of_joining=models.CharField(blank=True,null=True,max_length=120)
    work_starting_date=models.CharField(blank=True,null=True,max_length=120)
    full_name_english=models.CharField(max_length=300,blank=True,null=True)
    father_name=models.CharField(max_length=300,blank=True,null=True)
    mother_name=models.CharField(max_length=300,blank=True,null=True)
    choice_sex = (('1', 'Male'), ('2', 'Female'), ('3', 'Others'))
    sex = models.CharField(max_length=12, choices=choice_sex, blank=True, null=True)
    date_of_birth=models.CharField(blank=True,null=True,max_length=120)
    choice_status = (('1', 'Single'), ('2', 'Married'), ('3', 'Widow'), ('4', 'Divorce'), ('5', 'Separated'))
    marital_status = models.CharField(max_length=120, choices=choice_status, null=True)
    national_ID_No = models.CharField(max_length=128, blank=True, null=True)
    students_mobile_no = models.CharField(max_length=200, null=True)
    email_address = models.EmailField(max_length=128, blank=True, null=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True)
    district = ChainedForeignKey(
        'District',
        chained_field="division", chained_model_field="division", show_all=False, auto_choose=True, null=True)
    thana = ChainedForeignKey(
        'Thana', null=True,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True
    )
    village = models.CharField(max_length=300, null=True)
    post_office = models.CharField(max_length=300, null=True)
    postal_code = models.CharField(max_length=300, blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, null=True)
    student=models.ForeignKey(Student,on_delete=None,null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.student:
                self.full_name_english=None
                self.father_name=None
                self.mother_name=None
                self.marital_status=None
                self.sex=None
                self.nationality=None
                self.division=None
                self.district=None
                self.thana=None
                self.village=None
                self.email_address=None
                self.post_office=None
                self.postal_code=None
                self.date_of_birth=None

        else:
            if self.student:
                self.full_name_english = None
                self.father_name = None
                self.mother_name = None
                self.marital_status = None
                self.sex = None
                self.nationality = None
                self.division = None
                self.district = None
                self.thana = None
                self.village = None
                self.email_address = None
                self.post_office = None
                self.postal_code = None
                self.date_of_birth = None
        super(IntuitionProfile, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(IntuitionProfile, self).__init__(*args, **kwargs)

        if self.student:
            student_exit=Student.objects.get(id=self.student.id)
            if student_exit:
                self.full_name_english=student_exit.first_name
                self.father_name=student_exit.fathers_name
                self.mother_name=student_exit.mothers_name
                self.marital_status=student_exit.marital_status
                self.sex=student_exit.sex
                self.nationality=student_exit.nationality
                self.date_of_birth=student_exit.date_of_birth
                self.division=student_exit.division
                self.district=student_exit.district
                self.thana=student_exit.thana
                self.postal_code=student_exit.postal_code
                self.post_office=student_exit.post_office
                self.village=student_exit.village


class ApplyLicense(models.Model):
    choice_type = (('1', 'Government'), ('2', 'Nongovernment'))
    currently_working_place=models.CharField(max_length=300,blank=True,null=True,choices=choice_type)
    current_position=models.CharField(max_length=300,blank=True,null=True)
    Working_years_as_a_registered=models.CharField(max_length=300,blank=True,null=True)
    Training=models.CharField(max_length=300,blank=True,null=True)
    Attendance_in_Seminar=models.CharField(verbose_name='Attendance in Seminar/ Symposium/Workshop/Case Presentation/ Meeting',max_length=300,blank=True,null=True)
    Research_skills=models.CharField(verbose_name='Research Publications/ Other skills',max_length=300,blank=True,null=True)
    license_id=models.ForeignKey(license_receive,on_delete=None,null=True,blank=True)
    I_am_satisfied=models.BooleanField(blank=True,default=False,verbose_name='I am satisfied with my Job')
    before_starting=models.BooleanField(blank=True,default=False,verbose_name='Before starting my work I exchange my greetings with the patients')
    I_own_my =models.BooleanField(blank=True,default=False,verbose_name='I own my responsibility as one of the  Medical Team Members')
    I_am_interested =models.BooleanField(blank=True,default=False,verbose_name='I am interested  to act as a nurse teacher in my working situation')
    I_am_aware =models.BooleanField(blank=True,default=False,verbose_name='I am aware of  my  working area, delegated authority & responsibilities')
    I_am_aware_of_prescribed =models.BooleanField(blank=True,default=False,verbose_name='I am aware of  prescribed code of conduct & ethics of Bangladesh Nursing Council')
    In_Bangladesh_most =models.BooleanField(blank=True,default=False,verbose_name='In Bangladesh most of the basic nursing activities are performed by patients’ attendance')
    Every_day =models.BooleanField(blank=True,default=False,verbose_name='Every day I do my work through nursing care plan')
    I_always_try =models.BooleanField(blank=True,default=False,verbose_name='I always try my best level to treat the patients equally in terms of race, religion, gender, age, nationality & economical class')
    I_am_aware_of_functions =models.BooleanField(blank=True,default=False,verbose_name='I am aware of  functions of Bangladesh Nursing Council')
    I_always_wear_my_professional =models.BooleanField(blank=True,default=False,verbose_name='I always wear my professional Uniform as approved by the Govt. of Bangladesh')
    I_feel_the_present =models.BooleanField(blank=True,default=False,verbose_name='I feel the present existing system of Registration & Renewal should be digitalized')
    I_feel_there_should_be =models.BooleanField(blank=True,default=False,verbose_name='I feel there should be provision of examination system for Registration Renewal in Bangladesh like other countries')
    I_know_the_number =models.BooleanField(blank=True,default=False,verbose_name='I know the  number of registered nurses, nursing institutions & colleges')
    urgent=models.BooleanField(blank=True,default=False)
    image=models.ImageField(upload_to="media/",blank=True,null=True)


class RequestedLicense(models.Model):
    program=models.ForeignKey(Program,on_delete=None,null=True,blank=True)
    license_number=models.CharField(max_length=120,blank=True,null=True)
    applyLicense=models.ForeignKey(ApplyLicense,on_delete=None,null=True,blank=True)
    name=models.CharField(max_length=300,blank=True,null=True)

class UserPermissionResult(models.Model):
    institutions=models.ManyToManyField(Institution)
    final_exam=models.ForeignKey(Final_exam,on_delete=None,null=True,blank=True)
    main_subjects=models.ManyToManyField(ExamSubject)
    program=models.ManyToManyField(Program)
    exam_year=models.ManyToManyField(ExamYear)

    sub_subjects=models.ManyToManyField(SubSubject)
    user=models.ForeignKey(User,on_delete=None,null=True)
    start_roll=models.CharField(blank=True,null=True,max_length=120)
    end_roll=models.CharField(blank=True,null=True,max_length=120)



    def __str__(self):
        return self.start_roll