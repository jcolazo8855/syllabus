import json
import math
from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="BAT 3305 • Interactive Syllabus Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# Source-based course data distilled from the uploaded syllabus
# -------------------------------------------------------------------
COURSE_META = {
    "course": "BAT 3305",
    "title": "Machine Learning",
    "term": "Spring 2021 syllabus prototype",
    "format": "Special online edition",
    "meeting": "Tu/Th 9:55–11:10 • Online",
    "instructor": "Dr. Jorge Colazo",
    "focus": "Applied machine learning for real problems using small to medium in-memory datasets.",
}

GRADE_WEIGHTS = {
    "Conceptual checkpoint #1": 7,
    "Conceptual checkpoint #2": 7,
    "Conceptual checkpoint #3": 7,
    "Assignment 1 (Regression)": 21,
    "Assignment 2 (Classification)": 21,
    "Group project": 27,
    "Participation in class": 10,
}

LETTER_BANDS = [
    (93, "A"),
    (90, "A-"),
    (87, "B+"),
    (83, "B"),
    (80, "B-"),
    (77, "C+"),
    (73, "C"),
    (70, "C-"),
    (67, "D+"),
    (60, "D"),
    (0, "F"),
]

COURSE_OBJECTIVES = [
    "Understand the role, uses, and limitations of machine learning methods in a business context.",
    "Identify a problem and select the best ML strategy to solve it.",
    "Compare ML methods and their performance.",
    "Apply ML to real-life data.",
    "Explain ML methods, results, and applications to a non-specialist audience.",
]

EXPECTATION_STATEMENTS = [
    "This course will not spoon-feed students; proactivity and decision making are part of the learning design.",
    "Students are expected to read assigned materials before class and come prepared.",
    "Debugging responsibility sits primarily with the student; outside resources should be exhausted first.",
    "The class is tool-agnostic in principle, though much coding is expected to happen in R.",
    "Preparedness, steady progress, and professionalism are treated as major performance indicators.",
]

TOPIC_BLOCKS = [
    {
        "module": "Foundations",
        "theme": "Orientation and analytical fundamentals",
        "color": "#4f46e5",
        "items": [
            "Introduction to ML and review of fundamental concepts",
            "Supervised vs. unsupervised ML",
            "Review of data cleaning and preparation",
            "Review of matrix algebra",
            "Review of multivariate OLS regression",
        ],
    },
    {
        "module": "Supervised ML",
        "theme": "Prediction, fit, and comparison",
        "color": "#0f766e",
        "items": [
            "OLS as an ML method",
            "Bias-variance tradeoff / fit metrics",
            "Ridge and LASSO regression",
            "Logistic regression",
            "Anomaly detection",
            "K-nearest neighbors",
            "Support vector machines",
            "SVM regression",
            "Random trees, random forests, bagging, boosting",
        ],
    },
    {
        "module": "Unsupervised ML",
        "theme": "Structure discovery and text/network analysis",
        "color": "#b45309",
        "items": [
            "K-means",
            "Hierarchical clustering",
            "Social network analysis",
            "Text mining",
            "PERL and regular expressions",
            "Spidering, scraping, parsing, cleaning, extraction",
            "Word frequencies, sentiment analysis, LDA topic modeling",
        ],
    },
    {
        "module": "Neural Nets + RL",
        "theme": "Introductory modern ML topics",
        "color": "#be123c",
        "items": [
            "Perceptrons and single-layer neural nets",
            "Deep learning",
            "Pre-trained neural networks",
            "Introduction to reinforcement learning",
        ],
    },
]

MILESTONES = {
    "1": "Understanding all fields in the dataset",
    "2": "Data pre-processing strategy: how and why you add, delete, or modify features",
    "3": "Analytical strategy: what you will do and how you will measure success",
    "4": "Model implementation 1: about half the models are implemented",
    "5": "Model implementation 2: all models are implemented",
    "6": "Analysis / feedback and modifications are implemented",
    "7": "Final models and results ready for feedback",
    "8": "Report write-up draft ready",
}

POLICIES = {
    "Attendance": {
        "summary": "One free excused absence, up to two additional medically excused absences with documentation, 1% final-grade deduction per net unexcused absence, and four unexcused absences can trigger being dropped.",
        "risk": "High",
    },
    "Late work": {
        "summary": "Late work, if admitted, is penalized 25% per day or fraction thereof. The final group project cannot be submitted late for credit.",
        "risk": "High",
    },
    "Participation": {
        "summary": "Participation reflects preparedness, quality of contribution, and evidence of early, continuous, steady progress.",
        "risk": "Medium",
    },
    "Grade appeals": {
        "summary": "Students have two business days after work is returned to request a written review; the full work may be re-graded up, down, or unchanged.",
        "risk": "Medium",
    },
    "Honor code": {
        "summary": "All work must be pledged, and students are expected to use their own words and avoid unauthorized assistance.",
        "risk": "High",
    },
    "Technology": {
        "summary": "R and RStudio are expected, Keras/TensorFlow should be installed early, and Windows is preferred when possible.",
        "risk": "Medium",
    },
}

