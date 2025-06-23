from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum, Max, Min
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, date
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Transaction, TollUser
from django.urls import reverse


@login_required
def home_view(request):
    """Overview page - equivalent to Laravel Overview route"""
    return render(request, 'transactions/overview.html')


@login_required
def daily_report(request):
    """Daily report view - equivalent to Laravel dailyReport() method"""
    # Get current date for default values
    today = date.today()
    current_date_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Filter transactions
        transactions = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class='0'
        ).order_by('-capturedate')
        
        paginator = Paginator(transactions, 30)
        page = request.POST.get('page') or request.GET.get('page')
        
        try:
            daily_page = paginator.page(page)
        except PageNotAnInteger:
            daily_page = paginator.page(1)
        except EmptyPage:
            daily_page = paginator.page(paginator.num_pages)
        
        # Calculate total revenue for all transactions in the period
        total_revenue = transactions.aggregate(total=Sum('fare'))['total'] or 0
        
        # Calculate start index for sequential numbering
        start_index = int((daily_page.number - 1) * paginator.per_page)
        
        context = {
            'transactions': daily_page,
            'page_obj': daily_page,
            'start_index': start_index,
            'total_revenue': total_revenue,
            'startDate': start_date,
            'endDate': end_date,
            'startTime': start_time,
            'endTime': end_time,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Daily Transaction Report',
            'current_date': current_date_str,
        }
        
        return render(request, 'transactions/daily_report.html', context)
    
    # For GET requests, provide current date as defaults
    context = {
        'current_date': current_date_str,
        'default_start_date': current_date_str,
        'default_end_date': current_date_str,
    }
    return render(request, 'transactions/report_date.html', context)


@login_required
def lane_shift_report(request):
    """Lane shift report - equivalent to Laravel laneShiftReport() method"""
    # Get current date for default values
    today = date.today()
    current_date_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        lane = request.POST.get('lane')
        v_type = request.POST.get('vType')
        p_type = request.POST.get('pType')
        
        # Convert vehicle type
        if v_type == 'Violation':
            v_type = '0'
        
        # Convert payment type
        if p_type == 'Cash':
            p_type = 'CSH'
        elif p_type == 'Exempt':
            p_type = 'VCH'
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Build query
        transactions = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        )
        
        # Apply filters based on selections
        if lane != "All":
            transactions = transactions.filter(lane=lane)
        if v_type != "All":
            transactions = transactions.filter(vehicle_class=v_type)
        if p_type != "All":
            transactions = transactions.filter(paytype=p_type)
        
        transactions = transactions.order_by('-capturedate')
        
        paginator = Paginator(transactions, 30)
        page = request.POST.get('page') or request.GET.get('page')
        
        try:
            lane_shift_page = paginator.page(page)
        except PageNotAnInteger:
            lane_shift_page = paginator.page(1)
        except EmptyPage:
            lane_shift_page = paginator.page(paginator.num_pages)
        
        # Calculate start index for sequential numbering (ensuring integer)
        start_index = int((lane_shift_page.number - 1) * paginator.per_page)
        
        # Create dynamic title based on filters
        title_parts = []
        selected_vtype_val = request.POST.get('vType', 'All')
        selected_ptype = request.POST.get('pType', 'All')

        if lane and lane != "All":
            title_parts.append(f"Lane {lane}")
        if selected_vtype_val and selected_vtype_val != "All":
            # Convert vehicle class number to name for the title
            vtype_name = get_vehicle_class_display(selected_vtype_val)
            title_parts.append(vtype_name)
        if selected_ptype and selected_ptype != "All":
            title_parts.append(selected_ptype)

        if not title_parts:
            title = 'Unfiltered Transaction Report'
        else:
            title = ' | '.join(title_parts) + ' Filtered Report'

        context = {
            'transactions': lane_shift_page,
            'start_index': start_index,
            'startDate': start_date,
            'endDate': end_date,
            'startTime': start_time,
            'endTime': end_time,
            'lane': lane,
            'title': title,
            'current_date': current_date_str,
        }
        
        return render(request, 'transactions/lane_shift_report.html', context)
    
    # For GET requests, provide current date as defaults
    context = {
        'current_date': current_date_str,
        'default_start_date': current_date_str,
        'default_end_date': current_date_str,
    }
    return render(request, 'transactions/report_date_lane.html', context)


