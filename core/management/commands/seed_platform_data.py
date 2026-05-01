from django.core.management.base import BaseCommand

from accounts.models import User
from core.bootstrap import ensure_platform_catalog, ensure_user_preparation_data


class Command(BaseCommand):
    help = "Seed the placement platform catalog, a complete demo student account, and a staff admin account."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="student@prepsmart.dev")
        parser.add_argument("--password", default="PrepSmart@123")
        parser.add_argument("--name", default="Aarav Sharma")
        parser.add_argument("--admin-email", default="admin@prepsmart.dev")
        parser.add_argument("--admin-password", default="Admin@12345")
        parser.add_argument("--admin-name", default="PrepSmart Admin")
        parser.add_argument("--skip-admin", action="store_true")

    def handle(self, *args, **options):
        ensure_platform_catalog()

        user, created = User.objects.get_or_create(
            email=options["email"],
            defaults={"name": options["name"]},
        )

        if created:
            user.set_password(options["password"])
            user.save(update_fields=["password"])
        elif not user.name:
            user.name = options["name"]
            user.save(update_fields=["name"])

        ensure_user_preparation_data(user)

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Seed data {action} for {user.email}"))

        if not options["skip_admin"]:
            admin_user, admin_created = User.objects.get_or_create(
                email=options["admin_email"],
                defaults={
                    "name": options["admin_name"],
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )

            admin_updates = []
            if admin_created:
                admin_user.set_password(options["admin_password"])
                admin_updates.append("password")
            if admin_user.name != options["admin_name"]:
                admin_user.name = options["admin_name"]
                admin_updates.append("name")
            if not admin_user.is_staff:
                admin_user.is_staff = True
                admin_updates.append("is_staff")
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                admin_updates.append("is_superuser")
            if not admin_user.is_active:
                admin_user.is_active = True
                admin_updates.append("is_active")

            if admin_updates:
                admin_user.save(update_fields=sorted(set(admin_updates)))

            admin_action = "created" if admin_created else "updated"
            self.stdout.write(self.style.SUCCESS(f"Admin account {admin_action}: {admin_user.email}"))
