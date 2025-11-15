"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
from typing import Dict, Any, List


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description text."""
    return """
Senior Software Engineer - Backend

Requirements:
- 5+ years Python experience
- Kubernetes and Docker
- PostgreSQL and Redis
- AWS or GCP experience

Responsibilities:
- Build scalable microservices
- Mentor junior engineers
- Optimize database performance
"""


@pytest.fixture
def sample_experience() -> List[Dict[str, Any]]:
    """Sample experience entries."""
    return [
        {
            'company': 'Tech Corp',
            'position': 'Senior Engineer',
            'start_date': '2020-01',
            'highlights': [
                'Led team of 5 engineers',
                'Improved performance by 40%'
            ]
        }
    ]


@pytest.fixture
def sample_skills() -> List[Dict[str, Any]]:
    """Sample skills."""
    return [
        {'label': 'Languages', 'details': 'Python, Go, JavaScript'},
        {'label': 'Infrastructure', 'details': 'Docker, Kubernetes, AWS'}
    ]


@pytest.fixture
def temp_yaml_files(tmp_path: Path) -> tuple[Path, Path]:
    """Create temporary YAML files for testing.

    Returns:
        Tuple of (static_sections_path, base_resume_path)
    """
    # Create static sections
    static_yaml = tmp_path / "static.yaml"
    static_yaml.write_text("""cv:
  name: Test User
  email: test@example.com
  sections:
    education:
      - institution: Test University
        degree: BS
""")

    # Create base resume
    base_yaml = tmp_path / "base.yaml"
    base_yaml.write_text("""cv:
  name: Test User
  sections:
    experience:
      - company: Test Co
        position: Engineer
        start_date: "2020-01"
        highlights:
          - Did something
    skills:
      - label: Languages
        details: Python
""")

    return static_yaml, base_yaml
