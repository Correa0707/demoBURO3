from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Beneficiary, Appointment, Case, CaseHistory, Communication,
    Student, LegalRoom, Notification, SystemUser, Metrics,
    AppointmentStatus, CaseStatus, ReasonType, EventType
)
from .forms import (
    BeneficiaryForm, BeneficiaryEditForm,
    AppointmentForm, AppointmentEditForm, AppointmentCancelForm, AttendanceForm,
    CaseForm, CaseEditForm, CaseHistoryForm, ReassignCaseForm,
    CommunicationForm, SendEmailForm,
    LegalRoomForm, ReportFilterForm, CaseReportFilterForm,
    SystemUserCreationForm, StudentForm
)


# ==================== AUTH VIEWS ====================

class LoginView(View):
    """Maneja el inicio de sesion"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}')
            return redirect('home')
        
        messages.error(request, 'Usuario o contrasena incorrectos')
        return render(request, 'login.html')


class LogoutView(View):
    """Maneja el cierre de sesion"""
    
    def post(self, request):
        logout(request)
        messages.info(request, 'Sesion cerrada correctamente')
        return redirect('login')


# ==================== HOME VIEW ====================

class HomeView(LoginRequiredMixin, TemplateView):
    """Vista principal del dashboard"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Estadisticas generales
        context['total_beneficiaries'] = Beneficiary.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_cases'] = Case.objects.count()
        context['pending_appointments'] = Appointment.objects.filter(
            status=AppointmentStatus.PENDING
        ).count()
        
        # Citas de hoy
        context['today_appointments'] = Appointment.objects.filter(
            date__date=today
        ).select_related('beneficiary', 'student_assigned')[:5]
        
        # Citas pendientes proximas
        context['upcoming_appointments'] = Appointment.objects.filter(
            status=AppointmentStatus.PENDING,
            date__gte=timezone.now()
        ).select_related('beneficiary')[:5]
        
        # Casos activos
        context['active_cases'] = Case.objects.filter(
            status__in=[CaseStatus.ASSIGNED, CaseStatus.IN_PROCESS]
        ).count()
        
        # Notificaciones no leidas
        context['unread_notifications'] = Notification.objects.filter(
            user=self.request.user,
            read=False
        ).count()
        
        # Metricas de asistencia del mes
        month_start = today.replace(day=1)
        month_appointments = Appointment.objects.filter(
            date__date__gte=month_start,
            date__date__lte=today
        )
        attended = month_appointments.filter(attended=True).count()
        total = month_appointments.count()
        context['attendance_rate'] = round((attended / total * 100) if total > 0 else 0, 1)
        
        return context


# ==================== BENEFICIARY VIEWS ====================

class BeneficiaryListView(LoginRequiredMixin, ListView):
    """Lista de beneficiarios"""
    model = Beneficiary
    template_name = 'beneficiaries/list.html'
    context_object_name = 'beneficiaries'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(document__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset


class BeneficiaryCreateView(LoginRequiredMixin, CreateView):
    """Crear nuevo beneficiario"""
    model = Beneficiary
    form_class = BeneficiaryForm
    template_name = 'beneficiaries/create.html'
    success_url = reverse_lazy('beneficiary-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Beneficiario registrado exitosamente')
        return super().form_valid(form)


class BeneficiaryDetailView(LoginRequiredMixin, DetailView):
    """Detalle de beneficiario"""
    model = Beneficiary
    template_name = 'beneficiaries/detail.html'
    context_object_name = 'beneficiary'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = self.object.appointments.all()[:10]
        context['cases'] = self.object.cases.all()
        context['communications'] = self.object.communications.all()[:10]
        return context


class BeneficiaryEditView(LoginRequiredMixin, UpdateView):
    """Editar beneficiario"""
    model = Beneficiary
    form_class = BeneficiaryEditForm
    template_name = 'beneficiaries/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiary-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Beneficiario actualizado exitosamente')
        return super().form_valid(form)


# ==================== APPOINTMENT VIEWS ====================

