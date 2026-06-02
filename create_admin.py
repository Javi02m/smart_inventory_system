import os
import django

# 1. Configuramos el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from inventario.models import Categoria, Proveedor  # <-- Importamos tus modelos

# 2. Crear el Superusuario automáticamente
USERNAME = 'Javier'
EMAIL = 'javier@bodega.com'
PASSWORD = 'TuContraseñaSegura123'  # <-- Tu contraseña

try:
    if not User.objects.filter(username=USERNAME).exists():
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print(f"✅ ¡Éxito! El superusuario '{USERNAME}' ha sido creado.")
    else:
        print(f"ℹ️ El usuario '{USERNAME}' ya existe.")
except Exception as e:
    print(f"❌ Error al crear el usuario: {e}")


# 3. Crear las Categorías automáticamente si no existen
categorias_por_defecto = ['Alimentos', 'Bebidas', 'Limpieza', 'Cuidado Personal', 'Electrónicos', 'Otros']
try:
    for nombre_cat in categorias_por_defecto:
        Categoria.objects.get_or_create(nombre=nombre_cat)
    print("✅ Categorías base cargadas con éxito.")
except Exception as e:
    print(f"❌ Error al cargar categorías: {e}")


# 4. Crear los Proveedores de PANAMÁ automáticamente si no existen
proveedores_panama = [
    'M. Tzanetatos, S.A.', 
    'Agencias Feduro, S.A.', 
    'Felipe Motta e Hijos', 
    'Tagarópulos, S.A.'
]

try:
    for nombre_prov in proveedores_panama:
        Proveedor.objects.get_or_create(nombre=nombre_prov)
    print("✅ Proveedores de Panamá cargados con éxito.")
except Exception as e:
    print(f"❌ Error al cargar proveedores: {e}")