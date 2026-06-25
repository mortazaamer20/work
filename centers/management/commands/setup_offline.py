import os
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


FONTS = {
    "static/fonts/tajawal/Tajawal-Regular.ttf": "https://fonts.gstatic.com/s/tajawal/v12/Iura6YBj_oCad4k1rzY.ttf",
    "static/fonts/tajawal/Tajawal-Medium.ttf": "https://fonts.gstatic.com/s/tajawal/v12/Iurf6YBj_oCad4k1l8KiLrY.ttf",
    "static/fonts/tajawal/Tajawal-Bold.ttf": "https://fonts.gstatic.com/s/tajawal/v12/Iurf6YBj_oCad4k1l4qkLrY.ttf",
    "static/fonts/tajawal/Tajawal-ExtraBold.ttf": "https://fonts.gstatic.com/s/tajawal/v12/Iurf6YBj_oCad4k1l5anLrY.ttf",
}

BI_URL = "https://registry.npmjs.org/bootstrap-icons/-/bootstrap-icons-1.11.3.tgz"


class Command(BaseCommand):
    help = "تحميل ملفات الخطوط والأيقونات للعمل بدون إنترنت"

    def handle(self, *args, **options):
        base = settings.BASE_DIR

        for rel_path, url in FONTS.items():
            dest = base / rel_path
            if dest.exists():
                self.stdout.write(f"  موجود: {rel_path}")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f"  تحميل: {rel_path} ...")
            urllib.request.urlretrieve(url, dest)

        bi_dir = base / "static/fonts/bootstrap-icons"
        woff2 = bi_dir / "bootstrap-icons.woff2"
        if woff2.exists():
            self.stdout.write("  أيقونات Bootstrap موجودة")
        else:
            import tarfile, io, shutil
            self.stdout.write("  تحميل أيقونات Bootstrap Icons ...")
            bi_dir.mkdir(parents=True, exist_ok=True)
            resp = urllib.request.urlopen(BI_URL)
            data = resp.read()
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                for member in tar.getmembers():
                    if "font/fonts/" in member.name and member.isfile():
                        fname = os.path.basename(member.name)
                        f = tar.extractfile(member)
                        with open(bi_dir / fname, "wb") as out:
                            out.write(f.read())
                    elif member.name.endswith("bootstrap-icons.min.css"):
                        f = tar.extractfile(member)
                        css = f.read().decode()
                        css = css.replace('url("fonts/bootstrap-icons', 'url("bootstrap-icons')
                        with open(bi_dir / "bootstrap-icons.min.css", "w") as out:
                            out.write(css)

        self.stdout.write(self.style.SUCCESS("تم تجهيز ملفات العمل بدون إنترنت!"))
