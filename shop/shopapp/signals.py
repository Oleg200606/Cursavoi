from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Review

@receiver(post_save, sender=Review)
def notify_admin_about_review(sender, instance, created, **kwargs):
    if created and settings.REVIEW_SETTINGS['NOTIFY_ADMINS']:
        subject = f'Новый отзыв на продукт {instance.product.name}'
        message = f'Пользователь {instance.user.username} оставил отзыв:\n\n{instance.text}\n\nПроверить: {settings.ADMIN_URL}'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            settings.REVIEW_SETTINGS['ADMIN_EMAILS'],
            fail_silently=False,
        )

@receiver(post_save, sender=Review)
def notify_user_about_moderation(sender, instance, **kwargs):
    if not instance._state.adding:  # только при обновлении
        if instance.is_approved:
            subject = f'Ваш отзыв одобрен'
            message = f'Ваш отзыв на продукт {instance.product.name} был одобрен и опубликован.'
        elif instance.is_rejected:
            subject = f'Ваш отзыв отклонен'
            message = f'Ваш отзыв на продукт {instance.product.name} был отклонен модератором.'
        else:
            return
            
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False,
        )