from django.db import models

# Create your models here.


class SiteConfig(models.Model):
    """Site Configurations"""

    key = models.SlugField(unique=True) 
    value = models.CharField(max_length=200)

    # New fields for site configuration
    college_name = models.CharField(max_length=200, blank=True, null=True)
    college_address = models.TextField(blank=True, null=True)
    college_email = models.EmailField(blank=True, null=True)
    college_phone = models.CharField(max_length=15, blank=True, null=True)
    college_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    principal_name = models.CharField(max_length=200, blank=True, null=True)
    COLLEGE_TYPE_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Semi-Government', 'Semi-Government'),
    ]
    college_type = models.CharField(
        max_length=20, choices=COLLEGE_TYPE_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return self.key


class AcademicSession(models.Model):
    """Academic Session"""

    name = models.CharField(max_length=200, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic Term"""

    name = models.CharField(max_length=20, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Subject"""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CollegeProfile(models.Model):
    college_name = models.CharField(max_length=255)
    college_address = models.TextField()
    college_email = models.EmailField()
    college_phone = models.CharField(max_length=15)
    college_logo = models.ImageField(upload_to='college_logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField()
    principal_name = models.CharField(max_length=255)
    college_type = models.CharField(max_length=50, choices=[
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Semi-Government', 'Semi-Government'),
    ])
    admin_email = models.EmailField()
    admin_contact = models.CharField(max_length=15)
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.college_name




# fees settings
class FeeSetting(models.Model):
    class_name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50)
    fee_type = models.CharField(max_length=100)
    amount = models.FloatField()
    due_date = models.DateField()
    late_fee = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.class_name} - {self.fee_type}"