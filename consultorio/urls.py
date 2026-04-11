from django.urls import path
from .views import (
    # Auth
    LoginView, LogoutView,
    # Home
    HomeView,
    # Beneficiaries
    BeneficiaryListView, BeneficiaryCreateView, BeneficiaryDetailView, BeneficiaryEditView,
    # Appointments
    AppointmentListView, AppointmentCreateView, AppointmentDetailView, 
    AppointmentEditView, AppointmentCancelView, AppointmentAttendanceView,
    AppointmentReassignView,
    # Cases
    CaseListView, CaseCreateView, CaseDetailView, CaseEditView,
    CaseAddHistoryView, CaseReassignView, CaseCloseView,
    # Communications
    CommunicationListView, CommunicationCreateView, SendEmailView,
    # Notifications
    NotificationListView, NotificationMarkReadView, NotificationMarkAllReadView,
    # Reports
    ReportDashboardView, AppointmentReportView, CaseReportView, AbsenceReportView,
    # Students
    StudentListView, StudentDetailView,
    # Legal Rooms
    LegalRoomListView, LegalRoomCreateView,
)

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Home
    path('', HomeView.as_view(), name='home'),
    
    # Beneficiaries
    path('beneficiarios/', BeneficiaryListView.as_view(), name='beneficiary-list'),
    path('beneficiarios/crear/', BeneficiaryCreateView.as_view(), name='beneficiary-create'),
    path('beneficiarios/<uuid:pk>/', BeneficiaryDetailView.as_view(), name='beneficiary-detail'),
    path('beneficiarios/<uuid:pk>/editar/', BeneficiaryEditView.as_view(), name='beneficiary-edit'),
    
    # Appointments
    path('citas/', AppointmentListView.as_view(), name='appointment-list'),
    path('citas/crear/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('citas/<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('citas/<uuid:pk>/editar/', AppointmentEditView.as_view(), name='appointment-edit'),
    path('citas/<uuid:pk>/cancelar/', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('citas/<uuid:pk>/asistencia/', AppointmentAttendanceView.as_view(), name='appointment-attendance'),
    path('citas/<uuid:pk>/reasignar/', AppointmentReassignView.as_view(), name='appointment-reassign'),
    
    # Cases
    path('casos/', CaseListView.as_view(), name='case-list'),
    path('casos/crear/', CaseCreateView.as_view(), name='case-create'),
    path('casos/<uuid:pk>/', CaseDetailView.as_view(), name='case-detail'),
    path('casos/<uuid:pk>/editar/', CaseEditView.as_view(), name='case-edit'),
    path('casos/<uuid:pk>/historial/', CaseAddHistoryView.as_view(), name='case-add-history'),
    path('casos/<uuid:pk>/reasignar/', CaseReassignView.as_view(), name='case-reassign'),
    path('casos/<uuid:pk>/cerrar/', CaseCloseView.as_view(), name='case-close'),
    
    # Communications
    path('comunicaciones/', CommunicationListView.as_view(), name='communication-list'),
    path('comunicaciones/crear/', CommunicationCreateView.as_view(), name='communication-create'),
    path('comunicaciones/enviar-correo/', SendEmailView.as_view(), name='send-email'),
    
    # Notifications
    path('notificaciones/', NotificationListView.as_view(), name='notification-list'),
    path('notificaciones/<uuid:pk>/leer/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notificaciones/leer-todas/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    
    # Reports
    path('reportes/', ReportDashboardView.as_view(), name='report-dashboard'),
    path('reportes/citas/', AppointmentReportView.as_view(), name='report-appointments'),
    path('reportes/casos/', CaseReportView.as_view(), name='report-cases'),
    path('reportes/inasistencias/', AbsenceReportView.as_view(), name='report-absences'),
    
    # Students
    path('estudiantes/', StudentListView.as_view(), name='student-list'),
    path('estudiantes/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    
    # Legal Rooms
    path('salas/', LegalRoomListView.as_view(), name='legal-room-list'),
    path('salas/crear/', LegalRoomCreateView.as_view(), name='legal-room-create'),
]