@login_required
def lane_wise_report(request):
    """Lane wise revenue summary - equivalent to Laravel laneWiseReport() method"""
    # Get current date for default values
    today = date.today()
    current_date_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        base_query = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        )

        # Get all lanes
        all_lanes = base_query.values_list('lane', flat=True).distinct().order_by('lane')
        
        lane_summary = []
        grand_totals = {
            'total_cash': 0,
            'total_exempt': 0,
            'total_revenue': 0
        }
        
        for lane in all_lanes:
            lane_transactions = base_query.filter(lane=lane)
            
            cash_transactions = lane_transactions.filter(paytype='CSH').count()
            exempt_transactions = lane_transactions.filter(paytype='VCH').count()
            total_revenue = lane_transactions.filter(paytype='CSH').aggregate(
                total=Sum('fare')
            )['total'] or 0
            
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'cash_transactions': cash_transactions,
                'exempt_transactions': exempt_transactions,
                'total_revenue': total_revenue
            }
            
            lane_summary.append(lane_data)
            
            grand_totals['total_cash'] += cash_transactions
            grand_totals['total_exempt'] += exempt_transactions
            grand_totals['total_revenue'] += total_revenue

        # Calculate summary statistics
        total_traffic = grand_totals['total_cash'] + grand_totals['total_exempt']
        average_revenue_per_vehicle = (grand_totals['total_revenue'] / grand_totals['total_cash']) if grand_totals['total_cash'] > 0 else 0
        
        summary_stats = {
            'total_traffic': total_traffic,
            'total_revenue': grand_totals['total_revenue'],
            'average_revenue_per_vehicle': average_revenue_per_vehicle,
            'total_cash_vehicles': grand_totals['total_cash'],
            'total_exempt_vehicles': grand_totals['total_exempt']
        }

        context = {
            'lane_summary': lane_summary,
            'grand_totals': grand_totals,
            'summary_stats': summary_stats,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Lane Wise Summary',
            'current_date': current_date_str,
        }
        
        return render(request, 'transactions/lane_wise_report.html', context)
    
    # For GET requests, provide current date as defaults
    context = {
        'current_date': current_date_str,
        'default_start_date': current_date_str,
        'default_end_date': current_date_str,
    }
    return render(request, 'transactions/summary_brief.html', context)


