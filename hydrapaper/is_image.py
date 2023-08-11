from pathlib import Path

IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg',
    '.png',
    '.tiff',
    # '.svg'
]


def is_image(p):
    p = Path(p)
    return (
        p.suffix.lower() in IMAGE_EXTENSIONS and
        p.exists() and
        not p.is_dir()
    )
