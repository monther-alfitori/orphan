from django.db import models, transaction
from django.db.models import Sum, Count


class Sponsor(models.Model):
    # Sponsor Name
    name = models.CharField(max_length=255, help_text="اسم الكفيل")

    CITY_CHOICES = [
        ('مصراتة', 'مصراتة'),
        ('طرابلس', 'طرابلس'),
        ('زليتن', 'زليتن'),
        ('الخمس', 'الخمس'),
        ('بنغازي', 'بنغازي'),
        ('مسلاتة', 'مسلاتة'),
        ('الزاوية', 'الزاوية'),
    ]
    # Residence Location
    residence_location = models.CharField(choices=CITY_CHOICES, max_length=255, help_text="مكان الاقامة")

    # Phone Number Fields
    primary_phone = models.CharField(max_length=15, help_text="رقم الهاتف")
    secondary_phone = models.CharField(max_length=15, null=True, blank=True, help_text="رقم هاتف آخر")

    # Sponsorship Amount Choices
    SPONSORSHIP_AMOUNT_CHOICES = [
        (700, '700'),
        (600, '600'),
        (500, '500'),
        (400, '400'),
        (300, '300'),
        (200, '200'),
        (100, '100'),
    ]
    sponsorship_amount = models.IntegerField(choices=SPONSORSHIP_AMOUNT_CHOICES, help_text="قيمة الكفالة  في الشهر")

    # Custom Sponsorship Amount if Greater than 700
    custom_amount = models.IntegerField(null=True, blank=True, help_text="في حال اخترت قيمة أكبر من 700 دينار يرجى كتابة القيمة")

    # Payment Frequency Choices
    PAYMENT_FREQUENCY_CHOICES = [
        ('سنوي', 'سنوي'),
        ('نصف سنوي', 'نصف سنوي'),
        ('ربع سنوي', 'ربع سنوي'),
        ('شهري', 'شهري'),
    ]
    payment_frequency = models.CharField(max_length=100, choices=PAYMENT_FREQUENCY_CHOICES, help_text="يكون تسليم  الكفالة بشكل")

    # Initial Payment Timing Choices
    INITIAL_PAYMENT_CHOICES = [
        ('بداية من هذا الشهر', 'بداية من هذا الشهر'),
        ('بداية من الشهر القادم', 'بداية من الشهر القادم'),
    ]
    initial_payment_timing = models.CharField(max_length=200, choices=INITIAL_PAYMENT_CHOICES, help_text="موعد تسليم الدفعة الاولى من الكفالة")

    # Payment Method Choices
    PAYMENT_METHOD_CHOICES = [
        ('نقدي', 'نقدي'),
        ('التحويل عن طريق مكاتب الصرافة الخاصة', 'التحويل عن طريق مكاتب الصرافة الخاصة'),
        ('التحويل المصرفي', 'التحويل المصرفي'),
        ('البطاقة المصرفية', 'البطاقة المصرفية'),
    ]
    payment_method = models.CharField(max_length=200, choices=PAYMENT_METHOD_CHOICES, help_text="ما وسيلة الدفع المناسبة لك")

    # Orphan Selection Choices
    ORPHAN_SELECTION_CHOICES = [
        ('اريد اختيار اليتيم بنفسي', 'اريد اختيار اليتيم بنفسي'),
        ('افوض الحملة في اختيار اليتيم وفق المتبع لديها وابلاغي بالمعلومات', 'افوض الحملة في اختيار اليتيم وفق المتبع لديها وابلاغي بالمعلومات'),
        ('غير مهتم بالحصول على معلومات عن اليتيم مع متابعة تسليم دفعات الكفالة', 'غير مهتم بالحصول على معلومات عن اليتيم مع متابعة تسليم دفعات الكفالة'),
    ]
    orphan_selection = models.CharField(max_length=200, choices=ORPHAN_SELECTION_CHOICES, help_text="اختيار اليتيم")

    # Submission Timestamp
    submitted_at = models.DateTimeField(auto_now_add=True, help_text="تاريخ تقديم النموذج")


    @classmethod
    def get_statistics(cls):
        # Calculate total sponsorship amount
        total_amount_data = cls.objects.aggregate(
            regular_amount=Sum('sponsorship_amount'),
            custom_amount=Sum('custom_amount')
        )
        total_amount = (total_amount_data['regular_amount'] or 0) + \
                       (total_amount_data['custom_amount'] or 0)

        stats = {
            # Total unique sponsors
            'total_sponsors': cls.objects.values('name').distinct().count(),
            
            # Total sponsorship amount
            'total_amount': total_amount,
            
            # Count of active cities (cities that have at least one sponsor)
            'active_cities': cls.objects.values('residence_location').distinct().count(),
            
            # Calculate total_sponsorships as total_amount / 700
            'total_sponsorships': int(total_amount / 700) if total_amount else 0,
        }
        return stats

    def __str__(self):
        return f"{self.name} - {self.primary_phone}"