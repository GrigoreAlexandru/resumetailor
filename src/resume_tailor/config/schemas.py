"""Data models for resume sections and configuration."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ExperienceEntry(BaseModel):
    """Single work experience entry."""
    company: str
    position: str
    location: Optional[str] = None
    start_date: str  # YYYY-MM format
    end_date: Optional[str] = None  # None for current, YYYY-MM otherwise
    highlights: List[str] = Field(default_factory=list)

    @field_validator('highlights')
    @classmethod
    def validate_highlights(cls, v: List[str]) -> List[str]:
        """Ensure highlights are non-empty strings."""
        return [h.strip() for h in v if h.strip()]


class SkillCategory(BaseModel):
    """Skills grouped by category."""
    label: str
    details: str  # Comma-separated or descriptive text


class StaticSections(BaseModel):
    """Static sections that don't change per job."""
    name: str
    location: Optional[str] = None
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    social_networks: List[Dict[str, str]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)


class DynamicSections(BaseModel):
    """Dynamic sections tailored per job."""
    summary: Optional[List[str]] = None
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: List[SkillCategory] = Field(default_factory=list)
    bold_keywords: List[str] = Field(default_factory=list)


class RendererConfig(BaseModel):
    """RenderCV rendering configuration."""
    theme: str = "engineeringresumes"
    output_folder: str = "./output"
    design_overrides: Dict[str, Any] = Field(default_factory=dict)


class JobDescription(BaseModel):
    """Parsed job description."""
    text: str
    company: Optional[str] = None
    role: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)

    @classmethod
    def from_file(cls, path: str) -> "JobDescription":
        """Load from text file."""
        with open(path, 'r', encoding='utf-8') as f:
            return cls(text=f.read())
