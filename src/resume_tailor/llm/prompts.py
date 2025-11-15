"""Prompt templates for resume tailoring."""
from typing import List, Dict, Any
import yaml


SYSTEM_PROMPT = """You are an expert ATS-optimized resume writer. Your task is to tailor resume sections for specific job descriptions.

**Critical Requirements:**
1. Output ONLY valid YAML - no explanatory text before or after
2. Use **bold** markdown syntax to emphasize key achievements and technologies
3. Match keywords from the job description naturally
4. Quantify achievements with metrics whenever possible
5. Use strong action verbs (Led, Built, Architected, Improved, etc.)
6. Keep bullet points concise (1-2 lines maximum)
7. Prioritize most relevant experience and skills

**Formatting Rules:**
- Bold numbers and percentages: **40%**, **5 engineers**
- Bold key technologies: **Python**, **Kubernetes**
- Bold impact words: **reduced**, **improved**, **increased**
- Use proper YAML indentation (2 spaces)
- Maintain list structure with proper dashes
"""




def create_highlights_tailoring_prompt(
    job_description: str,
    experience_entry: Dict[str, Any],
) -> str:
    """Create prompt for tailoring experience highlights."""
    highlights_yaml = yaml.dump(
        {"highlights": experience_entry.get("highlights", [])},
        default_flow_style=False,
        sort_keys=False
    )

    prompt = f"""Job Description:
{job_description}

---

Current Experience Entry:
Company: {experience_entry.get('company')}
Position: {experience_entry.get('position')}
Highlights:
```yaml
{highlights_yaml}
```

---

**Task:** Rewrite the highlights for this experience entry to best match the job description.

**Instructions:**
1.  **Do not remove any highlights.**
2.  Rewrite the highlights to emphasize achievements relevant to the job description.
3.  Use strong action verbs and quantify results.
4.  Reorder the highlights to put the most relevant ones first.

**Output Format:**
Return ONLY a YAML list of the tailored highlights (no other text):

```yaml
highlights:
  - "Tailored highlight 1"
  - "Tailored highlight 2"
```
"""
    return prompt


def create_skills_tailoring_prompt(
    job_description: str,
    current_skills: List[Dict[str, Any]],
) -> str:
    """Create prompt for tailoring skills."""
    skills_yaml = yaml.dump(
        {"skills": current_skills},
        default_flow_style=False,
        sort_keys=False
    )

    prompt = f"""Job Description:
{job_description}

---

Current Skills Section:
```yaml
{skills_yaml}
```

---

**Task:** Reorder the skills sections to prioritize those most relevant to the job description.

**Instructions:**
1.  **Do not remove any skills or skill categories.**
2.  Reorder the skill categories to put the most relevant ones first.
3.  Within each category, reorder the skills to put the most relevant ones first.

**Output Format:**
Return ONLY a YAML list of the tailored skills (no other text):

```yaml
skills:
  - label: "Most relevant category"
    details: "Most relevant skill, ..."
  - label: "Next relevant category"
    details: "..."
```
"""
    return prompt


def create_summary_prompt(job_description: str, current_summary: str) -> str:
    """Create prompt for tailoring professional summary.

    Args:
        job_description: Full job posting
        current_summary: Current summary text

    Returns:
        Formatted prompt
    """
    prompt = f"""Job Description:
{job_description}

Current Summary:
{current_summary}

Task: Rewrite the professional summary to align with this job posting.

Requirements:
- 2-3 sentences maximum
- Lead with years of experience and most relevant expertise
- Mention 2-3 key technologies/skills from the job description
- Use **bold** for key qualifications
- Be concise and impactful

Output Format:
Return ONLY the following YAML structure:

```yaml
summary:
  - "Your tailored summary text with **bold** emphasis on key points."
```"""

    return prompt


def extract_keywords_prompt(job_description: str) -> str:
    """Create prompt to extract key technical terms from job description.

    Args:
        job_description: Full job posting

    Returns:
        Formatted prompt
    """
    prompt = f"""Job Description:
{job_description}

Task: Extract 10-15 key technical terms, technologies, and skills from this job description that should be emphasized in a resume.

Focus on:
- Programming languages
- Frameworks and tools
- Methodologies (Agile, DevOps, etc.)
- Domain expertise
- Key responsibilities

Output Format:
Return ONLY a YAML list (no explanatory text):

```yaml
keywords:
  - Keyword1
  - Keyword2
  - Keyword3
```"""

    return prompt

def extract_jd_details_prompt(job_description: str) -> str:
    """Create prompt to extract company and role from job description."""
    prompt = f"""From the following job description, extract the company name and the job title.

Job Description:
{job_description}

Respond with ONLY a YAML structure. Do not include any other text. The company name should be just the company's name, not a full sentence.

Example:
```yaml
company: "Google"
role: "Software Engineer"
```

Your output:
```yaml
company: "..."
role: "..."
```"""
    return prompt