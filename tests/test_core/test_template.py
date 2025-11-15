"""Tests for template manager."""
import pytest
from pathlib import Path
from resume_tailor.core.template import TemplateManager
from resume_tailor.config.schemas import RendererConfig


def test_load_static_sections(temp_yaml_files: tuple[Path, Path]) -> None:
    """Test loading static sections."""
    static_path, base_path = temp_yaml_files
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=base_path
    )

    data = template_mgr.load_static_sections()

    assert 'cv' in data
    assert data['cv']['name'] == 'Test User'
    assert 'education' in data['cv']['sections']


def test_load_base_resume(temp_yaml_files: tuple[Path, Path]) -> None:
    """Test loading base resume."""
    static_path, base_path = temp_yaml_files
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=base_path
    )

    data = template_mgr.load_base_resume()

    assert 'cv' in data
    assert 'experience' in data['cv']['sections']
    assert 'skills' in data['cv']['sections']


def test_extract_dynamic_sections(temp_yaml_files: tuple[Path, Path]) -> None:
    """Test extracting dynamic sections."""
    static_path, base_path = temp_yaml_files
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=base_path
    )

    base = template_mgr.load_base_resume()
    dynamic = template_mgr.extract_dynamic_sections(base)

    assert 'experience' in dynamic
    assert 'skills' in dynamic
    assert len(dynamic['experience']) == 1


def test_merge_sections(temp_yaml_files: tuple[Path, Path]) -> None:
    """Test merging static and dynamic sections."""
    static_path, base_path = temp_yaml_files
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=base_path
    )

    static = template_mgr.load_static_sections()
    dynamic = {'experience': [], 'skills': []}
    bold_keywords = ['Python', 'Go']

    config = RendererConfig(theme='classic')

    result = template_mgr.merge_sections(static, dynamic, bold_keywords, config)

    assert 'cv' in result
    assert 'rendercv_settings' in result
    assert result['rendercv_settings']['bold_keywords'] == bold_keywords
    assert 'design' in result
    assert result['design']['theme'] == 'classic'


def test_save_yaml(temp_yaml_files: tuple[Path, Path], tmp_path: Path) -> None:
    """Test saving YAML file."""
    static_path, base_path = temp_yaml_files
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=base_path
    )

    output_path = tmp_path / "output" / "test.yaml"
    test_data = {'cv': {'name': 'Test'}}

    template_mgr.save_yaml(test_data, output_path)

    assert output_path.exists()
    assert 'Test' in output_path.read_text()
