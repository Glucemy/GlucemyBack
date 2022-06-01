import datetime
from datetime import timedelta

from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.http import FileResponse, JsonResponse
from drf_spectacular.utils import extend_schema_view, extend_schema
from fpdf import FPDF
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from records.fullSerializers import UpdateRecordSerializer, CreateRecordSerializer, FullRecordSerializer
from shared.mixins import DynamicSerializersMixin
from records.models import Records
from shared.permissions import IsOwner


@extend_schema_view(
    list=extend_schema(description='Get paginated list of records.'),
    update=extend_schema(description='Update record data.'),
    partial_update=extend_schema(description='Partially update record data.'),
    destroy=extend_schema(description='Delete a record.'),
    create=extend_schema(description='Create a new record.'),
)
class RecordViewSet(DynamicSerializersMixin, viewsets.ModelViewSet):
    queryset = Records.objects.all()
    serializer_class = FullRecordSerializer

    serializer_classes_by_action = {
        'update': UpdateRecordSerializer,
        'create': CreateRecordSerializer,
        'partial_update': UpdateRecordSerializer,
    }

    permission_classes_by_action = {
        'create': (permissions.IsAuthenticated,),
        'update': (permissions.IsAdminUser | IsOwner,),
        'partial_update': (permissions.IsAdminUser | IsOwner,),
        'destroy': (permissions.IsAdminUser | IsOwner,),
        'charts': (permissions.IsAdminUser | IsOwner,),
        'records_day': (permissions.IsAdminUser | IsOwner,),
        'report': (permissions.IsAuthenticated,)
    }

    @action(methods=['get'], detail=False, url_path='(?P<day>[^/.]+)', url_name="record_day")
    def records_day(self, request, day):
        start_date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=1)
        records = Records.objects.filter(created_date__range=[start_date, end_date], user=request.user)
        serializer = self.get_serializer(records, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(methods=["get"], detail=False, url_path='(?P<start_date>[^/.]+)/(?P<end_date>[^/.]+)',
            url_name="charts")
    def charts(self, arg, start_date, end_date):
        labels = []
        blood_glucose_data = []
        carbohydrates_data = []

        queryset = Records.objects.annotate(day=TruncDay('created_date')).values('day').annotate(
            totalBlood=Sum('blood_glucose'), totalCarbohydrates=Sum('carbohydrates')).order_by('day').filter(
            created_date__range=[start_date, end_date], user=arg.user)

        for record in queryset:
            labels.append(record['day'].strftime("%d/%m/%Y"))
            blood_glucose_data.append(record['totalBlood']),
            carbohydrates_data.append(record['totalCarbohydrates'])

        return JsonResponse(data={
            'blood_glucose_data': blood_glucose_data,
            'carbohydrates_data': carbohydrates_data,
            'labels': labels,
        })

    @action(methods=["post"], detail=False, url_path='report', url_name="report")
    def report(self, arg):
        data = []

        # Query
        queryset = Records.objects.all().filter(user=arg.user).order_by('created_date')
        for record in list(queryset):
            data.append(record)

        # PDF
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(40, 10, 'Glucose reports:', 0, 1)
        pdf.cell(40, 10, '', 0, 1)
        pdf.line(10, 30, 200, 30)

        # Table
        line_height = pdf.font_size * 1.5
        col_width = pdf.epw / 6

        # Headers
        pdf.set_font('helvetica', 'B', 11)
        pdf.line(10, 38, 200, 38)
        lista = ['Food name', 'Blood glucose', 'Rations', 'Unities', 'Phase day', 'Date']
        for item in lista:
            pdf.multi_cell(col_width, line_height, item, border=0, ln=3)

        # Data
        pdf.set_font('helvetica', '', 10)
        pdf.ln(line_height)
        pdf.line(10, 38, 200, 38)

        for record in data:
            for food in list(record.foods.all()):
                foodN = (str(food.name)[:13] + '...') if len(str(food.name)) > 13 else str(food.name)
                lista = [foodN, str(round(record.blood_glucose)), str(round(food.hc_rations)),
                         str(round(record.units)),
                         str(record.phasesDay.name), str(record.created_date.strftime('%m/%d/%Y, %H:%M'))]
                for item in lista:
                    pdf.multi_cell(col_width, line_height, item, border=0, ln=3)
                pdf.ln(line_height)

        # Output
        pdf.output('report.pdf', 'F')
        return FileResponse(open('report.pdf', 'rb'), as_attachment=True, content_type='application/pdf')
