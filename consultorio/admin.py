from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    SystemUser, Student, Beneficiary, LegalRoom, 
    Case, CaseHistory, Appointment, Communication, 
    Notification, Metrics
)


@admin.register(SystemUser)
class SystemUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion Adicional', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informacion Adicional', {'fields': ('role', 'phone')}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_professional', 'available', 'area']
    list_filter = ['available', 'area']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'enrollment_professional']


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'email', 'phone', 'is_authorized', 'registration_date']
    list_filter = ['is_authorized', 'registration_date']
    search_fields = ['name', 'document', 'email']
    readonly_fields = ['id', 'registration_date']


@admin.register(LegalRoom)
class LegalRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'beneficiary', 'student_assigned', 'status', 'creation_date', 'legal_room']
    list_filter = ['status', 'legal_room', 'creation_date']
    search_fields = ['beneficiary__name', 'description']
    readonly_fields = ['id', 'creation_date']


@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ['case', 'action', 'responsible', 'date']
    list_filter = ['date']
    readonly_fields = ['id', 'date']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'beneficiary', 'student_assigned', 'date', 'type', 'status', 'attended']
    list_filter = ['status', 'type', 'attended', 'date']
    search_fields = ['beneficiary__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'type', 'responsible', 'date']
    list_filter = ['type', 'date']
    search_fields = ['beneficiary__name', 'description']
    readonly_fields = ['id', 'date']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'beneficiary', 'event_type', 'read', 'date']
    list_filter = ['event_type', 'read', 'date']
    readonly_fields = ['id', 'date']


@admin.register(Metrics)
class MetricsAdmin(admin.ModelAdmin):
    list_display = ['date_generated', 'period_start', 'period_end', 'total_cases', 'scheduled_appointments', 'attendance_rate']
    readonly_fields = ['id', 'date_generated']
