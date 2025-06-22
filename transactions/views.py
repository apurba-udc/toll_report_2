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
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Transaction


def home_view(request):
    """Overview page - equivalent to Laravel Overview route"""
    return render(request, 'transactions/overview.html')


def transaction_list(request):
    """Transaction list with pagination - equivalent to Laravel show() method"""
    transactions = Transaction.objects.exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class='0'
    ).order_by('-capturedate')
    
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    
    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)
    
    return render(request, 'transactions/list.html', {
        'data': transactions_page,
        'title': 'Transaction Details'
    })


def transaction_pdf(request):
    """Generate PDF report - equivalent to Laravel pdf() method"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
    
    # Create PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph('<b>Transaction Report</b>', styles['Title'])
    elements.append(title)
    
    # Get data
    transactions = Transaction.objects.all()[:100]  # Limit for performance
    
    # Create table data
    data = [['Plaza ID', 'Plaza Name', 'Lane', 'Collector ID', 'Class', 'Date', 'Fare']]
    
    for trans in transactions:
        data.append([
            trans.plazaid or '',
            trans.plazaname or '',
            trans.lane or '',
            trans.collectorid or '',
            trans.vehicle_class or '',
            trans.capturedate.strftime('%Y-%m-%d %H:%M:%S') if trans.capturedate else '',
            trans.get_formatted_fare
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


def daily_report(request):
    """Daily report view - equivalent to Laravel dailyReport() method"""
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
        
        context = {
            'transactions': daily_page,
            'page_obj': daily_page,
            'total_revenue': total_revenue,
            'startDate': start_date,
            'endDate': end_date,
            'startTime': start_time,
            'endTime': end_time,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Daily Transaction Report'
        }
        
        return render(request, 'transactions/transaction_list_simple.html', context)
    
    return render(request, 'transactions/report_date.html')


def lane_shift_report(request):
    """Lane shift report - equivalent to Laravel laneShiftReport() method"""
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
        
        paginator = Paginator(transactions, 10)
        page = request.GET.get('page')
        
        try:
            lane_shift_page = paginator.page(page)
        except PageNotAnInteger:
            lane_shift_page = paginator.page(1)
        except EmptyPage:
            lane_shift_page = paginator.page(paginator.num_pages)
        
        context = {
            'laneShift': lane_shift_page,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'selected_lane': lane,
            'selected_vtype': request.POST.get('vType'),
            'selected_ptype': request.POST.get('pType'),
            'title': 'Lane Wise Transaction Details'
        }
        
        return render(request, 'transactions/lane_shift_report.html', context)
    
    return render(request, 'transactions/report_date_lane.html')


def lane_wise_report(request):
    """Lane wise revenue summary - equivalent to Laravel laneWiseReport() method"""
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Get lane wise summary
        lane_wise = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='CSH'
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class='0'
        ).values('lane').annotate(
            transaction_count=Count('vehicle_class'),
            total_fare=Sum('fare')
        ).order_by('lane')
        
        context = {
            'laneWise': lane_wise,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Revenue Summary (Cash Only)'
        }
        
        return render(request, 'transactions/lane_wise_report.html', context)
    
    return render(request, 'transactions/summary_brief.html')


def get_vehicle_class_display(vehicle_class):
    """Get vehicle class display name"""
    vehicle_types = {
        '1': 'Motorcycle',
        '2': 'Car/Jeep',
        '3': 'Small Truck',
        '4': 'Medium Truck',
        '5': 'Large Truck',
        '6': 'Bus',
        '7': 'Large Bus',
        '8': 'Trailer',
        '9': 'Multi-Axle',
        '10': 'Special Vehicle',
        '0': 'Violation'
    }
    return vehicle_types.get(vehicle_class, f"Class {vehicle_class}")

def get_lane_display(lane_code):
    """Get lane display name"""
    lane_names = {
        'E101': 'Emergency Lane',
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

def lane_class_wise_report(request):
    """Cash transactions summary with detailed class breakdown - equivalent to Laravel laneClassWiseReport() method"""
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        start_time = request.POST.get('startTime', '00:00:00')
        end_time = request.POST.get('endTime', '23:59:59')
        
        # Combine date and time
        start_datetime = f"{start_date} {start_time}"
        end_datetime = f"{end_date} {end_time}"
        
        # Get all lanes that have cash transactions
        all_lanes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='CSH'  # Only cash transactions
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('lane', flat=True).distinct().order_by('lane')
        
        # Get all vehicle classes that exist in the data for this period
        all_vehicle_classes = Transaction.objects.filter(
            capturedate__gte=start_datetime,
            capturedate__lte=end_datetime,
            paytype='CSH'  # Only cash transactions
        ).exclude(
            transtype__in=['LOGIN', 'LOGOUT']
        ).exclude(
            vehicle_class__in=['0', '', None]
        ).values_list('vehicle_class', flat=True).distinct().order_by('vehicle_class')
        
        # Build cash transaction summary
        traffic_summary = []
        grand_totals = {
            'total_vehicles': 0,
            'total_amount': 0,
            'classes': {}  # Store class totals in nested dictionary
        }
        
        # Initialize grand totals for each class
        for vc in all_vehicle_classes:
            grand_totals[f'class_{vc}_count'] = 0
            grand_totals[f'class_{vc}_amount'] = 0
            grand_totals['classes'][vc] = {
                'count': 0,
                'amount': 0
            }
        
        for lane in all_lanes:
            lane_data = {
                'lane': lane,
                'lane_display': get_lane_display(lane),
                'total_vehicles': 0,
                'total_amount': 0,
                'classes': {}  # Store class data in a nested dictionary
            }
            
            # Get cash transactions for this lane only
            lane_transactions = Transaction.objects.filter(
                capturedate__gte=start_datetime,
                capturedate__lte=end_datetime,
                lane=lane,
                paytype='CSH'  # Only cash transactions
            ).exclude(
                transtype__in=['LOGIN', 'LOGOUT']
            ).exclude(
                vehicle_class__in=['0', '', None]
            )
            
            # Count and sum by each vehicle class
            for vehicle_class in all_vehicle_classes:
                class_transactions = lane_transactions.filter(vehicle_class=vehicle_class)
                class_count = class_transactions.count()
                class_amount = class_transactions.aggregate(total=Sum('fare'))['total'] or 0
                
                # Store in lane data (both ways for template compatibility)
                lane_data[f'class_{vehicle_class}_count'] = class_count
                lane_data[f'class_{vehicle_class}_amount'] = class_amount
                lane_data['classes'][vehicle_class] = {
                    'count': class_count,
                    'amount': class_amount
                }
                
                # Add to lane totals
                lane_data['total_vehicles'] += class_count
                lane_data['total_amount'] += class_amount
                
                # Add to grand totals
                grand_totals[f'class_{vehicle_class}_count'] += class_count
                grand_totals[f'class_{vehicle_class}_amount'] += class_amount
                grand_totals['classes'][vehicle_class]['count'] += class_count
                grand_totals['classes'][vehicle_class]['amount'] += class_amount
            
            # Add lane totals to grand totals
            grand_totals['total_vehicles'] += lane_data['total_vehicles']
            grand_totals['total_amount'] += lane_data['total_amount']
            
            # Only add lanes that have transactions
            if lane_data['total_vehicles'] > 0:
                traffic_summary.append(lane_data)
        
        # Create vehicle class display mapping
        vehicle_class_displays = {}
        for vc in all_vehicle_classes:
            vehicle_class_displays[vc] = get_vehicle_class_display(vc)
        
        context = {
            'traffic_summary': traffic_summary,
            'grand_totals': grand_totals,
            'vehicle_classes': sorted(all_vehicle_classes),
            'vehicle_class_displays': vehicle_class_displays,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Cash Transactions Summary by Lane and Class'
        }
        
        return render(request, 'transactions/lane_class_wise_report.html', context)
    
    return render(request, 'transactions/summary_detail.html')


def exempt_report(request):
    """Exempt transaction report - equivalent to Laravel lane() method"""
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
        vehicle_class_displays = {}
        for vc in all_vehicle_classes:
            vehicle_class_displays[vc] = get_vehicle_class_display(vc)
        
        context = {
            'exempt_summary': exempt_summary,
            'grand_totals': grand_totals,
            'vehicle_classes': sorted(all_vehicle_classes),
            'vehicle_class_displays': vehicle_class_displays,
            'total_exempt_vehicles': grand_totals['total_vehicles'],
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'title': 'Traffic Summary (Exempt Only)'
        }
        
        return render(request, 'transactions/exempt_report.html', context)
    
    return render(request, 'transactions/exempt_details.html')


def get_image_view(request, transaction_id):
    """Get transaction image - serves binary image data directly for AJAX requests"""
    try:
        # Handle duplicate sequences by getting the first one with image
        transaction = Transaction.objects.filter(
            sequence=transaction_id,
            pic__isnull=False
        ).first()
        
        if transaction and transaction.pic:
            # Return image as HTTP response with proper content type
            response = HttpResponse(transaction.pic, content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="vehicle_{transaction_id}.jpg"'
            return response
        else:
            # Return 404 if no image found
            return HttpResponse('Image not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


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