SCHEDULE_ROWS = [
    {"wk": 1, "session": 1, "day": "T", "date": "1/26", "topic": "Syllabus, Introduction and overview", "milestone": "", "notes": "", "module": "Foundations"},
    {"wk": 1, "session": 2, "day": "R", "date": "1/28", "topic": "Know your data - Data cleaning and prep tips", "milestone": "", "notes": "", "module": "Foundations"},
    {"wk": 2, "session": 3, "day": "T", "date": "2/2", "topic": "Ordinary least squares regression (OLS)", "milestone": "", "notes": "", "module": "Supervised ML"},
    {"wk": 2, "session": 4, "day": "R", "date": "2/4", "topic": "Gradient descent", "milestone": "", "notes": "", "module": "Supervised ML"},
    {"wk": 3, "session": 5, "day": "T", "date": "2/9", "topic": "Polynomial, Feature selection", "milestone": "1-1 / 1-2", "notes": "", "module": "Supervised ML"},
    {"wk": 3, "session": 6, "day": "R", "date": "2/11", "topic": "Ridge / LASSO regression", "milestone": "", "notes": "", "module": "Supervised ML"},
    {"wk": 4, "session": 7, "day": "T", "date": "2/16", "topic": "Regression Trees, random forests", "milestone": "", "notes": "", "module": "Supervised ML"},
    {"wk": 4, "session": 8, "day": "R", "date": "2/18", "topic": "Bagging, Boosting for regression", "milestone": "1-3 / 1-4 / 2-1 / 3-1", "notes": "", "module": "Supervised ML"},
    {"wk": 5, "session": 9, "day": "T", "date": "2/23", "topic": "University Holiday", "milestone": "", "notes": "", "module": "Calendar"},
    {"wk": 5, "session": 10, "day": "R", "date": "2/25", "topic": "Logistic regression", "milestone": "", "notes": "CC #1 revealed", "module": "Supervised ML"},
    {"wk": 6, "session": 11, "day": "T", "date": "3/2", "topic": "K-nearest neighbors", "milestone": "1-5 / 1-6", "notes": "CC #1 due before class", "module": "Supervised ML"},
    {"wk": 6, "session": 12, "day": "R", "date": "3/4", "topic": "Support Vector Machines (SVM)", "milestone": "1-7", "notes": "", "module": "Supervised ML"},
    {"wk": 7, "session": 13, "day": "T", "date": "3/9", "topic": "SVM for regression and anomaly detection", "milestone": "", "notes": "", "module": "Supervised ML"},
    {"wk": 7, "session": 14, "day": "R", "date": "3/11", "topic": "K-means, Classification Tree methods", "milestone": "1-8 / 2-3 / 3-2", "notes": "", "module": "Supervised ML"},
    {"wk": 8, "session": 15, "day": "T", "date": "3/16", "topic": "Hierarchical clustering", "milestone": "", "notes": "Assignment #1 due", "module": "Unsupervised ML"},
    {"wk": 8, "session": 16, "day": "R", "date": "3/18", "topic": "Social Network Analysis I", "milestone": "", "notes": "", "module": "Unsupervised ML"},
    {"wk": 9, "session": 17, "day": "T", "date": "3/23", "topic": "NO CLASS - Work on your projects", "milestone": "2-4", "notes": "", "module": "Calendar"},
    {"wk": 9, "session": 18, "day": "R", "date": "3/25", "topic": "Social Network Analysis II", "milestone": "", "notes": "CC #2 revealed", "module": "Unsupervised ML"},
    {"wk": 10, "session": 19, "day": "T", "date": "3/30", "topic": "Spidering and Scraping I", "milestone": "2-5 / 3-3 / 3-4", "notes": "CC #2 due before class", "module": "Unsupervised ML"},
    {"wk": 10, "session": 20, "day": "R", "date": "4/1", "topic": "Spidering and Scraping II", "milestone": "", "notes": "", "module": "Unsupervised ML"},
    {"wk": 11, "session": 21, "day": "T", "date": "4/6", "topic": "Spidering and scraping III", "milestone": "", "notes": "", "module": "Unsupervised ML"},
    {"wk": 11, "session": 22, "day": "R", "date": "4/8", "topic": "Natural Language Processing I", "milestone": "2-6 / 2-7 / 2-8 / 3-5", "notes": "", "module": "Unsupervised ML"},
    {"wk": 12, "session": 23, "day": "T", "date": "4/13", "topic": "NO CLASS - Work on your projects", "milestone": "", "notes": "", "module": "Calendar"},
    {"wk": 12, "session": 24, "day": "R", "date": "4/15", "topic": "University Holiday", "milestone": "", "notes": "", "module": "Calendar"},
    {"wk": 13, "session": 25, "day": "T", "date": "4/20", "topic": "Natural Language Processing II", "milestone": "3-6", "notes": "Assignment #2 due", "module": "Unsupervised ML"},
    {"wk": 13, "session": 26, "day": "R", "date": "4/22", "topic": "Artificial Neural networks I", "milestone": "", "notes": "", "module": "Neural Nets + RL"},
    {"wk": 14, "session": 27, "day": "T", "date": "4/27", "topic": "Artificial Neural networks II", "milestone": "3-7", "notes": "", "module": "Neural Nets + RL"},
    {"wk": 14, "session": 28, "day": "R", "date": "4/29", "topic": "Artificial Neural networks III", "milestone": "", "notes": "", "module": "Neural Nets + RL"},
    {"wk": 15, "session": 29, "day": "T", "date": "5/4", "topic": "Introduction to reinforcement learning", "milestone": "3-8", "notes": "", "module": "Neural Nets + RL"},
    {"wk": 15, "session": 30, "day": "R", "date": "5/6", "topic": "Project presentations", "milestone": "", "notes": "CC #3 revealed", "module": "Neural Nets + RL"},
]