@login_required
def lane_wise_report_pdf(request):
    """Generate PDF for lane wise report"""
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        base_query = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        )

        # Get all lanes
        all_lanes = base_query.values_list('lane', flat=True).distinct().order_by('lane')
        
        lane_summary = []
        grand_totals = {
            'total_cash': 0,
            'total_exempt': 0,
            'total_revenue': 0
        }
        
        for lane in all_lanes:
            lane_transactions = base_query.filter(lane=lane)
            
            cash_transactions = lane_transactions.filter(paytype='CSH').count()
            exempt_transactions = lane_transactions.filter(paytype='VCH').count()
            total_revenue = lane_transactions.filter(paytype='CSH').aggregate(
                total=Sum('fare')
            )['total'] or 0
            
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'cash_transactions': cash_transactions,
                'exempt_transactions': exempt_transactions,
                'total_revenue': total_revenue
            }
            
            lane_summary.append(lane_data)
            
            grand_totals['total_cash'] += cash_transactions
            grand_totals['total_exempt'] += exempt_transactions
            grand_totals['total_revenue'] += total_revenue

        # Calculate summary statistics
        total_traffic = grand_totals['total_cash'] + grand_totals['total_exempt']
        average_revenue_per_vehicle = (grand_totals['total_revenue'] / grand_totals['total_cash']) if grand_totals['total_cash'] > 0 else 0

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lane_wise_report_{start_date}_to_{end_date}.pdf"'
        
        # Ensure A4 size
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title with different font sizes and closer spacing
        title_style = styles['Title'].clone('TitleStyle')
        title_style.spaceAfter = 6  # Reduced space after title
        title = Paragraph('''
        <font size="16"><b>Shaheed Wasim Akram Expressway</b></font><br/>
        <font size="12">Patenga Toll Plaza</font><br/>
        <font size="12">Lane Wise Summary Report</font>
        ''', title_style)
        elements.append(title)
        
        # Date range - centered with smaller font and reduced spacing
        date_style = styles['Normal'].clone('DateStyle')
        date_style.alignment = 1  # Center alignment
        date_style.fontSize = 10
        date_style.spaceBefore = 6  # Reduced space before
        date_style.spaceAfter = 6   # Reduced space after
        date_para = Paragraph(f'<b>Period:</b> {start_date} {start_time} to {end_date} {end_time}', date_style)
        elements.append(date_para)
        
        # Gap between period and table
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Create table data
        data = [['S/N', 'Lane', 'Cash Traffic', 'Exempted Traffic', 'Total Revenue']]
        
        for i, lane in enumerate(lane_summary, 1):
            data.append([
                str(i),
                lane['lane_display'],
                str(lane['cash_transactions']),
                str(lane['exempt_transactions']),
                f"{lane['total_revenue']:,.0f}"
            ])
        
        # Add grand total row
        data.append([
            '',
            'Grand Total',
            str(grand_totals['total_cash']),
            str(grand_totals['total_exempt']),
            f"{grand_totals['total_revenue']:,.0f}"
        ])
        
        # Create table with lighter borders and header
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        
        # Gap between table and summary statistics
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Summary Statistics - after table with "Taka" text
        summary_para = Paragraph(f'''
        <b>Summary Statistics:</b><br/>
        Total Traffic: {total_traffic:,} vehicles<br/>
        Total Revenue: Taka {grand_totals['total_revenue']:,.0f}<br/>
        Average Revenue per Vehicle: Taka {average_revenue_per_vehicle:.2f}<br/>
        Cash Vehicles: {grand_totals['total_cash']:,}<br/>
        Exempt Vehicles: {grand_totals['total_exempt']:,}
        ''', styles['Normal'])
        elements.append(summary_para)
        
        doc.build(elements)
        
        return response
    
    return redirect('summary_lane')


def get_vehicle_class_display(vehicle_class):
    """Get vehicle class display name"""
    vehicle_types = {
        '1': 'Motor Bike',
        '2': 'CNG',
        '3': 'CAR',
        '4': 'Jeep',
        '5': 'Micro Bus',
        '6': 'Pickup',
        '7': 'Mini Bus',
        '8': 'Bus',
        '9': 'Truck 4W',
        '10': 'Truck 6W',
        '11': 'Covered Van',
        '0': 'Violation'
    }
    # Ensure the key is a stripped string to handle potential whitespace or type issues
    key = str(vehicle_class).strip()
    return vehicle_types.get(key, f"Class {key}")

def get_lane_display(lane_code):
    """Get lane display name"""
    lane_names = {
        'E101': 'ECR 1',
        'L101': 'Lane 1',
        'L102': 'Lane 2', 
        'L103': 'Lane 3',
        'L104': 'Lane 4',
        'L105': 'Lane 5',
        'L106': 'Lane 6',
        'L107': 'Lane 7',
        'L108': 'Lane 8',
        'L109': 'Lane 9',
        'L110': 'Lane 10',
        'L112': 'Lane 12',
        # Add more lane mappings as needed
    }
    return lane_names.get(lane_code, lane_code or 'Unknown Lane')

