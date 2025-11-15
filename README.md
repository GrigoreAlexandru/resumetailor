# Resume Tailor

AI-powered resume tailoring using RenderCV and local LLMs. Generate customized resumes for specific job descriptions while maintaining full control over your data.

## Features

- **Multiple LLM Providers**: Supports both local (Ollama) and cloud (Google Gemini) LLMs
- **RenderCV Powered**: Professional PDF generation with multiple themes
- **Bold Emphasis**: Automatically emphasizes key achievements and technologies
- **Modular Architecture**: Swap LLM providers, customize prompts, extend easily
- **Batch Processing**: Generate resumes for multiple jobs at once
- **Fully Customizable**: Control every aspect of resume generation

## Quick Start

### Prerequisites

- Python 3.10 or higher
- **LLM Provider** (choose one or both):
  - [Ollama](https://ollama.com/) for local/privacy-focused LLM
  - [Google Gemini API key](https://aistudio.google.com/app/apikey) for cloud-based LLM
- A LaTeX distribution (for RenderCV PDF generation)

### Installation

#### Option 1: Using uv (Recommended - Faster)

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-tailor.git
cd resume-tailor

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with uv
uv pip install -e ".[dev]"

# Install Ollama and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

#### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-tailor.git
cd resume-tailor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install Ollama and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

### Initialize Your Resume

```bash
# Create a starter resume template
resume-tailor init "Your Name"

# This creates Your_Name_CV.yaml - edit it with your information
```

Or copy the template files from `examples/` to `source/` directory:

```bash
# Copy templates to source directory (your personal resume data)
cp -r examples/* source/
# Then edit source/base_resume.yaml and source/static_sections.yaml with your information
```

**Note**: The `source/` directory is gitignored to protect your personal information.

### Generate Tailored Resume

```bash
# Single job description
resume-tailor generate source/job_descriptions/senior_backend.txt

# Custom output location
resume-tailor generate job.txt -o ./resumes/google

# Use different model
resume-tailor generate job.txt --model mistral:7b

# Use different theme
resume-tailor generate job.txt --theme classic

# Skip PDF rendering (YAML only)
resume-tailor generate job.txt --no-render
```

### Batch Processing

```bash
# Process multiple job descriptions at once
resume-tailor batch ./job_descriptions/ -o ./output
```

### Render Original Resume (No LLM)

```bash
# Render your base resume without any LLM tailoring
# Useful for testing design changes quickly
resume-tailor original

# Custom output location
resume-tailor original -o ./test_design

# Renders: output/original/original_resume.yaml and PDF
```

### Check Configuration

```bash
# View current settings
resume-tailor info
```

## How It Works

1. **Load Base Resume**: Your master resume with all experience and skills
2. **Extract Keywords**: LLM analyzes job description for key terms
3. **Tailor Sections**: LLM rewrites experience/skills to emphasize relevant points
4. **Add Bold Emphasis**: Automatically bolds key achievements and technologies
5. **Merge & Render**: Combines tailored sections with static info, generates PDF

## Project Structure

```
resume-tailor/
├── src/resume_tailor/
│   ├── cli/                # Command-line interface
│   │   └── commands.py     # Typer CLI commands
│   ├── core/               # Business logic
│   │   ├── service.py      # Main orchestrator
│   │   └── template.py     # YAML merging
│   ├── llm/                # LLM abstraction
│   │   ├── base.py         # Abstract interface
│   │   ├── ollama.py       # Ollama implementation
│   │   ├── gemini.py       # Google Gemini implementation
│   │   ├── mock.py         # Mock provider for testing
│   │   └── prompts.py      # Prompt templates
│   ├── renderer/           # PDF generation
│   │   └── rendercv.py     # RenderCV wrapper
│   ├── config/             # Configuration
│   │   ├── schemas.py      # Pydantic models
│   │   └── settings.py     # Settings management
│   ├── utils/              # Utilities
│   │   └── logger.py       # Logging setup
│   ├── __init__.py         # Package init
│   └── __main__.py         # Entry point for python -m
├── source/                 # Your personal resume files (gitignored)
│   ├── base_resume.yaml    # Your full master resume
│   ├── static_sections.yaml # Your static info (name, education)
│   └── job_descriptions/   # Your job postings
├── examples/               # Example/template files (committed to repo)
│   ├── base_resume.yaml    # Template resume with placeholder data
│   ├── static_sections.yaml # Template static sections
│   └── job_descriptions/   # Sample job postings
├── tests/                  # Unit tests
│   ├── test_core/          # Core logic tests
│   ├── test_llm/           # LLM provider tests
│   ├── test_integration/   # Integration tests
│   └── conftest.py         # Pytest fixtures
├── .env.example            # Example environment configuration
├── .env                    # Your environment config (gitignored)
├── README.md               # This file
└── pyproject.toml          # Project metadata and dependencies
```

## Configuration

Create a `.env` file to customize settings:

### Using Ollama (Local)

```env
RESUME_TAILOR_LLM_PROVIDER=ollama
RESUME_TAILOR_LLM_MODEL=gemma3:27b
RESUME_TAILOR_LLM_BASE_URL=http://localhost:11434
RESUME_TAILOR_LLM_TEMPERATURE=0.3
RESUME_TAILOR_BASE_RESUME_PATH=source/base_resume.yaml
RESUME_TAILOR_STATIC_SECTIONS_PATH=source/static_sections.yaml
RESUME_TAILOR_RENDERCV_THEME=engineeringresumes
RESUME_TAILOR_OUTPUT_DIR=./output
```

### Using Google Gemini (Cloud)

```env
RESUME_TAILOR_LLM_PROVIDER=gemini
RESUME_TAILOR_LLM_MODEL=gemini-2.5-flash
RESUME_TAILOR_GEMINI_API_KEY=your_api_key_here
RESUME_TAILOR_LLM_TEMPERATURE=0.3
RESUME_TAILOR_BASE_RESUME_PATH=source/base_resume.yaml
RESUME_TAILOR_STATIC_SECTIONS_PATH=source/static_sections.yaml
RESUME_TAILOR_RENDERCV_THEME=engineeringresumes
RESUME_TAILOR_OUTPUT_DIR=./output
```

Get your Gemini API key at: https://aistudio.google.com/app/apikey

### Available RenderCV Themes

- `engineeringresumes` (default)
- `classic`
- `sb2nov`
- `moderncv`

## Resume Template Structure

### Static Sections (static_sections.yaml)

Contains information that never changes:

```yaml
cv:
  name: Your Name
  email: you@example.com
  phone: "+1 (555) 123-4567"
  sections:
    education:
      - institution: University Name
        degree: BS
        area: Computer Science
```

### Base Resume (base_resume.yaml)

Your complete master resume with all experience:

```yaml
cv:
  sections:
    experience:
      - company: Company Name
        position: Senior Engineer
        start_date: "2020-01"
        highlights:
          - Led team of 5 engineers
          - Improved performance by 40%
    skills:
      - label: Languages
        details: Python, Go, JavaScript
```

The tool extracts `experience` and `skills` from your base resume, tailors them with the LLM, then merges with static sections.

## Development

### Run Tests

```bash
# Make sure your virtual environment is activated first
# If using uv: source .venv/bin/activate
# If using pip: source venv/bin/activate

# Run all tests
pytest

# With coverage
pytest --cov=src/resume_tailor

# Run specific test file
pytest tests/test_core/test_template.py -v

# Or use the venv directly without activation
.venv/bin/pytest  # For uv-created venv
# OR
venv/bin/pytest   # For pip-created venv
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff src/ tests/

# Type check
mypy src/
```

## Extending the Tool

### Add a New LLM Provider

Create a new provider in `src/resume_tailor/llm/`:

```python
from .base import BaseLLMProvider, LLMMessage, LLMResponse
from typing import List, Iterator, Any

class MyProvider(BaseLLMProvider):
    def __init__(self, model: str, temperature: float = 0.3, **kwargs: Any):
        super().__init__(model, temperature, **kwargs)
        # Initialize your client here

    def chat(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        # Your implementation
        pass

    def stream_chat(self, messages: List[LLMMessage], **kwargs: Any) -> Iterator[str]:
        # Your implementation
        pass
```

Then add it to `cli/commands.py` in the `create_service` function. See `gemini.py` and `ollama.py` for examples.

### Customize Prompts

Edit `src/resume_tailor/llm/prompts.py` to adjust how the LLM tailors content. The prompts control:

- How experience highlights are rewritten
- Which keywords are emphasized
- How skills are prioritized
- Bold formatting rules

### Customize Resume Design

You can customize the PDF appearance by adding a `design` section to your `base_resume.yaml`:

```yaml
cv:
  sections:
    # Your resume content here...

design:
  theme: engineeringresumes
  page:
    size: us-letter
    top_margin: 1.5cm
    bottom_margin: 1.5cm
    left_margin: 1.5cm
    right_margin: 1.5cm
    show_page_numbering: false
    show_last_updated_date: false  # Remove "last updated" date
  text:
    font_family: Source Sans 3
    font_size: 12pt  # Minimum 12pt for readability
    leading: 0.55em
    alignment: justified
  colors:
    text: rgb(0, 0, 0)
    name: rgb(0, 79, 144)
    section_titles: rgb(0, 79, 144)
    links: rgb(0, 79, 144)
  # ... more customization options
```

**Key Design Options:**
- `font_size`: Recommended minimum 12pt for ATS readability
- `show_last_updated_date`: Set to `false` to remove timestamp
- `show_page_numbering`: Toggle page numbers
- `colors`: Customize colors (use professional tech-friendly blues/grays)
- `margins`: Adjust spacing (1.5cm recommended)

**Testing Design Changes:**
```bash
# Quickly render your base resume with design changes (no LLM processing)
resume-tailor original -o ./test_design
```

See the full design schema in RenderCV docs: https://docs.rendercv.com

## Troubleshooting

### "RenderCV not installed"

```bash
pip install rendercv
```

### "Ollama API error"

Ensure Ollama is running:

```bash
ollama serve
```

### LaTeX errors during PDF generation

Install a LaTeX distribution:

- **macOS**: `brew install --cask mactex`
- **Ubuntu/Debian**: `sudo apt-get install texlive-full`
- **Windows**: Install [MiKTeX](https://miktex.org/)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Roadmap

- [x] Multiple LLM providers (Ollama, Gemini)
- [ ] Add OpenAI/Anthropic provider support
- [ ] Implement ATS scoring
- [ ] Create interactive TUI
- [ ] Add cover letter generation
- [ ] Support multiple resume profiles
- [ ] Web interface for non-technical users

## Acknowledgments

- [RenderCV](https://github.com/sinaatalay/rendercv) for PDF generation
- [Ollama](https://ollama.com/) for local LLM inference
- [Typer](https://typer.tiangolo.com/) for the CLI framework
