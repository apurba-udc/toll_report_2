from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'transactions'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.home_view, name='overview'),
    
    # Utility URLs
    path('system-date/', views.system_date_check, name='system_date_check'),
    
    # Report pages
    path('report_date/', views.daily_report, name='report_date'),
    path('daily_report/', views.daily_report, name='daily_report'),
    path('report_date_lane/', views.lane_shift_report, name='report_date_lane'),
    path('daily_shift_report/', views.lane_shift_report, name='daily_shift_report'),
    
    # Summary pages
    path('summary_brief/', views.lane_wise_report, name='summary_brief'),
    path('summary_lane/', views.lane_wise_report, name='summary_lane'),
    path('summary_lane/pdf/', views.lane_wise_report_pdf, name='summary_lane_pdf'),
    path('summary_detail/', views.lane_class_wise_report, name='summary_detail'),
    path('summary_class/', views.lane_class_wise_report, name='summary_class'),
    path('summary_class/pdf/', views.lane_class_wise_report_pdf, name='summary_class_pdf'),
    
    # Exempt reports
    path('exempt/', views.exempt_report, name='exempt'),  # Form page (GET) and report (POST)
    path('exempt/', views.exempt_report, name='exempt_details'),  # Alternative name
    path('exempt_detail/', views.exempt_report, name='exempt_detail'),  # Alternative URL
    path('exempt/pdf/', views.exempt_report_pdf, name='exempt_pdf'),
    
    # Exempt transaction detail report (new)
    path('exempt_transaction_detail/', views.exempt_transaction_detail_report, name='exempt_transaction_detail'),
    
    # API endpoints
    path('api/image/<str:transaction_id>/', views.get_image_view, name='get_image'),
    
    # Test page
    path('test-images/', TemplateView.as_view(template_name='test_images.html'), name='test_images'),
] 