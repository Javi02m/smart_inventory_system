import os
import django

# Configuramos el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Definimos las credenciales que deseas usar
USERNAME = 'Javier'
EMAIL = 'javier@bodega.com'
PASSWORD = 'TuContraseñaSegura123'  # <-- Cambia esto por la contraseña que quieras

try:
    if not User.objects.filter(username=USERNAME).exists():
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print(f"✅ ¡Éxito! El superusuario '{USERNAME}' ha sido creado automáticamente.")
    else:
        print(f"ℹ️ El usuario '{USERNAME}' ya existe. No se realizaron cambios.")
except Exception as e:
    print(f"❌ Error al intentar crear el usuario: {e}")