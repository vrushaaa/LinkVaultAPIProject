import click
from app import db
from app.models.bookmark import Bookmark
from datetime import datetime

def generate_netscape_html(bookmarks):
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">",
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>"
    ]

    for b in bookmarks:
        tags = ",".join(t.name for t in b.tags) if b.tags else ""
        add_date = int(b.created_at.timestamp()) if b.created_at else 0
        lines.append(f"    <DT><A HREF=\"{b.url}\" ADD_DATE=\"{add_date}\" TAGS=\"{tags}\">{b.title or b.url}</A>")
        if b.notes:
            lines.append(f"    <DD>{b.notes}")

    lines.append("</DL><p>")
    return "\n".join(lines)

@click.command(name = "export")
@click.argument('filename', type=click.Path())
def export(filename):
    """Export bookmarks to Netscape HTML format."""
    bookmarks = Bookmark.query.order_by(Bookmark.created_at.desc()).all()
    html = generate_netscape_html(bookmarks)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    click.echo(f"Exported {len(bookmarks)} bookmarks to {filename}")

if __name__ == '__main__':
    export()