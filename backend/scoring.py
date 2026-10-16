import re

SKILLS = {
    "Python": ["python"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "HTML": ["html"],
    "CSS": ["css"],
    "MySQL": ["mysql"],
    "SQL": ["sql", "structured query language"],
    "REST APIs": ["rest api", "rest apis", "restful api"],
    "Git": ["git", "github"],
    "Docker": ["docker", "containerization"],
    "AWS": ["aws", "amazon web services"],
    "Machine Learning": ["machine learning", "scikit-learn"],
    "Pandas": ["pandas"],
    "Data Analysis": ["data analysis", "data analytics"],
    "React": ["react", "react.js"],
    "Node.js": ["node.js", "nodejs"],
    "FastAPI": ["fastapi"],
    "Communication": ["communication skills"]
}


def normalize(text):
    return re.sub(r"[^a-z0-9+#.]+", " ", text.lower())


def find_skills(text):
    normalized = normalize(text)
    found = []

    for skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"

            if re.search(pattern, normalized):
                found.append(skill)
                break

    return found


def calculate_match(resume_text, job_description):
    resume_skills = set(find_skills(resume_text))
    job_skills = find_skills(job_description)

    # Remove duplicate requirements.
    job_skills = list(dict.fromkeys(job_skills))

    if not job_skills:
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "resume_skills": sorted(resume_skills),
            "required_skills": [],
            "error": "No recognized skills found in the job description"
        }

    matched = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    # Simple weighted scoring.
    # Tune these weights according to the requirements.
    weights = {
        "Python": 3,
        "Java": 3,
        "JavaScript": 3,
        "REST APIs": 3,
        "SQL": 3,
        "MySQL": 3,
        "Docker": 2,
        "AWS": 2,
        "Communication": 1
    }

    total_weight = sum(
        weights.get(skill, 2) for skill in job_skills
    )

    matched_weight = sum(
        weights.get(skill, 2) for skill in matched
    )

    score = round(
        matched_weight / total_weight * 100, 2
    ) if total_weight else 0.0

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": sorted(resume_skills),
        "required_skills": job_skills
    }