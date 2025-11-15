"""Tests for configuration schemas."""
from pathlib import Path
import pytest
from resume_tailor.config.schemas import (
    ExperienceEntry,
    SkillCategory,
    JobDescription,
    RendererConfig
)


def test_experience_entry_creation() -> None:
    """Test creating experience entry."""
    entry = ExperienceEntry(
        company="Test Corp",
        position="Engineer",
        start_date="2020-01",
        highlights=["Did something", "  ", "Did more"]
    )

    assert entry.company == "Test Corp"
    assert len(entry.highlights) == 2  # Empty string filtered out


def test_skill_category_creation() -> None:
    """Test creating skill category."""
    skill = SkillCategory(
        label="Languages",
        details="Python, Go, JavaScript"
    )

    assert skill.label == "Languages"
    assert "Python" in skill.details


def test_renderer_config_defaults() -> None:
    """Test renderer config defaults."""
    config = RendererConfig()

    assert config.theme == "engineeringresumes"
    assert config.output_folder == "./output"


def test_job_description_from_file(tmp_path: Path) -> None:
    """Test loading job description from file."""
    jd_file = tmp_path / "job.txt"
    jd_file.write_text("Senior Engineer position\nRequires Python")

    jd = JobDescription.from_file(str(jd_file))

    assert "Senior Engineer" in jd.text
    assert "Python" in jd.text
