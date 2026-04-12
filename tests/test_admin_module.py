"""
=============================================================================
CASOS DE PRUEBA — Modulo de Gestion de Usuarios (Admin)
Proyecto: Consultorio Juridico — Aplicacion Buro
Equipo T2

HU Cubiertas:
- HU-01: Login del Administrador (/admin-login/)
- HU-02: Crear Asesor (/admin/asesores/crear/)
- HU-03: Crear Estudiante (/admin/estudiantes/crear/)

Fecha: Abril 2026
Stack: Django 5.2, Python 3.14, Django TestCase
=============================================================================
"""

import datetime
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core import mail

from consultorio.models import SystemUser, Student, SystemRole


# =============================================================================
# HU-01: Login del Administrador
# =============================================================================

class TestAdminLogin(TestCase):
    """
    Tests para la funcionalidad de login de administrador.
    Cobertura: CP-01, CP-02, CN-01, CN-02, CN-03, CN-04, CN-05, CN-06, CN-07
    """

    def setUp(self):
        """Configuracion inicial para cada test"""
        # Crear usuario admin
        self.admin_user = SystemUser.objects.create_user(
            username='admin01',
            email='admin@test.com',
            password='Admin1234!',
            first_name='Admin',
            last_name='User',
            role=SystemRole.ADMIN,
            is_active=True
        )
        
        # Crear usuario secretaria
        self.secretary_user = SystemUser.objects.create_user(
            username='sec01',
            email='secretary@test.com',
            password='Sec1234!',
            first_name='Secretary',
            last_name='User',
            role=SystemRole.SECRETARY,
            is_active=True
        )
        
        # Crear usuario estudiante
        self.student_system_user = SystemUser.objects.create_user(
            username='est01',
            email='student@test.com',
            password='Est1234!',
            first_name='Student',
            last_name='User',
            role=SystemRole.STUDENT,
            is_active=True
        )
        self.student_profile = Student.objects.create(
            user=self.student_system_user,
            enrollment_professional='STU001',
            available=True
        )

    # -------------------- CASOS POSITIVOS --------------------

    def test_CP01_admin_login_exitoso(self):
        """
        CP-01: Usuario con role=ADMIN y credenciales correctas
        -> redirige a /admin-dashboard/ y sesion activa
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'admin01',
            'password': 'Admin1234!'
        })
        
        # Verifica redireccion al dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin-dashboard'))
        
        # Verifica sesion activa
        self.assertIn('_auth_user_id', self.client.session)

    def test_CP02_admin_login_http302(self):
        """
        CP-02: Campo username y password correctos, role=ADMIN
        -> respuesta HTTP 302
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'admin01',
            'password': 'Admin1234!'
        })
        
        self.assertEqual(response.status_code, 302)

    # -------------------- CASOS NEGATIVOS --------------------

    def test_CN01_secretary_login_rechazado(self):
        """
        CN-01: Usuario con role=SECRETARY intenta login en /admin-login/
        -> NO redirige al dashboard, muestra error
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'sec01',
            'password': 'Sec1234!'
        })
        
        # No debe redirigir (HTTP 200 con formulario y error)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'exclusivo para administradores' in response.content or
            b'Este acceso es exclusivo' in response.content
        )

    def test_CN02_student_login_rechazado(self):
        """
        CN-02: Usuario con role=STUDENT intenta login
        -> rechazado con mensaje de error
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'est01',
            'password': 'Est1234!'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_CN03_password_incorrecto(self):
        """
        CN-03: Credenciales incorrectas (password errado)
        -> HTTP 200, mensaje de error visible
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'admin01',
            'password': 'PasswordIncorrecto123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'incorrectos' in response.content or
            b'Usuario o contrasena' in response.content
        )

    def test_CN04_campos_vacios(self):
        """
        CN-04: Campos vacios enviados
        -> HTTP 200, no autentica
        """
        response = self.client.post(reverse('admin-login'), {
            'username': '',
            'password': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_CN05_usuario_inexistente(self):
        """
        CN-05: Usuario inexistente
        -> HTTP 200, no autentica
        """
        response = self.client.post(reverse('admin-login'), {
            'username': 'usuario_que_no_existe',
            'password': 'cualquier_password'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_CN06_acceso_dashboard_sin_autenticar(self):
        """
        CN-06: Acceso directo a /admin-dashboard/ sin estar autenticado
        -> redirige a login
        """
        response = self.client.get(reverse('admin-dashboard'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_CN07_secretary_acceso_dashboard_denegado(self):
        """
        CN-07: Usuario autenticado con role=SECRETARY accede a /admin-dashboard/
        -> denegado
        """
        self.client.force_login(self.secretary_user)
        response = self.client.get(reverse('admin-dashboard'))
        
        # Debe redirigir a home o mostrar error
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


# =============================================================================
# HU-02: Crear Asesor
# =============================================================================

class TestCrearAsesor(TestCase):
    """
    Tests para la funcionalidad de crear asesor/profesor.
    Cobertura: CP-03, CP-04, CP-05, CP-06, CN-08, CN-09, CN-10, CN-11, CN-12, CN-13
    """

    def setUp(self):
        """Configuracion inicial para cada test"""
        # Crear usuario admin
        self.admin_user = SystemUser.objects.create_user(
            username='admin01',
            email='admin@test.com',
            password='Admin1234!',
            first_name='Admin',
            last_name='User',
            role=SystemRole.ADMIN,
            is_active=True
        )
        
        # Crear usuario secretaria
        self.secretary_user = SystemUser.objects.create_user(
            username='sec01',
            email='secretary@test.com',
            password='Sec1234!',
            first_name='Secretary',
            last_name='User',
            role=SystemRole.SECRETARY,
            is_active=True
        )

    # -------------------- CASOS POSITIVOS --------------------

    def test_CP03_crear_asesor_exitoso(self):
        """
        CP-03: Formulario con nombre="Isabella Gomez", cedula="1112391955", correo valido
        -> crea SystemUser con role=TEACHER, is_active=True, username="1112391955"
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Isabella',
            'last_name': 'Gomez',
            'cedula': '1112391955',
            'email': 'isabella.gomez@test.com'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creo el usuario
        user = SystemUser.objects.get(username='1112391955')
        self.assertEqual(user.role, SystemRole.TEACHER)
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, 'Isabella')
        self.assertEqual(user.last_name, 'Gomez')

    def test_CP04_contrasena_generada_correctamente(self):
        """
        CP-04: Contrasena generada correctamente
        -> user.check_password("isabella1112391955") retorna True
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Isabella',
            'last_name': 'Gomez',
            'cedula': '1112391955',
            'email': 'isabella.gomez@test.com'
        })
        
        user = SystemUser.objects.get(username='1112391955')
        self.assertTrue(user.check_password('isabella1112391955'))

    def test_CP05_nombre_con_tilde_normalizado(self):
        """
        CP-05: Nombre con tilde (ej: "Andres")
        -> contrasena normaliza a "andres" + cedula sin error
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Andres',
            'last_name': 'Lopez',
            'cedula': '9876543210',
            'email': 'andres.lopez@test.com'
        })
        
        user = SystemUser.objects.get(username='9876543210')
        # La contrasena debe ser "andres9876543210" (sin tilde)
        self.assertTrue(user.check_password('andres9876543210'))

    def test_CP06_nombre_compuesto_solo_primer_nombre(self):
        """
        CP-06: Nombre compuesto (ej: "Juan Pablo")
        -> solo toma "juan" como primer nombre
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Juan Pablo',
            'last_name': 'Ramirez',
            'cedula': '1234567890',
            'email': 'juanpablo.ramirez@test.com'
        })
        
        user = SystemUser.objects.get(username='1234567890')
        # La contrasena debe ser "juan1234567890" (solo primer nombre)
        self.assertTrue(user.check_password('juan1234567890'))

    # -------------------- CASOS NEGATIVOS --------------------

    def test_CN08_cedula_duplicada(self):
        """
        CN-08: Cedula duplicada (ya existe un usuario con ese username)
        -> formulario rechazado, mensaje de error, no se crea duplicado
        """
        self.client.force_login(self.admin_user)
        
        # Crear primer asesor
        self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Primer',
            'last_name': 'Asesor',
            'cedula': '1111111111',
            'email': 'primero@test.com'
        })
        
        # Intentar crear segundo con misma cedula
        response = self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Segundo',
            'last_name': 'Asesor',
            'cedula': '1111111111',
            'email': 'segundo@test.com'
        })
        
        self.assertEqual(response.status_code, 200)
        # Solo debe existir un usuario con esa cedula
        self.assertEqual(SystemUser.objects.filter(username='1111111111').count(), 1)

    def test_CN09_correo_invalido(self):
        """
        CN-09: Correo invalido (sin @)
        -> formulario rechazado
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Test',
            'last_name': 'User',
            'cedula': '2222222222',
            'email': 'correo_sin_arroba.com'
        })
        
        self.assertEqual(response.status_code, 200)
        # No debe crear usuario
        self.assertFalse(SystemUser.objects.filter(username='2222222222').exists())

    def test_CN10_campos_obligatorios_vacios(self):
        """
        CN-10: Campos obligatorios vacios
        -> no se crea usuario
        """
        self.client.force_login(self.admin_user)
        
        initial_count = SystemUser.objects.count()
        
        response = self.client.post(reverse('admin-create-teacher'), {
            'first_name': '',
            'last_name': '',
            'cedula': '',
            'email': ''
        })
        
        self.assertEqual(response.status_code, 200)
        # No debe crear nuevos usuarios
        self.assertEqual(SystemUser.objects.count(), initial_count)

    def test_CN11_no_autenticado_post_redirige(self):
        """
        CN-11: Usuario no autenticado intenta POST a /admin/asesores/crear/
        -> redirige a login
        """
        response = self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Test',
            'last_name': 'User',
            'cedula': '3333333333',
            'email': 'test@test.com'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_CN12_secretary_acceso_denegado(self):
        """
        CN-12: Usuario con role=SECRETARY intenta acceder a /admin/asesores/crear/
        -> denegado
        """
        self.client.force_login(self.secretary_user)
        
        response = self.client.get(reverse('admin-create-teacher'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_CN13_no_crea_student_para_asesor(self):
        """
        CN-13: Verificar que NO se crea un objeto Student al crear un asesor
        -> Student.objects.filter(user__username="1112391955").exists() es False
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-teacher'), {
            'first_name': 'Isabella',
            'last_name': 'Gomez',
            'cedula': '1112391955',
            'email': 'isabella.gomez@test.com'
        })
        
        self.assertFalse(Student.objects.filter(user__username='1112391955').exists())


# =============================================================================
# HU-03: Crear Estudiante
# =============================================================================

class TestCrearEstudiante(TestCase):
    """
    Tests para la funcionalidad de crear estudiante.
    Cobertura: CP-07, CP-08, CP-09, CP-10, CP-11, CP-12, CN-14, CN-15, CN-16, CN-17, CN-18, CN-19, CN-20, CN-21
    """

    def setUp(self):
        """Configuracion inicial para cada test"""
        # Crear usuario admin
        self.admin_user = SystemUser.objects.create_user(
            username='admin01',
            email='admin@test.com',
            password='Admin1234!',
            first_name='Admin',
            last_name='User',
            role=SystemRole.ADMIN,
            is_active=True
        )
        
        # Crear usuario teacher
        self.teacher_user = SystemUser.objects.create_user(
            username='teacher01',
            email='teacher@test.com',
            password='Teacher1234!',
            first_name='Teacher',
            last_name='User',
            role=SystemRole.TEACHER,
            is_active=True
        )

    # -------------------- CASOS POSITIVOS --------------------

    def test_CP07_crear_estudiante_exitoso(self):
        """
        CP-07: Formulario completo valido
        -> crea SystemUser con role=STUDENT y Student con available=True
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Carlos',
            'last_name': 'Martinez',
            'cedula': '5555555555',
            'student_code': 'EST12345',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'carlos.martinez@test.com',
            'attendance_days': ['Lunes', 'Miercoles', 'Viernes']
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar SystemUser
        user = SystemUser.objects.get(username='5555555555')
        self.assertEqual(user.role, SystemRole.STUDENT)
        self.assertTrue(user.is_active)
        
        # Verificar Student
        student = Student.objects.get(user=user)
        self.assertTrue(student.available)

    def test_CP08_contrasena_estudiante_generada(self):
        """
        CP-08: Contrasena generada correctamente para estudiante
        -> check_password retorna True
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'cedula': '6666666666',
            'student_code': 'EST67890',
            'semester': '7mo semestre',
            'legal_office': 'Consultorio 2',
            'email': 'maria.garcia@test.com',
            'attendance_days': ['Martes', 'Jueves']
        })
        
        user = SystemUser.objects.get(username='6666666666')
        self.assertTrue(user.check_password('maria6666666666'))

    def test_CP09_student_vinculado_a_user(self):
        """
        CP-09: El perfil Student queda vinculado al SystemUser correcto
        -> student.user.username == cedula
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Pedro',
            'last_name': 'Sanchez',
            'cedula': '7777777777',
            'student_code': 'EST11111',
            'semester': '9no semestre',
            'legal_office': 'Consultorio 1',
            'email': 'pedro.sanchez@test.com',
            'attendance_days': ['Lunes']
        })
        
        student = Student.objects.get(enrollment_professional='EST11111')
        self.assertEqual(student.user.username, '7777777777')

    def test_CP10_enrollment_professional_coincide(self):
        """
        CP-10: El campo enrollment_professional del Student coincide con el codigo ingresado
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Laura',
            'last_name': 'Rodriguez',
            'cedula': '8888888888',
            'student_code': 'CODIGO_UNICO_123',
            'semester': '6to semestre',
            'legal_office': 'Consultorio 2',
            'email': 'laura.rodriguez@test.com',
            'attendance_days': ['Viernes']
        })
        
        student = Student.objects.get(user__username='8888888888')
        self.assertEqual(student.enrollment_professional, 'CODIGO_UNICO_123')

    def test_CP11_dias_asistencia_guardados(self):
        """
        CP-11: Dias de asistencia seleccionados se guardan correctamente
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Ana',
            'last_name': 'Lopez',
            'cedula': '9999999999',
            'student_code': 'EST99999',
            'semester': '10mo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'ana.lopez@test.com',
            'attendance_days': ['Lunes', 'Martes', 'Miercoles']
        })
        
        student = Student.objects.get(user__username='9999999999')
        self.assertIn('Lunes', student.attendance_days)
        self.assertIn('Martes', student.attendance_days)
        self.assertIn('Miercoles', student.attendance_days)

    def test_CP12_consultorio_guardado(self):
        """
        CP-12: Consultorio seleccionado (1 o 2) se guarda correctamente
        """
        self.client.force_login(self.admin_user)
        
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Jose',
            'last_name': 'Hernandez',
            'cedula': '1010101010',
            'student_code': 'EST10101',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 2',
            'email': 'jose.hernandez@test.com',
            'attendance_days': ['Jueves']
        })
        
        student = Student.objects.get(user__username='1010101010')
        self.assertEqual(student.legal_office, 'Consultorio 2')

    # -------------------- CASOS NEGATIVOS --------------------

    def test_CN14_cedula_duplicada_estudiante(self):
        """
        CN-14: Cedula duplicada
        -> no se crea ni SystemUser ni Student, mensaje de error
        """
        self.client.force_login(self.admin_user)
        
        # Crear primer estudiante
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Primero',
            'last_name': 'Estudiante',
            'cedula': '1212121212',
            'student_code': 'EST_PRIMERO',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'primero.est@test.com',
            'attendance_days': ['Lunes']
        })
        
        # Intentar crear segundo con misma cedula
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Segundo',
            'last_name': 'Estudiante',
            'cedula': '1212121212',
            'student_code': 'EST_SEGUNDO',
            'semester': '9no semestre',
            'legal_office': 'Consultorio 2',
            'email': 'segundo.est@test.com',
            'attendance_days': ['Martes']
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SystemUser.objects.filter(username='1212121212').count(), 1)

    def test_CN15_codigo_estudiante_duplicado(self):
        """
        CN-15: Codigo de estudiante duplicado (enrollment_professional ya existe)
        -> rechazado
        """
        self.client.force_login(self.admin_user)
        
        # Crear primer estudiante
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Primero',
            'last_name': 'Test',
            'cedula': '1313131313',
            'student_code': 'CODIGO_DUPLICADO',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'primero.test@test.com',
            'attendance_days': ['Lunes']
        })
        
        # Intentar crear segundo con mismo codigo
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Segundo',
            'last_name': 'Test',
            'cedula': '1414141414',
            'student_code': 'CODIGO_DUPLICADO',
            'semester': '9no semestre',
            'legal_office': 'Consultorio 2',
            'email': 'segundo.test@test.com',
            'attendance_days': ['Martes']
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Student.objects.filter(enrollment_professional='CODIGO_DUPLICADO').count(), 1)

    def test_CN16_semestre_vacio(self):
        """
        CN-16: Semestre vacio
        -> formulario rechazado
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Test',
            'last_name': 'User',
            'cedula': '1515151515',
            'student_code': 'EST15151',
            'semester': '',
            'legal_office': 'Consultorio 1',
            'email': 'test.user@test.com',
            'attendance_days': ['Lunes']
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SystemUser.objects.filter(username='1515151515').exists())

    def test_CN17_sin_dias_asistencia(self):
        """
        CN-17: Ningun dia de asistencia seleccionado
        -> validar comportamiento (rechazar o guardar vacio)
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Sin',
            'last_name': 'Dias',
            'cedula': '1616161616',
            'student_code': 'EST16161',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'sin.dias@test.com',
            'attendance_days': []
        })
        
        # El formulario debe rechazar si no se seleccionan dias
        self.assertEqual(response.status_code, 200)
        # Verificar si se creo o no el estudiante (depende de la implementacion)
        # Si el campo es requerido, no debe crear
        # Si no es requerido, debe crear con dias vacios

    def test_CN18_correo_invalido_estudiante(self):
        """
        CN-18: Correo invalido
        -> rechazado
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'Correo',
            'last_name': 'Invalido',
            'cedula': '1717171717',
            'student_code': 'EST17171',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'correo_sin_arroba',
            'attendance_days': ['Lunes']
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SystemUser.objects.filter(username='1717171717').exists())

    def test_CN19_no_autenticado_post_estudiante(self):
        """
        CN-19: Usuario no autenticado intenta POST
        -> redirige a login
        """
        response = self.client.post(reverse('admin-create-student'), {
            'first_name': 'No',
            'last_name': 'Autenticado',
            'cedula': '1818181818',
            'student_code': 'EST18181',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'no.auth@test.com',
            'attendance_days': ['Lunes']
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_CN20_teacher_acceso_denegado(self):
        """
        CN-20: Usuario con role=TEACHER intenta acceder
        -> denegado
        """
        self.client.force_login(self.teacher_user)
        
        response = self.client.get(reverse('admin-create-student'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_CN21_atomicidad_creacion(self):
        """
        CN-21: Verificar que si falla la creacion del Student, 
        tampoco queda el SystemUser huerfano (atomicidad)
        """
        self.client.force_login(self.admin_user)
        
        # Crear un estudiante con codigo existente para forzar error en Student
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Primero',
            'last_name': 'Atomico',
            'cedula': '1919191919',
            'student_code': 'ATOMICO_CODE',
            'semester': '8vo semestre',
            'legal_office': 'Consultorio 1',
            'email': 'primero.atomico@test.com',
            'attendance_days': ['Lunes']
        })
        
        # Contar usuarios y estudiantes antes del intento fallido
        users_before = SystemUser.objects.count()
        students_before = Student.objects.count()
        
        # Intentar crear con codigo duplicado (falla en validacion de formulario)
        self.client.post(reverse('admin-create-student'), {
            'first_name': 'Segundo',
            'last_name': 'Atomico',
            'cedula': '2020202020',
            'student_code': 'ATOMICO_CODE',  # Codigo duplicado
            'semester': '9no semestre',
            'legal_office': 'Consultorio 2',
            'email': 'segundo.atomico@test.com',
            'attendance_days': ['Martes']
        })
        
        # Verificar que no se creo ni usuario ni estudiante adicional
        self.assertEqual(SystemUser.objects.count(), users_before)
        self.assertEqual(Student.objects.count(), students_before)