@login_required
def lane_class_wise_report(request):
    """Cash transactions summary with detailed class breakdown - equivalent to Laravel laneClassWiseReport() method"""
    # Get current date for default values
    today = date.today()
    current_date_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        base_transactions = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        )

        all_lanes = base_transactions.values_list('lane', flat=True).distinct().order_by('lane')
        
        all_vehicle_classes = base_transactions.filter(paytype='CSH').values_list('vehicle_class', flat=True).distinct().order_by('vehicle_class')
        
        traffic_summary = []
        grand_totals = {
            'total_vehicles': 0,
            'total_amount': 0,
            'total_exempt': 0,
            'classes': {}
        }
        
        for vc in all_vehicle_classes:
            grand_totals['classes'][vc] = { 'count': 0, 'amount': 0 }
        
        for lane in all_lanes:
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'total_vehicles': 0,
                'total_amount': 0,
                'exempt_count': 0,
                'classes': {}
            }
            
            lane_transactions_all = base_transactions.filter(lane=lane)
            
            exempt_count = lane_transactions_all.filter(paytype='VCH').count()
            lane_data['exempt_count'] = exempt_count
            grand_totals['total_exempt'] += exempt_count
            
            lane_cash_transactions = lane_transactions_all.filter(paytype='CSH')

            for vehicle_class in all_vehicle_classes:
                class_transactions = lane_cash_transactions.filter(vehicle_class=vehicle_class)
                class_count = class_transactions.count()
                class_amount = class_transactions.aggregate(total=Sum('fare'))['total'] or 0
                
                lane_data['classes'][vehicle_class] = { 'count': class_count, 'amount': class_amount }
                
                lane_data['total_vehicles'] += class_count
                lane_data['total_amount'] += class_amount
                
                grand_totals['classes'][vehicle_class]['count'] += class_count
                grand_totals['classes'][vehicle_class]['amount'] += class_amount
            
            grand_totals['total_vehicles'] += lane_data['total_vehicles']
            grand_totals['total_amount'] += lane_data['total_amount']
            
            if lane_data['total_vehicles'] > 0 or lane_data['exempt_count'] > 0:
                traffic_summary.append(lane_data)
        
        vehicle_class_displays = {vc: get_vehicle_class_display(vc) for vc in all_vehicle_classes}
        
        # Calculate summary statistics
        total_traffic = grand_totals['total_vehicles'] + grand_totals['total_exempt']
        average_revenue_per_vehicle = (grand_totals['total_amount'] / grand_totals['total_vehicles']) if grand_totals['total_vehicles'] > 0 else 0
        
        summary_stats = {
            'total_traffic': total_traffic,
            'total_revenue': grand_totals['total_amount'],
            'average_revenue_per_vehicle': average_revenue_per_vehicle,
            'total_cash_vehicles': grand_totals['total_vehicles'],
            'total_exempt_vehicles': grand_totals['total_exempt']
        }
        
        context = {
            'traffic_summary': traffic_summary,
            'grand_totals': grand_totals,
            'summary_stats': summary_stats,
            'vehicle_classes': sorted(all_vehicle_classes),
            'vehicle_class_displays': vehicle_class_displays,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Lane & Class Wise Summary',
            'current_date': current_date_str,
        }
        
        return render(request, 'transactions/lane_class_wise_report.html', context)
    
    # For GET requests, provide current date as defaults
    context = {
        'current_date': current_date_str,
        'default_start_date': current_date_str,
        'default_end_date': current_date_str,
    }
    return render(request, 'transactions/summary_detail.html', context)


