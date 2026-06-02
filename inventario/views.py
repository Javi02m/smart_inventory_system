from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Q
from django.utils import timezone
from .models import Producto, Movimiento
from .forms import ProductoForm, MovimientoForm

@login_required
def dashboard(request):
    hoy = timezone.now().date()
    dentro_de_15_dias = hoy + timezone.timedelta(days=15)
    
    # 1. Contamos los totales para las tarjetas informativas
    total_productos = Producto.objects.count()
    stock_critico_count = Producto.objects.filter(cantidad_en_stock__lt=10).count()
    proximos_vencer_count = Producto.objects.filter(fecha_caducidad__lte=dentro_de_15_dias).count()
    
    # 2. Traemos la LISTA de objetos para la tabla
    productos_criticos = Producto.objects.filter(
        Q(cantidad_en_stock__lt=10) | Q(fecha_caducidad__lte=dentro_de_15_dias)
    ).distinct()
    
    # 3. Últimos 5 movimientos
    ultimos_movimientos = Movimiento.objects.all()[:5]

    context = {
        'total_productos': total_productos,
        'stock_critico_count': stock_critico_count,
        'proximos_vencer_count': proximos_vencer_count,
        'productos_criticos': productos_criticos,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'inventario/dashboard.html', context)

@login_required
def producto_list(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(codigo_de_barras__icontains=query)
        )
    else:
        productos = Producto.objects.all()
    return render(request, 'inventario/producto_list.html', {'productos': productos})

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {'form': form})

@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {'form': form, 'producto': producto})

@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('producto_list')
    return render(request, 'inventario/producto_confirm_delete.html', {'producto': producto})

@login_required
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            producto = movimiento.producto

            if movimiento.tipo == 'SALIDA' and movimiento.cantidad > producto.cantidad_en_stock:
                messages.error(request, 'Error: No puedes retirar más unidades de las que hay en stock')
            else:
                if movimiento.tipo == 'ENTRADA':
                    producto.cantidad_en_stock = F('cantidad_en_stock') + movimiento.cantidad
                else:
                    producto.cantidad_en_stock = F('cantidad_en_stock') - movimiento.cantidad
                producto.save(update_fields=['cantidad_en_stock'])
                producto.refresh_from_db(fields=['cantidad_en_stock'])

                movimiento.save(actualizar_stock=False)
                messages.success(request, 'Movimiento registrado correctamente y stock actualizado')
                return redirect('producto_list')
    else:
        form = MovimientoForm()
    return render(request, 'inventario/movimiento_form.html', {'form': form})
