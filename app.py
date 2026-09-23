from flask import Flask, render_template, request, send_file
import os
import io
import csv
from datetime import datetime 
from html import escape
from utils.text_preprocessor import preprocess_text
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from utils.pdf_extractor import extract_text_from_pdf
from utils.text_preprocessor import preprocess_text
from utils.jd_analyzer import analyze_job_description
from utils.candidate_parser import extract_candidate_profile

from utils.scorer import (
    calculate_similarity,
    calculate_skill_match,
    calculate_keyword_coverage,
    calculate_skill_relevance,
    calculate_final_score,
    get_recommendation
)


app = Flask(__name__)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Stores latest analysis results
latest_results = []

# Stores latest job description analysis
latest_jd_analysis = {}

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# RESUME RANKING
# =========================================================

@app.route(
    "/rank",
    methods=["POST"]
)
def rank_resumes():

    global latest_results, latest_jd_analysis 

    # -----------------------------------------------------
    # Get Job Description
    # -----------------------------------------------------

    job_description = request.form.get(
        "job_description",
        ""
    )

    # -----------------------------------------------------
    # Get Required Skills
    # -----------------------------------------------------

    required_skills_text = request.form.get(
        "required_skills",
        ""
    )

    # -----------------------------------------------------
    # Get Uploaded Resumes
    # -----------------------------------------------------

    resume_files = request.files.getlist(
        "resumes"
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not resume_files:

        return (
            "Please upload at least one resume."
        )

    if not job_description.strip():

        return (
            "Please enter a job description."
        )

    # -----------------------------------------------------
    # Convert Skills into List
    # -----------------------------------------------------

    required_skills = [
        skill.strip()
        for skill in required_skills_text.split(",")
        if skill.strip()
    ]

    # -----------------------------------------------------
    # Analyze Job Description
    # -----------------------------------------------------

    jd_analysis = analyze_job_description(
        job_description
    )

    latest_jd_analysis = jd_analysis


    # Use automatically detected skills when
    # no skills were manually provided
    if not required_skills:
        required_skills = jd_analysis["skills"]

    # -----------------------------------------------------
    # Store Results
    # -----------------------------------------------------

    results = []

    # =====================================================
    # PROCESS EACH RESUME
    # =====================================================

    for resume_file in resume_files:

        # -------------------------------------------------
        # Skip Empty Files
        # -------------------------------------------------

        if not resume_file.filename:

            continue

        filename = resume_file.filename

        # -------------------------------------------------
        # Save Uploaded Resume
        # -------------------------------------------------

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        resume_file.save(
            file_path
        )

        try:

            # =============================================
            # STEP 1 — Extract Resume Text
            # =============================================

            resume_text = extract_text_from_pdf(
                file_path
            )

            # =============================================
            # STEP 1A ? Extract Candidate Profile
            # =============================================

            candidate_profile = extract_candidate_profile(
                resume_text
            )

            # =============================================
            # STEP 2 — Preprocess Resume
            # =============================================

            processed_resume = preprocess_text(
                resume_text
            )

            # =============================================
            # STEP 3 — Preprocess Job Description
            # =============================================

            processed_jd = preprocess_text(
                job_description
            )

            # =============================================
            # STEP 4 — JD Similarity
            # =============================================

            similarity_score = calculate_similarity(
                processed_resume,
                processed_jd
            )

            # =============================================
            # STEP 5 — Required Skill Matching
            # =============================================

            skill_result = calculate_skill_match(
                resume_text,
                required_skills
            )

            skill_score = skill_result[
                "score"
            ]

            # =============================================
            # STEP 6 — Keyword Coverage
            # =============================================

            keyword_score = calculate_keyword_coverage(
                resume_text,
                job_description,
                required_skills
            )

            # =============================================
            # STEP 7 — Skill Relevance
            # =============================================

            relevance_score = calculate_skill_relevance(
                resume_text,
                required_skills
            )

            # =============================================
            # STEP 8 — Final ATS Score
            # =============================================

            final_score = calculate_final_score(
                similarity_score,
                skill_score,
                keyword_score,
                relevance_score
            )
            
                  
 
            # =============================================
            # STEP 8.1 — Explainable Score Contributions
            # =============================================

            similarity_contribution = round(
                similarity_score * 0.40,
                2
            )

            skill_contribution = round(
                 skill_score * 0.35,
                 2
            )

            keyword_contribution = round(
               keyword_score * 0.15,
               2
            )

            relevance_contribution = round(
                relevance_score * 0.10,
                2
            )



            # =============================================
            # STEP 9 — Recommendation
            # =============================================

            recommendation = get_recommendation(
                final_score
            )

            # =============================================
            # STEP 10 — Store Result
            # =============================================

            results.append({

                "filename": filename,

                # Candidate Profile
                "name": candidate_profile.get("name", ""),
                "email": candidate_profile.get("email", ""),
                "phone": candidate_profile.get("phone", ""),
                "linkedin": candidate_profile.get("linkedin", ""),
                "github": candidate_profile.get("github", ""),

                # Main scores
                "similarity": similarity_score,

                "skill_score": skill_score,

                "keyword_score": keyword_score,

                "relevance_score": relevance_score,

                "final_score": final_score,
                 
                # Explainable score contributions
                "similarity_contribution": similarity_contribution,
                "skill_contribution": skill_contribution,
                "keyword_contribution": keyword_contribution,
                "relevance_contribution": relevance_contribution,

                # Skill information
                "matched": skill_result[
                    "matched"
                ],

                "partial": skill_result[
                    "partial"
                ],

                "missing": skill_result[
                    "missing"
                ],

                # Recommendation
                "recommendation": (
                    recommendation["status"]
                ),

                "recommendation_message": (
                    recommendation["message"]
                )
            })

        except Exception as e:

            # -------------------------------------------------
            # Error Result
            # -------------------------------------------------

            results.append({

                "filename": filename,

                "similarity": 0,

                "skill_score": 0,

                "keyword_score": 0,

                "relevance_score": 0,

                "final_score": 0,

                "matched": [],

                "partial": [],

                "missing": [],

                "recommendation": "Error",

                "recommendation_message": str(e),

                "error": str(e)
            })

    # =====================================================
    # SORT RESULTS
    # =====================================================

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    # =====================================================
    # ASSIGN RANK
    # =====================================================

    for index, result in enumerate(
        results,
        start=1
    ):

        result["rank"] = index

    # =====================================================
    # SAVE LATEST RESULTS
    # =====================================================

    latest_results = results

    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    return render_template(
       "index.html",
       result=True,
       results=results,
       jd_analysis=jd_analysis
    )

# =========================================================
# DOWNLOAD CSV
# =========================================================

@app.route(
    "/download_csv"
)
def download_csv():

    if not latest_results:

        return (
            "No analysis results available. "
            "Please analyze resumes first."
        )

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    # -----------------------------------------------------
    # CSV Header
    # -----------------------------------------------------

    writer.writerow([
        "Rank",
        "Resume",
        "JD Similarity (%)",
        "Skill Match (%)",
        "Keyword Coverage (%)",
        "Skill Relevance (%)",
        "Final Score (%)",
        "Recommendation",
        "Matched Skills",
        "Partial Skills",
        "Missing Skills"
    ])

    # -----------------------------------------------------
    # CSV Data
    # -----------------------------------------------------

    for result in latest_results:

        writer.writerow([

            result.get(
                "rank",
                ""
            ),

            result.get(
                "filename",
                ""
            ),

            result.get(
                "similarity",
                0
            ),

            result.get(
                "skill_score",
                0
            ),

            result.get(
                "keyword_score",
                0
            ),

            result.get(
                "relevance_score",
                0
            ),

            result.get(
                "final_score",
                0
            ),

            result.get(
                "recommendation",
                ""
            ),

            ", ".join(
                result.get(
                    "matched",
                    []
                )
            ),

            ", ".join(
                result.get(
                    "partial",
                    []
                )
            ),

            ", ".join(
                result.get(
                    "missing",
                    []
                )
            )
        ])

    output.seek(0)

    return send_file(

        io.BytesIO(
            output.getvalue().encode(
                "utf-8-sig"
            )
        ),

        mimetype="text/csv",

        as_attachment=True,

        download_name=(
            "resume_ranking_report.csv"
        )
    )


# =========================================================
# DOWNLOAD PDF
# =========================================================

@app.route(
    "/download_pdf"
)
def download_pdf():

    global latest_jd_analysis

    if not latest_results:

        return (
            "No analysis results available. "
            "Please analyze resumes first."
        )

    buffer = io.BytesIO()

    # -----------------------------------------------------
    # PDF Document
    # -----------------------------------------------------

    document = SimpleDocTemplate(

        buffer,

        pagesize=landscape(A4),

        rightMargin=30,

        leftMargin=30,

        topMargin=30,

        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # -----------------------------------------------------
    # Styles
    # -----------------------------------------------------

    title_style = ParagraphStyle(

        "TitleStyle",

        parent=styles["Title"],

        alignment=TA_CENTER,

        fontSize=20,

        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(

        "SubtitleStyle",

        parent=styles["Normal"],

        alignment=TA_CENTER,

        fontSize=9,

        textColor=colors.grey,

        spaceAfter=20
    )

    normal_style = ParagraphStyle(

        "NormalStyle",

        parent=styles["Normal"],

        fontSize=8,

        leading=10
    )

    small_style = ParagraphStyle(

        "SmallStyle",

        parent=styles["Normal"],

        fontSize=7,

        leading=9
    )

    elements = []

    # =====================================================
    # PDF TITLE
    # =====================================================

    elements.append(

        Paragraph(
            "AI Resume Ranker - Analysis Report",
            title_style
        )
    )

    # -----------------------------------------------------
    # Generated Date
    # -----------------------------------------------------

    generated_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    elements.append( 

        Paragraph(
            f"Generated on: {generated_time}",
            subtitle_style
        )
    )
        # -----------------------------------------------------
    # Total Resumes
    # -----------------------------------------------------

    elements.append(
        Paragraph(
            f"<b>Total Resumes Analyzed:</b> "
            f"{len(latest_results)}",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    # -----------------------------------------------------
    # Job Description Analysis Summary
    # -----------------------------------------------------

    detected_skills = latest_jd_analysis.get(
        "skills",
        []
    )

    detected_keywords = latest_jd_analysis.get(
        "keywords",
        []
    )

    elements.append(
        Paragraph(
            "<b>Job Description Analysis</b>",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 5)
    )

    elements.append(
        Paragraph(
            f"<b>Skills Detected:</b> "
            f"{len(detected_skills)}",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Important Keywords Detected:</b> "
            f"{len(detected_keywords)}",
            normal_style
        )
    )

    if detected_skills:
        skills_text = ", ".join(
            escape(skill)
            for skill in detected_skills
        )

        elements.append(
            Paragraph(
                f"<b>Detected Skills:</b> "
                f"{skills_text}",
                small_style
            )
        )

    if detected_keywords:
        keywords_text = ", ".join(
            escape(keyword)
            for keyword in detected_keywords
        )

        elements.append(
            Paragraph(
                f"<b>Important Keywords:</b> "
                f"{keywords_text}",
                small_style
            )
        )

    elements.append(
        Spacer(1, 15)
    )

    table_data = [

        [
            "Rank",
            "Resume",
            "JD Similarity",
            "Skill Match",
            "Keyword Coverage",
            "Skill Relevance",
            "Final Score",
            "Recommendation",
            "Matched Skills",
            "Partial Skills",
            "Missing Skills"
        ]
    ]

    # =====================================================
    # PDF TABLE ROWS
    # =====================================================

    for result in latest_results:

        matched = ", ".join(
            result.get(
                "matched",
                []
            )
        )

        partial = ", ".join(
            result.get(
                "partial",
                []
            )
        )

        missing = ", ".join(
            result.get(
                "missing",
                []
            )
        )

        table_data.append([

            str(
                result.get(
                    "rank",
                    ""
                )
            ),

            Paragraph(
                escape(
                    result.get(
                        "filename",
                        ""
                    )
                ),
                small_style
            ),

            f"{result.get('similarity', 0)}%",

            f"{result.get('skill_score', 0)}%",

            f"{result.get('keyword_score', 0)}%",

            f"{result.get('relevance_score', 0)}%",

            f"{result.get('final_score', 0)}%",

            Paragraph(
                escape(
                    result.get(
                        "recommendation",
                        ""
                    )
                ),
                small_style
            ),

            Paragraph(
                escape(
                    matched
                ) if matched else "-",
                small_style
            ),

            Paragraph(
                escape(
                    partial
                ) if partial else "-",
                small_style
            ),

            Paragraph(
                escape(
                    missing
                ) if missing else "-",
                small_style
            )
        ])

    # =====================================================
    # CREATE TABLE
    # =====================================================

    table = Table(

        table_data,

        repeatRows=1,

        colWidths=[

            30,     # Rank
            90,     # Resume
            65,     # JD Similarity
            60,     # Skill Match
            75,     # Keyword
            65,     # Relevance
            60,     # Final
            80,     # Recommendation
            120,    # Matched
            100,    # Partial
            120     # Missing
        ]
    )

    # =====================================================
    # TABLE STYLE
    # =====================================================

    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f2937")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                7
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                6.5
            ),

            (
                "ALIGN",
                (0, 1),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (2, 1),
                (6, -1),
                "CENTER"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elements.append(
        table
    )

    elements.append(
        Spacer(1, 20)
    )

    # =====================================================
    # SCORING METHOD
    # =====================================================

    elements.append(

        Paragraph(

            "<b>Scoring Method:</b> "
            "Final Score = "
            "40% JD Similarity + "
            "35% Skill Match + "
            "15% Keyword Coverage + "
            "10% Skill Relevance",

            normal_style
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(
        elements
    )

    buffer.seek(0)

    return send_file(

        buffer,

        mimetype="application/pdf",

        as_attachment=True,

        download_name=(
            "resume_ranking_report.pdf"
        )
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )