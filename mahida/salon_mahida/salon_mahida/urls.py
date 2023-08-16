from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from user.views import *
from adminn.views import *


urlpatterns = [
    path('login/',login, name='login'),
    path('logout/',logout, name='logout'),
    path('daftar/',daftar, name='daftar'),

    path('booking/<int:id>/',booking, name='booking'),
    path('bayar/<int:id>/',bayar, name='bayar_sekarang'),

    path('',home, name='home'),
    path('index/',home, name='home'),
    path('service/',service, name='service'),
    path('detail/<str:jenis_layanan>/<int:id>/',service_detail, name='service_detail'),
    path('detailproduk/<int:id>/',detailproduk, name='detailproduk'),
    path('contact/',contact, name='contact'),
    path('about/',about, name='about'),
    path('product/',product, name='product'),
    path('tambah_keranjang/<int:produk_id>/',tambah_keranjang, name='tambah_keranjang'),
    path('edit_jumlah/<int:id>/',edit_jumlah, name='edit_jumlah'),
    path('delete_keranjang/<int:id>/',delete_keranjang, name='delete_keranjang'),

    path('admin/',admin, name='admin'),
    path('data/',data, name='data'),

    path('kelola_user/',kelola_user, name='kelola_user'),
    path('tambah_user/',tambah_user, name='tambah_user'),
    path('edit/user/<int:id>/', edit_user, name='edit_user'),
    path('edit/user/<int:id>/update/',update_user, name='update_user'),
    path('delete/user/<int:id>/', delete_user, name='delete_user'),

    path('kelola_jadwal/',kelola_jadwal, name='kelola_jadwal'),
    path('tambah_jadwal/',tambah_jadwal, name='tambah_jadwal'),
    path('edit/jadwal/<int:id>/', edit_jadwal, name='edit_jadwal'),
    path('edit/jadwal/<int:id>/update/',update_jadwal, name='update_jadwal'),
    path('delete/jadwal/<int:id>/', delete_jadwal, name='delete_jadwal'),

    path('kelola_service/',kelola_service, name='kelola_service'),
    path('tambah_service/',tambah_service, name='tambah_service'),
    path('edit/service/<int:id>/', edit_service, name='edit_service'),
    path('edit/service/<int:id>/update/',update_service, name='update_service'),
    path('delete/service/<int:id>/', delete_service, name='delete_service'),

    path('kelola_produk/',kelola_produk, name='kelola_produk'),
    path('tambah_produk/',tambah_produk, name='tambah_produk'),
    path('delete/produk/<int:id>/', delete_produk, name='delete_produk'),
    path('edit/produk/<int:id>/', edit_produk, name='edit_produk'),
    path('edit/produk/<int:id>/update/',update_produk, name='update_produk'),
    
    path('kelola_pembelian/',kelola_pembelian, name='kelola_pembelian'),
    path('tambah_pembelian/',tambah_pembelian, name='tambah_pembelian'),
    path('edit/pembelian/<int:id>/', edit_pembelian, name='edit_pembelian'),
    path('edit/pembelian/<int:id>/update/',update_pembelian, name='update_pembelian'),
    path('delete/pembelian/<int:id>/', delete_pembelian, name='delete_pembelian'),


    path('kelola_penjualan/',kelola_penjualan, name='kelola_penjualan'),
    path('delete/penjualan/<int:id>/', delete_penjualan, name='delete_penjualan'),
    # path('tambah_produk/',tambah_produk, name='tambah_produk'),
    # path('edit/service/<int:id>/', edit_service, name='edit_service'),
    # path('edit/service/<int:id>/update/',update_service, name='update_service'),

    path('kelola_booking/',kelola_booking, name='kelola_booking'),
    path('setuju/<int:id>/', setuju, name='setuju'),
    path('tolak/<int:id>/', tolak, name='tolak'),
    # path('tambah_service/',tambah_service, name='tambah_service'),
    # path('edit/user/<int:id>/', edit_user, name='edit_user'),
    # path('edit/user/<int:id>/update/',update_user, name='update_user'),
    # path('delete/user/<int:id>/', delete_user, name='delete_user')

    path('kelola_transaksi/',kelola_transaksi, name='kelola_transaksi'),
    path('dikirim/<int:id>/', dikirim, name='dikirim'),
    path('ditolak/<int:id>/', ditolak, name='ditolak'),
    # path('tambah_service/',tambah_service, name='tambah_service'),
    # path('edit/user/<int:id>/', edit_user, name='edit_user'),
    # path('edit/user/<int:id>/update/',update_user, name='update_user'),
    # path('delete/user/<int:id>/', delete_user, name='delete_user')

    path('laporan_reservasi/', laporan_reservasi, name='laporan_reservasi'),
    path('laporan_reservasi_pdf/',laporan_pdf_reservasi,name='laporan_reservasi_pdf'),

    path('laporan_penjualan/', laporan_penjualan, name='laporan_penjualan'),
    path('laporan_penjualan_pdf/',laporan_pdf_penjualan,name='laporan_penjualan_pdf'),

    path('laporan_pembelian/', laporan_pembelian, name='laporan_pembelian'),
    path('laporan_pembelian_pdf/',laporan_pdf_pembelian,name='laporan_pembelian_pdf'),
    # after login
    path('beranda/',index, name='index'),
    path('.service/',serviceuser, name='serviceuser'),
    path('.about/',aboutuser, name='aboutuser'),
    path('.contact/',contactuser, name='contactuser'),
    path('.product/',produkuser, name='produkuser'),
    path('keranjang/',keranjang, name='keranjang'),
    path('.detail_produk/<int:id>/',detailprodukuser, name='detailprodukuser'),
    path('.detail/<str:jenis_layanan>/<int:id>/',detailuser, name='detailuser'),
    path('status/<int:booking_id>/',status, name='status'),
    path('status_beli/<int:transaksi_id>/',status_beli, name='status_beli'),
    path('status_pembayaran/<int:transaksi_id>/',status_pembayaran, name='status_pembayaran'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
