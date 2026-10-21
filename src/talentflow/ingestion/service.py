from talentflow.config import Settings
from talentflow.domain.models import ContentInput, ResolvedContent, SourceKind
from talentflow.domain.errors import InputError
from talentflow.ingestion.documents import read_document
from talentflow.ingestion.web import fetch_job_content


class ContentService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def resolve(self, source: ContentInput, *, allow_url: bool) -> ResolvedContent:
        if source.kind == SourceKind.URL:
            if not allow_url:
                raise InputError("Resume URLs are not supported. Upload or paste the resume.")
            text = fetch_job_content(source.url or "")
            label = source.url or "Job URL"
        elif source.kind == SourceKind.FILE:
            text = read_document(source.filename or "", source.file_bytes or b"", self.settings)
            label = source.filename or "Document"
        else:
            text = (source.text or "").strip()
            label = "Pasted text"
        if len(text) > self.settings.max_characters:
            raise InputError("Text exceeds the maximum allowed length.")
        if len(text) < 40:
            raise InputError("Provide more complete content for analysis.")
        return ResolvedContent(text=text, source=source.kind, label=label)
