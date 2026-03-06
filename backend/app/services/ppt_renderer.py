from pathlib import Path

from pptx import Presentation


def render_ppt(slides: list[dict], output_path: str, template_path: str | None = None) -> str:
    prs = Presentation(template_path) if template_path else Presentation()
    layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]

    for spec in slides:
        slide = prs.slides.add_slide(layout)
        if getattr(slide.shapes, "title", None):
            slide.shapes.title.text = spec["title"]

        if len(slide.placeholders) > 1:
            body = slide.placeholders[1].text_frame
        else:
            body = slide.shapes.add_textbox(1000000, 1500000, 8000000, 4000000).text_frame

        body.clear()
        for idx, bullet in enumerate(spec["bullets"]):
            p = body.paragraphs[0] if idx == 0 else body.add_paragraph()
            p.text = bullet
            p.level = 0

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return str(out)
