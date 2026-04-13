"""Gallery HTML rendering."""

import json
import re
from pathlib import Path
from datetime import datetime
from .schema import Gallery


def get_gallery_template() -> str:
    """Load the gallery HTML template from data/gallery-template.html."""
    template_path = Path(__file__).parent.parent.parent / "data" / "gallery-template.html"
    if not template_path.exists():
        raise FileNotFoundError(
            f"Gallery template not found at {template_path}. "
            "Please ensure data/gallery-template.html exists."
        )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_gallery(gallery: Gallery) -> str:
    """
    Render a Gallery to a self-contained HTML file.
    
    Loads the template and injects gallery data at the GALLERY_DATA marker.
    All rendering logic (stats, sidebar, chips, refs) is handled client-side.
    """
    template = get_gallery_template()
    
    # Convert gallery to JSON for injection
    gallery_json = json.dumps(gallery.to_dict())
    
    # Inject data at the GALLERY_DATA marker
    html = re.sub(
        r'/\*GALLERY_DATA\*/.*?/\*END_GALLERY_DATA\*/',
        f'/*GALLERY_DATA*/{gallery_json}/*END_GALLERY_DATA*/',
        template,
        flags=re.DOTALL
    )
    
    # Replace title placeholder
    html = html.replace('{{CONCEPT}}', escape_html(gallery.concept))
    
    return html


def save_gallery(gallery: Gallery, output_path: Path) -> Path:
    """
    Save a rendered gallery to a file.
    
    Returns the path to the saved file.
    """
    html = render_gallery(gallery)
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return output_path


def get_default_output_path(concept: str) -> Path:
    """
    Get the default output path for a gallery.
    
    Outputs to .uir-output/ in the current working directory.
    """
    # Sanitize concept for filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in concept)
    safe_name = safe_name.strip().replace(" ", "-").lower()[:50]
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{safe_name}.html"
    
    output_dir = Path.cwd() / ".uir-output"
    return output_dir / filename
