"""bnmc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import path
from django.conf.urls import include, url
from bnmc_project.views import registration_step,all_student,rest,get_parameter,get_slide,get_all_post
from bnmc_project import views as bnmc_view
from bnmc import settings
from django.views.generic.base import TemplateView
from django.contrib.auth import user_logged_in
from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.conf.urls import (handler400, handler403, handler404, handler500)


handler404 = 'bnmc_project.views.bad_request'
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^changeStatus/',bnmc_view.registration_step,name="registration"),
    url(r'^changeStatus_exam/', bnmc_view.changeStatus_exam, name="changeStatus_exam"),
    url(r'^changeExamStatus/',bnmc_view.changeExamStatus,name="changeExamStatus"),
    url(r'^get_info_moneyrecipte/',bnmc_view.get_info_moneyrecipte,name="get_info_moneyrecipte"),
    url(r'^get_info_moneyrecipte_li/',bnmc_view.get_info_moneyrecipte_li,name="get_info_moneyrecipte_li"),
    # url(r'^$',bnmc_view.home_view,name="home_view"),
    url(r'^changeStatus_li/',bnmc_view.registration_step_li,name="registration_step_li"),
    url(r'^edit_center/',bnmc_view.edit_center,name="edit_center"),
    url(r'^admin/settings/', login_required(TemplateView.as_view(template_name='admin/settings.html'))),
    url(r'^admin/accounts/', login_required(TemplateView.as_view(template_name='admin/accounts.html'))),
    # url(r'^admin/search_list/student_info', login_required(TemplateView.as_view(template_name='admin/student_info.html'))),

    url(r'^admin/set_center', login_required(bnmc_view.set_center), name="process_licnese"),
    url(r'^get_info_moneyrecipte/',bnmc_view.get_info_moneyrecipte,name="get_info_moneyrecipte"),
    url(r'^get_info_moneyrecipte_li/',bnmc_view.get_info_moneyrecipte_li,name="get_info_moneyrecipte_li"),
    url(r'^admin/setting/user/', login_required(TemplateView.as_view(template_name='admin/user.html'))),
    url(r'^admin/setting/address/', login_required(TemplateView.as_view(template_name='admin/address.html'))),
    url(r'^admin/setting/institution/', login_required(TemplateView.as_view(template_name='admin/institution.html'))),
    url(r'^admin/setting/program/', login_required(TemplateView.as_view(template_name='admin/program.html'))),
    url(r'^admin/registration/', login_required(TemplateView.as_view(template_name='admin/student_registration.html'))),
    url(r'^admin/examination_management/', login_required(TemplateView.as_view(template_name='admin/examination_management.html'))),
    url(r'^admin/apply_final_exam/', login_required(TemplateView.as_view(template_name='admin/apply_final_exam.html'))),
    # url(r'^admin/registration/',bnmc_view.programm_list,'admin/student_registration.html' ),
    url(r'^admin/registrations/program_all/', login_required(TemplateView.as_view(template_name='admin/program_reg_link.html'))),
    url(r'^admin/registrations/exam_all/', login_required(TemplateView.as_view(template_name='admin/exam_reg_link.html'))),
    url(r'^admin/registrations/student_selection/', login_required(TemplateView.as_view(template_name='admin/student_selection_page.html'))),
    url(r'^admin/search_list/', login_required(bnmc_view.all_student,)),
    url(r'^admin/search/student_info/(?P<student_id>[0-9]+)$', bnmc_view.info,name='info'),
    url(r'^admin/search/student_sort_info', login_required(bnmc_view.sort_info,)),
    url(r'^admin/registation_panel/', bnmc_view.registation_panel,name="registation_panel"),
    url(r'^get_std_info/', bnmc_view.get_registation_student_info,name="get_std_info"),
    url(r'^get_std_lisence/', bnmc_view.get_registation_student_license,name="get_std_info"),
    url(r'^address_type/', bnmc_view.address,name="address_type"),
    url(r'^search_village/', bnmc_view.search_village, name="search_village"),
    url(r'^search_post/', bnmc_view.search_post_office, name="search_post"),
    url(r'^search_snd_village/', bnmc_view.search_snd_village, name="search_snd_village"),
    url(r'^search_snd_post_office/', bnmc_view.search_snd_post_office, name="search_snd_post_office"),
    url(r'^q_search/', bnmc_view.Search_student, name="search_student"),
    url(r'^get_program_info/', bnmc_view.get_program_info, name="get_program_info"),
    url(r'^admin/send_notification/', login_required(bnmc_view.send_notification), name="send_notification"),
    url(r'^log/', login_required(bnmc_view.log), name="log"),
    url(r'^license_data/', login_required(bnmc_view.license_exam_data), name="license_exam_data"),
    url(r'^re_store_data/', login_required(bnmc_view.re_store_data), name="re_store_data"),
    url(r'^re_store_session/', login_required(bnmc_view.re_store_session), name="re_store_session"),
    url(r'^re_store_stid/', login_required(bnmc_view.re_store_stid), name="re_store_stid"),
    url(r'^get_registation_student_info/', bnmc_view.get_registation_student_info,name="get_registation_student_info"),
    url(r'^get_post/(?P<post_id>[0-9]+)$', get_parameter.as_view()),
    url(r'^get_license_rec_stu/(?P<licenserec_id>[0-9]+)$', bnmc_view.get_license_rec_stu,name='get_license_rec_stu'),
    url(r'^get_slider/', get_slide.as_view()),
    url(r'^get_all_post/', get_all_post.as_view()),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^update_exam/', login_required(bnmc_view.update_exam), name="update_exam"),
    url(r'^admin/center_report/(?P<center_id>[0-9]+)$', login_required(bnmc_view.report_of_center), name="report_of_center"),

    url(r'^edit_final_center/', bnmc_view.edit_final_center, name="edit_final_center"),
    url(r'^admin/center_report_for_final_exam/(?P<center_id>[0-9]+)$',
                      login_required(bnmc_view.report_of_center_for_final_exam),
                      name="report_of_center_for_final_exam"),

    url(r'^approve/', login_required(bnmc_view.approve_student), name="approve_student"),
    url(r'^get_division/', login_required(bnmc_view.get_division), name="get_division"),
    url(r'^get_district/', login_required(bnmc_view.get_district), name="get_district"),
    url(r'^get_division_fisrt/', login_required(bnmc_view.get_division_fisrt), name="get_division_fisrt"),
    url(r'^get_district_first/', login_required(bnmc_view.get_district_first), name="get_district_first"),
    url(r'^get_years/', login_required(bnmc_view.get_years), name="get_years"),
    url(r'^get_subjects/', login_required(bnmc_view.get_sub), name="get_sub"),

    url(r'^admin/principal_signature_form/', login_required(bnmc_view.signature_upload_principal), name="signature_upload_principal"),
    url(r'^admin/final_exam_wise_report/', login_required(bnmc_view.final_exam_wise_report),name="final_exam_wise_report"),

    url(r'^found_pass/', login_required(bnmc_view.found_pass), name="found_pass"),
    url(r'^remove_cgpa/', login_required(bnmc_view.remove_cgpa), name="remove_cgpa"),
    # url(r'^render/pdf/', login_required(bnmc_view.get_view)),
    url(r'^clear_reg_number_by_programs/', login_required(bnmc_view.clear_reg_number_by_programs), name="clear_reg_number_by_programs"),
    url(r'^admin/process_licnese', login_required(bnmc_view.process_licnese), name="process_licnese"),
    url(r'^renew_licence/(?P<license_id>[0-9]+)$', login_required(bnmc_view.renew_licence), name="renew_licence"),
    url(r'^admin/print_license_card/(?P<license_history_card>[0-9]+)$',login_required(bnmc_view.print_license_card), name="print_license_card"),
    url(r'^admin/unlock/(?P<id_history>[0-9]+)$',login_required(bnmc_view.unlock_history), name="unlock_history"),

    url(r'^institute_code_add/', bnmc_view.institute_code_add, name="institute_code_add"),
    url(r'^rnm_data/', login_required(bnmc_view.rnm_data), name="rnm_data"),

    url(r'^delete_rnm/', login_required(bnmc_view.delete_), name="delete_"),




    url(r'^admin/student_management',login_required(TemplateView.as_view(template_name='admin/student_manage.html'))),
    url(r'^admin/registration_manage_license',login_required(TemplateView.as_view(template_name='admin/registration_license.html'))),
    url(r'^admin/institute_profile',login_required(TemplateView.as_view(template_name='admin/instiute_profile.html'))),

    url(r'^license_data_import/', bnmc_view.license_data_import, name="license_data_import"),
    url(r'^license_data__/', bnmc_view.license_data, name="license_data"),
    url(r'^signature_upload/', bnmc_view.signature_upload, name="signature_upload"),
    url(r'^admin/exam_wise_report/', login_required(bnmc_view.exam_wise_report), name="exam_wise_report"),
    url(r'^admin/division_report/', login_required(bnmc_view.division_wise_report), name="division_wise_report"),

    url(r'^add_student_info/', bnmc_view.add_student_info, name='add_student_info'),
    url(r'^add_distric/', bnmc_view.add_distric, name='add_distric'),
    url(r'^add_thana/', bnmc_view.add_thana, name='add_thana'),
    url(r'^add_instatuited/', bnmc_view.add_instatuited, name='add_instatuited'),
    url(r'^upload_file/', bnmc_view.upload_file, name='upload_file'),
    url(r'^print_license/(?P<license_id>[0-9]+)$', bnmc_view.print_license, name='print_license'),
    url(r'^mark_sheet/(?P<id>[0-9]+)$', bnmc_view.print_exam_mark_sheet, name='print_exam_mark_sheet'),
    url(r'^student_money_recept/', bnmc_view.student_money_recept, name='student_money_recept'),
    #url(r'^student_money_recept/', bnmc_view.student_money_recept, name='student_money_recept')
    url(r'^get_approve/',bnmc_view.get_approve,name="get_approve"),
    url(r'^license_card/',bnmc_view.license_card,name="license_card"),
    url(r'^import_user/',login_required(bnmc_view.import_user),name="import_user"),
    url(r'^change_password/',login_required(bnmc_view.change_password),name="change_password"),

    url(r'^bnc/(?P<entry>[\w\-]+)+.html$', (bnmc_view.license_card_info), name="license_card_info"),

    url(r'^admin/lic_num_src/$', (bnmc_view.search_with_license_number),name="search_with_license_number"),


    url(r'^search_place/', bnmc_view.search_place, name="search_place"),
    url(r'^search_traning/', bnmc_view.search_traning, name="search_traning"),

    url(r'^admin/teacher_form/', bnmc_view.teacher_form, name="teacher_form"),
    url(r'^apply_license_renew/', bnmc_view.apply_for_renew, name="apply_for_renew"),

    url(r'^get_data/', bnmc_view.get_data, name="get_data"),
    url(r'^license_select/', bnmc_view.license_select, name="license_select"),
    url(r'^old/', bnmc_view.old, name="old"),


    url(r'^admin/edit_teacher_form/(?P<id>[0-9]+)$', bnmc_view.edit_teacher_form, name='edit_teacher_form'),
    url(r'^admin/examination_result_add/', bnmc_view.examination_result_add_u_p, name='examination_result_add_u_p'),
    url(r'^all_subjects/(?P<exam_id>[-\w]+)',bnmc_view.all_subjects,name='all_subjects'),

    url(r'^get_sub_subject/(?P<subject_id>[-\w]+)',bnmc_view.get_sub_subject,name='get_sub_subject'),

    url(r'^get_year_url/(?P<program_id>[-\w]+)',bnmc_view.get_year_url,name='get_year_url'),
    url(r'^program_text/',bnmc_view.program_text,name='program_text'),


    url(r'^subject_text/',bnmc_view.subject_text,name='subject_text'),



    url(r'^admin/add_result/(?P<main_subject>[-\w]+)',bnmc_view.examination_result_add,name='examination_result_add'),
    url(r'^admin/choice_subject',bnmc_view.subject_list_result,name='subject_list_result'),

    url(r'^dataUpdate',bnmc_view.dataUpdate,name='dataUpdate'),



              ] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







