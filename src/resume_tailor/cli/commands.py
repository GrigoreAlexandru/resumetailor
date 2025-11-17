"""Typer CLI commands."""
from datetime import datetime
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from ..config.settings import settings, LLMProvider
from ..config.schemas import JobDescription, RendererConfig
from ..core.service import ResumeService
from ..core.template import TemplateManager
from ..llm.ollama import OllamaProvider
from ..llm.gemini import GeminiLLM
from ..llm.mock import MockProvider
from ..renderer.rendercv import RenderCVRenderer

app = typer.Typer(
    name="resume-tailor",
    help="AI-powered resume tailoring using RenderCV",
    add_completion=False
)
console = Console()


def create_service(
    llm_model: str,
    base_resume: Path,
    static_sections: Optional[Path] = None,
) -> ResumeService:
    """Factory to create configured ResumeService.

    Args:
        llm_model: LLM model name
        base_resume: Path to base resume
        static_sections: Path to static sections

    Returns:
        Configured ResumeService
    """
    # Initialize LLM provider based on settings
    if settings.llm_provider == LLMProvider.OLLAMA:
        llm = OllamaProvider(
            model=llm_model,
            temperature=settings.llm_temperature,
            base_url=settings.llm_base_url
        )
    elif settings.llm_provider == LLMProvider.GEMINI:
        llm = GeminiLLM(
            model=llm_model,
            temperature=settings.llm_temperature
        )
    # Basic mock provider handling for testing, can be expanded
    elif settings.llm_provider.value == "mock":
        llm = MockProvider(model=llm_model)
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    # Initialize template manager
    template_mgr = TemplateManager(
        static_sections_path=static_sections,
        base_resume_path=base_resume
    )

    # Renderer config
    renderer_config = RendererConfig(
        theme=settings.rendercv_theme,
        output_folder=str(settings.output_dir)
    )

    return ResumeService(
        llm_provider=llm,
        template_manager=template_mgr,
        renderer_config=renderer_config
    )


