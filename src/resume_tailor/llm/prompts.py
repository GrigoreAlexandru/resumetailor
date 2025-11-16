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

**Golden Formula for Each Bullet:**
[Action Verb] + [What You Did] + [Specific Technology/Tool] + [Quantified Impact]

Example: "Reduced API latency by 40% by implementing Redis caching in Python/Django, serving 1M+ daily users"

**Instructions:**
1.  **Do not remove any highlights** - rewrite all of them
2.  **Reorder highlights** to put most relevant ones first (based on job description requirements)
3.  **Preserve ALL metrics and numbers** from original (%, $, time, scale, users)
4.  Use strong action verbs: Led, Architected, Reduced, Increased, Built, Scaled, Migrated, Optimized
5.  Include specific technologies mentioned in both the highlight and job description
6.  **Keep bullets concise** - 1-2 lines maximum
7.  Use plain text ONLY - do NOT use markdown bold syntax (**text**)

**CRITICAL - NEVER DO THESE:**
- ❌ Do NOT add explanatory phrases like "demonstrating expertise in", "showcasing ability to", "highlighting skills in", "fostering growth", "ensuring quality"
- ❌ Do NOT explain soft skills or add clarifying clauses - let achievements speak for themselves
- ❌ Do NOT add content that wasn't in the original - only rewrite what exists
- ❌ Do NOT add redundant bullets or filler content
- ❌ Do NOT make bullets longer than 2 lines
- ❌ Do NOT use vague terms like "contributed to" - be specific about what YOU did
- ❌ The system will automatically bold key terms - do NOT use ** markers

**SHOW, DON'T TELL:**
- ✅ GOOD: "Mentored 4+ engineers on best practices for testing, code quality, and distributed system design"
- ❌ BAD: "Mentored 4+ engineers, demonstrating strong communication and collaboration skills"
- ❌ BAD: "Mentored 4+ engineers, fostering team growth and adherence to standards"

**Output Format:**
Return ONLY a YAML list of the tailored highlights with plain text (no ** markers):

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
1.  **CRITICAL: Preserve ALL existing skill category labels EXACTLY as they are. Do NOT add, remove, or modify any labels.**
2.  **Do not remove any skills or skill categories.**
3.  Reorder the skill categories to put the most relevant ones first.
4.  Within each category, reorder the skills in the details field to put the most relevant ones first.
5.  Keep the exact same label names - only change the order of categories and the order of skills within details.

**Output Format:**
Return ONLY a YAML list of the tailored skills (no other text):

```yaml
skills:
  - label: "Exact original label 1"
    details: "Reordered skills, ..."
  - label: "Exact original label 2"
    details: "Reordered skills, ..."
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

Task: Rewrite the professional summary to align with this job posting while maintaining impact.

Requirements:
- **MUST be 2-3 sentences** (not shorter!)
- **Preserve ALL quantified achievements from the original** (percentages, numbers, metrics)
- Lead with: [Title] with [X]+ years of experience in [specific domain]
- Include 2-4 specific technologies from job description that match your background
- Include 1-2 quantified achievements or key accomplishments from the original summary
- Match job description keywords naturally
- Use plain text ONLY - do NOT use markdown bold syntax (**text**)
- Write in third person or implied first person (avoid "has enabled me to", "I have")

CRITICAL RULES:
- Do NOT shorten the summary - keep it substantial (2-3 sentences)
- Do NOT lose metrics and numbers from the original
- Do NOT add metrics that don't exist in the original
- Do NOT use awkward phrases like "has enabled me to" or "I have achieved"
- Do NOT use generic phrases like "extensive experience" - be specific
- The system will automatically bold key terms - do NOT use ** markers

Example Structure:
"[Title] with [X]+ years of experience [doing what], specializing in [specific area]. Expert in [2-4 specific technologies from job description], with proven success in [quantified achievement from original] and [another quantified achievement from original]."

Output Format:
Return ONLY the following YAML structure with plain text (no ** markers):

```yaml
summary:
  - "Your tailored summary text in plain text format."
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


def extract_resume_keywords_prompt(resume_content: str) -> str:
    """Create prompt to extract all technical terms from resume content.

    Args:
        resume_content: YAML resume content

    Returns:
        Formatted prompt
    """
    prompt = f"""Resume Content:
{resume_content}

Task: Extract ALL technical terms, technologies, tools, and frameworks mentioned in this resume that should be emphasized with bold formatting.

Extract:
- Programming languages (Python, JavaScript, PHP, Go, Java, etc.)
- Frameworks and libraries (React, Django, Symfony, Vue.js, Node.js, etc.)
- Databases (PostgreSQL, MySQL, MongoDB, Redis, etc.)
- Cloud platforms (AWS, GCP, Azure, etc.)
- DevOps tools (Docker, Kubernetes, Jenkins, GitLab CI, etc.)
- Methodologies (Agile, Scrum, TDD, CI/CD, etc.)
- Other technologies (Kafka, Elasticsearch, RabbitMQ, etc.)

Be comprehensive - include every technical term that appears in the resume.

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