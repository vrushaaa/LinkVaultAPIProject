import click
from app import db
from app.models.bookmark import Bookmark, normalize_url, generate_url_hash
from app.models.tag import Tag
from bs4 import BeautifulSoup
import re

def parse_netscape_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    bookmarks = []
    for a in soup.find_all('a'):
        url = a.get('href')
        title = a.get_text()
        add_date = a.get('add_date')
        tags = a.get('tags', '')

        # Find next <DD> for notes
        notes = ''
        sibling = a.find_next_sibling()
        if sibling and sibling.name == 'dd':
            notes = sibling.get_text()

        bookmarks.append({
            'url': url,
            'title': title,
            'notes': notes,
            'tags': [t.strip() for t in tags.split(',') if t.strip()],
            'archived': False
        })
    return bookmarks

@click.command(name = "import")
@click.argument('filename', type=click.Path(exists=True))
def import_bookmarks(filename):
    """Import bookmarks from Netscape HTML format."""
    data = parse_netscape_html(filename)
    added = 0
    skipped = 0

    for item in data:
        url = item['url']
        if not url or not url.startswith(('http://', 'https://')):
            skipped += 1
            continue

        norm_url = normalize_url(url)
        url_hash = generate_url_hash(url)

        if Bookmark.query.filter_by(hash_url=url_hash).first():
            skipped += 1
            continue

        bookmark = Bookmark(url=norm_url, title=item['title'], notes=item['notes'], archived=item['archived'])
        bookmark.set_hash()
        bookmark.set_short_url()

        for tag_name in item['tags']:
            tag_name = tag_name.lower()
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            bookmark.tags.append(tag)

        db.session.add(bookmark)
        added += 1

    db.session.commit()
    click.echo(f"Imported {added} bookmarks, skipped {skipped} duplicates.")

if __name__ == '__main__':
    import_bookmarks()