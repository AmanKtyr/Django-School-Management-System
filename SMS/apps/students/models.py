from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
import random
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Sum

class Student(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    category = [("N/A", "N/A"),("Gen", "Gen"), ("OBC", "OBC"), ("SC/ST", "SC/ST"), ("Other", "Other")]

    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    registration_number = models.CharField(max_length=200, unique=True, null=True, blank=True)
    fullname = models.CharField(max_length=200)
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    category = models.CharField(max_length=10, choices=category, default="N/A")

# Aadhaar number validator (must be 12 digits)
    aadhar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Aadhaar number must be exactly 12 digits.",
    code='invalid_aadhar'
    )
    aadhar = models.CharField(validators=[aadhar_validator], max_length=12, blank=True)
    


    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(
        'corecode.StudentClass',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    section = models.CharField(max_length=10, blank=True)
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    Father_name = models.CharField(max_length=255, null=False, blank=False)

    Father_mobile_number = models.CharField( validators=[mobile_num_regex] ,max_length=15,)
    Father_aadhar = models.CharField(validators=[aadhar_validator], max_length=12, blank=True)
    Mother_name = models.CharField(max_length=255, null=True, blank=True)


    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")
    # Barcode Field
    # barcode_image = models.ImageField(upload_to="students/barcodes/", blank=True, null=True)



    def generate_registration_number(self):
        """Generate registration number only once during creation"""
        if not self.registration_number:
            year_suffix = str(self.date_of_admission.year)[-2:]
            unique_number = str(random.randint(1000, 9999))
            current_class = self.current_class.name if self.current_class else "00"
            self.registration_number = f"{year_suffix}{current_class}{unique_number}"
        return self.registration_number

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()
        super().save(*args, **kwargs)

    def get_total_fee(self):
        """Calculate total fee for the student"""
        from apps.fees.models import FeePayment
        return FeePayment.objects.filter(
            student=self,
            status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

    def get_paid_fee(self):
        """Calculate total paid fee for the student"""
        from apps.fees.models import FeePayment
        return FeePayment.objects.filter(
            student=self,
            status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

    def get_due_fee(self):
        """Calculate due fee for the student"""
        return self.get_total_fee() - self.get_paid_fee()

    class Meta:
        ordering = ["fullname",]

    def __str__(self):
        return f"{self.fullname} "

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})


class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")    
