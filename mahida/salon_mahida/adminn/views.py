from django.shortcuts import render, redirect, get_object_or_404
from user.models import User, Service, Jadwal, Reservasi
from adminn.models import Produk, Penjualan,Pembelian, Transaksi, Keranjang
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings 
from datetime import date, datetime, time
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from django.http import FileResponse
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count
import json
from django.urls import reverse_lazy

def is_user(user):
    return user.role == User.ADMIN_ROLE

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)

def admin(request):
    # Retrieve data from the database
    reservasi_count = Reservasi.objects.count()
    service_count = Service.objects.count()
    jadwal_count = Jadwal.objects.count()

    produk_count = Produk.objects.count()
    penjualan_count = Penjualan.objects.count()
    pembelian_count = Pembelian.objects.count()
    transaksi_count = Transaksi.objects.count()


    # Prepare data for the template
    data = {
        'reservasi_count': reservasi_count,
        'service_count': service_count,
        'jadwal_count': jadwal_count,
        'produk_count': produk_count,
        'penjualan_count': penjualan_count,
        'pembelian_count': pembelian_count,
        'transaksi_count': transaksi_count,
    }

    # Convert data to JSON format
    data_json = json.dumps(data)

    return render(request, 'menu_admin.html', {'data_json': data_json})


def data(request):
    booking = Reservasi.objects.values('status_konfirmasi').annotate(jumlah=Count('id'))
    jadwal = Jadwal.objects.values('sibuk').annotate(jumlah=Count('id'))
    service = Service.objects.values('jenis_layanan').annotate(jumlah=Count('id'))
    transaksi = Transaksi.objects.all()
    
    data = {
        'booking': list(booking),
        'jadwal': list(jadwal),
        'service': list(service),
        'transaksi': list(transaksi.values()),
    }
    
    return JsonResponse(data)

# user
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_user(request):
    user = User.objects.exclude(role='Admin')
    context ={
        'user':user
    }
    return render(request, 'user/kelolauser.html', context)

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def tambah_user(request):
    if request.method == 'POST':
        username=request.POST['username']
        no_wa=request.POST['wa']
        password=request.POST['password']
        user = User(username=username, no_wa=no_wa, password=password)
        user.save()
        return redirect('kelola_user')
    else:
        return render(request, 'user/tambahuser.html')

def edit_user(request, id):
    user = User.objects.get(id=id)
    return render(request, 'user/edituser.html', {'user':user})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def update_user(request, id):
    user = get_object_or_404(User, id=id)
    if request.method=='POST':
        user.username=request.POST['username']
        user.no_wa=request.POST['wa']
        user.password=request.POST['password']
        user.save()
        return redirect('kelola_user')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_user(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        user.delete()
    return redirect('kelola_user')
# end

# service
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_service(request):
    service = Service.objects.all()
    return render(request, 'service/kelolaservice.html', {'services':service})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def tambah_service(request):
    if request.method == 'POST':
        nama_layanan=request.POST['username']
        jenis_layanan=request.POST['js']
        harga_layanan=request.POST['harga']
        foto_service=request.FILES['file_foto']
        deskripsi=request.POST['deskripsi']
        service = Service(nama_layanan=nama_layanan, jenis_layanan=jenis_layanan, harga_layanan=harga_layanan, foto_service=foto_service, deskripsi=deskripsi)
        if foto_service:
            service.foto_service.save(foto_service.name, foto_service, save=True)
        service.save()
        return redirect('kelola_service')
    else:
        return render(request, 'service/tambahservice.html')
    
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def edit_service(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'service/editservice.html', {'service':service})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def update_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method=='POST':
        service.nama_layanan=request.POST['username']
        service.jenis_layanan=request.POST['js']
        service.harga_layanan=request.POST['harga']
        if 'file_foto' in request.FILES:
            service.foto_service = request.FILES['file_foto']
        service.deskripsi=request.POST['deskripsi']
        service.save()
        return redirect('kelola_service')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_service(request, id):
    if request.method == 'POST':
        service = Service.objects.get(id=id)
        service.delete()
    return redirect('kelola_service')

# end

# jadwal
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_jadwal(request):
    jadwal = Jadwal.objects.all()
    return render(request, 'jadwal/kelolajadwal.html', {'jadwal':jadwal})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def tambah_jadwal(request):
    if request.method == 'POST':
        nama_pegawai = request.POST['nama_pegawai']
        sibuk = request.POST['status']
        jam= request.POST['jam']
        tanggal = request.POST['tanggal']

        jadwal = Jadwal()
        jadwal.nama_pegawai = nama_pegawai
        jadwal.sibuk = sibuk
        jadwal.jam = jam
        jadwal.tanggal = tanggal
        jadwal.save()

        return redirect('kelola_jadwal')

    return render(request, 'jadwal/tambahjadwal.html')

    
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def edit_jadwal(request, id):
    jadwal = Jadwal.objects.get(id=id)
    return render(request, 'jadwal/editjadwal.html', {'jadwal':jadwal})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def update_jadwal(request, id):
    jadwal = get_object_or_404(Jadwal, id=id)
    if request.method=='POST':
        jadwal.nama_pegawai = request.POST['nama_pegawai']
        jadwal.sibuk = request.POST['status']
        jadwal.jam= request.POST['jam']
        jadwal.tanggal = request.POST['tanggal']
        jadwal.save()
        return redirect('kelola_jadwal')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_jadwal(request, id):
    if request.method == 'POST':
        jadwal = Jadwal.objects.get(id=id)
        jadwal.delete()
    return redirect('kelola_jadwal')

# end

# laporan reservasi
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_reservasi(request):
    booking = Reservasi.objects.all()
    service = Service.objects.all()
    jadwal = Jadwal.objects.all()
    context ={
        'booking':booking,
        'service':service,
        'jadwal':jadwal,
    }
    return render(request, 'laporan.html',{'booking':booking,'service':service,'jadwal':jadwal})  

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_pdf_reservasi(request):
    buffer = io.BytesIO()
    bookings = Reservasi.objects.select_related('layanan', 'jadwal')

    data = [['Nama Lengkap', 'Email', 'Nama Pegawai', 'Layanan', 'Jam', 'Tanggal', 'Tanggal Booking']]

    for booking in bookings:
        try:
            service_data = booking.layanan
            jadwal_data = booking.jadwal
            row = [
                booking.nama_lengkap,
                booking.email,
                jadwal_data.nama_pegawai,
                service_data.nama_layanan,
                jadwal_data.jam,
                jadwal_data.tanggal,
                booking.created_at,
            ]
            data.append(row)
        except (Service.DoesNotExist, Jadwal.DoesNotExist):
            pass
    # Continue your code here...

        
    # Lanjutan kode Anda ...

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Update the font size to 6
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    title = Paragraph(f"LAPORAN RESERVASI",
                    style=ParagraphStyle(name='Title', fontSize=18, alignment=1, spaceAfter=10, leading=18))
    elements.append(title)
    
    # Add table to the elements list
    table = Table(data)
    table.setStyle(style)
    elements.append(table)
    
    pdf.build(elements)
    
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='laporan_reservasi.pdf')
# end

