"""Bounded public web retrieval with defense-in-depth against SSRF."""
import ipaddress
import socket
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from talentflow.domain.errors import SourceUnavailable

MAX_BYTES = 1_000_000
MAX_REDIRECTS = 3


def _public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise SourceUnavailable("Enter a public HTTP(S) job posting URL.")
    if parsed.port not in (None, 80, 443):
        raise SourceUnavailable("Custom network ports are not supported.")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise SourceUnavailable("Only public job posting URLs are supported.")
    try:
        addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except OSError as exc:
        raise SourceUnavailable("Unable to resolve the job posting website.") from exc
    if not addresses or any(not ipaddress.ip_address(entry[4][0]).is_global for entry in addresses):
        raise SourceUnavailable("The job posting URL does not resolve to a public address.")
    return url


def fetch_job_content(url: str) -> str:
    """Retrieve public pages; use a network egress policy in production to prevent DNS rebinding."""
    current = url
    try:
        with httpx.Client(timeout=httpx.Timeout(12), follow_redirects=False, trust_env=False) as client:
            for _ in range(MAX_REDIRECTS + 1):
                _public_url(current)
                with client.stream("GET", current, headers={"User-Agent": "TalentFlowAI/2.0", "Accept": "text/html"}) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise SourceUnavailable("Job posting redirected without a destination.")
                        current = urljoin(current, location)
                        continue
                    response.raise_for_status()
                    if "text/html" not in response.headers.get("content-type", "").lower():
                        raise SourceUnavailable("The link did not return an HTML job posting.")
                    chunks = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise SourceUnavailable("Job posting webpage is too large.")
                        chunks.append(chunk)
                    soup = BeautifulSoup(b"".join(chunks), "html.parser")
                    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                        tag.decompose()
                    text = " ".join(soup.stripped_strings)
                    if len(text) < 80:
                        raise SourceUnavailable("No readable job details were found at this URL.")
                    return text[:60000]
            raise SourceUnavailable("Job posting redirected too many times.")
    except SourceUnavailable:
        raise
    except (httpx.HTTPError, OSError, ValueError) as exc:
        raise SourceUnavailable("Unable to access the job posting. Paste the job description instead.") from exc
