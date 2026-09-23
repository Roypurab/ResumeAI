import re


# Common technical skills that can be detected from a job description
KNOWN_SKILLS = [
    "Python",
    "Java",
    "C++",
    "C",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Flask",
    "Django",
    "FastAPI",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "REST API",
    "REST APIs",
    "Linux",
    "DevOps",
    "CI/CD",
    "Jenkins",
    "Cloud Computing",
    "Figma",
    "Power BI",
    "Tableau"
]


def normalize_text(text):
    """Normalize text for easier skill detection."""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    return text


def extract_skills(job_description):
    """
    Detect known technical skills from a job description.
    """

    normalized_jd = normalize_text(job_description)

    detected_skills = []

    for skill in KNOWN_SKILLS:

        skill_lower = skill.lower()

        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(skill_lower)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, normalized_jd):

            # Avoid duplicate REST API / REST APIs
            if skill in ["REST API", "REST APIs"]:
                if "REST API" not in detected_skills:
                    detected_skills.append("REST API")
            else:
                detected_skills.append(skill)

    return detected_skills


def extract_keywords(job_description):
    """
    Extract important non-skill keywords from the job description.
    """

    normalized_jd = normalize_text(job_description)

    important_keywords = [
        "software development",
        "web development",
        "application development",
        "problem solving",
        "debugging",
        "testing",
        "deployment",
        "database",
        "version control",
        "team collaboration",
        "communication",
        "api development",
        "cloud",
        "maintenance",
        "programming"
    ]

    detected_keywords = []

    for keyword in important_keywords:

        if keyword in normalized_jd:

            detected_keywords.append(keyword.title())

    return detected_keywords


def analyze_job_description(job_description):
    """
    Perform complete JD analysis.
    """

    if not job_description or not job_description.strip():

        return {
            "skills": [],
            "keywords": [],
            "skill_count": 0,
            "keyword_count": 0
        }

    skills = extract_skills(job_description)

    keywords = extract_keywords(job_description)

    return {
        "skills": skills,
        "keywords": keywords,
        "skill_count": len(skills),
        "keyword_count": len(keywords)
    }