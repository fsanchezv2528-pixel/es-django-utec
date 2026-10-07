"""Suite de pruebas W03 — Archivos de despliegue y configuración."""
from pathlib import Path

from django.conf import settings
from django.test import TestCase

BASE_DIR = Path(settings.BASE_DIR)


class ArchivosDespliegueTest(TestCase):
    """Verifica que los archivos de despliegue existen en el repositorio."""

    def test_procfile_existe(self):
        self.assertTrue((BASE_DIR / 'Procfile').exists(),
                        "Procfile no encontrado en la raíz del proyecto")

    def test_procfile_contiene_gunicorn(self):
        procfile = BASE_DIR / 'Procfile'
        if procfile.exists():
            content = procfile.read_text(encoding='utf-8')
            self.assertIn('gunicorn', content,
                          "Procfile debe usar gunicorn, no runserver")

    def test_dockerfile_existe(self):
        self.assertTrue((BASE_DIR / 'Dockerfile').exists(),
                        "Dockerfile no encontrado")

    def test_render_yaml_existe(self):
        self.assertTrue((BASE_DIR / 'render.yaml').exists(),
                        "render.yaml no encontrado")

    def test_docker_compose_existe(self):
        self.assertTrue((BASE_DIR / 'docker-compose.yml').exists(),
                        "docker-compose.yml no encontrado")

    def test_ficha_schmelkes_e1_existe(self):
        self.assertTrue((BASE_DIR / 'fichas' / 'espiral_01_infra.md').exists(),
                        "fichas/espiral_01_infra.md no encontrado")


class RequirementsProduccionTest(TestCase):
    """Verifica que requirements.txt incluye dependencias de producción."""

    def _leer_requirements(self):
        req_path = BASE_DIR / 'requirements.txt'
        if not req_path.exists():
            self.fail("requirements.txt no encontrado")
        return req_path.read_text(encoding='utf-8').lower()

    def test_gunicorn_en_requirements(self):
        self.assertIn('gunicorn', self._leer_requirements())

    def test_psycopg2_en_requirements(self):
        self.assertIn('psycopg2', self._leer_requirements())

    def test_dj_database_url_en_requirements(self):
        self.assertIn('dj-database-url', self._leer_requirements())


class SettingsProdTest(TestCase):
    """Verifica el contenido de settings_prod.py leyendo el archivo."""

    def _leer_settings_prod(self):
        path = BASE_DIR / 'core' / 'settings_prod.py'
        if not path.exists():
            self.fail("core/settings_prod.py no encontrado")
        return path.read_text(encoding='utf-8')

    def test_settings_prod_tiene_debug_false(self):
        self.assertIn('DEBUG = False', self._leer_settings_prod())

    def test_settings_prod_importa_dj_database_url(self):
        self.assertIn('dj_database_url', self._leer_settings_prod())