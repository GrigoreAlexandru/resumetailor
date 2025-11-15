"""Core resume tailoring service."""
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import re
import yaml
from rich.console import Console

from ..config.schemas import JobDescription, RendererConfig
from ..llm.base import BaseLLMProvider
from ..llm.prompts import (
    create_summary_prompt,
    create_highlights_tailoring_prompt,
    create_skills_tailoring_prompt,
    extract_keywords_prompt,
    extract_jd_details_prompt
)
from .template import TemplateManager

logger = logging.getLogger(__name__)
console = Console()


class ResumeService:
    """Main service for resume tailoring operations."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        template_manager: TemplateManager,
        renderer_config: Optional[RendererConfig] = None
    ):
        """Initialize service.

        Args:
            llm_provider: LLM provider instance
            template_manager: Template manager instance
            renderer_config: RenderCV configuration
        """
        self.llm = llm_provider
        self.template_mgr = template_manager
        self.renderer_config = renderer_config or RendererConfig()

    @staticmethod
    def _clean_llm_output(content: str) -> str:
        """Strips markdown code fences from LLM output."""
        match = re.search(r"```(yaml)?\n(.*)```", content, re.DOTALL)
        if match:
            content = match.group(2)

        return content.strip()

    def extract_jd_details(self, job_description: str) -> Dict[str, str]:
        """Extract company and role from job description."""
        console.print("[cyan]Extracting job details...[/cyan]")

        prompt = extract_jd_details_prompt(job_description)
        response = self.llm.simple_completion(prompt)

        try:
            cleaned_response = self._clean_llm_output(response)
            data = yaml.safe_load(cleaned_response)
            company = data.get('company')
            role = data.get('role')
            console.print(f"[green]✓[/green] Company: {company}, Role: {role}")
            return {"company": company, "role": role}
        except (yaml.YAMLError, AttributeError) as e:
            logger.warning(f"Failed to parse job details: {e}")
            logger.debug(f"Raw job details response: {response}")
            return {}

    def extract_keywords(self, job_description: str) -> List[str]:
        """Extract key terms from job description.

        Args:
            job_description: Job posting text

        Returns:
            List of keywords
        """
        console.print("[cyan]Extracting keywords from job description...[/cyan]")

        prompt = extract_keywords_prompt(job_description)
        response = self.llm.simple_completion(prompt)

        try:
            # Clean and parse YAML response
            cleaned_response = self._clean_llm_output(response)
            data = yaml.safe_load(cleaned_response)
            keywords = data.get('keywords', [])
            console.print(f"[green]✓[/green] Extracted {len(keywords)} keywords")
            return keywords
        except (yaml.YAMLError, AttributeError) as e:
            logger.warning(f"Failed to parse keywords: {e}")
            logger.debug(f"Raw keyword response: {response}")
            return []

    def _tailor_summary(self, job_description: str, current_summary: str) -> str:
        """Tailor the professional summary."""
        console.print("[cyan]Tailoring summary...[/cyan]")
        prompt = create_summary_prompt(job_description, current_summary)
        response = self.llm.simple_completion(prompt)
        try:
            cleaned_response = self._clean_llm_output(response)
            data = yaml.safe_load(cleaned_response)
            return data.get('summary', [current_summary])[0]
        except (yaml.YAMLError, AttributeError) as e:
            logger.warning(f"Failed to parse tailored summary: {e}")
            return current_summary

    def _tailor_experience(self, job_description: str, current_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tailor the experience section."""
        console.print("[cyan]Tailoring experience...[/cyan]")
        tailored_experience = []
        for entry in current_experience:
            prompt = create_highlights_tailoring_prompt(job_description, entry)
            response = self.llm.simple_completion(prompt)
            try:
                cleaned_response = self._clean_llm_output(response)
                data = yaml.safe_load(cleaned_response)
                new_highlights = data.get('highlights', entry.get('highlights', []))
                new_entry = entry.copy()
                new_entry['highlights'] = new_highlights
                tailored_experience.append(new_entry)
            except (yaml.YAMLError, AttributeError) as e:
                logger.warning(f"Failed to parse tailored highlights for {entry.get('company')}: {e}")
                tailored_experience.append(entry)
        return tailored_experience

    def _tailor_skills(self, job_description: str, current_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tailor the skills section."""
        console.print("[cyan]Tailoring skills...[/cyan]")
        prompt = create_skills_tailoring_prompt(job_description, current_skills)
        response = self.llm.simple_completion(prompt)
        try:
            cleaned_response = self._clean_llm_output(response)
            data = yaml.safe_load(cleaned_response)
            return data.get('skills', current_skills)
        except (yaml.YAMLError, AttributeError) as e:
            logger.warning(f"Failed to parse tailored skills: {e}")
            return current_skills

    def generate_tailored_resume(
        self,
        job_description: JobDescription,
        output_path: Path,
    ) -> Path:
        """Complete workflow: tailor resume for job description.

        Args:
            job_description: Job to tailor for
            output_path: Where to save tailored YAML

        Returns:
            Path to saved YAML
        """
        console.print(f"\n[bold]Tailoring resume for: {job_description.role or 'position'}[/bold]\n")

        # Load base sections
        static_sections = self.template_mgr.load_static_sections()
        base_resume = self.template_mgr.load_base_resume()
        current_dynamic = self.template_mgr.extract_dynamic_sections(base_resume)

        # Tailor dynamic sections
        tailored_summary = self._tailor_summary(
            job_description.text,
            current_dynamic.get('summary', [''])[0]
        )
        tailored_experience = self._tailor_experience(
            job_description.text,
            current_dynamic.get('experience', [])
        )
        tailored_skills = self._tailor_skills(
            job_description.text,
            current_dynamic.get('skills', [])
        )

        tailored_dynamic = {
            "summary": [tailored_summary],
            "skills": tailored_skills,
            "experience": tailored_experience,
        }

        # Extract bold keywords
        bold_keywords = self.extract_keywords(job_description.text)

        # Extract design from base_resume if present
        base_design = base_resume.get('design')

        # Merge everything
        complete_resume = self.template_mgr.merge_sections(
            static_sections=static_sections,
            dynamic_sections=tailored_dynamic,
            bold_keywords=bold_keywords,
            renderer_config=self.renderer_config,
            base_design=base_design
        )

        # Save
        self.template_mgr.save_yaml(complete_resume, output_path)
        console.print(f"\n[green]✓[/green] Tailored resume saved to: {output_path}")

        return output_path
