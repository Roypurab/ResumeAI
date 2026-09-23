import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# SKILL VARIATIONS
# =========================================================

SKILL_VARIATIONS = {
    "python": [
        "python",
        "python3"
    ],

    "flask": [
        "flask"
    ],

    "django": [
        "django"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "sqlite"
    ],

    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "neural network",
        "neural networks",
        "dl"
    ],

    "scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "git": [
        "git",
        "github",
        "gitlab"
    ],

    "rest api": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
        "restful services"
    ],

    "docker": [
        "docker",
        "containerization"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure",
        "microsoft azure"
    ],

    "gcp": [
        "gcp",
        "google cloud",
        "google cloud platform"
    ],

    "java": [
        "java"
    ],

    "c++": [
        "c++",
        "cpp"
    ],

    "javascript": [
        "javascript",
        "js"
    ],

    "react": [
        "react",
        "reactjs",
        "react.js"
    ],

    "html": [
        "html",
        "html5"
    ],

    "css": [
        "css",
        "css3"
    ],

    "mongodb": [
        "mongodb",
        "mongo db"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ]
}


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize text for consistent matching.
    """

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    replacements = {
        "machine-learning": "machine learning",
        "machinelearning": "machine learning",
        "restful apis": "rest api",
        "restful api": "rest api",
        "rest apis": "rest api",
        "scikit learn": "scikit-learn"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# =========================================================
# SAFE SKILL MATCHING
# =========================================================

def contains_skill(text, skill):
    """
    Check whether a skill exists as a complete term.
    """

    text = normalize_text(text)
    skill = normalize_text(skill)

    variations = SKILL_VARIATIONS.get(
        skill,
        [skill]
    )

    for variation in variations:

        variation = normalize_text(variation)

        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(variation)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, text):
            return True

    return False


# =========================================================
# JD SIMILARITY
# =========================================================

def calculate_similarity(resume_text, job_description):
    """
    Calculate TF-IDF cosine similarity between
    resume and job description.
    """

    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=8000,
        sublinear_tf=True
    )

    vectors = vectorizer.fit_transform([
        resume_text,
        job_description
    ])

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(similarity * 100, 2)


# =========================================================
# SKILL MATCHING
# =========================================================

def calculate_skill_match(resume_text, required_skills):
    """
    Calculate required skill matching.

    Returns:
    - matched
    - partial
    - missing
    - score
    """

    resume_text = normalize_text(resume_text)

    matched_skills = []
    partial_skills = []
    missing_skills = []

    for skill in required_skills:

        skill = skill.strip()

        if not skill:
            continue

        normalized_skill = normalize_text(skill)

        # Full skill match
        if contains_skill(
            resume_text,
            normalized_skill
        ):

            matched_skills.append(skill)

            continue

        # Partial match for multi-word skills
        words = normalized_skill.split()

        if len(words) > 1:

            matched_words = 0

            for word in words:

                if contains_skill(
                    resume_text,
                    word
                ):
                    matched_words += 1

            if matched_words > 0:

                partial_skills.append(skill)

                continue

        missing_skills.append(skill)

    total = (
        len(matched_skills)
        + len(partial_skills)
        + len(missing_skills)
    )

    if total == 0:

        score = 0

    else:

        score = (
            len(matched_skills)
            + (len(partial_skills) * 0.5)
        ) / total * 100

    return {
        "score": round(score, 2),
        "matched": matched_skills,
        "partial": partial_skills,
        "missing": missing_skills
    }


# =========================================================
# KEYWORD COVERAGE
# =========================================================

def calculate_keyword_coverage(
    resume_text,
    job_description,
    required_skills
):
    """
    Measure important job-related keyword coverage.
    """

    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    important_keywords = [
        "develop",
        "development",
        "software",
        "application",
        "web",
        "api",
        "database",
        "testing",
        "debugging",
        "deployment",
        "cloud",
        "programming",
        "problem solving",
        "team",
        "project",
        "maintenance",
        "version control"
    ]

    skill_words = set()

    for skill in required_skills:

        for word in normalize_text(skill).split():

            skill_words.add(word)

    jd_keywords = []

    for keyword in important_keywords:

        if keyword in job_description:

            keyword_words = set(
                keyword.split()
            )

            if not keyword_words.intersection(
                skill_words
            ):

                jd_keywords.append(keyword)

    if not jd_keywords:

        return 100.0

    matched = 0

    for keyword in jd_keywords:

        if keyword in resume_text:

            matched += 1

    score = (
        matched / len(jd_keywords)
    ) * 100

    return round(score, 2)


# =========================================================
# SKILL RELEVANCE
# =========================================================

def calculate_skill_relevance(
    resume_text,
    required_skills
):
    """
    Measure how meaningfully required skills
    appear in the resume.
    """

    resume_text = normalize_text(resume_text)

    if not required_skills:

        return 0.0

    relevance_scores = []

    for skill in required_skills:

        skill = skill.strip()

        if not skill:
            continue

        variations = SKILL_VARIATIONS.get(
            normalize_text(skill),
            [normalize_text(skill)]
        )

        count = 0

        for variation in variations:

            count += resume_text.count(
                normalize_text(variation)
            )

        if count == 0:

            relevance_scores.append(0)

        elif count == 1:

            relevance_scores.append(70)

        elif count == 2:

            relevance_scores.append(85)

        else:

            relevance_scores.append(100)

    if not relevance_scores:

        return 0.0

    return round(
        sum(relevance_scores)
        / len(relevance_scores),
        2
    )


# =========================================================
# FINAL ATS SCORE
# =========================================================

def calculate_final_score(
    similarity_score,
    skill_score,
    keyword_score,
    relevance_score
):
    """
    Calculate final ATS-style score.

    Weights:
    - JD Similarity      = 40%
    - Skill Match        = 35%
    - Keyword Coverage   = 15%
    - Skill Relevance    = 10%
    """

    final_score = (
        similarity_score * 0.40
        + skill_score * 0.35
        + keyword_score * 0.15
        + relevance_score * 0.10
    )

    return round(final_score, 2)


# =========================================================
# RECOMMENDATION
# =========================================================

def get_recommendation(final_score):

    if final_score >= 80:

        return {
            "status": "Strong Match",
            "message": "High alignment with the job requirements."
        }

    elif final_score >= 65:

        return {
            "status": "Good Match",
            "message": "Good alignment with the job requirements."
        }

    elif final_score >= 50:

        return {
            "status": "Moderate Match",
            "message": "Some relevant requirements are matched."
        }

    else:

        return {
            "status": "Low Match",
            "message": "Limited alignment with the current job requirements."
        }