@app.command()
def generate(
    job_description: Path = typer.Argument(
        ...,
        help="Path to job description text file",
        exists=True,
        dir_okay=False
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (default: generated from name, company, and date)"
    ),
    base_resume: Optional[Path] = typer.Option(
        None,
        "--base-resume",
        help="Path to base resume YAML"
    ),
    static_sections: Optional[Path] = typer.Option(
        None,
        "--static-sections",
        help="Path to static sections YAML"
    ),
    llm_model: str = typer.Option(
        settings.llm_model,
        "--model", "-m",
        help="LLM model to use"
    ),
    theme: str = typer.Option(
        settings.rendercv_theme,
        "--theme", "-t",
        help="RenderCV theme"
    ),
    render: bool = typer.Option(
        True,
        "--render/--no-render",
        help="Automatically render PDF"
    ),
) -> None:
    """Generate tailored resume for a job description.

    Example:
        resume-tailor generate job_description.txt
        resume-tailor generate job.txt -o ./resumes/google --model gemini-1.5-flash
    """
    # Determine paths
    resume_path = base_resume or settings.base_resume_path
    static_path = static_sections or settings.static_sections_path

    # Initialize service
    service = create_service(
        llm_model=llm_model,
        base_resume=resume_path,
        static_sections=static_path,
    )

    # Load JD and extract details
    try:
        jd_text = job_description.read_text(encoding='utf-8')
        details = service.extract_jd_details(jd_text)
        jd = JobDescription(text=jd_text, **details)
    except FileNotFoundError:
        console.print(f"[red]Error: Job description file not found at {job_description}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(1)

    # Determine output directory
    if output:
        output_dir = output
    else:
        static_sections_data = service.template_mgr.load_static_sections()
        user_name = static_sections_data.get('cv', {}).get('name', 'Default_User')
        company_name = jd.company or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        dir_name = f"{user_name.replace(' ', '_')}_{company_name.replace(' ', '_')}_{timestamp}"
        output_dir = settings.output_dir / dir_name

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate tailored resume (pass details to avoid duplicate API call)
    yaml_output = output_dir / "tailored_resume.yaml"
    service.generate_tailored_resume(jd, yaml_output, job_details=details)

    # Render if requested
    if render:
        renderer = RenderCVRenderer()
        renderer.render(yaml_output, output_folder=output_dir, pdf_only=False)

        # Show results
        console.print(f"\n[bold green]✓ Resume generated successfully![/bold green]")
        console.print(f"[green]Output:[/green] {output_dir}")


@app.command()
def batch(
    jobs_dir: Path = typer.Argument(
        ...,
        help="Directory containing job description .txt files",
        exists=True,
        file_okay=False
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Base output directory"
    ),
    base_resume: Optional[Path] = typer.Option(
        None,
        "--base-resume",
        help="Path to base resume YAML"
    ),
    llm_model: str = typer.Option(
        settings.llm_model,
        "--model", "-m",
        help="LLM model"
    ),
) -> None:
    """Batch generate resumes for multiple job descriptions.

    Creates a separate folder for each job description.

    Example:
        resume-tailor batch ./job_descriptions -o ./output
    """
    base_resume = base_resume or settings.base_resume_path
    output_base = output or Path("./batch_output")

    # Find all .txt files
    job_files = list(jobs_dir.glob("*.txt"))

    if not job_files:
        console.print(f"[red]No .txt files found in {jobs_dir}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Found {len(job_files)} job descriptions[/bold]\n")

    # Process each
    for i, job_file in enumerate(job_files, 1):
        console.print(f"\n[bold cyan]═══ Job {i}/{len(job_files)}: {job_file.name} ═══[/bold cyan]")

        job_output = output_base / job_file.stem

        # Use generate command logic
        try:
            jd = JobDescription.from_file(str(job_file))
            service = create_service(llm_model, base_resume)
            service.renderer_config.output_folder = str(job_output)

            yaml_output = job_output / "tailored_resume.yaml"
            service.generate_tailored_resume(jd, yaml_output)

            renderer = RenderCVRenderer()
            renderer.render(yaml_output, output_folder=job_output, pdf_only=True)

        except Exception as e:
            console.print(f"[red]✗ Failed: {e}[/red]")
            continue

    console.print(f"\n[bold green]✓ Batch processing complete![/bold green]")
    console.print(f"Resumes saved to: {output_base}")


@app.command()
def init(
    name: str = typer.Argument(..., help="Your full name"),
) -> None:
    """Initialize a new base resume template.

    Creates example YAML files to get started.

    Example:
        resume-tailor init "John Doe"
    """
    # Try using RenderCV's CLI to generate a starter. If that fails (some
    # rendercv releases expose a different import layout and the entrypoint
    # script can error), fall back to writing a minimal starter YAML file.
    console.print(f"[cyan]Creating starter resume for {name}...[/cyan]")

    import subprocess
    try:
        result = subprocess.run(
            ["rendercv", "new", name],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        result = None

    if result is not None and result.returncode == 0:
        console.print(f"[green]✓[/green] Created {name.replace(' ', '_')}_CV.yaml")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the YAML file with your information")
        console.print("2. Run: [cyan]resume-tailor generate job_description.txt[/cyan]")
        return

    # Fallback: create a minimal starter YAML in the current working dir
    out_name = f"{name.replace(' ', '_')}_CV.yaml"
    out_path = Path.cwd() / out_name

    if out_path.exists():
        console.print(f"[yellow]File already exists:[/yellow] {out_path}")
        console.print("Open and edit it to add your information.")
        raise typer.Exit()

    yaml_content = (
        f"cv:\n  name: {name}\n\n"
        f"design:\n  theme: {settings.rendercv_theme}\n\n"
        "cv_template:\n  sections:\n    - experience: []\n    - skills: []\n    - education: []\n"
    )

    try:
        out_path.write_text(yaml_content)
        console.print(f"[green]✓[/green] Created starter YAML: {out_path}")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the YAML file with your information")
        console.print("2. Run: [cyan]resume-tailor generate job_description.txt[/cyan]")
        if result is not None and result.stderr:
            console.print(f"\n[dim]Note: rendercv reported: {result.stderr.strip()}[/dim]")
    except Exception as e:
        console.print(f"[red]Failed to write starter file: {e}[/red]")


@app.command()
def original(
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (default: ./output/original)"
    ),
    base_resume: Optional[Path] = typer.Option(
        None,
        "--base-resume",
        help="Path to base resume YAML"
    ),
    static_sections: Optional[Path] = typer.Option(
        None,
        "--static-sections",
        help="Path to static sections YAML"
    ),
) -> None:
    """Render original base resume without LLM tailoring.

    Useful for testing design changes and verifying base resume formatting.

    Example:
        resume-tailor original
        resume-tailor original -o ./test_design
    """
    # Determine paths
    resume_path = base_resume or settings.base_resume_path
    static_path = static_sections or settings.static_sections_path

    # Initialize template manager
    template_mgr = TemplateManager(
        static_sections_path=static_path,
        base_resume_path=resume_path
    )

    console.print("\n[bold]Rendering original base resume (no LLM tailoring)[/bold]\n")

    # Load sections
    static_sections_data = template_mgr.load_static_sections()
    base_resume_data = template_mgr.load_base_resume()
    dynamic_sections = template_mgr.extract_dynamic_sections(base_resume_data)

    # Extract design from base resume if present
    base_design = base_resume_data.get('design')

    # Determine output directory
    if output:
        output_dir = output
    else:
        output_dir = settings.output_dir / "original"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Merge sections without LLM processing
    renderer_config = RendererConfig(
        theme=settings.rendercv_theme,
        output_folder=str(output_dir)
    )

    complete_resume = template_mgr.merge_sections(
        static_sections=static_sections_data,
        dynamic_sections=dynamic_sections,
        bold_keywords=[],  # No keywords for original
        renderer_config=renderer_config,
        base_design=base_design
    )

    # Save
    yaml_output = output_dir / "original_resume.yaml"
    template_mgr.save_yaml(complete_resume, yaml_output)
    console.print(f"[green]✓[/green] Original resume YAML saved to: {yaml_output}")

    # Render with RenderCV
    renderer = RenderCVRenderer()
    renderer.render(yaml_output, output_folder=output_dir, pdf_only=False)

    console.print(f"\n[bold green]✓ Original resume rendered successfully![/bold green]")
    console.print(f"[green]Output:[/green] {output_dir}")


@app.command()
def info() -> None:
    """Show configuration and system information."""
    table = Table(title="Resume Tailor Configuration")

    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("LLM Provider", settings.llm_provider.value)
    table.add_row("LLM Model", settings.llm_model)
    table.add_row("Temperature", str(settings.llm_temperature))
    table.add_row("Base Resume", str(settings.base_resume_path))
    table.add_row("Output Dir", str(settings.output_dir))
    table.add_row("Theme", settings.rendercv_theme)

    console.print(table)

    # Check RenderCV
    try:
        RenderCVRenderer()
        console.print("\n[green]✓[/green] RenderCV is installed")
    except RuntimeError as e:
        console.print(f"\n[red]✗[/red] {e}")


if __name__ == "__main__":
    app()
