import pytest
from consultorio.models import SystemUser, Student, SystemRole


@pytest.fixture
def admin_user(db):
    """Fixture para usuario administrador"""
    return SystemUser.objects.create_user(
        username='admin01',
        password='Admin1234!',
        first_name='Admin',
        last_name='Test',
        email='admin@test.com',
        role=SystemRole.ADMIN,
        is_active=True
    )


@pytest.fixture
def secretary_user(db):
    """Fixture para usuario secretaria"""
    return SystemUser.objects.create_user(
        username='sec01',
        password='Sec1234!',
        first_name='Secretaria',
        last_name='Test',
        email='secretary@test.com',
        role=SystemRole.SECRETARY,
        is_active=True
    )


@pytest.fixture
def student_user(db):
    """Fixture para usuario estudiante"""
    user = SystemUser.objects.create_user(
        username='est01',
        password='Est1234!',
        first_name='Estudiante',
        last_name='Test',
        email='student@test.com',
        role=SystemRole.STUDENT,
        is_active=True
    )
    Student.objects.create(
        user=user,
        enrollment_professional='EST001',
        available=True
    )
    return user


@pytest.fixture
def teacher_user(db):
    """Fixture para usuario profesor/asesor"""
    return SystemUser.objects.create_user(
        username='prof01',
        password='Prof1234!',
        first_name='Profesor',
        last_name='Test',
        email='teacher@test.com',
        role=SystemRole.TEACHER,
        is_active=True
    )