@login_required
def lane_class_wise_report_pdf(request):
    """Generate PDF for lane class wise report"""
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        base_transactions = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        )

        all_lanes = base_transactions.values_list('lane', flat=True).distinct().order_by('lane')
        all_vehicle_classes = base_transactions.filter(paytype='CSH').values_list('vehicle_class', flat=True).distinct().order_by('vehicle_class')
        
        traffic_summary = []
        grand_totals = {
            'total_vehicles': 0,
            'total_amount': 0,
            'total_exempt': 0,
            'classes': {}
        }
        
        for vc in all_vehicle_classes:
            grand_totals['classes'][vc] = { 'count': 0, 'amount': 0 }
        
        for lane in all_lanes:
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'total_vehicles': 0,
                'total_amount': 0,
                'exempt_count': 0,
                'classes': {}
            }
            
            lane_transactions_all = base_transactions.filter(lane=lane)
            exempt_count = lane_transactions_all.filter(paytype='VCH').count()
            lane_data['exempt_count'] = exempt_count
            grand_totals['total_exempt'] += exempt_count
            
            lane_cash_transactions = lane_transactions_all.filter(paytype='CSH')

            for vehicle_class in all_vehicle_classes:
                class_transactions = lane_cash_transactions.filter(vehicle_class=vehicle_class)
                class_count = class_transactions.count()
                class_amount = class_transactions.aggregate(total=Sum('fare'))['total'] or 0
                
                lane_data['classes'][vehicle_class] = { 'count': class_count, 'amount': class_amount }
                lane_data['total_vehicles'] += class_count
                lane_data['total_amount'] += class_amount
                
                grand_totals['classes'][vehicle_class]['count'] += class_count
                grand_totals['classes'][vehicle_class]['amount'] += class_amount
            
            grand_totals['total_vehicles'] += lane_data['total_vehicles']
            grand_totals['total_amount'] += lane_data['total_amount']
            
            if lane_data['total_vehicles'] > 0 or lane_data['exempt_count'] > 0:
                traffic_summary.append(lane_data)
        
        vehicle_class_displays = {vc: get_vehicle_class_display(vc) for vc in all_vehicle_classes}
        
        # Calculate summary statistics
        total_traffic = grand_totals['total_vehicles'] + grand_totals['total_exempt']
        average_revenue_per_vehicle = (grand_totals['total_amount'] / grand_totals['total_vehicles']) if grand_totals['total_vehicles'] > 0 else 0

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lane_class_wise_report_{start_date}_to_{end_date}.pdf"'
        
        # Use landscape orientation for wide table
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title with different font sizes and closer spacing
        title_style = styles['Title'].clone('TitleStyle')
        title_style.spaceAfter = 6  # Reduced space after title
        title = Paragraph('''
        <font size="16"><b>Shaheed Wasim Akram Expressway</b></font><br/>
        <font size="12">Patenga Toll Plaza</font><br/>
        <font size="12">Lane & Class Wise Summary Report</font>
        ''', title_style)
        elements.append(title)
        
        # Date range - centered with smaller font and reduced spacing
        date_style = styles['Normal'].clone('DateStyle')
        date_style.alignment = 1  # Center alignment
        date_style.fontSize = 10
        date_style.spaceBefore = 6  # Reduced space before
        date_style.spaceAfter = 6   # Reduced space after
        date_para = Paragraph(f'<b>Period:</b> {start_date} {start_time} to {end_date} {end_time}', date_style)
        elements.append(date_para)
        
        # Gap between period and table
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Create table headers
        headers = ['S/N', 'Lane']
        for vc in sorted(all_vehicle_classes):
            headers.append(vehicle_class_displays[vc])
        headers.extend(['Traffic', 'Exempted', 'Revenue'])
        
        data = [headers]
        
        # Add data rows
        for i, lane in enumerate(traffic_summary, 1):
            row = [str(i), lane['lane_display']]
            for vc in sorted(all_vehicle_classes):
                row.append(str(lane['classes'].get(vc, {}).get('count', 0)))
            row.extend([
                str(lane['total_vehicles']),
                str(lane['exempt_count']),
                f"{lane['total_amount']:,.0f}"
            ])
            data.append(row)
        
        # Add grand total row
        total_row = ['', 'Grand Total']
        for vc in sorted(all_vehicle_classes):
            total_row.append(str(grand_totals['classes'].get(vc, {}).get('count', 0)))
        total_row.extend([
            str(grand_totals['total_vehicles']),
            str(grand_totals['total_exempt']),
            f"{grand_totals['total_amount']:,.0f}"
        ])
        data.append(total_row)
        
        # Create table with lighter borders and header
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        
        # Gap between table and summary statistics
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Summary Statistics - after table with "Taka" text
        summary_para = Paragraph(f'''
        <b>Summary Statistics:</b><br/>
        Total Traffic: {total_traffic:,} vehicles<br/>
        Total Revenue: Taka {grand_totals['total_amount']:,.0f}<br/>
        Average Revenue per Vehicle: Taka {average_revenue_per_vehicle:.2f}<br/>
        Cash Vehicles: {grand_totals['total_vehicles']:,}<br/>
        Exempt Vehicles: {grand_totals['total_exempt']:,}
        ''', styles['Normal'])
        elements.append(summary_para)
        
        doc.build(elements)
        
        return response
    
    return redirect('summary_class')