class AppointmentListView(LoginRequiredMixin, ListView):
    """Lista de citas"""
    model = Appointment
    template_name = 'appointments/list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('beneficiary', 'student_assigned')
        
        # Filtros
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = AppointmentStatus.choices
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Crear nueva cita"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create.html'
    success_url = reverse_lazy('appointment-list')
    
    def form_valid(self, form):
        appointment = form.save()
        
        # Crear notificacion
        Notification.objects.create(
            beneficiary=appointment.beneficiary,
            event_type=EventType.APPOINTMENT_SCHEDULED,
            title='Nueva cita agendada',
            message=f'Se ha agendado una cita para el {appointment.date.strftime("%d/%m/%Y %H:%M")}'
        )
        
        messages.success(self.request, 'Cita agendada exitosamente')
        return super().form_valid(form)


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Detalle de cita"""
    model = Appointment
    template_name = 'appointments/detail.html'
    context_object_name = 'appointment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendance_form'] = AttendanceForm()
        context['cancel_form'] = AppointmentCancelForm()
        return context


class AppointmentEditView(LoginRequiredMixin, UpdateView):
    """Editar cita"""
    model = Appointment
    form_class = AppointmentEditForm
    template_name = 'appointments/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('appointment-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Cita actualizada exitosamente')
        return super().form_valid(form)


class AppointmentCancelView(LoginRequiredMixin, View):
    """Cancelar cita"""
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        reason = request.POST.get('reason', '')
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.reason = reason
        appointment.save()
        
        # Crear notificacion
        Notification.objects.create(
            beneficiary=appointment.beneficiary,
            event_type=EventType.APPOINTMENT_CANCELLED,
            title='Cita cancelada',
            message=f'La cita del {appointment.date.strftime("%d/%m/%Y")} ha sido cancelada. Motivo: {reason}'
        )
        
        messages.success(request, 'Cita cancelada exitosamente')
        return redirect('appointment-list')


class AppointmentAttendanceView(LoginRequiredMixin, View):
    """Registrar asistencia a cita"""
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        attended = request.POST.get('attended') == 'on'
        absence_reason = request.POST.get('absence_reason', '')
        
        if attended:
            appointment.register_attendance()
            
            # Si es primera cita, crear caso
            if appointment.is_first_appointment() and not appointment.case:
                case = Case.objects.create(
                    beneficiary=appointment.beneficiary,
                    student_assigned=appointment.student_assigned,
                    description=f'Caso creado a partir de cita del {appointment.date.strftime("%d/%m/%Y")}'
                )
                appointment.case = case
                appointment.save()
                
                messages.info(request, f'Se ha creado el caso {str(case.id)[:8]} a partir de esta cita')
            
            messages.success(request, 'Asistencia registrada exitosamente')
        else:
            appointment.register_absence(absence_reason)
            messages.warning(request, 'Inasistencia registrada')
        
        return redirect('appointment-detail', pk=pk)


class AppointmentReassignView(LoginRequiredMixin, View):
    """Reasignar cita a otro estudiante"""
    
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        students = Student.objects.filter(available=True)
        return render(request, 'appointments/reassign.html', {
            'appointment': appointment,
            'students': students
        })
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        student_id = request.POST.get('student')
        reason = request.POST.get('reason', '')
        
        if student_id:
            new_student = get_object_or_404(Student, pk=student_id)
            old_student = appointment.student_assigned
            
            appointment.student_assigned = new_student
            appointment.status = AppointmentStatus.REASSIGNED
            appointment.reason = reason
            appointment.save()
            
            # Notificar al nuevo estudiante
            Notification.objects.create(
                user=new_student.user,
                event_type=EventType.APPOINTMENT_REASSIGNED,
                title='Nueva cita asignada',
                message=f'Se te ha asignado una cita para el {appointment.date.strftime("%d/%m/%Y %H:%M")}'
            )
            
            messages.success(request, 'Cita reasignada exitosamente')
        
        return redirect('appointment-detail', pk=pk)


# ==================== CASE VIEWS ====================

class CaseListView(LoginRequiredMixin, ListView):
    """Lista de casos"""
    model = Case
    template_name = 'cases/list.html'
    context_object_name = 'cases'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('beneficiary', 'student_assigned', 'legal_room')
        
        status = self.request.GET.get('status')
        legal_room = self.request.GET.get('legal_room')
        
        if status:
            queryset = queryset.filter(status=status)
        if legal_room:
            queryset = queryset.filter(legal_room_id=legal_room)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = CaseStatus.choices
        context['legal_rooms'] = LegalRoom.objects.all()
        return context


class CaseCreateView(LoginRequiredMixin, CreateView):
    """Crear nuevo caso"""
    model = Case
    form_class = CaseForm
    template_name = 'cases/create.html'
    success_url = reverse_lazy('case-list')
    
    def form_valid(self, form):
        case = form.save()
        
        # Registrar en historial
        CaseHistory.objects.create(
            case=case,
            action='Caso creado',
            responsible=getattr(self.request.user, 'student_profile', None)
        )
        
        messages.success(self.request, 'Caso creado exitosamente')
        return super().form_valid(form)


class CaseDetailView(LoginRequiredMixin, DetailView):
    """Detalle de caso"""
    model = Case
    template_name = 'cases/detail.html'
    context_object_name = 'case'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = self.object.history.all()
        context['appointments'] = self.object.appointments.all()
        context['communications'] = self.object.communications.all()
        context['history_form'] = CaseHistoryForm()
        context['reassign_form'] = ReassignCaseForm()
        return context


class CaseEditView(LoginRequiredMixin, UpdateView):
    """Editar caso"""
    model = Case
    form_class = CaseEditForm
    template_name = 'cases/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('case-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Registrar cambio en historial
        CaseHistory.objects.create(
            case=self.object,
            action='Caso actualizado',
            responsible=getattr(self.request.user, 'student_profile', None)
        )
        messages.success(self.request, 'Caso actualizado exitosamente')
        return super().form_valid(form)


class CaseAddHistoryView(LoginRequiredMixin, View):
    """Agregar entrada al historial del caso"""
    
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        form = CaseHistoryForm(request.POST)
        
        if form.is_valid():
            history = form.save(commit=False)
            history.case = case
            history.responsible = getattr(request.user, 'student_profile', None)
            history.save()
            messages.success(request, 'Historial agregado exitosamente')
        
        return redirect('case-detail', pk=pk)


class CaseReassignView(LoginRequiredMixin, View):
    """Reasignar caso a otro estudiante"""
    
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        student_id = request.POST.get('student')
        reason = request.POST.get('reason', '')
        
        if student_id:
            new_student = get_object_or_404(Student, pk=student_id)
            old_student = case.student_assigned
            
            case.student_assigned = new_student
            case.reason_for_reassignment = reason
            case.save()
            
            # Registrar en historial
            CaseHistory.objects.create(
                case=case,
                action=f'Caso reasignado de {old_student} a {new_student}',
                observation=reason,
                responsible=getattr(request.user, 'student_profile', None)
            )
            
            # Notificar al nuevo estudiante
            Notification.objects.create(
                user=new_student.user,
                event_type=EventType.CASE_ASSIGNED,
                title='Caso asignado',
                message=f'Se te ha asignado el caso {str(case.id)[:8]}'
            )
            
            messages.success(request, 'Caso reasignado exitosamente')
        
        return redirect('case-detail', pk=pk)


class CaseCloseView(LoginRequiredMixin, View):
    """Cerrar caso"""
    
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        observation = request.POST.get('observation', '')
        
        case.close_case(observation)
        
        # Notificar al beneficiario
        Notification.objects.create(
            beneficiary=case.beneficiary,
            event_type=EventType.CASE_CLOSED,
            title='Caso cerrado',
            message=f'El caso {str(case.id)[:8]} ha sido cerrado'
        )
        
        messages.success(request, 'Caso cerrado exitosamente')
        return redirect('case-detail', pk=pk)


# ==================== COMMUNICATION VIEWS ====================

class CommunicationListView(LoginRequiredMixin, ListView):
    """Lista de comunicaciones"""
    model = Communication
    template_name = 'communications/list.html'
    context_object_name = 'communications'
    paginate_by = 10


class CommunicationCreateView(LoginRequiredMixin, CreateView):
    """Registrar nueva comunicacion"""
    model = Communication
    form_class = CommunicationForm
    template_name = 'communications/create.html'
    success_url = reverse_lazy('communication-list')
    
    def form_valid(self, form):
        communication = form.save(commit=False)
        communication.responsible = self.request.user
        communication.save()
        messages.success(self.request, 'Comunicacion registrada exitosamente')
        return super().form_valid(form)


class SendEmailView(LoginRequiredMixin, View):
    """Enviar correo electronico"""
    template_name = 'communications/send_email.html'
    
    def get(self, request):
        form = SendEmailForm()
        beneficiary_id = request.GET.get('beneficiary')
        if beneficiary_id:
            try:
                beneficiary = Beneficiary.objects.get(pk=beneficiary_id)
                form.initial['recipient'] = beneficiary.email
            except Beneficiary.DoesNotExist:
                pass
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SendEmailForm(request.POST)
        
        if form.is_valid():
            try:
                send_mail(
                    form.cleaned_data['subject'],
                    form.cleaned_data['message'],
                    None,
                    [form.cleaned_data['recipient']],
                )
                
                # Registrar la comunicacion
                beneficiary = Beneficiary.objects.filter(
                    email=form.cleaned_data['recipient']
                ).first()
                
                if beneficiary:
                    Communication.objects.create(
                        beneficiary=beneficiary,
                        type='EMAIL',
                        description=f"Asunto: {form.cleaned_data['subject']}\n\n{form.cleaned_data['message']}",
                        responsible=request.user
                    )
                
                messages.success(request, 'Correo enviado exitosamente')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {e}')
        
        return render(request, self.template_name, {'form': form})


# ==================== NOTIFICATION VIEWS ====================

class NotificationListView(LoginRequiredMixin, ListView):
    """Lista de notificaciones"""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(LoginRequiredMixin, View):
    """Marcar notificacion como leida"""
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        return redirect('notification-list')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    """Marcar todas las notificaciones como leidas"""
    
    def post(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        messages.success(request, 'Todas las notificaciones marcadas como leidas')
        return redirect('notification-list')


# ==================== REPORT VIEWS ====================

class ReportDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de reportes"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = timezone.now().date()
        
        # Filtrar citas
        appointments = Appointment.objects.filter(
            date__date__gte=start_date,
            date__date__lte=end_date
        )
        
        # Estadisticas de citas
        context['total_appointments'] = appointments.count()
        context['attended_appointments'] = appointments.filter(attended=True).count()
        context['cancelled_appointments'] = appointments.filter(status=AppointmentStatus.CANCELLED).count()
        context['absence_appointments'] = appointments.filter(status=AppointmentStatus.ABSENCE).count()
        
        # Tasa de asistencia
        total = context['total_appointments']
        attended = context['attended_appointments']
        context['attendance_rate'] = round((attended / total * 100) if total > 0 else 0, 1)
        
        # Por tipo de cita
        context['appointments_by_type'] = appointments.values('type').annotate(count=Count('id'))
        
        # Por estado
        context['appointments_by_status'] = appointments.values('status').annotate(count=Count('id'))
        
        # Casos
        cases = Case.objects.filter(
            creation_date__date__gte=start_date,
            creation_date__date__lte=end_date
        )
        context['total_cases'] = cases.count()
        context['cases_by_status'] = cases.values('status').annotate(count=Count('id'))
        
        # Formularios de filtro
        context['filter_form'] = ReportFilterForm(initial={
            'start_date': start_date,
            'end_date': end_date
        })
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        return context


class AppointmentReportView(LoginRequiredMixin, ListView):
    """Reporte detallado de citas"""
    model = Appointment
    template_name = 'reports/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('beneficiary', 'student_assigned')
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        status = self.request.GET.get('status')
        student = self.request.GET.get('student')
        
        if start_date:
            queryset = queryset.filter(date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__date__lte=end_date)
        if status:
            queryset = queryset.filter(status=status)
        if student:
            queryset = queryset.filter(student_assigned_id=student)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ReportFilterForm(self.request.GET)
        
        # Calcular totales
        queryset = self.get_queryset()
        context['total'] = queryset.count()
        context['attended'] = queryset.filter(attended=True).count()
        context['absences'] = queryset.filter(status=AppointmentStatus.ABSENCE).count()
        
        return context


class CaseReportView(LoginRequiredMixin, ListView):
    """Reporte detallado de casos"""
    model = Case
    template_name = 'reports/cases.html'
    context_object_name = 'cases'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('beneficiary', 'student_assigned', 'legal_room')
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        status = self.request.GET.get('status')
        legal_room = self.request.GET.get('legal_room')
        
        if start_date:
            queryset = queryset.filter(creation_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(creation_date__date__lte=end_date)
        if status:
            queryset = queryset.filter(status=status)
        if legal_room:
            queryset = queryset.filter(legal_room_id=legal_room)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = CaseReportFilterForm(self.request.GET)
        
        # Calcular totales
        queryset = self.get_queryset()
        context['total'] = queryset.count()
        context['by_status'] = queryset.values('status').annotate(count=Count('id'))
        
        return context


class AbsenceReportView(LoginRequiredMixin, ListView):
    """Reporte de inasistencias"""
    model = Appointment
    template_name = 'reports/absences.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        return Appointment.objects.filter(
            status=AppointmentStatus.ABSENCE
        ).select_related('beneficiary', 'student_assigned')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Beneficiarios con mas inasistencias
        context['top_absences'] = Beneficiary.objects.annotate(
            absence_count=Count('appointments', filter=Q(appointments__status=AppointmentStatus.ABSENCE))
        ).filter(absence_count__gt=0).order_by('-absence_count')[:10]
        
        return context


# ==================== STUDENT VIEWS ====================

class StudentListView(LoginRequiredMixin, ListView):
    """Lista de estudiantes"""
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 10


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Detalle de estudiante"""
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assigned_cases'] = self.object.assigned_cases.all()
        context['appointments'] = self.object.appointments.all()[:10]
        return context


# ==================== LEGAL ROOM VIEWS ====================

class LegalRoomListView(LoginRequiredMixin, ListView):
    """Lista de salas juridicas"""
    model = LegalRoom
    template_name = 'legal_rooms/list.html'
    context_object_name = 'legal_rooms'


class LegalRoomCreateView(LoginRequiredMixin, CreateView):
    """Crear sala juridica"""
    model = LegalRoom
    form_class = LegalRoomForm
    template_name = 'legal_rooms/create.html'
    success_url = reverse_lazy('legal-room-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Sala juridica creada exitosamente')
        return super().form_valid(form)
