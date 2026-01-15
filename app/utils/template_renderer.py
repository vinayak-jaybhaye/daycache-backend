from pathlib import Path


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_template(template_path: str, context: dict) -> str:
    template_file = TEMPLATES_DIR / template_path
    content = template_file.read_text()

    for key, value in context.items():
        content = content.replace(f"{{{{ {key} }}}}", str(value))

    return content
