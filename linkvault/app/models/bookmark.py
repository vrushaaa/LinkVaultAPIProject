from datetime import datetime
from app import db
import hashlib
from urllib.parse import urlparse, urlunparse

# Association table for many-to-many
bookmark_tags = db.Table(
    'bookmark_tags',
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmark.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

def normalize_url(url: str) -> str:
    """Normalize URL for hashing and deduplication."""
    parsed = urlparse(url)
    # Remove fragments, normalize scheme/path
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # no fragment
    ))
    return normalized

def generate_url_hash(url: str) -> str:
    """Generate SHA-256 hash of normalized URL."""
    norm_url = normalize_url(url)
    return hashlib.sha256(norm_url.encode('utf-8')).hexdigest()

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(20), unique=True)  # e.g. x7k9p
    hash_url = db.Column(db.String(64), unique=True, nullable=False)  # SHA-256
    title = db.Column(db.String(200))
    notes = db.Column(db.Text)
    archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tags = db.relationship('Tag', secondary=bookmark_tags, back_populates='bookmarks')

    def set_hash(self):
        self.hash_url = generate_url_hash(self.url)

    def generate_short_code(self):
        """Generate 6-char short code from hash."""
        import base64
        short = base64.urlsafe_b64encode(bytes.fromhex(self.hash_url[:12])).decode('utf-8').rstrip('=')
        return short[:6]

    def set_short_url(self):
        self.short_url = self.generate_short_code()

    def __repr__(self):
        return f'<Bookmark {self.short_url or self.url}>'