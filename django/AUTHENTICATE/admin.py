from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django import forms
from .models import Brother_Profile, Role, Major, DashboardLink
from adminsortable2.admin import SortableAdminMixin

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Profile', {'fields': ('brother_profile',)}),
    )
    readonly_fields = ('brother_profile',)
    filter_horizontal = ()

    def brother_profile(self, obj):
        return obj.brother_profile.profileImage

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('brother_profile')
        return qs

    def brother_profile(self, obj):
        return obj.brother_profile.profileImage

    brother_profile.short_description = 'Profile Image'

class Brother_ProfileForm(forms.ModelForm):
    new_major = forms.CharField(required=False)

    class Meta:
        model = Brother_Profile
        fields = ('majors',)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['new_major']:
            major, created = Major.objects.get_or_create(name=self.cleaned_data['new_major'])
            instance.majors.add(major)
        if commit:
            instance.save()
        return instance

class Brother_ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'firstName',
        'lastName',
        'hometown',
        'pclass',
        'get_majors',
        'get_roles',
        'profileImage',
    )

    def get_majors(self, obj):
        return ', '.join([major.name for major in obj.majors.all()])

    def get_roles(self, obj):
        return ', '.join([role.get_name_display() for role in obj.roles.all()])

    get_majors.short_description = 'Majors'
    get_roles.short_description = 'Roles'

    def save_model(self, request, obj, form, change):
        if 'profileImage' in request.FILES:
            obj.profileImage = request.FILES['profileImage']
        obj.save()

class MajorAdmin(admin.ModelAdmin):
    list_display = ('name',)

class DashboardLinkAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('text', 'link')

User  = get_user_model()
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Brother_Profile, Brother_ProfileAdmin)
admin.site.register(Role)
admin.site.register(Major, MajorAdmin)
admin.site.register(DashboardLink, DashboardLinkAdmin)