@login_required
def exempt_report(request):
    """Exempt transaction report - equivalent to Laravel lane() method"""
    # Get current date for default values
    today = date.today()
    current_date_str = today.strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Get all lanes that have exempt transactions
        all_lanes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='VCH'
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('lane', flat=True).distinct().order_by('lane')
        
        # Get all vehicle classes that have exempt transactions
        all_vehicle_classes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='VCH'
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('vehicle_class', flat=True).distinct().order_by('vehicle_class')
        
        # Build exempt transaction summary
        exempt_summary = []
        grand_totals = {
            'total_vehicles': 0,
            'classes': {}
        }
        
        # Initialize grand totals for each class
        for vc in all_vehicle_classes:
            grand_totals['classes'][vc] = 0
        
        for lane in all_lanes:
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'total_vehicles': 0,
                'classes': {}
            }
            
            # Get exempt transactions for this lane
            lane_transactions = Transaction.objects.filter(
                capturedate__gte=start_datetime,
                capturedate__lte=end_datetime,
                lane=lane,
                paytype='VCH'  # Only exempt transactions
            ).exclude(
                transtype__in=['LOGIN', 'LOGOUT']
            ).exclude(
                vehicle_class__in=['0', '', None]
            )
            
            # Count by each vehicle class
            for vehicle_class in all_vehicle_classes:
                class_count = lane_transactions.filter(vehicle_class=vehicle_class).count()
                
                # Store in lane data
                lane_data['classes'][vehicle_class] = class_count
                lane_data['total_vehicles'] += class_count
                
                # Add to grand totals
                grand_totals['classes'][vehicle_class] += class_count
            
            # Add lane totals to grand totals
            grand_totals['total_vehicles'] += lane_data['total_vehicles']
            
            # Only add lanes that have transactions
            if lane_data['total_vehicles'] > 0:
                exempt_summary.append(lane_data)
        
        # Create vehicle class display mapping
        vehicle_class_displays = {vc: get_vehicle_class_display(vc) for vc in all_vehicle_classes}
        
        # Calculate summary statistics for exempt transactions
        summary_stats = {
            'total_exempt_vehicles': grand_totals['total_vehicles'],
            'total_lanes_with_exemptions': len(exempt_summary),
            'total_vehicle_classes': len(all_vehicle_classes),
        }
        
        # Calculate average exemptions per lane
        if summary_stats['total_lanes_with_exemptions'] > 0:
            summary_stats['average_exemptions_per_lane'] = summary_stats['total_exempt_vehicles'] / summary_stats['total_lanes_with_exemptions']
        else:
            summary_stats['average_exemptions_per_lane'] = 0
        
        context = {
            'traffic_summary': exempt_summary,
            'grand_totals': grand_totals,
            'vehicle_classes': sorted(all_vehicle_classes),
            'vehicle_class_displays': vehicle_class_displays,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Exempt Traffic Summary',
            'summary_stats': summary_stats,
            'current_date': current_date_str,
        }
        
        return render(request, 'transactions/exempt_report.html', context)
    
    # For GET requests, provide current date as defaults
    context = {
        'current_date': current_date_str,
        'default_start_date': current_date_str,
        'default_end_date': current_date_str,
    }
    return render(request, 'transactions/exempt_details.html', context)


