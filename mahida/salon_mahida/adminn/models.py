from django.db import models
from user.models import User, Service, Reservasi, Jadwal
from django.utils import timezone

class Produk(models.Model):
    KATEGORI_CHOICES = [
        ('Haircare', 'Haircare'),
        ('Bodycare', 'Bodycare'),
        ('Skincare', 'Skincare'),
    ]
    nama = models.CharField(max_length=100)
    stok = models.IntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    deskripsi = models.TextField()
    kategori = models.CharField(max_length=100, choices=KATEGORI_CHOICES)
    foto_produk = models.ImageField(upload_to='produk/')

    class Meta:
        db_table = "produk"

class KeranjangItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    keranjang = models.ForeignKey('Keranjang', on_delete=models.CASCADE, null=True)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE, null=True)
    jumlah = models.PositiveIntegerField(default=1)
    class Meta:
        db_table = "keranjangitem"
    def harga_subtotal(self):
        return self.produk.harga * self.jumlah

class Keranjang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField(Produk, through=KeranjangItem)

    class Meta:
        db_table = "keranjang"

    def total_harga(self):
        total = 0
        keranjang_items = KeranjangItem.objects.filter(keranjang=self)
        for item in keranjang_items:
            total += item.harga_subtotal()
        return total

    def total_item(self):
        return self.items.count()




class Penjualan(models.Model):
    KATEGORI_CHOICES = [
        ('Haircare', 'Haircare'),
        ('Bodycare', 'Bodycare'),
        ('Skincare', 'Skincare'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keranjang = models.ForeignKey(Keranjang, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE, null=True)
    nama_pembeli = models.CharField(max_length=100)
    kategori = models.CharField(max_length=100, choices=KATEGORI_CHOICES)
    no_wa = models.CharField(max_length=20)
    total_pembayaran = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    class Meta:
        db_table = "penjualan"

    def save(self, *args, **kwargs):
        self.total_pembayaran = self.keranjang.total_harga()
        super().save(*args, **kwargs)
        keranjang_item = KeranjangItem.objects.filter(keranjang=self.keranjang).first()
        if keranjang_item:
            self.produk = keranjang_item.produk
            self.produk.stok -= keranjang_item.jumlah
            self.produk.save()




class Pembelian(models.Model):
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    created_at = models.DateTimeField(null=True,default=timezone.now)

    class Meta:
        db_table = "pembeliann"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.produk.stok += int(self.jumlah)
        self.produk.save()

class Transaksi(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Disetujui', 'Disetujui'),
        ('Ditolak', 'Ditolak'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keranjang = models.ForeignKey(Keranjang, on_delete=models.CASCADE, null=True)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE, null=True)
    penjualan = models.ForeignKey(Penjualan, on_delete=models.CASCADE)
    nama_pengirim = models.CharField(max_length=100)
    alamat = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    bukti_transfer = models.ImageField(upload_to='bukti_transfer/')
    created_at = models.DateTimeField(null=True,default=timezone.now)

    class Meta:
        db_table = "transaksi"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        produk = self.penjualan.produk  # Get the produk from the penjualan model
        self.produk = produk 