# laporan pembelian
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_pembelian(request):
    pembelian = Pembelian.objects.all()
    return render(request, 'laporanpembelian.html',{'pembelian':pembelian})  

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_pdf_pembelian(request):
    buffer = io.BytesIO()
    pembelian = Pembelian.objects.all()

    data = [['No', 'Nama Produk', 'Jumlah', 'Tanggal Pembelian']]

    for p in pembelian:
        produk = Produk.objects.get(id=p.produk_id)  # Mengambil data produk berdasarkan ID dari penjualan
        row = [
            str(p.id),
            produk.nama,
            str(p.jumlah),
            p.created_at,
        ]
        data.append(row)
    # Continue your code here...

        
    # Lanjutan kode Anda ...

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Update the font size to 6
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    title = Paragraph(f"LAPORAN PEMBELIAN",
                    style=ParagraphStyle(name='Title', fontSize=18, alignment=1, spaceAfter=10, leading=18))
    elements.append(title)
    
    # Add table to the elements list
    table = Table(data)
    table.setStyle(style)
    elements.append(table)
    
    pdf.build(elements)
    
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='laporan_pembelian.pdf')
# end
    
# laporan penjualan
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_penjualan(request):
    penjualan = Penjualan.objects.all()
    return render(request, 'laporanpenjualan.html',{'penjualan':penjualan})  

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def laporan_pdf_penjualan(request):
    buffer = io.BytesIO()
    penjualan = Penjualan.objects.all()

    # Prepare table data
    data = [['No', 'Nama Pembeli', 'No Whatsapp', 'Nama Akun', 'No Keranjang', 'Total Pembelian']]

    for p in penjualan: # Mengambil data produk berdasarkan ID dari penjualan
        row = [
            str(p.id),
            p.nama_pembeli,
            p.no_wa,
            p.user.username,
            p.keranjang_id,
            p.total_pembayaran,
        ]
        data.append(row)
    styles = getSampleStyleSheet()
    # Define table style
    style = TableStyle([
('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),  # Update the font size to 10
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])

    # Create PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    # Add title
    title = Paragraph("LAPORAN PENJUALAN", style=ParagraphStyle(name='Title', fontSize=18, alignment=1, spaceAfter=10, leading=18))
    elements.append(title)

    # Add table to the elements list
    table = Table(data)
    table.setStyle(style)
    elements.append(table)

    # Build the PDF document
    pdf.build(elements)

    buffer.seek(0)

    # Return the PDF file as a response
    return FileResponse(buffer, as_attachment=True, filename='laporan_penjualan.pdf')
# end
    


# booking
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_booking(request):
    booking = Reservasi.objects.all()
    service = Service.objects.all()
    jadwal = Jadwal.objects.all()
    context ={
        'booking':booking,
        'service':service,
        'jadwal':jadwal
    }
    return render(request, 'reservasi/kelolabooking.html', context)

def setuju(request, id):
    booking = get_object_or_404(Reservasi, id=id)

    if booking.status_konfirmasi == 'Pending':
        booking.status_konfirmasi = 'Disetujui'
        booking.save()

    return redirect('kelola_booking')

def tolak(request, id):
    booking = get_object_or_404(Reservasi, id=id)

    if booking.status_konfirmasi == 'Pending':
        booking.status_konfirmasi = 'Ditolak'
        booking.save()
        messages.error(request, 'Persetujuan Anda ditolak. Silahkan booking ulang.')

    return redirect('kelola_booking')
# end

# produk
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_produk(request):
    produk = Produk.objects.all()
    context ={
        'produk':produk,
    }
    return render(request, 'produk/kelolaproduk.html', context)

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def tambah_produk(request):
    if request.method == 'POST':
        nama = request.POST['nama']
        kategori = request.POST['js']
        harga = request.POST['harga']
        stok= request.POST['stok']
        foto_produk = request.FILES['foto']
        deskripsi = request.POST['deskripsi']
        produk = Produk(nama=nama, harga=harga, kategori=kategori, stok=stok, foto_produk=foto_produk, deskripsi=deskripsi)
        if foto_produk:
            produk.foto_produk.save(foto_produk.name, foto_produk, save=True)
        produk.save()
        return redirect('kelola_produk')
    else:
        return render(request, 'produk/tambahproduk.html')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def edit_produk(request, id):
    produk = Produk.objects.get(id=id)
    return render(request, 'produk/editproduk.html', {'produk':produk})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def update_produk(request, id):
    produk = get_object_or_404(Produk, id=id)
    if request.method=='POST':
        produk.nama = request.POST['nama']
        produk.kategori = request.POST['js']
        produk.harga = request.POST['harga']
        produk.stok= request.POST['stok']
        produk.deskripsi = request.POST['deskripsi']
        if 'foto' in request.FILES:
            produk.foto_produk = request.FILES['foto']
        produk.save()
        return redirect('kelola_produk')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_produk(request, id):
    if request.method == 'POST':
        produk = Produk.objects.get(id=id)
        produk.delete()
    return redirect('kelola_produk')

# end


# penjualan
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_penjualan(request):
    penjualan = Penjualan.objects.all()
    context ={
        'penjualan':penjualan,
    }
    return render(request, 'penjualan/kelolapenjualan.html', context)

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_penjualan(request, id):
    if request.method == 'POST':
        jadwal = Penjualan.objects.get(id=id)
        jadwal.delete()
    return redirect('kelola_penjualan')

# end

# transaksi
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_transaksi(request):
    transaksi = Transaksi.objects.all()
    context ={
        'transaksi':transaksi,
    }
    return render(request, 'transaksi/kelolatransaksi.html', context)

def dikirim(request, id):
    transaksi = get_object_or_404(Transaksi, id=id)

    if transaksi.status == 'Pending':
        transaksi.status = 'Disetujui'

    elif transaksi.status == 'Disetujui':
        transaksi.status = 'Ditolak'
    transaksi.save()
    return redirect('kelola_transaksi')

def ditolak(request, id):
    transaksi = get_object_or_404(Transaksi, id=id)

    if transaksi.status == 'Pending':
        transaksi.status = 'Ditolak'

    elif transaksi.status == 'Ditolak':
        transaksi.status = 'Disetujui'
    transaksi.save()
    return redirect('kelola_transaksi')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_penjualan(request, id):
    if request.method == 'POST':
        penjualan = Penjualan.objects.get(id=id)
        penjualan.delete()
    return redirect('kelola_penjualan')

# end

# pembelian
@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def kelola_pembelian(request):
    pembelian = Pembelian.objects.all()
    context ={
        'pembelian':pembelian,
    }
    return render(request, 'pembelian/kelolapembelian.html', context)

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def tambah_pembelian(request):
    produk = Produk.objects.all()
    
    if request.method == 'POST':
        produk_id = request.POST['nama']
        jumlah = request.POST['jumlah']
        
        try:
            produk = Produk.objects.get(id=produk_id)
        except (Produk.DoesNotExist, ValueError):
            messages.warning(request, 'Produk tidak ditemukan.')
            return redirect('tambah_pembelian')
        
        pembelian = Pembelian(
            produk=produk,
            jumlah=jumlah,
        )
        pembelian.save()
        return redirect('kelola_pembelian')
    
    return render(request, 'pembelian/tambahpembelian.html', {'produk': produk})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def edit_pembelian(request, id):
    pembelian = Pembelian.objects.get(id=id)
    return render(request, 'pembelian/editpembelian.html', {'pembelian':pembelian})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def update_pembelian(request, id):
    pembelian = get_object_or_404(Pembelian, id=id)
    if request.method=='POST':
        pembelian.produk.nama = request.POST['nama']
        pembelian.jumlah = request.POST['jumlah']
        pembelian.save()
        return redirect('kelola_pembelian')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def delete_pembelian(request, id):
    if request.method == 'POST':
        pembelian = Pembelian.objects.get(id=id)
        pembelian.delete()
    return redirect('kelola_pembelian')

# end