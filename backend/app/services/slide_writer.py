from app.models.domain import SlideSpec


def write_slides(slides: list[SlideSpec]) -> list[dict]:
    output: list[dict] = []
    for slide in slides:
        output.append(
            {
                "title": slide.title,
                "objective": slide.objective,
                "bullets": [b.strip()[:120] for b in slide.bullets if b.strip()][:5],
                "references": slide.references,
            }
        )
    return output
