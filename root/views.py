from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from pathlib import Path
import re


def index(request):
    dist_index = Path(settings.BASE_DIR) / 'static' / 'dist' / 'index.html'
    if not dist_index.exists():
        return HttpResponseNotFound('Build file not found: static/dist/index.html')

    html = dist_index.read_text(encoding='utf-8')

    # Supprime les balises Django si elles apparaissent dans le HTML brut.
    html = re.sub(r'{%\s*load\s+static\s*%}', '', html)
    html = re.sub(
        r"\{%%\s*static\s+['\"]([^'\"]+)['\"]\s*%%\}",
        lambda m: f"/{settings.STATIC_URL.lstrip('/').rstrip('/')}/{m.group(1)}",
        html,
    )

    if '<base' not in html.lower():
        static_url = settings.STATIC_URL
        if not static_url.startswith('/'):
            static_url = '/' + static_url
        if not static_url.endswith('/'):
            static_url += '/'
        base_tag = f'<base href="{static_url}dist/">\n'
        html = html.replace('<head>', f'<head>\n  {base_tag}', 1)

    return HttpResponse(html)