QUIZ_ITEMS = [
    {
        "question": "Which part of the course grade carries the largest weight?",
        "options": ["Any single conceptual checkpoint", "Participation", "Group project", "Assignment 1"],
        "answer": "Group project",
        "explanation": "The group project is weighted at 27%, making it the single largest component.",
    },
    {
        "question": "What is the syllabus stance on student debugging?",
        "options": [
            "The instructor is expected to find code bugs for students.",
            "Students should first exhaust other resources and come with focused questions.",
            "Coding is optional in the course.",
            "Only textbook examples are allowed.",
        ],
        "answer": "Students should first exhaust other resources and come with focused questions.",
        "explanation": "The syllabus is explicit that students are primarily responsible for making their code work.",
    },
    {
        "question": "What happens to each net unexcused absence?",
        "options": [
            "No effect unless there are 4",
            "It lowers the final course grade by 1%",
            "It lowers participation only",
            "It automatically triggers a make-up assignment",
        ],
        "answer": "It lowers the final course grade by 1%",
        "explanation": "Attendance is treated as a direct final-grade penalty, not just a participation factor.",
    },
    {
        "question": "How long does a student generally have to request a grade review?",
        "options": ["24 hours", "2 business days", "1 week", "Until the next class"],
        "answer": "2 business days",
        "explanation": "The review window is two business days after work is returned or the grade is made available.",
    },
]

AI_PROMPTS = {
    "Course onboarding": "Read this BAT 3305 syllabus and produce: (1) the five biggest risks students underestimate, (2) the three most grade-leveraged habits, and (3) a first-two-weeks action plan.",
    "Assignment planning": "Based on this syllabus, design a milestone-by-milestone execution plan for the regression assignment, including what I should show at each instructor check-in.",
    "Participation strategy": "Turn this participation rubric into a concrete weekly checklist I can follow to stay in the 93-100 band.",
    "Office hours prep": "Using this syllabus, draft a highly efficient office-hours agenda that shows preparation, asks focused questions, and demonstrates progress.",
    "Policy translator": "Translate the most important BAT 3305 policies into plain English with examples of mistakes students commonly make.",
}


# -------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------
def letter_grade(score: float) -> str:
    for threshold, letter in LETTER_BANDS:
        if score >= threshold:
            return letter
    return "F"


def weighted_grade(scores: dict[str, float]) -> float:
    return sum(scores[item] * weight / 100 for item, weight in GRADE_WEIGHTS.items())


def apply_attendance_penalty(score: float, unexcused_absences: int, lates: int) -> tuple[float, float]:
    penalty = max(0, unexcused_absences) * 1.0 + max(0, lates) * 0.5
    return max(0.0, score - penalty), penalty


def project_grade_after_peer_factor(team_grade: float, expected_pct: float, actual_pct: float) -> tuple[float, float]:
    factor = 0.0 if expected_pct <= 0 else actual_pct / expected_pct
    return max(0.0, team_grade * factor), factor


def parse_milestone_count(value: str) -> int:
    return len([x for x in str(value).split("/") if x.strip()]) if value else 0


def make_schedule_df() -> pd.DataFrame:
    df = pd.DataFrame(SCHEDULE_ROWS)
    df["is_holiday"] = df["topic"].str.contains("Holiday|NO CLASS", case=False, na=False)
    df["is_deadline"] = df["notes"].str.contains("due|revealed", case=False, na=False)
    df["milestone_count"] = df["milestone"].apply(parse_milestone_count)
    df["intensity"] = df["milestone_count"] + df["is_deadline"].astype(int) + (~df["is_holiday"]).astype(int)
    df["label"] = "W" + df["wk"].astype(str) + " • " + df["date"] + " • " + df["topic"]
    return df


def init_state() -> None:
    defaults = {
        "notes": "",
        "personal_plan": "",
        "onboarding_checks": {
            "I understand the grading weights": False,
            "I understand the attendance consequences": False,
            "I understand late-work penalties": False,
            "I know the milestone system": False,
            "I know the software setup expectations": False,
            "I have a weekly work plan": False,
            "I know how I will use office hours": False,
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def progress_pct() -> int:
    checks = st.session_state["onboarding_checks"]
    return int(round(100 * sum(bool(v) for v in checks.values()) / len(checks)))


init_state()
schedule_df = make_schedule_df()

# -------------------------------------------------------------------
# Styling
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2.2rem; max-width: 1450px;}
    .hero {
        padding: 1.3rem 1.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(79,70,229,.18), rgba(14,165,233,.12), rgba(34,197,94,.10));
        border: 1px solid rgba(255,255,255,.09);
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(0,0,0,.10);
    }
    .glass {
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        min-height: 132px;
    }
    .policy-box {
        background: rgba(255,255,255,.025);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 18px;
        padding: 1rem 1rem .9rem 1rem;
        min-height: 150px;
    }
    .pill {
        display: inline-block;
        font-size: .75rem;
        padding: .22rem .55rem;
        border-radius: 999px;
        background: rgba(99,102,241,.18);
        border: 1px solid rgba(99,102,241,.35);
        margin-right: .35rem;
        margin-bottom: .35rem;
    }
    .tiny {font-size: .88rem; opacity: .88;}
    .subtitle {font-size: 1.02rem; opacity: .88; margin-top: .25rem;}
    div[data-testid='stMetric'] {
        background: rgba(255,255,255,.025);
        border: 1px solid rgba(255,255,255,.08);
        padding: .75rem;
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
st.sidebar.markdown("## BAT 3305")
st.sidebar.caption("Interactive Syllabus Studio")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Syllabus Atlas",
        "Assessment Lab",
        "Timeline Studio",
        "Policy Engine",
        "Strategy Builder",
        "Syllabus Quiz",
        "AI Toolkit",
    ],
)