@login_required
def exempt_report_pdf(request):
    """Generate PDF for exempt report"""
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Get all lanes that have exempt transactions
        all_lanes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='VCH'
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('lane', flat=True).distinct().order_by('lane')
        
        # Get all vehicle classes that have exempt transactions
        all_vehicle_classes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='VCH'
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('vehicle_class', flat=True).distinct().order_by('vehicle_class')
        
        exempt_summary = []
        grand_totals = {
            'total_vehicles': 0,
            'classes': {}
        }
        
        for vc in all_vehicle_classes:
            grand_totals['classes'][vc] = 0
        
        for lane in all_lanes:
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'total_vehicles': 0,
                'classes': {}
            }
            
            lane_transactions = Transaction.objects.filter(
                capturedate__gte=start_datetime,
                capturedate__lte=end_datetime,
                lane=lane,
                paytype='VCH'
            ).exclude(
                transtype__in=['LOGIN', 'LOGOUT']
            ).exclude(
                vehicle_class__in=['0', '', None]
            )
            
            for vehicle_class in all_vehicle_classes:
                class_count = lane_transactions.filter(vehicle_class=vehicle_class).count()
                lane_data['classes'][vehicle_class] = class_count
                lane_data['total_vehicles'] += class_count
                grand_totals['classes'][vehicle_class] += class_count
            
            grand_totals['total_vehicles'] += lane_data['total_vehicles']
            
            if lane_data['total_vehicles'] > 0:
                exempt_summary.append(lane_data)
        
        vehicle_class_displays = {vc: get_vehicle_class_display(vc) for vc in all_vehicle_classes}
        
        # Calculate summary statistics
        total_lanes_with_exemptions = len(exempt_summary)
        average_exemptions_per_lane = (grand_totals['total_vehicles'] / total_lanes_with_exemptions) if total_lanes_with_exemptions > 0 else 0

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="exempt_report_{start_date}_to_{end_date}.pdf"'
        
        # Use landscape orientation for wide table
        doc = SimpleDocTemplate(response, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title with different font sizes and closer spacing
        title_style = styles['Title'].clone('TitleStyle')
        title_style.spaceAfter = 6  # Reduced space after title
        title = Paragraph('''
        <font size="16"><b>Shaheed Wasim Akram Expressway</b></font><br/>
        <font size="12">Patenga Toll Plaza</font><br/>
        <font size="12">Exempt Traffic Summary Report</font>
        ''', title_style)
        elements.append(title)
        
        # Date range - centered with smaller font and reduced spacing
        date_style = styles['Normal'].clone('DateStyle')
        date_style.alignment = 1  # Center alignment
        date_style.fontSize = 10
        date_style.spaceBefore = 6  # Reduced space before
        date_style.spaceAfter = 6   # Reduced space after
        date_para = Paragraph(f'<b>Period:</b> {start_date} {start_time} to {end_date} {end_time}', date_style)
        elements.append(date_para)
        
        # Gap between period and table
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Create table headers
        headers = ['S/N', 'Lane']
        for vc in sorted(all_vehicle_classes):
            headers.append(vehicle_class_displays[vc])
        headers.append('Total Exempted')
        
        data = [headers]
        
        # Add data rows
        for i, lane in enumerate(exempt_summary, 1):
            row = [str(i), lane['lane_display']]
            for vc in sorted(all_vehicle_classes):
                row.append(str(lane['classes'].get(vc, 0)))
            row.append(str(lane['total_vehicles']))
            data.append(row)
        
        # Add grand total row
        total_row = ['', 'Grand Total']
        for vc in sorted(all_vehicle_classes):
            total_row.append(str(grand_totals['classes'].get(vc, 0)))
        total_row.append(str(grand_totals['total_vehicles']))
        data.append(total_row)
        
        # Create table with lighter borders and header
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        
        # Gap between table and summary statistics
        elements.append(Paragraph('<br/><br/>', styles['Normal']))
        
        # Summary Statistics - after table
        summary_para = Paragraph(f'''
        <b>Summary Statistics:</b><br/>
        Total Exempt Vehicles: {grand_totals['total_vehicles']:,}<br/>
        Total Lanes with Exemptions: {total_lanes_with_exemptions}<br/>
        Total Vehicle Classes: {len(all_vehicle_classes)}<br/>
        Average Exemptions per Lane: {average_exemptions_per_lane:.2f}
        ''', styles['Normal'])
        elements.append(summary_para)
        
        doc.build(elements)
        
        return response
    
    return redirect('exempt_report')


@login_required
def get_image_view(request, transaction_id):
    """Get transaction image - serves binary image data directly for AJAX requests"""
    try:
        print(f"Image request for transaction: {transaction_id}")
        
        # Handle duplicate sequences by getting the first one with image
        transaction = Transaction.objects.filter(
            sequence=transaction_id,
            pic__isnull=False
        ).first()
        
        print(f"Found transaction: {transaction is not None}")
        
        if transaction and transaction.pic:
            image_size = len(transaction.pic)
            print(f"Image size: {image_size} bytes")
            
            # Check if it's a valid JPEG
            is_jpeg = transaction.pic.startswith(b'\xff\xd8\xff')
            print(f"Is JPEG: {is_jpeg}")
            
            # Return image as HTTP response with proper content type and headers
            response = HttpResponse(transaction.pic, content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="vehicle_{transaction_id}.jpg"'
            response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
            response['Access-Control-Allow-Origin'] = '*'  # Allow CORS
            response['Access-Control-Allow-Methods'] = 'GET'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            response['Content-Length'] = str(image_size)
            
            print(f"Returning image response with {image_size} bytes")
            return response
        else:
            print(f"No image found for transaction: {transaction_id}")
            # Return 404 if no image found
            response = HttpResponse('Image not found', status=404)
            response['Access-Control-Allow-Origin'] = '*'
            return response
    except Exception as e:
        print(f"Error loading image for transaction {transaction_id}: {str(e)}")
        response = HttpResponse(f'Error: {str(e)}', status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


# Helper functions for class and exempt reports
def get_class_type_count(vehicle_class, lane, max_date, min_date):
    """Get count for specific class type - equivalent to Laravel classTypeReport()"""
    count = Transaction.objects.filter(
        capturedate__lte=max_date,
        capturedate__gte=min_date,
        lane=lane,
        vehicle_class=vehicle_class,
        paytype='CSH'
    ).exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class='0'
    ).count()
    
    return count if count else 0


def get_exempt_by_lane_count(lane, max_date, min_date):
    """Get exempt count by lane - equivalent to Laravel exemptByLane()"""
    count = Transaction.objects.filter(
        capturedate__lte=max_date,
        capturedate__gte=min_date,
        lane=lane,
        paytype='VCH'
    ).exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class='0'
    ).count()
    
    return count if count else 0


def get_exempt_by_class_count(vehicle_class, lane, max_date, min_date):
    """Get exempt count by class - equivalent to Laravel exemptByClassReport()"""
    count = Transaction.objects.filter(
        capturedate__lte=max_date,
        capturedate__gte=min_date,
        lane=lane,
        vehicle_class=vehicle_class,
        paytype='VCH'
    ).exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class='0'
    ).count()
    
    return count if count else 0


def login_view(request):
    """Login view for toll system users"""
    if request.user.is_authenticated:
        return redirect('transactions:overview')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirect to next page or default
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('transactions:overview')
            else:
                # Add error context to template instead of using messages
                context = {
                    'error': 'Invalid username or password. Please check your credentials.',
                    'username': username
                }
                return render(request, 'auth/login.html', context)
        else:
            # Add error context to template instead of using messages
            context = {
                'error': 'Please enter both username and password.',
                'username': username if username else ''
            }
            return render(request, 'auth/login.html', context)
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('transactions:login')

@login_required
def system_date_check(request):
    """Utility view to check current system date"""
    current_date = date.today()
    current_datetime = datetime.now()
    
    data = {
        'current_date': current_date.strftime('%Y-%m-%d'),
        'current_datetime': current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'formatted_date': current_date.strftime('%B %d, %Y'),
        'day_of_week': current_date.strftime('%A'),
        'timezone': str(current_datetime.astimezone().tzinfo)
    }
    
    if request.GET.get('format') == 'json':
        return JsonResponse(data)
    
    return HttpResponse(f"""
    <h2>🕐 System Date & Time Check</h2>
    <p><strong>Current Date:</strong> {data['current_date']}</p>
    <p><strong>Current DateTime:</strong> {data['current_datetime']}</p>
    <p><strong>Formatted Date:</strong> {data['formatted_date']}</p>
    <p><strong>Day of Week:</strong> {data['day_of_week']}</p>
    <p><strong>Timezone:</strong> {data['timezone']}</p>
    <hr>
    <p><a href="?format=json">View as JSON</a> | <a href="/">Back to Home</a></p>
    """, content_type='text/html')
