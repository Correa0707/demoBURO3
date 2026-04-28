from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    SystemUser, Student, Beneficiary, Appointment, Communication, 
    Notification, Case, CaseHistory, LegalRoom,
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

# ==================== CASE HISTORY INLINE ====================
class CaseHistoryInline(admin.TabularInline):
    model = CaseHistory
    extra = 0
    readonly_fields = ('date',)
    fields = ('date', 'action', 'responsible', 'observation')
    ordering = ('-date',)

# ==================== CASE ADMIN ====================
@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'beneficiary',
        'student_assigned',
        'status',
        'creation_date'
    )
    list_filter = ('status', 'creation_date', 'legal_room')
    search_fields = ('title', 'beneficiary__name', 'titular_nombre')
    readonly_fields = ('id', 'creation_date', 'absences_beneficiary')

    autocomplete_fields = ('beneficiary', 'student_assigned', 'legal_room')

    inlines = [CaseHistoryInline]

    fieldsets = (
        ('Información General', {
            'fields': ('id', 'title', 'description', 'status', 'creation_date')
        }),
        ('Relaciones', {
            'fields': ('beneficiary', 'student_assigned', 'legal_room', 'appointment_origin')
        }),
        ('Titular del Caso', {
            'fields': (
                'titular_is_beneficiary',
                'titular_cedula',
                'titular_nombre',
                'titular_telefono',
                'titular_correo'
            )
        }),
        ('Datos Demográficos', {
            'fields': ('sexo', 'poblacion', 'etnia', 'estrato', 'discapacidad')
        }),
        ('Control', {
            'fields': ('absences_beneficiary', 'reason_for_reassignment')
        }),
    )


# ==================== CASE HISTORY ADMIN ====================
@admin.register(CaseHistory)
class CaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('case', 'action', 'responsible', 'date')
    list_filter = ('date', 'responsible')
    search_fields = ('case__title', 'action', 'observation')
    readonly_fields = ('id', 'date')


# ==================== LEGAL ROOM ADMIN ====================
@admin.register(LegalRoom)
class LegalRoomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