st.sidebar.progress(progress_pct() / 100, text=f"Onboarding progress: {progress_pct()}%")

with st.sidebar.expander("Onboarding checklist", expanded=True):
    for key, value in st.session_state["onboarding_checks"].items():
        st.session_state["onboarding_checks"][key] = st.checkbox(key, value=value)

with st.sidebar.expander("Running notes", expanded=False):
    st.session_state["notes"] = st.text_area(
        "Questions, reminders, or office-hour topics",
        value=st.session_state["notes"],
        height=180,
        placeholder="Example: Ask about what counts as strong milestone evidence for the group project.",
    )

# -------------------------------------------------------------------
# Page helpers
# -------------------------------------------------------------------
def render_hero():
    st.markdown(
        f"""
        <div class='hero'>
            <div class='pill'>{COURSE_META['course']}</div>
            <div class='pill'>{COURSE_META['title']}</div>
            <div class='pill'>{COURSE_META['meeting']}</div>
            <h1 style='margin:.35rem 0 .15rem 0;'>{COURSE_META['course']} • {COURSE_META['title']}</h1>
            <div class='subtitle'>{COURSE_META['focus']}</div>
            <div class='tiny' style='margin-top:.5rem;'>Instructor: {COURSE_META['instructor']} • Format: {COURSE_META['format']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_weights_figure() -> go.Figure:
    weight_df = pd.DataFrame({"Component": list(GRADE_WEIGHTS.keys()), "Weight": list(GRADE_WEIGHTS.values())})
    fig = px.bar(
        weight_df,
        x="Weight",
        y="Component",
        orientation="h",
        text="Weight",
        color="Weight",
        color_continuous_scale="Blues",
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    return fig


def build_timeline_figure(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="wk",
        y="module",
        size="intensity",
        color="module",
        hover_name="topic",
        hover_data={"date": True, "milestone": True, "notes": True, "wk": True, "intensity": True},
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), legend_title_text="Module")
    fig.update_xaxes(dtick=1, title="Week")
    fig.update_yaxes(title="")
    return fig


def build_milestone_heatmap(df: pd.DataFrame) -> go.Figure:
    heat = df.groupby(["wk", "module"], as_index=False)["milestone_count"].sum()
    pivot = heat.pivot(index="module", columns="wk", values="milestone_count").fillna(0)
    fig = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        labels=dict(x="Week", y="Module", color="Milestones"),
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    return fig


def required_average_for_target(current_scores: dict[str, float], unlocked_items: list[str], target_score: float) -> float | None:
    locked_total = 0.0
    remaining_weight = 0.0
    for item, weight in GRADE_WEIGHTS.items():
        if item in unlocked_items:
            remaining_weight += weight
        else:
            locked_total += current_scores[item] * weight / 100
    if remaining_weight <= 0:
        return None
    needed_points = target_score - locked_total
    return needed_points / (remaining_weight / 100)


# -------------------------------------------------------------------
# Pages
# -------------------------------------------------------------------
if page == "Dashboard":
    render_hero()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Class meetings", len(schedule_df))
    m2.metric("Graded components", len(GRADE_WEIGHTS))
    m3.metric("Milestone framework", "8 steps")
    m4.metric("Applied emphasis", "High")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Why this course feels demanding")
        st.write(
            "The syllabus frames machine learning as a full analytical workflow: understand the data, prepare it intelligently, choose methods well, run the models, interpret results, and communicate the business story. "
            "The tone is intentionally demanding and repeatedly emphasizes preparation, independence, and steady progress."
        )
        st.markdown("### Core design logic")
        st.markdown(
            "<span class='pill'>Applied ML</span>"
            "<span class='pill'>Real datasets</span>"
            "<span class='pill'>Milestone-driven</span>"
            "<span class='pill'>Interpretation matters</span>"
            "<span class='pill'>Professional execution</span>",
            unsafe_allow_html=True,
        )
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Course objectives")
            for item in COURSE_OBJECTIVES:
                st.markdown(f"- {item}")
        with c2:
            st.markdown("#### Expectation signals")
            for item in EXPECTATION_STATEMENTS:
                st.markdown(f"- {item}")

    with right:
        st.subheader("Assessment architecture")
        st.plotly_chart(build_weights_figure(), use_container_width=True)

    st.subheader("Policy radar")
    cols = st.columns(3)
    for i, (title, body) in enumerate(POLICIES.items()):
        with cols[i % 3]:
            risk_badge = f"<div class='pill'>{body['risk']} consequence</div>"
            st.markdown(
                f"<div class='policy-box'><h4 style='margin-top:0;'>{title}</h4>{risk_badge}<div class='tiny'>{body['summary']}</div></div>",
                unsafe_allow_html=True,
            )

    st.subheader("Course tempo view")
    col_a, col_b = st.columns([1.15, 0.85])
    with col_a:
        st.plotly_chart(build_timeline_figure(schedule_df), use_container_width=True)
    with col_b:
        st.plotly_chart(build_milestone_heatmap(schedule_df), use_container_width=True)
        high_pressure = schedule_df.sort_values("intensity", ascending=False).head(5)[["wk", "date", "topic", "notes"]]
        st.markdown("#### Highest-pressure sessions")
        st.dataframe(high_pressure, use_container_width=True, hide_index=True)

elif page == "Syllabus Atlas":
    render_hero()
    st.title("Syllabus Atlas")
    st.caption("A navigable map of topics, structure, milestones, and design assumptions.")

    tab1, tab2, tab3, tab4 = st.tabs(["Topic map", "Milestones", "Assessment logic", "Expectation decoder"])

    with tab1:
        selected = st.selectbox("Focus on a module", [x["module"] for x in TOPIC_BLOCKS])
        module_cards = st.columns(4)
        for idx, block in enumerate(TOPIC_BLOCKS):
            with module_cards[idx]:
                st.markdown(
                    f"<div class='glass'><h4 style='margin-top:0'>{block['module']}</h4><div class='tiny'>{block['theme']}</div><div style='margin-top:.55rem;font-size:.92rem;'><b>{len(block['items'])}</b> topic elements</div></div>",
                    unsafe_allow_html=True,
                )
        for block in TOPIC_BLOCKS:
            expanded = block["module"] == selected
            with st.expander(f"{block['module']} • {block['theme']}", expanded=expanded):
                for item in block["items"]:
                    st.markdown(f"- {item}")

    with tab2:
        milestone_df = pd.DataFrame({"Milestone": list(MILESTONES.keys()), "Meaning": list(MILESTONES.values())})
        st.dataframe(milestone_df, use_container_width=True, hide_index=True)
        chosen = st.select_slider("Which milestone are you planning around?", options=list(MILESTONES.keys()), value="3")
        st.success(f"Milestone {chosen}: {MILESTONES[chosen]}")

        st.markdown("#### Why this matters")
        st.write(
            "The milestone system makes the course less about one-time submission and more about visible evidence of process quality. "
            "It rewards early starts, instructor feedback loops, and incremental refinement."
        )

    with tab3:
        weight_df = pd.DataFrame({"Component": list(GRADE_WEIGHTS.keys()), "Weight": list(GRADE_WEIGHTS.values())})
        weight_df["Bucket"] = [
            "Conceptual verification", "Conceptual verification", "Conceptual verification",
            "Individual applied work", "Individual applied work", "Collaborative applied work", "Behavioral/professional"
        ]
        st.dataframe(weight_df, use_container_width=True, hide_index=True)
        bucket_fig = px.sunburst(weight_df, path=["Bucket", "Component"], values="Weight", color="Bucket")
        bucket_fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(bucket_fig, use_container_width=True)

    with tab4:
        st.markdown("#### Translate the syllabus tone")
        option = st.radio(
            "Choose a lens",
            ["Student behavior", "Instructor expectations", "Where students usually fail"],
            horizontal=True,
        )
        if option == "Student behavior":
            st.info("The syllabus rewards initiative, preparation, professionalism, and visible progress. Passive attendance is not enough.")
        elif option == "Instructor expectations":
            st.info("The course expects students to be analytically independent, responsible for debugging, and able to justify methods and results.")
        else:
            st.warning("Common failure modes implied by the syllabus: falling behind, treating milestones casually, weak participation, and underestimating attendance penalties.")

elif page == "Assessment Lab":
    render_hero()
    st.title("Assessment Lab")
    st.caption("Model grades, peer-factor effects, attendance penalties, and target-grade pathways.")

    st.subheader("1) Current or projected scores")
    left, right = st.columns(2)
    scores = {}
    with left:
        scores["Conceptual checkpoint #1"] = st.slider("Conceptual checkpoint #1", 0, 100, 86)
        scores["Conceptual checkpoint #2"] = st.slider("Conceptual checkpoint #2", 0, 100, 88)
        scores["Conceptual checkpoint #3"] = st.slider("Conceptual checkpoint #3", 0, 100, 90)
        scores["Assignment 1 (Regression)"] = st.slider("Assignment 1 (Regression)", 0, 100, 87)
    with right:
        scores["Assignment 2 (Classification)"] = st.slider("Assignment 2 (Classification)", 0, 100, 89)
        scores["Group project"] = st.slider("Group project", 0, 100, 93)
        scores["Participation in class"] = st.slider("Participation in class", 0, 100, 92)

    st.subheader("2) Policy-related adjustments")
    c1, c2, c3, c4 = st.columns(4)
    team_grade = c1.slider("Team project grade", 0, 100, int(scores["Group project"]))
    expected_pct = c2.number_input("Expected contribution %", min_value=1.0, max_value=100.0, value=33.0)
    actual_pct = c3.number_input("Peer-assessed contribution %", min_value=0.0, max_value=100.0, value=33.0)
    unexcused_absences = c4.number_input("Net unexcused absences", min_value=0, max_value=10, value=0)
    lates = st.slider("Late arrivals", 0, 12, 0)

    individual_project_grade, peer_factor = project_grade_after_peer_factor(team_grade, expected_pct, actual_pct)
    adjusted_scores = scores.copy()
    adjusted_scores["Group project"] = min(100.0, individual_project_grade)

    weighted = weighted_grade(scores)
    weighted_after_peer = weighted_grade(adjusted_scores)
    final_score, attendance_penalty = apply_attendance_penalty(weighted_after_peer, unexcused_absences, lates)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Weighted score", f"{weighted:.2f}")
    m2.metric("Peer factor", f"{peer_factor:.2f}")
    m3.metric("Attendance penalty", f"-{attendance_penalty:.2f}")
    m4.metric("Projected final", f"{final_score:.2f} ({letter_grade(final_score)})")

    score_flow = pd.DataFrame(
        {
            "Stage": ["Base weighted", "After peer adjustment", "After attendance"],
            "Score": [weighted, weighted_after_peer, final_score],
        }
    )
    flow_fig = px.line(score_flow, x="Stage", y="Score", markers=True)
    flow_fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(flow_fig, use_container_width=True)

    st.subheader("3) Target-grade planner")
    target_label = st.selectbox("Target letter grade", [x[1] for x in LETTER_BANDS[:-1]])
    target_score = next(th for th, letter in LETTER_BANDS if letter == target_label)
    remaining_items = st.multiselect(
        "Treat these as not yet completed / still improvable",
        list(GRADE_WEIGHTS.keys()),
        default=["Conceptual checkpoint #3", "Assignment 2 (Classification)", "Group project", "Participation in class"],
    )
    needed_avg = required_average_for_target(scores, remaining_items, target_score)
    if needed_avg is None:
        st.info("Choose at least one remaining component.")
    else:
        if needed_avg <= 100:
            st.success(f"To finish with a {target_label}, you need an average of about {needed_avg:.2f} across the remaining items selected.")
        else:
            st.error(f"A {target_label} is mathematically out of reach under the assumptions above. Required remaining average: {needed_avg:.2f}.")

    st.subheader("4) Sensitivity grid")
    grid_rows = []
    for absence in range(0, 5):
        for pf in [0.85, 0.95, 1.00, 1.05]:
            temp_scores = scores.copy()
            temp_scores["Group project"] = min(100.0, scores["Group project"] * pf)
            temp_final, _ = apply_attendance_penalty(weighted_grade(temp_scores), absence, lates)
            grid_rows.append({"Absences": absence, "Peer factor": pf, "Final": round(temp_final, 2)})
    grid_df = pd.DataFrame(grid_rows)
    heat = grid_df.pivot(index="Absences", columns="Peer factor", values="Final")
    heat_fig = px.imshow(heat, text_auto=True, color_continuous_scale="Viridis", aspect="auto")
    heat_fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(heat_fig, use_container_width=True)

elif page == "Timeline Studio":
    render_hero()
    st.title("Timeline Studio")
    st.caption("Filter the schedule, surface deadlines, and locate the pressure points of the semester.")

    c1, c2, c3, c4 = st.columns(4)
    week_range = c1.slider("Week range", 1, 15, (1, 15))
    modules = c2.multiselect("Modules", sorted(schedule_df["module"].unique()), default=sorted(schedule_df["module"].unique()))
    show_only_action = c3.toggle("Only milestone / deadline rows", value=False)
    keyword = c4.text_input("Keyword filter", value="")

    filtered = schedule_df[
        (schedule_df["wk"] >= week_range[0])
        & (schedule_df["wk"] <= week_range[1])
        & (schedule_df["module"].isin(modules))
    ].copy()
    if show_only_action:
        filtered = filtered[(filtered["milestone"].str.strip() != "") | (filtered["notes"].str.strip() != "")]
    if keyword.strip():
        mask = filtered["topic"].str.contains(keyword, case=False, na=False) | filtered["notes"].str.contains(keyword, case=False, na=False)
        filtered = filtered[mask]

    st.dataframe(filtered[["wk", "session", "day", "date", "module", "topic", "milestone", "notes"]], use_container_width=True, hide_index=True)

    left, right = st.columns([1.05, 0.95])
    with left:
        st.plotly_chart(build_timeline_figure(filtered if not filtered.empty else schedule_df), use_container_width=True)
    with right:
        density = filtered.groupby("wk", as_index=False).agg(
            sessions=("session", "count"),
            milestones=("milestone_count", "sum"),
            deadlines=("is_deadline", "sum"),
        )
        density_fig = px.bar(density, x="wk", y=["sessions", "milestones", "deadlines"], barmode="group")
        density_fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="Week")
        st.plotly_chart(density_fig, use_container_width=True)

    st.subheader("Pressure-point explorer")
    ranked = filtered.sort_values(["intensity", "wk", "session"], ascending=[False, True, True])
    for _, row in ranked.head(8).iterrows():
        with st.expander(f"Week {row['wk']} • {row['date']} • {row['topic']}"):
            st.write(f"**Module:** {row['module']}")
            st.write(f"**Milestone(s):** {row['milestone'] or '—'}")
            st.write(f"**Notes:** {row['notes'] or '—'}")
            st.write(f"**Intensity score:** {row['intensity']}")

elif page == "Policy Engine":
    render_hero()
    st.title("Policy Engine")
    st.caption("Convert policy text into lived consequences through scenarios and calculators.")

    scenario = st.selectbox(
        "Choose a scenario",
        [
            "Late-work calculator",
            "Attendance consequence model",
            "Project contribution mismatch",
            "Grade-appeal pathway",
            "Participation band estimator",
        ],
    )

    if scenario == "Late-work calculator":
        days_late = st.slider("Days late (or fraction thereof)", 0.0, 4.0, 1.5, 0.5)
        original = st.slider("Original score", 0, 100, 92)
        penalty_pct = math.ceil(days_late) * 25
        final = max(0.0, original * (1 - penalty_pct / 100))
        a, b, c = st.columns(3)
        a.metric("Penalty rate", f"{penalty_pct}%")
        b.metric("Original", f"{original}")
        c.metric("Adjusted", f"{final:.1f}")
        st.info("Because the rule is 25% per day or fraction thereof, 1.5 days is treated as 2 full days for penalty purposes.")

    elif scenario == "Attendance consequence model":
        pre = st.slider("Pre-penalty final grade", 0, 100, 88)
        absences = st.slider("Net unexcused absences", 0, 6, 2)
        lates = st.slider("Late arrivals", 0, 10, 1)
        after, penalty = apply_attendance_penalty(pre, absences, lates)
        a, b, c = st.columns(3)
        a.metric("Penalty", f"-{penalty:.1f}")
        b.metric("Projected final", f"{after:.1f}")
        c.metric("Letter grade", letter_grade(after))
        if absences >= 4:
            st.error("The syllabus indicates that four unexcused absences can result in being dropped from the course.")

    elif scenario == "Project contribution mismatch":
        team = st.slider("Team project grade", 0, 100, 95)
        expected = st.number_input("Expected contribution %", min_value=1.0, max_value=100.0, value=33.0)
        actual = st.number_input("Actual peer-assessed contribution %", min_value=0.0, max_value=100.0, value=30.0)
        final, factor = project_grade_after_peer_factor(team, expected, actual)
        a, b = st.columns(2)
        a.metric("Peer factor", f"{factor:.2f}")
        b.metric("Individual project grade", f"{final:.1f}")
        st.write("This models the example embedded in the syllabus, where a student can be scaled down if teammates assess below-expected contribution.")

    elif scenario == "Grade-appeal pathway":
        elapsed = st.radio("How long since the grade was returned?", ["1 business day", "2 business days", "3+ business days"], horizontal=True)
        if elapsed in {"1 business day", "2 business days"}:
            st.success("A written email request is still within the typical allowed window.")
            st.write("The syllabus warns that the full work may be re-reviewed, so the result could go up, go down, or remain unchanged.")
        else:
            st.error("The ordinary review window has passed according to the syllabus.")

    elif scenario == "Participation band estimator":
        frequency = st.select_slider("Frequency", ["Seldom", "Most classes", "Every class"], value="Most classes")
        quality = st.select_slider("Comment quality", ["Low", "Medium", "Medium-high", "High"], value="Medium-high")
        progress = st.toggle("Evidence of early, steady, continuous progress", value=True)
        civility = st.toggle("Professional, civil, supportive participation", value=True)
        if frequency == "Every class" and quality in {"Medium-high", "High"} and progress and civility:
            st.success("This resembles the top participation band in spirit.")
        elif frequency in {"Most classes", "Every class"} and quality in {"Medium", "Medium-high", "High"} and progress:
            st.info("This resembles a mid-to-strong participation profile.")
        else:
            st.warning("The syllabus suggests this profile would drift into lower participation bands.")

elif page == "Strategy Builder":
    render_hero()
    st.title("Strategy Builder")
    st.caption("Turn the syllabus into a semester operating system tailored to the student profile.")

    left, right = st.columns([1, 1])
    with left:
        strength = st.selectbox(
            "Strongest starting area",
            ["Programming", "Statistics", "Writing / communication", "Domain knowledge", "None strongly"],
        )
        risk = st.selectbox(
            "Likeliest failure mode",
            ["Falling behind", "Debugging bottlenecks", "Weak reporting / presentation", "Passive participation", "Attendance slippage"],
        )
        hours = st.slider("Planned weekly hours for this course", 2, 20, 8)
        team_style = st.selectbox("How do you usually behave in teams?", ["Reliable contributor", "Over-functioner", "Uneven pace", "Quiet but solid", "Needs structure"])

    with right:
        setup_checks = {
            "R installed": st.checkbox("R installed", value=True),
            "RStudio installed": st.checkbox("RStudio installed", value=True),
            "Keras / TensorFlow plan": st.checkbox("Keras / TensorFlow plan", value=False),
            "Textbook located": st.checkbox("Textbook located", value=True),
            "Office-hours strategy ready": st.checkbox("Office-hours strategy ready", value=False),
        }
        readiness = sum(int(v) for v in setup_checks.values())
        st.metric("Operational readiness", f"{readiness}/{len(setup_checks)}")

    recs = []
    if strength == "Programming":
        recs.append("Exploit coding speed, but deliberately invest in interpretation and business framing so implementation does not outpace insight.")
    elif strength == "Statistics":
        recs.append("Use statistical intuition to choose methods wisely, but schedule dedicated build time so implementation does not become the bottleneck.")
    elif strength == "Writing / communication":
        recs.append("You can differentiate through reports and presentations; offset this by starting coding milestones unusually early.")
    elif strength == "Domain knowledge":
        recs.append("Use domain intuition to generate stronger features and better problem framing, but still verify method fit carefully.")
    else:
        recs.append("Start with operational basics: software, textbook, calendar, and milestone pacing before anything else.")

    risk_map = {
        "Falling behind": "Treat every milestone as an internal due date and schedule work before instructor checkpoints rather than after them.",
        "Debugging bottlenecks": "Create a debugging playbook: isolate the issue, reduce the example, search docs and forums, then ask one sharply bounded question.",
        "Weak reporting / presentation": "After every modeling step, write one sentence explaining the business implication; do not wait until the final report to translate results.",
        "Passive participation": "Prepare one substantive question or insight before each class and tie it to reading or project progress.",
        "Attendance slippage": "Protect class time as non-negotiable because attendance hits the final grade directly and can cascade into course failure.",
    }
    recs.append(risk_map[risk])

    if hours < 5:
        recs.append("The planned weekly time is likely too low for the tone and structure of this course.")
    elif hours < 8:
        recs.append("This may work, but only with unusual consistency and early starts.")
    else:
        recs.append("Your planned weekly time is closer to what the syllabus implicitly demands.")

    if team_style in {"Uneven pace", "Needs structure"}:
        recs.append("Use a formal team cadence and visible ownership tracking, because peer assessment can materially change the project grade.")

    st.subheader("Your recommended operating system")
    for rec in recs:
        st.markdown(f"- {rec}")

    st.subheader("Build a personal semester plan")
    st.session_state["personal_plan"] = st.text_area(
        "Write your plan",
        value=st.session_state["personal_plan"],
        height=180,
        placeholder="Example: I will review the schedule every Sunday, begin milestones one week early, attend office hours once per assignment, and keep attendance perfect.",
    )

    payload = {
        "onboarding_progress_percent": progress_pct(),
        "readiness": readiness,
        "recommendations": recs,
        "notes": st.session_state["notes"],
        "personal_plan": st.session_state["personal_plan"],
    }
    st.download_button(
        "Download strategy bundle (JSON)",
        data=json.dumps(payload, indent=2),
        file_name="bat3305_strategy_bundle.json",
        mime="application/json",
    )

elif page == "Syllabus Quiz":
    render_hero()
    st.title("Syllabus Quiz")
    st.caption("Use retrieval and explanation, not just recall, to make the syllabus stick.")

    correct = 0
    for idx, item in enumerate(QUIZ_ITEMS, start=1):
        st.markdown(f"### Question {idx}")
        choice = st.radio(item["question"], item["options"], key=f"quiz_{idx}")
        if choice == item["answer"]:
            st.success(item["explanation"])
            correct += 1
        else:
            st.info(item["explanation"])

    score_pct = 100 * correct / len(QUIZ_ITEMS)
    st.metric("Quiz score", f"{correct}/{len(QUIZ_ITEMS)} • {score_pct:.0f}%")
    if score_pct == 100:
        st.success("You have a strong operational grasp of the syllabus.")
    elif score_pct >= 75:
        st.info("Good understanding, but review the areas you missed before the semester accelerates.")
    else:
        st.warning("There are still important policy and structure details worth reviewing closely.")

elif page == "AI Toolkit":
    render_hero()
    st.title("AI Toolkit")
    st.caption("Ready-to-use prompts that turn the syllabus into a live advisor, planner, and translator.")

    st.subheader("Prompt library")
    prompt_name = st.selectbox("Choose a prompt", list(AI_PROMPTS.keys()))
    st.code(AI_PROMPTS[prompt_name], language="markdown")

    st.subheader("Custom prompt builder")
    goal = st.selectbox("What do you want the AI to do?", [
        "Summarize the course",
        "Build a study plan",
        "Decode a policy",
        "Prepare for office hours",
        "Plan an assignment",
        "Optimize participation",
    ])
    tone = st.selectbox("Tone", ["Direct", "Supportive", "Strict", "Analytical", "Executive summary"])
    output = st.selectbox("Output format", ["Bullet list", "Checklist", "Table", "Step-by-step plan", "Risk memo"])
    custom = (
        f"Using the BAT 3305 syllabus, {goal.lower()} in a {tone.lower()} tone. "
        f"Return the answer as a {output.lower()} and make the advice specific to this course's grading, milestones, policies, and expectations."
    )
    st.code(custom, language="markdown")

    st.subheader("Suggested uses")
    use_cols = st.columns(3)
    use_cols[0].markdown("- Convert the attendance and late-work rules into examples\n- Ask for milestone-specific checklists\n- Create a first-two-weeks onboarding plan")
    use_cols[1].markdown("- Draft office-hours agendas\n- Compare what matters most for assignments vs. project\n- Translate instructor tone into action items")
    use_cols[2].markdown("- Make a participation checklist\n- Generate a risk register for the semester\n- Build a personal pacing plan")

st.caption("Interactive prototype built from the BAT 3305 syllabus.")
