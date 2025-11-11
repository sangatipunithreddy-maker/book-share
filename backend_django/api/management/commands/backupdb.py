from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import shutil, time, os

class Command(BaseCommand):
    help = "Backup the SQLite database to backups/ with a timestamped filename."

    def handle(self, *args, **options):
        db_path = Path(settings.DATABASES['default']['NAME'])
        if not db_path.exists():
            self.stderr.write(self.style.ERROR(f"Database file not found: {db_path}"))
            return

        backups_dir = Path(settings.BASE_DIR) / 'backups'
        backups_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        dest = backups_dir / f"bookshare-{ts}.db"
        shutil.copy2(db_path, dest)
        self.stdout.write(self.style.SUCCESS(f"Backup created: {dest}"))