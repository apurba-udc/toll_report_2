from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'transactions'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='overview'),
    path('list/', views.transaction_list, name='transaction_list'),
    path('list/pdf/', views.transaction_pdf, name='transaction_pdf'),
    
    # Report pages
    path('report_date/', views.daily_report, name='report_date'),
    path('daily_report/', views.daily_report, name='daily_report'),
    path('report_date_lane/', views.lane_shift_report, name='report_date_lane'),
    path('daily_shift_report/', views.lane_shift_report, name='daily_shift_report'),
    
    # Summary pages
    path('summary_brief/', views.lane_wise_report, name='summary_brief'),
    path('summary_lane/', views.lane_wise_report, name='summary_lane'),
    path('summary_detail/', views.lane_class_wise_report, name='summary_detail'),
    path('summary_class/', views.lane_class_wise_report, name='summary_class'),
    
    # Exempt reports
    path('exempt/', views.exempt_report, name='exempt'),  # Form page (GET) and report (POST)
    path('exempt/', views.exempt_report, name='exempt_details'),  # Alternative name
    path('exempt_detail/', views.exempt_report, name='exempt_detail'),  # Alternative URL
    
    # API endpoints
    path('api/image/<str:transaction_id>/', views.get_image_view, name='get_image'),
    
    # Test page
    path('test-images/', TemplateView.as_view(template_name='test_images.html'), name='test_images'),
] 