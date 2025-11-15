"""RenderCV wrapper for PDF generation."""
import subprocess
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class RenderCVRenderer:
    """Wrapper around RenderCV CLI."""

    def __init__(self, rendercv_cmd: str = "rendercv"):
        """Initialize renderer.

        Args:
            rendercv_cmd: Command to invoke rendercv (default: "rendercv")
        """
        self.cmd = rendercv_cmd
        self._check_installation()

    def _check_installation(self) -> None:
        """Verify RenderCV is installed."""
        try:
            result = subprocess.run(
                [self.cmd, "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise RuntimeError("RenderCV not found in PATH")
            logger.info(f"RenderCV available: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                "RenderCV not installed. Install with: pip install 'rendercv'"
            )

    def render(
        self,
        yaml_path: Path,
        output_folder: Optional[Path] = None,
        pdf_only: bool = False
    ) -> Path:
        """Render resume YAML to PDF (and other formats).

        Args:
            yaml_path: Path to resume YAML file
            output_folder: Custom output folder (default: same as YAML)
            pdf_only: If True, skip HTML/Markdown/PNG generation

        Returns:
            Path to output directory
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Resume YAML not found: {yaml_path}")

        console.print(f"\n[cyan]Rendering resume with RenderCV...[/cyan]")

        # Build command
        cmd = [self.cmd, "render", str(yaml_path)]

        if output_folder:
            cmd.extend(["--output-folder-name", str(output_folder)])

        if pdf_only:
            cmd.extend([
                "--dont-generate-html",
                "--dont-generate-markdown",
                "--dont-generate-png"
            ])

        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            logger.debug(f"RenderCV stdout: {result.stdout}")

            # Determine output path
            if output_folder:
                out_path = output_folder
            else:
                # RenderCV default: rendercv_output in same dir as YAML
                out_path = yaml_path.parent / "rendercv_output"

            console.print(f"[green]✓[/green] Resume rendered successfully")
            console.print(f"[dim]Output: {out_path}[/dim]")

            return out_path

        except subprocess.CalledProcessError as e:
            logger.error(f"RenderCV failed: {e.stderr}")
            console.print(f"[red]✗[/red] RenderCV rendering failed")
            console.print(f"[red]{e.stderr}[/red]")
            raise RuntimeError(f"RenderCV failed: {e.stderr}") from e

    def render_watch(self, yaml_path: Path) -> None:
        """Start RenderCV in watch mode for live preview.

        Args:
            yaml_path: Resume YAML to watch
        """
        console.print(f"[cyan]Starting RenderCV watch mode...[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        cmd = [self.cmd, "render", str(yaml_path), "--watch"]

        try:
            subprocess.run(cmd, cwd=yaml_path.parent)
        except KeyboardInterrupt:
            console.print("\n[yellow]Watch mode stopped[/yellow]")
