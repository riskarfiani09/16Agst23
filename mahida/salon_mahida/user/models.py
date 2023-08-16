from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if User.objects.filter(no_wa=extra_fields.get('wa')).exists():
        # Email sudah digunakan, tampilkan pesan error atau ambil tindakan yang sesuai
            print("Email sudah digunakan.")
            return None
        # Normalisasi username
        username = self.normalize_email(username)
        # Buat instance User baru
        user = self.model(username=username, **extra_fields)
        # Set password
        user.set_password(password)
        # Simpan user ke database
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # Buat user biasa dengan metode create_user
        user = self.create_user(username, password, **extra_fields)
        # Set atribut is_staff dan is_superuser menjadi True
        user.is_staff = True
        user.is_superuser = True
        user.role = 'Admin' 
        # Simpan perubahan pada user
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    USER_ROLE = 'User'
    ADMIN_ROLE = 'Admin'
    ROLE_CHOICES = [
        (USER_ROLE, 'User'),
        (ADMIN_ROLE, 'Admin'),
    ]
    username = models.CharField(max_length=15, unique=True)
    no_wa = models.CharField(null=True, max_length=15, unique=True)
    password = models.CharField(max_length=200)
    confirm_password = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER_ROLE)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['no_wa']

    class Meta:
        db_table = "user"

    def is_admin(self):
        return self.role == self.ADMIN_ROLE
    
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.role == self.ADMIN_ROLE

    def has_module_perms(self, app_label):
        return self.role == self.ADMIN_ROLE
    

class Service(models.Model):
    JENIS_LAYANAN_CHOICES = [
        ('Eyelash', 'Eyelash'),
        ('Haircare', 'Haircare'),
        ('Nails', 'Nails'),
    ]
    nama_layanan = models.CharField(null=True, max_length=100)
    jenis_layanan = models.CharField(null=True, max_length=100, choices=JENIS_LAYANAN_CHOICES)
    harga_layanan = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    foto_service = models.FileField(upload_to='service/')
    deskripsi = models.TextField(max_length=200)

    class Meta:
        db_table = "layanan"

class Jadwal(models.Model):
    KESIBUKAN_CHOICES = [
        ('Sibuk', 'Sibuk'),
        ('Tidak Sibuk', 'Tidak Sibuk'),
    ]
    nama_pegawai = models.CharField(null=True, max_length=100)
    jam = models.TimeField(max_length=5)
    tanggal = models.DateField()
    sibuk = models.CharField(null=True, max_length=50, choices=KESIBUKAN_CHOICES)

    class Meta:
        db_table = "jadwal"
    

class Reservasi(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Disetujui', 'Disetujui'),
        ('Ditolak', 'Ditolak'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status_konfirmasi = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    nama_lengkap = models.CharField(null=True,max_length=100)
    email = models.EmailField(null=True)
    pesan = models.TextField()
    layanan = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    jadwal = models.ForeignKey(Jadwal, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(null=True,default=timezone.now)

    class Meta:
        db_table = "booking"

    def __str__(self):
        return self.nama_lengkap
