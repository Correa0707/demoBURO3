from django.core.mail import send_mail
from django.conf import settings


def send_appointment_email(appointment):
    """Envía un correo al beneficiario con los detalles de la cita."""
    beneficiary = appointment.beneficiary

    if not beneficiary.email:
        return  # No enviar si el beneficiario no tiene correo

    # Determinar si es cita de seguimiento
    from .models import ReasonType
    is_followup = appointment.reason_type == ReasonType.CASE_FOLLOW_UP

    if is_followup:
        subject = "Cita de seguimiento agendada - Consultorio Jurídico Icesi"
        case_info = ""
        if appointment.case:
            case_info = f"\n📋 Caso: {appointment.case.title or 'Sin titulo'}\n"
        
        message = f"""
Estimado(a) {beneficiary.name},

Se ha agendado una cita de seguimiento para su caso en el Consultorio Jurídico.

📅 Fecha: {appointment.date.strftime('%d/%m/%Y')}
⏰ Hora: {appointment.hour}
📍 Modalidad: {appointment.get_type_display()}{case_info}

Por favor, preséntese con 10 minutos de anticipación.

Si no puede asistir, comuníquese con nosotros para reprogramar su cita.

Atentamente,
Consultorio Jurídico
"""
    else:
        subject = "Confirmación de cita - Consultorio Jurídico Icesi"
        message = f"""
Estimado(a) {beneficiary.name},

Su cita ha sido agendada exitosamente en el Consultorio Jurídico.

📅 Fecha: {appointment.date.strftime('%d/%m/%Y')}
⏰ Hora: {appointment.hour}
📍 Modalidad: {appointment.get_type_display()}
📌 Estado: {appointment.get_status_display()}

Por favor, preséntese con 10 minutos de anticipación.

Si no puede asistir, comuníquese con nosotros para reprogramar su cita.
O desde el portal en el que la agendó, puede cancelarla o reprogramarla.

Atentamente,
Consultorio Jurídico
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[beneficiary.email],
        fail_silently=False,
    )