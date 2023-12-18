"""Celery tasks for vpn_app."""
from celery import shared_task
from django.db import transaction
from django.db.models import F

from vpn_app.models import VpnSite


@shared_task()
def add_links_number(user_id: int, domain: str) -> None:
    """Increase used_links_number model field."""
    with transaction.atomic():
        vpn_site = VpnSite.objects.filter(owner_id=user_id, domain=domain).first()
        if vpn_site:
            vpn_site.used_links_number = F("used_links_number") + 1
            vpn_site.save()


@shared_task()
def add_loaded_volume(user_id: int, domain: str, volume: str | int) -> None:
    """Increase loaded_volume model field."""
    with transaction.atomic():
        vpn_site = VpnSite.objects.filter(owner_id=user_id, domain=domain).first()
        if vpn_site:
            vpn_site.loaded_volume = F("loaded_volume") + int(volume)
            vpn_site.save()


@shared_task()
def add_sended_volume(user_id: int, domain: str, volume: str | int) -> None:
    """Increase loaded_volume model field."""
    with transaction.atomic():
        vpn_site = VpnSite.objects.filter(owner_id=user_id, domain=domain).first()
        if vpn_site:
            vpn_site.sended_volume = F("sended_volume") + int(volume)
            vpn_site.save()
