from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class PClass(models.TextChoices):
    ALPHA = 'Alpha', 'Alpha'
    BETA = 'Beta', 'Beta'
    GAMMA = 'Gamma', 'Gamma'
    DELTA = 'Delta', 'Delta'
    EPSILON = 'Epsilon', 'Epsilon'
    ZETA = 'Zeta', 'Zeta'
    ETA = 'Eta', 'Eta'
    THETA = 'Theta', 'Theta'
    IOTA = 'Iota', 'Iota'
    KAPPA = 'Kappa', 'Kappa'
    LAMBDA = 'Lambda', 'Lambda'
    MU = 'Mu', 'Mu'
    NU = 'Nu', 'Nu'
    XI = 'Xi', 'Xi'
    OMICRON = 'Omicron', 'Omicron'
    PI = 'Pi', 'Pi'
    RHO = 'Rho', 'Rho'
    SIGMA = 'Sigma', 'Sigma'
    TAU = 'Tau', 'Tau'
    UPSILON = 'Upsilon', 'Upsilon'
    PHI = 'Phi', 'Phi'
    CHI = 'Chi', 'Chi'
    PSI = 'Psi', 'Psi'
    OMEGA = 'Omega', 'Omega'
    BETA_ALPHA = 'Beta Alpha', 'Beta Alpha'
    BETA_BETA = 'Beta Beta', 'Beta Beta'
    BETA_GAMMA = 'Beta Gamma', 'Beta Gamma'
    BETA_DELTA = 'Beta Delta', 'Beta Delta'
    BETA_EPSILON = 'Beta Epsilon', 'Beta Epsilon'
    BETA_ZETA = 'Beta Zeta', 'Beta Zeta'
    BETA_ETA = 'Beta Eta', 'Beta Eta'
    BETA_THETA = 'Beta Theta', 'Beta Theta'
    BETA_IOTA = 'Beta Iota', 'Beta Iota'
    BETA_KAPPA = 'Beta Kappa', 'Beta Kappa'
    BETA_LAMBDA = 'Beta Lambda', 'Beta Lambda'
    BETA_MU = 'Beta Mu', 'Beta Mu'
    BETA_NU = 'Beta Nu', 'Beta Nu'
    BETA_XI = 'Beta Xi', 'Beta Xi'
    BETA_OMICRON = 'Beta Omicron', 'Beta Omicron'
    BETA_PI = 'Beta Pi', 'Beta Pi'
    BETA_RHO = 'Beta Rho', 'Beta Rho'
    BETA_SIGMA = 'Beta Sigma', 'Beta Sigma'
    BETA_TAU = 'Beta Tau', 'Beta Tau'
    BETA_UPSILON = 'Beta Upsilon', 'Beta Upsilon'
    BETA_PHI = 'Beta Phi', 'Beta Phi'
    BETA_CHI = 'Beta Chi', 'Beta Chi'
    BETA_PSI = 'Beta Psi', 'Beta Psi'
    BETA_OMEGA = 'Beta Omega', 'Beta Omega'

class Role(models.Model):
    ROLE_CHOICES = [
        ('EXEC', 'Executive Board'),
        ('NM_BOARD', 'New Member Board'),
        ('ACTIVE', 'Active Member'),
        ('ALUMNI', 'Alumni'),
        ('NEW_MEMBER', 'New Member'),
        ('SOCIAL_CHAIR', 'Social Chair'),
        ('RECRUITMENT_CHAIR', 'Recruitment Chair'),
        ('PHIL_CHAIR', 'Philanthropy Chair'),
        ('RISK_MGR', 'Risk Manager'),
        ('PRESIDENT', 'President'),
        ('INT_VP', 'Internal VP'),
        ('EXT_VP', 'External VP'),
        ('BUSINESS_MGR', 'Business Manager'),
        ('AFFAIRS_DIRECTOR', 'Director of Chapter Affairs'),
        ('NME', 'New Member Educator'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class Major(models.Model):
    name = models.CharField(max_length=255, default='Unknown')

    def __str__(self):
        return self.name

class Brother_Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=200, null=True)
    lastName = models.CharField(max_length=200, null=True)
    profileImage = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    hometown = models.CharField(max_length=200, null=True, blank=True)
    pclass = models.CharField(max_length=50, choices=PClass.choices, null=True, blank=True)
    roles = models.ManyToManyField(Role)
    majors = models.ManyToManyField(Major, blank=True)
    
    def __str__(self):
        return f"{self.firstName} {self.lastName}"
        
    def save(self, *args, **kwargs):
        if self.profileImage:
            try:
                img = Image.open(self.profileImage)
                output_size = (300, 300)
                img.thumbnail(output_size)
                
                output = BytesIO()
                # Use original format if possible, default to PNG
                img_format = getattr(img, 'format', 'PNG')
                img.save(output, format=img_format, quality=85)
                output.seek(0)
                
                self.profileImage = InMemoryUploadedFile(
                    output, 
                    'ImageField',
                    f"{self.profileImage.name.split('/')[-1].split('.')[0]}.{img_format.lower()}", 
                    f'image/{img_format.lower()}',
                    sys.getsizeof(output), 
                    None
                )
            except Exception as e:
                # Log the error for debugging
                print(f"Error processing image: {e}")
                pass
                
        super().save(*args, **kwargs)

class DashboardLink(models.Model):
    text = models.CharField(max_length=200, help_text='Text to display on the button')
    link = models.CharField(max_length=200, help_text='URL for the button')
    order = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text