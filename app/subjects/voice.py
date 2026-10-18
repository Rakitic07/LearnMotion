from .music_catalog import build_music_subject
from ._subject_coverage import additions as _coverage_additions

CATEGORIES, TOPICS, SCENARIOS = build_music_subject("voice")
TOPICS += _coverage_additions("voice")
