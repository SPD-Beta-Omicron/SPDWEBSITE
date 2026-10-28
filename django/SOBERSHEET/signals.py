from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from AUTHENTICATE.models import Brother_Profile
from .models import Sober_Exemption


@receiver(m2m_changed, sender=Brother_Profile.roles.through)
def exempt_risk_managers(sender, instance, action, reverse, pk_set, **kwargs):
    if action != 'post_add' or not pk_set:
        return

    if reverse:
        # role.brother_profile_set.add(...): instance is the Role
        if instance.name != 'RISK_MGR':
            return
        profiles = Brother_Profile.objects.filter(pk__in=pk_set)
    else:
        # profile.roles.add(...): instance is the Brother_Profile
        if not instance.roles.filter(pk__in=pk_set, name='RISK_MGR').exists():
            return
        profiles = [instance]

    for p in profiles:
        if p.user_id:
            Sober_Exemption.objects.get_or_create(user_id=p.user_id)