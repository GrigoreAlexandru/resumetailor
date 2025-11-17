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

**Golden Formula for Each Bullet (First Person):**
[Action Verb] + [What You Did] + [Specific Technology/Tool] + [Quantified Impact]

Examples (First Person - No "I" Pronouns):
- "Reduced API latency by 40% by implementing Redis caching in Python/Django, serving 1M+ daily users"
- "Led migration of 20+ microservices to Kubernetes, reducing deployment time by 60%"
- "Architected real-time data pipeline processing 10M+ events/day using Kafka and Flink"

**Instructions:**
1.  **Write in FIRST PERSON** (implied first person - use action verbs without "I", "me", "my")
2.  **Do not remove any highlights** - rewrite all of them
3.  **Reorder highlights** to put most relevant ones first (based on job description requirements)
4.  **Preserve ALL metrics and numbers** from original (%, $, time, scale, users)
5.  Use strong action verbs: Led, Architected, Reduced, Increased, Built, Scaled, Migrated, Optimized
6.  Include specific technologies mentioned in both the highlight and job description
7.  **Keep bullets concise** - 1-2 lines maximum
8.  Use plain text ONLY - do NOT use markdown bold syntax (**text**)

**CRITICAL - NEVER DO THESE:**
- ❌ Do NOT use pronouns "I", "me", "my" - write in implied first person with action verbs
- ❌ Do NOT use third person ("he/she", "the engineer", etc.)
- ❌ Do NOT add explanatory phrases like "demonstrating expertise in", "showcasing ability to", "highlighting skills in", "fostering growth", "ensuring quality"
- ❌ Do NOT explain soft skills or add clarifying clauses - let achievements speak for themselves
- ❌ Do NOT add content that wasn't in the original - only rewrite what exists
- ❌ Do NOT add redundant bullets or filler content
- ❌ Do NOT make bullets longer than 2 lines
- ❌ Do NOT use vague terms like "contributed to" - be specific with action verbs
- ❌ The system will automatically bold key terms - do NOT use ** markers

**FIRST PERSON EXAMPLES:**
- ✅ GOOD: "Led team of 5 engineers to deliver..." (implied first person)
- ✅ GOOD: "Mentored 4+ engineers on best practices for testing, code quality, and distributed system design"
- ❌ BAD: "I mentored 4+ engineers..." (explicit pronoun - too informal)
- ❌ BAD: "The engineer mentored 4+ engineers..." (third person)
- ❌ BAD: "Mentored 4+ engineers, demonstrating strong communication skills" (explanatory fluff)

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
- **Write in FIRST PERSON** (implied first person - no "I" pronouns, just describe yourself directly)
- Lead with: [Title] with [X]+ years of experience in [specific domain]
- Include 2-4 specific technologies from job description that match your background
- Include 1-2 quantified achievements or key accomplishments from the original summary
- Match job description keywords naturally
- Use plain text ONLY - do NOT use markdown bold syntax (**text**)

CRITICAL RULES:
- Do NOT shorten the summary - keep it substantial (2-3 sentences)
- Do NOT lose metrics and numbers from the original
- Do NOT add metrics that don't exist in the original
- Do NOT use pronouns like "I", "me", "my" - use implied first person (standard resume style)
- Do NOT use third person phrases like "he/she has", "John is", etc.
- Do NOT use generic phrases like "extensive experience" - be specific
- The system will automatically bold key terms - do NOT use ** markers

Example Structure (First Person):
"Senior Backend Engineer with 5+ years of experience developing and deploying high-performance applications, specializing in microservices architecture. Expert in Python, Django, and PostgreSQL, with proven success in reducing API latency by 45% and improving system stability."

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


def extract_resume_keywords_prompt(resume_content: str, job_description: str) -> str:
    """Create prompt to extract job-relevant technical terms from resume content.

    Args:
        resume_content: YAML resume content
        job_description: Job posting text

    Returns:
        Formatted prompt
    """
    prompt = f"""Job Description:
{job_description}

---

Resume Content:
{resume_content}

---

Task: Extract ONLY the technical terms from the resume that are RELEVANT to this specific job description.

Instructions:
- Only include terms that appear in BOTH the resume AND are mentioned or implied in the job description
- Focus on technologies, skills, and tools that align with the job requirements
- Exclude technologies that aren't relevant to this job (e.g., if JD is for PHP/Symfony, don't include Go/Python unless JD mentions them)
- Include related/similar technologies (e.g., if JD mentions "databases" and resume has PostgreSQL, include it)

Examples of what to include:
- JD mentions "PHP" and resume has "PHP" ✓
- JD mentions "databases" and resume has "PostgreSQL", "MySQL" ✓
- JD mentions "Docker" and resume has "Docker", "Kubernetes" ✓
- JD mentions "REST APIs" and resume has "RESTful APIs" ✓

Examples of what to exclude:
- JD is for PHP role, resume has "Go" but JD doesn't mention Go ✗
- JD is for backend, resume has "React" but JD doesn't mention frontend ✗
- JD is for cloud, resume has "on-premise tools" not mentioned in JD ✗

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