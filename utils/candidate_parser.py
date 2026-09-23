import re


def extract_candidate_profile(text):
    """
    Extract basic candidate identity information from resume text.
    """

    profile = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    }

    if not text:
        return profile

    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    if email_match:
        profile["email"] = email_match.group(0).strip()

    # -------------------------------------------------
    # PHONE
    # -------------------------------------------------
    phone_matches = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    if phone_matches:
        profile["phone"] = phone_matches[0].strip()

    # -------------------------------------------------
    # LINKEDIN
    # -------------------------------------------------
    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._-]+",
        text,
        re.IGNORECASE
    )

    if linkedin_match:
        profile["linkedin"] = linkedin_match.group(0).strip()

    # -------------------------------------------------
    # GITHUB
    # -------------------------------------------------
    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE
    )

    if github_match:
        profile["github"] = github_match.group(0).strip()

    # -------------------------------------------------
    # NAME
    # -------------------------------------------------
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:15]:

        cleaned = re.sub(
            r"[^A-Za-z .'-]",
            "",
            line
        ).strip()

        words = cleaned.split()

        if 2 <= len(words) <= 4:
            if all(
                word.replace("-", "").replace("'", "").isalpha()
                for word in words
            ):
                profile["name"] = cleaned
                break

    return profile
