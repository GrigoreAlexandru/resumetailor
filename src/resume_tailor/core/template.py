"""Template management for resume YAML merging."""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from ..config.schemas import RendererConfig

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages resume template assembly."""

    def __init__(
        self,
        static_sections_path: Optional[Path] = None,
        base_resume_path: Optional[Path] = None
    ):
        """Initialize template manager.

        Args:
            static_sections_path: Path to static sections YAML
            base_resume_path: Path to full base resume YAML
        """
        self.static_sections_path = static_sections_path
        self.base_resume_path = base_resume_path
        self._static_data: Optional[Dict[str, Any]] = None
        self._base_data: Optional[Dict[str, Any]] = None

    def load_static_sections(self) -> Dict[str, Any]:
        """Load static resume sections from YAML.

        Returns:
            Parsed YAML data
        """
        if self._static_data is not None:
            return self._static_data

        if not self.static_sections_path or not self.static_sections_path.exists():
            logger.warning("Static sections file not found, using empty dict")
            self._static_data = {}
            return self._static_data

        with open(self.static_sections_path, 'r', encoding='utf-8') as f:
            self._static_data = yaml.safe_load(f) or {}

        logger.info(f"Loaded static sections from {self.static_sections_path}")
        return self._static_data

    def load_base_resume(self) -> Dict[str, Any]:
        """Load full base resume.

        Returns:
            Complete base resume data
        """
        if self._base_data is not None:
            return self._base_data

        if not self.base_resume_path or not self.base_resume_path.exists():
            raise FileNotFoundError(f"Base resume not found: {self.base_resume_path}")

        with open(self.base_resume_path, 'r', encoding='utf-8') as f:
            self._base_data = yaml.safe_load(f)

        logger.info(f"Loaded base resume from {self.base_resume_path}")
        return self._base_data

    def extract_dynamic_sections(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only the dynamic sections from resume.

        Args:
            resume_data: Full resume YAML data

        Returns:
            Dict with only experience, skills, summary
        """
        cv_data = resume_data.get('cv', {})
        sections = cv_data.get('sections', {})

        dynamic = {}

        # Extract experience
        if 'experience' in sections:
            dynamic['experience'] = sections['experience']

        # Extract skills
        if 'skills' in sections:
            dynamic['skills'] = sections['skills']

        # Extract summary
        if 'summary' in sections:
            dynamic['summary'] = sections['summary']

        return dynamic

    def merge_sections(
        self,
        static_sections: Dict[str, Any],
        dynamic_sections: Dict[str, Any],
        bold_keywords: Optional[List[str]] = None,
        renderer_config: Optional[RendererConfig] = None,
        base_design: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Merge static and dynamic sections into complete resume.

        Args:
            static_sections: Name, email, education, etc.
            dynamic_sections: Experience, skills, summary
            bold_keywords: Keywords to automatically bold
            renderer_config: RenderCV design configuration
            base_design: Design section from base resume (optional)

        Returns:
            Complete resume YAML structure for RenderCV
        """
        # Start with static sections, but create a new sections dictionary
        # to control the order.
        resume: Dict[str, Any] = {
            'cv': {
                **static_sections.get('cv', {}),
                'sections': {}
            }
        }

        # Merge dynamic sections in the desired order
        cv_sections = resume['cv']['sections']

        if 'summary' in dynamic_sections:
            cv_sections['summary'] = dynamic_sections['summary']

        if 'skills' in dynamic_sections:
            cv_sections['skills'] = dynamic_sections['skills']

        if 'experience' in dynamic_sections:
            cv_sections['experience'] = dynamic_sections['experience']

        # Add the rest of the static sections
        static_cv_sections = static_sections.get('cv', {}).get('sections', {})
        for key, value in static_cv_sections.items():
            if key not in cv_sections:
                cv_sections[key] = value

        # Add rendercv_settings
        if bold_keywords or renderer_config:
            resume['rendercv_settings'] = {}

            if bold_keywords:
                resume['rendercv_settings']['bold_keywords'] = bold_keywords

            if renderer_config:
                resume['rendercv_settings']['render_command'] = {
                    'output_folder_name': renderer_config.output_folder,
                }

        # Add design section - prefer base_design if provided, otherwise use renderer_config
        if base_design:
            resume['design'] = base_design
        elif renderer_config:
            resume['design'] = {
                'theme': renderer_config.theme,
                **renderer_config.design_overrides
            }

        return resume

    def save_yaml(self, data: Dict[str, Any], output_path: Path) -> None:
        """Save resume data to YAML file.

        Args:
            data: Resume data
            output_path: Where to save
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )

        logger.info(f"Saved resume YAML to {output_path}")
