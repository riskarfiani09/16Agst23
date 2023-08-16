from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout,authenticate, login as auth_login, get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from user.models import User, Service, Reservasi, Jadwal
from adminn.models import Produk, Penjualan,Pembelian, Transaksi, Keranjang, KeranjangItem
from django.db import IntegrityError
from django.conf import settings 
from django.shortcuts import redirect
from datetime import timedelta
from django.db.models import Sum, F
from django.contrib.humanize.templatetags.humanize import intcomma
import threading
import traceback
from django.utils import timezone


def is_user(user):
    return user.role == User.USER_ROLE

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.role == User.ADMIN_ROLE:
                return redirect('admin')
            elif user.role == User.USER_ROLE:
                    return redirect('index')
            else:
                messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        else:
            messages.error(request, 'Username/Password Anda Salah.')
    return render(request, 'login.html')

def daftar(request):
    User.objects.filter(no_wa='').delete()
    if request.method == 'POST':
        username = request.POST.get('username')
        no_wa = request.POST.get('wa')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password1')

        # Memeriksa apakah email kosong
        if not no_wa:
            messages.error(request, 'Nomor harus diisi.')
            return redirect('daftar')

        # Memeriksa apakah email sudah digunakan
        if User.objects.filter(no_wa=no_wa).exists():
            messages.error(request, 'No sudah terdaftar.')
            return redirect('daftar')

        # Memeriksa apakah username sudah digunakan
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('daftar')

        if password != confirm_password:
            messages.error(request, "Password tidak sesuai.")
            return redirect('daftar')

        hashed_password = make_password(password, confirm_password)

        user = User(username=username, no_wa=no_wa, password=hashed_password)
        try:
            user.save()
        except IntegrityError as e:
            messages.error(request, "Terjadi kesalahan saat menyimpan data pengguna.")
            traceback.print_exc()  # Cetak traceback kesalahan di konsol
            return redirect('daftar')

        # Authenticate user
        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            # User authentication successful
            messages.success(request, "Akun Kamu Berhasil Dibuat")
            return redirect('login')
        else:
            # User authentication failed
            messages.error(request, "Terjadi kesalahan saat membuat akun.")
            return redirect('daftar')
        

    else:
        return render(request, 'daftar.html')
    

def logout(request):
    auth_logout(request)
    return redirect('login')


def home(request):
    service = Service.objects.all()
    produk = Produk.objects.all()
    return render(request, 'index.html', {'service':service,'produk':produk})


def service(request):
    eyelash = Service.objects.filter(jenis_layanan='eyelash')
    haircare = Service.objects.filter(jenis_layanan='haircare')
    nails = Service.objects.filter(jenis_layanan='nails')

    return render(request, 'service.html', {
        'eyelash': eyelash,
        'haircare': haircare,
        'nails': nails,
    })

def service_detail(request, jenis_layanan, id):
    service = get_object_or_404(Service, jenis_layanan=jenis_layanan, id=id)
    return render(request, 'detail.html', {'service': service})
    
def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def detailproduk(request, id):
    produk = get_object_or_404(Produk, id=id )
    return render(request, 'detailproduk.html', {
        'produk': produk,
    })

def product(request):
    kategori = request.GET.get('kategori')

    if kategori == 'Haircare':
        produk = Produk.objects.filter(kategori='Haircare')
    elif kategori == 'Bodycare':
        produk = Produk.objects.filter(kategori='Bodycare')
    elif kategori == 'Skincare':
        produk = Produk.objects.filter(kategori='Skincare')
    else:
        produk = Produk.objects.all()

    return render(request, 'produk.html', {'produk':produk})



# after login
def hapus_pemesanan():
    created_at = timezone.now()
    waktu_terhapus = created_at - timezone.timedelta(hours=24)

    Reservasi.objects.filter(created_at__lte=waktu_terhapus).delete()


