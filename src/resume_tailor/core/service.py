"""Core resume tailoring service."""
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import re
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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

    @staticmethod
    def _validate_yaml_structure(data: Any, expected_keys: List[str]) -> bool:
        """Validate that parsed YAML has expected structure.

        Args:
            data: Parsed YAML data
            expected_keys: List of required top-level keys

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        for key in expected_keys:
            if key not in data:
                return False

        return True

    def _llm_call_with_retry(
        self,
        prompt: str,
        expected_keys: List[str],
        max_retries: int = 2,
        operation_name: str = "LLM call"
    ) -> Optional[Dict[str, Any]]:
        """Call LLM with validation and retry logic.

        Args:
            prompt: Prompt to send to LLM
            expected_keys: Expected top-level YAML keys
            max_retries: Maximum number of retry attempts
            operation_name: Name for logging purposes

        Returns:
            Parsed YAML dict if successful, None otherwise
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.llm.simple_completion(prompt)
                cleaned_response = self._clean_llm_output(response)
                data = yaml.safe_load(cleaned_response)

                # Validate structure
                if not self._validate_yaml_structure(data, expected_keys):
                    logger.warning(
                        f"{operation_name} attempt {attempt + 1}/{max_retries + 1}: "
                        f"Invalid YAML structure. Expected keys: {expected_keys}, got: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                    )
                    if attempt < max_retries:
                        console.print(f"[yellow]⚠[/yellow] Retrying {operation_name}...")
                        continue
                    return None

                return data

            except (yaml.YAMLError, AttributeError) as e:
                logger.warning(
                    f"{operation_name} attempt {attempt + 1}/{max_retries + 1}: "
                    f"Failed to parse YAML: {e}"
                )
                logger.debug(f"Raw response: {response if 'response' in locals() else 'N/A'}")

                if attempt < max_retries:
                    console.print(f"[yellow]⚠[/yellow] Retrying {operation_name}...")
                    continue

                return None

        return None

    def extract_jd_details(self, job_description: str) -> Dict[str, str]:
        """Extract company and role from job description."""
        console.print("[cyan]Extracting job details...[/cyan]")

        prompt = extract_jd_details_prompt(job_description)
        data = self._llm_call_with_retry(
            prompt,
            expected_keys=['company', 'role'],
            operation_name="job details extraction"
        )

        if data:
            company = data.get('company')
            role = data.get('role')
            console.print(f"[green]✓[/green] Company: {company}, Role: {role}")
            return {"company": company, "role": role}
        else:
            logger.warning("Failed to extract job details after retries")
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
        data = self._llm_call_with_retry(
            prompt,
            expected_keys=['keywords'],
            operation_name="keyword extraction"
        )

        if data:
            keywords = data.get('keywords', [])
            console.print(f"[green]✓[/green] Extracted {len(keywords)} keywords")
            return keywords
        else:
            logger.warning("Failed to extract keywords after retries")
            return []

    def _tailor_summary(self, job_description: str, current_summary: str) -> str:
        """Tailor the professional summary."""
        console.print("[cyan]Tailoring summary...[/cyan]")
        prompt = create_summary_prompt(job_description, current_summary)
        data = self._llm_call_with_retry(
            prompt,
            expected_keys=['summary'],
            operation_name="summary tailoring"
        )

        if data:
            summary_list = data.get('summary', [current_summary])
            if isinstance(summary_list, list) and summary_list:
                return summary_list[0]
            return current_summary
        else:
            logger.warning("Failed to tailor summary after retries, using original")
            return current_summary

    def _tailor_experience(self, job_description: str, current_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tailor the experience section."""
        console.print("[cyan]Tailoring experience...[/cyan]")
        tailored_experience = []
        for entry in current_experience:
            prompt = create_highlights_tailoring_prompt(job_description, entry)
            data = self._llm_call_with_retry(
                prompt,
                expected_keys=['highlights'],
                operation_name=f"highlights tailoring for {entry.get('company')}"
            )

            if data:
                new_highlights = data.get('highlights', entry.get('highlights', []))
                new_entry = entry.copy()
                new_entry['highlights'] = new_highlights
                tailored_experience.append(new_entry)
            else:
                logger.warning(f"Failed to tailor highlights for {entry.get('company')} after retries, using original")
                tailored_experience.append(entry)

        return tailored_experience

    def _tailor_skills(self, job_description: str, current_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tailor the skills section."""
        console.print("[cyan]Tailoring skills...[/cyan]")
        prompt = create_skills_tailoring_prompt(job_description, current_skills)
        data = self._llm_call_with_retry(
            prompt,
            expected_keys=['skills'],
            operation_name="skills tailoring"
        )

        if data:
            return data.get('skills', current_skills)
        else:
            logger.warning("Failed to tailor skills after retries, using original")
            return current_skills

    def _print_changes_summary(
        self,
        job_details: Dict[str, str],
        original_summary: str,
        tailored_summary: str,
        original_experience: List[Dict[str, Any]],
        tailored_experience: List[Dict[str, Any]],
        original_skills: List[Dict[str, Any]],
        tailored_skills: List[Dict[str, Any]],
        keywords: List[str]
    ) -> None:
        """Print keywords that will be bolded in the resume.

        Args:
            job_details: Extracted company and role
            original_summary: Original summary text
            tailored_summary: Tailored summary text
            original_experience: Original experience entries
            tailored_experience: Tailored experience entries
            original_skills: Original skills categories
            tailored_skills: Tailored skills categories
            keywords: Extracted keywords for bolding
        """
        console.print("\n" + "="*80)
        console.print("[bold cyan]📊 KEYWORDS TO BE EMPHASIZED[/bold cyan]", justify="center")
        console.print("="*80 + "\n")

        # Keywords
        if keywords:
            console.print(f"[bold]Extracted {len(keywords)} keywords for automatic bolding:[/bold]\n")

            # Display keywords in a nicely formatted way
            keywords_display = []
            for i, kw in enumerate(keywords, 1):
                keywords_display.append(f"  {i}. {kw}")

            console.print("\n".join(keywords_display))
            console.print("\n[dim]These terms will be automatically emphasized throughout your resume.[/dim]")
        else:
            console.print("[yellow]No keywords extracted.[/yellow]")

        console.print("\n" + "="*80 + "\n")

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

        # Extract job details for summary
        job_details = self.extract_jd_details(job_description.text)

        # Load base sections
        static_sections = self.template_mgr.load_static_sections()
        base_resume = self.template_mgr.load_base_resume()
        current_dynamic = self.template_mgr.extract_dynamic_sections(base_resume)

        # Store originals for comparison
        original_summary = current_dynamic.get('summary', [''])[0]
        original_experience = current_dynamic.get('experience', [])
        original_skills = current_dynamic.get('skills', [])

        # Tailor dynamic sections
        tailored_summary = self._tailor_summary(
            job_description.text,
            original_summary
        )
        tailored_experience = self._tailor_experience(
            job_description.text,
            original_experience
        )
        tailored_skills = self._tailor_skills(
            job_description.text,
            original_skills
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

        # Print changes summary
        self._print_changes_summary(
            job_details=job_details,
            original_summary=original_summary,
            tailored_summary=tailored_summary,
            original_experience=original_experience,
            tailored_experience=tailored_experience,
            original_skills=original_skills,
            tailored_skills=tailored_skills,
            keywords=bold_keywords
        )

        return output_path
