from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditAction, AuditLog
from apps.core.publication import PublicationStatus
from apps.documents.models import Document, DocumentCategory, DocumentKind

from .helpers import test_pdf


class LegacyConfidentialDocumentCompatibilityTests(TestCase):
    """Le dispositif d’autorisation a été retiré sans casser les anciennes données."""

    def setUp(self):
        self.author = User.objects.create_user(
            email="author@example.test",
            password="StrongPassword-123!",
        )
        # Catégorie créée par la migration 0002_seed_document_categories.
        self.category = DocumentCategory.objects.get(slug="rapports")
        # is_confidential a été supprimé (0007_cleanup_legacy_document_access) : un ancien document confidentiel
        # est un document ordinaire.
        self.document = Document.objects.create(
            title="Ancien rapport confidentiel",
            summary="Document désormais accessible publiquement",
            reference="DOC-001",
            category=self.category,
            kind=DocumentKind.REPORT,
            date=timezone.localdate(),
            file=test_pdf("document.pdf"),
            original_filename="document.pdf",
            file_size=128,
            mime_type="application/pdf",
            status=PublicationStatus.PUBLISHED,
            author=self.author,
            last_editor=self.author,
        )

    def test_legacy_confidential_flag_no_longer_blocks_public_reading(self):
        detail = self.client.get(
            reverse("documents_api:detail", kwargs={"slug": self.document.slug})
        )
        self.assertEqual(detail.status_code, 200)
        payload = detail.json()
        # Les champs du contrôle d'accès ont disparu de l'API avec lui (ni le frontend ni l'API ne les lisent).
        self.assertNotIn("isConfidential", payload)
        self.assertNotIn("canRead", payload)
        self.assertTrue(payload["fileUrl"].endswith("/content/"))
        self.assertTrue(payload["downloadUrl"].endswith("/download/"))

        content = self.client.get(
            reverse("documents_api:content", kwargs={"slug": self.document.slug})
        )
        self.assertEqual(content.status_code, 200)
        self.assertEqual(content["Content-Disposition"].split(";")[0], "inline")

    def test_download_endpoint_counts_and_audits_each_download(self):
        url = (
            reverse("documents_api:download", kwargs={"slug": self.document.slug})
            + "?source=/documents/test"
        )
        first = self.client.get(url)
        second = self.client.get(url)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertIn("attachment", first["Content-Disposition"])

        self.document.refresh_from_db()
        self.assertEqual(self.document.downloads, 2)
        logs = AuditLog.objects.filter(
            action=AuditAction.DOCUMENT_DOWNLOADED,
            target_id=str(self.document.pk),
        ).order_by("created_at")
        self.assertEqual(logs.count(), 2)
        self.assertEqual(logs.last().metadata["source"], "/documents/test")
        self.assertEqual(logs.last().metadata["downloads"], 2)

    def test_access_request_routes_are_no_longer_exposed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("documents_api:request_access", kwargs={"slug": self.document.slug})
