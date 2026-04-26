# Consultorio Juridico - Sistema de Gestion

Sistema de gestion integral para consultorios juridicos universitarios. Permite administrar beneficiarios, citas, casos legales, estudiantes y comunicaciones.

---

## Requisitos del Sistema

| Componente | Version |
|------------|---------|
| Python | 3.14.x |
| Django | 5.2.12 |
| SQLite | 3.x (incluido con Python) |

---

## Paquetes Requeridos

```
asgiref==3.11.1
Django==5.2.12
django-environ==0.13.0
sqlparse==0.5.5
tzdata==2025.3
```

---

## Instalacion

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd buro
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

```bash
python manage.py migrate
```

### 5. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

---

## Ejecucion del Proyecto

### Servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estara disponible en: `http://127.0.0.1:8000/`

### URLs principales

| URL | Descripcion |
|-----|-------------|
| `/acceso/` | Login unificado (estudiante, beneficiario, asesor) |
| `/admin/` | Panel de administracion Django |
| `/beneficiario/` | Portal del beneficiario |
| `/beneficiario/registro/` | Registro de beneficiario con primera cita |
| `/citas/` | Gestion de citas |
| `/citas/calendario/` | Calendario de citas |
| `/beneficiarios/` | Gestion de beneficiarios |
| `/casos/` | Gestion de casos legales |

---

## Ejecucion de Pruebas

### Ejecutar todas las pruebas

```bash
python manage.py test
```

### Ejecutar pruebas de una aplicacion especifica

```bash
python manage.py test consultorio
```

### Ejecutar pruebas con mayor detalle (verbosity)

```bash
python manage.py test -v 2
```

### Ejecutar una clase de prueba especifica

```bash
python manage.py test consultorio.tests.BeneficiaryModelTest
```

### Ejecutar un metodo de prueba especifico

```bash
python manage.py test consultorio.tests.BeneficiaryModelTest.test_beneficiary_set_password
```

---

## Estructura del Proyecto

```
buro/
├── buro_app/                   # Configuracion principal de Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── consultorio/                # Aplicacion principal
│   ├── migrations/             # Migraciones de base de datos
│   ├── templates/              # Plantillas HTML
│   │   ├── appointments/       # Plantillas de citas
│   │   ├── beneficiaries/      # Plantillas de beneficiarios
│   │   ├── beneficiary_portal/ # Portal del beneficiario
│   │   ├── cases/              # Plantillas de casos
│   │   ├── communications/     # Plantillas de comunicaciones
│   │   ├── reports/            # Plantillas de reportes
│   │   └── ...
│   ├── templatetags/           # Filtros personalizados
│   ├── admin.py
│   ├── forms.py                # Formularios
│   ├── models.py               # Modelos de datos
│   ├── tests.py                # Pruebas unitarias
│   ├── urls.py                 # Rutas de la aplicacion
│   └── views.py                # Vistas
├── db.sqlite3                  # Base de datos SQLite
├── manage.py                   # CLI de Django
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

---

## Funcionalidades Principales

### Sistema de Autenticacion

- **Login unificado** con seleccion de rol (estudiante, beneficiario, asesor)
- Autenticacion segura con hash de contrasenas (PBKDF2)
- Sesiones independientes para beneficiarios

### Gestion de Beneficiarios

- Registro con programacion de primera cita
- Portal de autoservicio para beneficiarios
- Autorizacion de tratamiento de datos

### Gestion de Citas

- Agendar, editar, cancelar y reprogramar citas
- Calendario visual con filtros por estudiante
- Validacion de conflictos de horarios
- Registro de asistencia/inasistencia


### Notificaciones

- Notificaciones automaticas para beneficiarios
- Centro de notificaciones en el portal

---

## Tipos de Usuario

| Rol | Descripcion | Acceso |
|-----|-------------|--------|
| Admin | Administrador del sistema | Acceso completo |
| Teacher | Profesor/Asesor | Supervision de estudiantes y casos |
| Student | Estudiante de derecho | Atencion de citas y casos |
| Secretary | Secretaria | Gestion administrativa |
| Beneficiary | Beneficiario | Portal de autoservicio |

---

## Comandos Utiles

```bash
# Crear migraciones despues de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo de Django
python manage.py shell

# Recopilar archivos estaticos (produccion)
python manage.py collectstatic

# Verificar configuracion del proyecto
python manage.py check
```

---

## Notas de Desarrollo

- La base de datos SQLite (`db.sqlite3`) se crea automaticamente al ejecutar las migraciones si hay errores eliminar la existente
- En desarrollo, el servidor se reinicia automaticamente al detectar cambios en el codigo
- Los templates usan Tailwind CSS via CDN
- Las sesiones de beneficiarios usan el sistema de sesiones de Django (separado de la autenticacion de usuarios)

---
