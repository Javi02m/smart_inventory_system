from datetime import timedelta

from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    codigo_de_barras = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_en_stock = models.PositiveIntegerField(default=0)
    fecha_ingreso = models.DateField()
    fecha_caducidad = models.DateField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def estado_stock(self):
        if self.cantidad_en_stock < 10:
            return 'CRÍTICO'
        if self.cantidad_en_stock < 20:
            return 'ALERTA'
        return 'OK'

    def estado_caducidad(self):
        hoy = timezone.localdate()
        if self.fecha_caducidad < hoy:
            return 'CADUCADO'
        if self.fecha_caducidad <= hoy + timedelta(days=15):
            return 'PRÓXIMO'
        return 'SEGURO'

    def estado_estante(self):
        hoy = timezone.localdate()
        dias_para_vencer = (self.fecha_caducidad - hoy).days
        if dias_para_vencer < 10:
            return 'BLOQUEADO'
        return 'OK'


class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada de Stock'),
        ('SALIDA', 'Salida de Stock'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad} unidades)'

    def save(self, *args, actualizar_stock=True, **kwargs):
        if actualizar_stock:
            if self.tipo == 'ENTRADA':
                self.producto.cantidad_en_stock += self.cantidad
            elif self.tipo == 'SALIDA':
                self.producto.cantidad_en_stock = max(0, self.producto.cantidad_en_stock - self.cantidad)
            self.producto.save()
        super().save(*args, **kwargs)