def booking(request, id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Anda harus login terlebih dahulu untuk melakukan booking.')
        return redirect('login')
    jadwal = Jadwal.objects.filter(sibuk="Tidak Sibuk")
    layanan_tersedia = Service.objects.filter(id=id).first()


    existing_booking = Reservasi.objects.filter(user=request.user, layanan__id=id).first()

    if existing_booking:
        status_url = reverse('status', kwargs={'booking_id': existing_booking.id})
        return redirect(status_url)

    if request.method == 'POST':
        nama_lengkap = request.POST.get('nama_lengkap')
        email = request.POST.get('email')
        pesan = request.POST.get('pesan')
        jadwal_id = request.POST.get('pegawai')
        layanan_id = request.POST.get('layanan')

        try:
            jadwal_terpilih = Jadwal.objects.get(id=jadwal_id)
            layanan_terpilih = Service.objects.get(id=layanan_id)

            booking = Reservasi.objects.create(
                nama_lengkap=nama_lengkap,
                email=email,
                pesan=pesan,
                layanan=layanan_terpilih,
                jadwal=jadwal_terpilih,
                user_id=request.user.id
            )
            status_url = reverse('status', kwargs={'booking_id': booking.id})
            return redirect(status_url)


        except Service.DoesNotExist:
            messages.error(request, 'Layanan dengan ID tersebut tidak ditemukan.')
        except Jadwal.DoesNotExist:
            messages.error(request, 'Pegawai dengan ID tersebut tidak ditemukan.')

    if not request.user.is_authenticated:
        messages.warning(request, 'Anda harus login terlebih dahulu untuk melakukan booking.')
        return redirect('login')

    return render(request, 'booking.html', {
        'jadwal': jadwal,
        'layanan_tersedia': layanan_tersedia
    })

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def status(request, booking_id):
    booking = get_object_or_404(Reservasi, id=booking_id)
    
    # Pengecekan apakah pemesanan dimiliki oleh pengguna yang sedang login
    if booking.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke pemesanan ini.')
        return redirect('serviceuser')
    hapus_pemesanan()
    return render(request, 'after_login/status.html', {'booking': booking})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def status_pembayaran(request, transaksi_id):
    transaksi = get_object_or_404(Transaksi, id=transaksi_id)
    keranjang = transaksi.keranjang 
    keranjang_item = KeranjangItem.objects.filter(keranjang_id=keranjang.id)

    total_harga = 0
    for item in keranjang_item:
        total_harga += item.produk.harga * item.jumlah
    
    # Pengecekan apakah pemesanan dimiliki oleh pengguna yang sedang login
    if transaksi.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke pemesanan ini.')
        return redirect('serviceuser')
    if transaksi.status == 'Disetujui':
        hapus_item_keranjang(keranjang.id)

    if transaksi.status == 'Disetujui':
        hapus_pembayaran(request.user.id)

    if transaksi.status == 'Disetujui':
        hapus_penjualan(request.user.id)
    return render(request, 'after_login/statuspembayaran.html', {'transaksi': transaksi, 'keranjang':keranjang, 'total_harga':total_harga})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def status_beli(request, transaksi_id):
    penjualan = get_object_or_404(Penjualan, id=transaksi_id)
    existing_transaksi = Transaksi.objects.filter(user=request.user, penjualan=penjualan).first()

    if existing_transaksi:
        return redirect('status_pembayaran', transaksi_id=existing_transaksi.id)

    keranjang = penjualan.keranjang
    keranjang_item = KeranjangItem.objects.filter(keranjang_id=keranjang.id)

    total_harga = 0
    for item in keranjang_item:
        total_harga += item.produk.harga * item.jumlah

    if request.method == 'POST':
        nama_pengirim = request.POST['nama_lengkap']
        bukti_transfer = request.FILES['bt']
        produk = Produk.objects.filter(keranjangitem__keranjang=keranjang).first()

        pembayaran = Transaksi.objects.create(
            nama_pengirim=nama_pengirim,
            bukti_transfer=bukti_transfer,
            user=request.user,
            keranjang=keranjang,
            produk=produk,
            penjualan=penjualan
        )
        pembayaran.save()
        messages.success(request, 'Pembayaran berhasil dilakukan.')
        return redirect('status_pembayaran', transaksi_id=pembayaran.id)

    # Pengecekan apakah pemesanan dimiliki oleh pengguna yang sedang login
    if penjualan.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke pemesanan ini.')
        return redirect('serviceuser')

    return render(request, 'after_login/statusproduk.html', {'transaksi': penjualan, 'keranjang': keranjang, 'keranjang_item': keranjang_item, 'total_harga': total_harga})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def bayar(request, id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Anda harus login terlebih dahulu untuk melakukan pembelian.')
        return redirect('login')

    keranjang = get_object_or_404(Keranjang, id=id)

    if not keranjang:
        messages.warning(request, 'Keranjang tidak ditemukan.')
        return redirect('keranjang')

    existing_penjualan = Penjualan.objects.filter(user=request.user, keranjang=keranjang).first()

    if existing_penjualan:
        return redirect('status_beli', transaksi_id=existing_penjualan.id)

    if request.method == 'POST':
        nama_pembeli = request.POST.get('nama_lengkap')
        no_wa = request.POST.get('wa')
        produk = Produk.objects.filter(keranjangitem__keranjang=keranjang).first()
        total_harga = keranjang.total_harga() 
        penjualan = Penjualan.objects.create(
            user=request.user,
            keranjang=keranjang,
            produk=produk,
            nama_pembeli=nama_pembeli,
            no_wa=no_wa,
            total_pembayaran=total_harga,
        )

        messages.success(request, 'Pembelian berhasil dilakukan.')
        return redirect('status_beli', transaksi_id=penjualan.id)

    return render(request, 'after_login/beli.html', {'total_harga': keranjang.total_harga(), 'keranjang': keranjang})


def hapus_item_keranjang(keranjang_id):
    # Menghapus item keranjang dalam waktu 60 detik
    timer = threading.Timer(60, hapus_keranjang, args=[keranjang_id])
    timer.start()

def hapus_keranjang(keranjang_id):
    # Menghapus item keranjang
    KeranjangItem.objects.filter(keranjang_id=keranjang_id).delete()

def hapus_pembayaran(user_id):
    # Menghapus item keranjang dalam waktu 60 detik
    timer = threading.Timer(60, hapus_transaksi, args=[user_id])
    timer.start()

def hapus_transaksi(user_id):
    # Menghapus item keranjang
    Transaksi.objects.filter(user_id=user_id).delete()

def hapus_penjualan(user_id):
    # Menghapus item keranjang dalam waktu 60 detik
    timer = threading.Timer(60, hapus_jual, args=[user_id])
    timer.start()

def hapus_jual(user_id):
    # Menghapus item keranjang
    Penjualan.objects.filter(user_id=user_id).delete()








@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def index(request):
    service = Service.objects.all()
    produk = Produk.objects.all()
    return render(request, 'after_login/beranda.html', {'service':service, 'produk':produk})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def aboutuser(request):
    return render(request, 'after_login/aboutuser.html')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def contactuser(request):
    return render(request, 'after_login/contactuser.html')

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def produkuser(request):
    kategori = request.GET.get('kategori')

    if kategori == 'Haircare':
        produk = Produk.objects.filter(kategori='Haircare')
    elif kategori == 'Bodycare':
        produk = Produk.objects.filter(kategori='Bodycare')
    elif kategori == 'Skincare':
        produk = Produk.objects.filter(kategori='Skincare')
    else:
        produk = Produk.objects.all()
    for p in produk:
        p.url_tambah_keranjang = reverse('tambah_keranjang', args=[p.id])
    return render(request, 'after_login/produk.html', {
        'produk': produk,
    })


def tambah_keranjang(request, produk_id):
        if not request.user.is_authenticated:
            messages.warning(request, 'Anda harus login terlebih dahulu untuk melakukan pembelian.')
            return redirect('login')
        user = request.user
        keranjang, created = Keranjang.objects.get_or_create(user=user)
        produk = Produk.objects.get(id=produk_id)
        keranjang_item, item_created = KeranjangItem.objects.get_or_create(keranjang=keranjang, produk=produk, user=user)


        if not item_created:
            keranjang_item.jumlah += 1
            keranjang_item.save()

        return redirect('keranjang')

def keranjang(request):
    user = request.user

    # Get the user's cart
    keranjang, created = Keranjang.objects.get_or_create(user=user)

    # Get all items in the cart
    keranjang_items = KeranjangItem.objects.filter(keranjang=keranjang)

    # Calculate total price and total item count
    total_harga = keranjang.total_harga()
    total_item = keranjang.total_item()

    return render(request, 'after_login/keranjang.html', {'keranjang_items': keranjang_items, 'total_harga': total_harga, 'total_item': total_item, 'keranjang':keranjang})

def edit_jumlah(request, id):
    keranjang_item = get_object_or_404(KeranjangItem, id=id)

    if request.method == 'POST':
        jumlah = int(request.POST.get('jumlah'))
        keranjang_item.jumlah = jumlah
        keranjang_item.save()
        return redirect('keranjang')

    return render(request, 'after_login/editkeranjang.html', {'keranjang_item': keranjang_item})

def delete_keranjang(request, id):
    if request.method == 'POST':
        keranjang = KeranjangItem.objects.get(id=id)
        keranjang.delete()
    return redirect('keranjang')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def detailprodukuser(request, id):
    produk = get_object_or_404(Produk, id=id)
    produk.url_tambah_keranjang = reverse('tambah_keranjang', args=[produk.id])
    return render(request, 'after_login/detailprodukuser.html', {
        'produk': produk,
    })




@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def detailuser(request, jenis_layanan, id):
    service = get_object_or_404(Service, jenis_layanan=jenis_layanan, id=id)
    return render(request, 'after_login/detailuser.html', {'service':service})

@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_user)
def serviceuser(request):
    eyelash = Service.objects.filter(jenis_layanan='eyelash')
    haircare = Service.objects.filter(jenis_layanan='haircare')
    nails = Service.objects.filter(jenis_layanan='nails')

    return render(request, 'after_login/serviceuser.html', {
        'eyelash': eyelash,
        'haircare': haircare,
        'nails': nails,
    })
