
import math
import json
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="BAT 3305 Interactive Syllabus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Data from the uploaded syllabus
# -----------------------------
GRADE_WEIGHTS = {
    "Conceptual checkpoint #1": 7,
    "Conceptual checkpoint #2": 7,
    "Conceptual checkpoint #3": 7,
    "Assignment 1 (Regression)": 21,
    "Assignment 2 (Classification)": 21,
    "Group project": 27,
    "Participation in class": 10,
}

TOPICS = [
    {
        "module": "Foundations",
        "items": [
            "Introduction to ML and review of fundamental concepts",
            "Supervised vs. unsupervised ML",
            "Data cleaning and preparation",
            "Matrix algebra review",
            "Multivariate ordinary least squares regression",
        ],
    },
    {
        "module": "Supervised ML",
        "items": [
            "OLS as a machine learning method",
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
        "items": [
            "K-means clustering",
            "Hierarchical clustering",
            "Social network analysis",
            "Text mining",
            "PERL and regular expressions",
            "Spidering, scraping, parsing, cleaning and extraction",
            "Word frequencies, sentiment analysis, LDA topic modeling",
        ],
    },
    {
        "module": "Neural Nets + RL",
        "items": [
            "Perceptrons and single-layer neural nets",
            "Deep learning",
            "Pre-trained neural networks",
            "Introduction to reinforcement learning",
        ],
    },
]

SCHEDULE_ROWS = [
    {"wk":1,"session":1,"day":"T","date":"1/26","topic":"Syllabus, Introduction and overview","milestone":"","notes":""},
    {"wk":1,"session":2,"day":"R","date":"1/28","topic":"Know your data - Data cleaning and prep tips","milestone":"","notes":""},
    {"wk":2,"session":3,"day":"T","date":"2/2","topic":"Ordinary least squares regression (OLS)","milestone":"","notes":""},
    {"wk":2,"session":4,"day":"R","date":"2/4","topic":"Gradient descent","milestone":"","notes":""},
    {"wk":3,"session":5,"day":"T","date":"2/9","topic":"Polynomial, Feature selection","milestone":"1-1 / 1-2","notes":""},
    {"wk":3,"session":6,"day":"R","date":"2/11","topic":"Ridge / LASSO regression","milestone":"","notes":""},
    {"wk":4,"session":7,"day":"T","date":"2/16","topic":"Regression Trees, random forests","milestone":"","notes":""},
    {"wk":4,"session":8,"day":"R","date":"2/18","topic":"Bagging, Boosting for regression","milestone":"1-3 / 1-4 / 2-1 / 3-1","notes":""},
    {"wk":5,"session":9,"day":"T","date":"2/23","topic":"University Holiday","milestone":"","notes":""},
    {"wk":5,"session":10,"day":"R","date":"2/25","topic":"Logistic regression","milestone":"","notes":"CC #1 revealed"},
    {"wk":6,"session":11,"day":"T","date":"3/2","topic":"K-nearest neighbors","milestone":"1-5 / 1-6","notes":"CC #1 due before class"},
    {"wk":6,"session":12,"day":"R","date":"3/4","topic":"Support Vector Machines (SVM)","milestone":"1-7","notes":""},
    {"wk":7,"session":13,"day":"T","date":"3/9","topic":"SVM for regression and anomaly detection","milestone":"","notes":""},
    {"wk":7,"session":14,"day":"R","date":"3/11","topic":"K-means, Classification Tree methods","milestone":"1-8 / 2-3 / 3-2","notes":""},
    {"wk":8,"session":15,"day":"T","date":"3/16","topic":"Hierarchical clustering","milestone":"","notes":"Assignment #1 due"},
    {"wk":8,"session":16,"day":"R","date":"3/18","topic":"Social Network Analysis I","milestone":"","notes":""},
    {"wk":9,"session":17,"day":"T","date":"3/23","topic":"NO CLASS - Work on your projects","milestone":"2-4","notes":""},
    {"wk":9,"session":18,"day":"R","date":"3/25","topic":"Social Network Analysis II","milestone":"","notes":"CC #2 revealed"},
    {"wk":10,"session":19,"day":"T","date":"3/30","topic":"Spidering and Scraping I","milestone":"2-5 / 3-3 / 3-4","notes":"CC #2 due before class"},
    {"wk":10,"session":20,"day":"R","date":"4/1","topic":"Spidering and Scraping II","milestone":"","notes":""},
    {"wk":11,"session":21,"day":"T","date":"4/6","topic":"Spidering and scraping III","milestone":"","notes":""},
    {"wk":11,"session":22,"day":"R","date":"4/8","topic":"Natural Language Processing I","milestone":"2-6 / 2-7 / 2-8 / 3-5","notes":""},
    {"wk":12,"session":23,"day":"T","date":"4/13","topic":"NO CLASS - Work on your projects","milestone":"","notes":""},
    {"wk":12,"session":24,"day":"R","date":"4/15","topic":"University Holiday","milestone":"","notes":""},
    {"wk":13,"session":25,"day":"T","date":"4/20","topic":"Natural Language Processing II","milestone":"3-6","notes":"Assignment #2 due"},
    {"wk":13,"session":26,"day":"R","date":"4/22","topic":"Artificial Neural networks I","milestone":"","notes":""},
    {"wk":14,"session":27,"day":"T","date":"4/27","topic":"Artificial Neural networks II","milestone":"3-7","notes":""},
    {"wk":14,"session":28,"day":"R","date":"4/29","topic":"Artificial Neural networks III","milestone":"","notes":""},
    {"wk":15,"session":29,"day":"T","date":"5/4","topic":"Introduction to reinforcement learning","milestone":"3-8","notes":""},
    {"wk":15,"session":30,"day":"R","date":"5/6","topic":"Project presentations","milestone":"","notes":"CC #3 revealed"},
]

MILESTONES = {
    "1": "Understanding all fields in the dataset",
    "2": "Data pre-processing strategy: how and why features are added, deleted, or modified",
    "3": "Analytical strategy: what you are going to do and how; how you will measure success",
    "4": "Model implementation 1: about half the models are implemented",
    "5": "Model implementation 2: all models are implemented",
    "6": "Analysis / feedback and modifications needed are implemented",
    "7": "Final models and results ready for feedback",
    "8": "Report write-up draft ready",
}

POLICY_CARDS = [
    ("Attendance", "1 free excused absence, up to 2 additional medical excused absences with documentation; each net unexcused absence lowers the final course grade by 1%; 4 unexcused absences can lead to being dropped."),
    ("Late work", "Late work, if admitted, receives a 25% penalty per day or fraction thereof. The final group project cannot be submitted late for credit."),
    ("Participation", "Based on preparedness, meaningful contributions, and evidence of early, steady, continuous progress."),
    ("Honor code", "All submitted work must be pledged. Use your own words or risk a plagiarism charge."),
    ("Technology expectations", "R and RStudio are expected. Keras and TensorFlow should be installed early. Windows is preferred if possible."),
    ("Communication", "The syllabus emphasizes proactive help-seeking, organized requests, and using office hours strategically."),
]

def init_state():
    defaults = {
        "checklist": {
            "Read the course overview": False,
            "Review grading weights": False,
            "Check the schedule": False,
            "Understand attendance policy": False,
            "Understand late penalties": False,
            "Locate milestone system": False,
            "Confirm software setup expectations": False,
        },
        "notes": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def weighted_grade(values_dict):
    total = 0
    for item, weight in GRADE_WEIGHTS.items():
        total += values_dict[item] * weight / 100
    return total

def letter_grade(score):
    if score >= 93:
        return "A"
    if score >= 90:
        return "A-"
    if score >= 87:
        return "B+"
    if score >= 83:
        return "B"
    if score >= 80:
        return "B-"
    if score >= 77:
        return "C+"
    if score >= 73:
        return "C"
    if score >= 70:
        return "C-"
    if score >= 67:
        return "D+"
    if score >= 60:
        return "D"
    return "F"

def apply_attendance_penalty(score, unexcused_absences, lates):
    penalty = max(0, unexcused_absences) * 1.0 + lates * 0.5
    return max(0, score - penalty), penalty

def progress_pct():
    checks = st.session_state["checklist"]
    return int(round(100 * sum(checks.values()) / len(checks)))

init_state()

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.hero {
    padding: 1.2rem 1.4rem;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(21,101,192,.12), rgba(76,175,80,.10));
    border: 1px solid rgba(120,120,120,.18);
    margin-bottom: 1rem;
}
.metric-card {
    padding: .9rem 1rem;
    border-radius: 16px;
    background: rgba(250,250,250,.02);
    border: 1px solid rgba(120,120,120,.18);
}
.policy-card {
    padding: .9rem 1rem;
    border-radius: 14px;
    border: 1px solid rgba(120,120,120,.18);
    background: rgba(250,250,250,.02);
    min-height: 140px;
}
.small-muted {font-size: 0.92rem; opacity: .85;}
.big-number {font-size: 2rem; font-weight: 700; margin-bottom: .2rem;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("BAT 3305")
st.sidebar.caption("Interactive syllabus prototype")
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Course Explorer",
        "Grade Simulator",
        "Schedule Navigator",
        "Policy Scenarios",
        "Student Success Planner",
    ],
)

pct = progress_pct()
st.sidebar.progress(pct / 100, text=f"Onboarding progress: {pct}%")

with st.sidebar.expander("Quick-start checklist", expanded=True):
    for k, v in st.session_state["checklist"].items():
        st.session_state["checklist"][k] = st.checkbox(k, value=v)

with st.sidebar.expander("Personal notes"):
    st.session_state["notes"] = st.text_area(
        "Questions, reminders, or office-hour topics",
        value=st.session_state["notes"],
        height=140,
        placeholder="Example: Ask about milestone expectations for Assignment 1."
    )

# -----------------------------
# Pages
# -----------------------------
if page == "Home":
    st.markdown("""
    <div class="hero">
        <h1 style="margin-bottom:.2rem;">BAT 3305 — Machine Learning</h1>
        <div class="small-muted">A high-interactivity syllabus prototype built from the uploaded course syllabus.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Major graded items", len(GRADE_WEIGHTS))
    c2.metric("Class meetings", len(SCHEDULE_ROWS))
    c3.metric("Milestone framework", "8 steps")
    c4.metric("Course emphasis", "Applied ML")

    st.write("")
    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.subheader("What this course is trying to do")
        st.write(
            "This course frames machine learning as an applied analytics toolkit for deriving "
            "meaningful insight from small to medium in-memory datasets. The emphasis is not only "
            "running models, but also choosing methods appropriately, preparing data well, interpreting "
            "results, and telling the full story from data to actionable recommendations."
        )

        st.subheader("What makes this prototype interactive")
        st.markdown("""
        - Explore grading consequences with a live simulator
        - Filter the full class schedule by module, deliverable, or week
        - Test your understanding through policy scenarios
        - Build a semester action plan around milestones and software setup
        - Use checklists and notes as a live onboarding layer
        """)

    with col2:
        st.subheader("Syllabus heatmap")
        summary_df = pd.DataFrame({
            "Area": ["Grading", "Assignments", "Policies", "Schedule", "Milestones", "Tech setup"],
            "Importance (prototype)": [10, 10, 9, 9, 8, 7]
        })
        st.bar_chart(summary_df.set_index("Area"))

        st.subheader("Core workflow")
        st.info(
            "Know the data → choose the method → implement the model → compare performance "
            "→ interpret the results → communicate the story."
        )

    st.subheader("Key policy cards")
    cols = st.columns(3)
    for i, (title, body) in enumerate(POLICY_CARDS):
        with cols[i % 3]:
            st.markdown(
                f"<div class='policy-card'><h4>{title}</h4><div class='small-muted'>{body}</div></div>",
                unsafe_allow_html=True,
            )

elif page == "Course Explorer":
    st.title("Course Explorer")
    st.caption("Navigate the course structure by theme, skills, and expectations.")

    tab1, tab2, tab3 = st.tabs(["Topic map", "Grading architecture", "Milestones"])

    with tab1:
        selected_module = st.selectbox(
            "Jump to a module",
            [x["module"] for x in TOPICS]
        )
        for block in TOPICS:
            expanded = block["module"] == selected_module
            with st.expander(block["module"], expanded=expanded):
                for item in block["items"]:
                    st.markdown(f"- {item}")

        st.write("")
        st.subheader("Self-check")
        topic_confidence = st.slider("How ready do you feel for this course right now?", 0, 100, 55)
        if topic_confidence < 40:
            st.warning("You may want an early software setup check, textbook review, and office-hours plan.")
        elif topic_confidence < 75:
            st.info("You have a workable starting point; focus on consistency and milestone discipline.")
        else:
            st.success("Strong starting confidence. The biggest risk is underestimating workload and pacing.")

    with tab2:
        weight_df = pd.DataFrame(
            {"Component": list(GRADE_WEIGHTS.keys()), "Weight": list(GRADE_WEIGHTS.values())}
        )
        st.dataframe(weight_df, use_container_width=True, hide_index=True)
        st.bar_chart(weight_df.set_index("Component"))

        st.subheader("What matters most")
        st.write(
            "The course is heavily driven by authentic application: the two individual assignments "
            "and the group project together account for 69% of the grade, while checkpoints add conceptual "
            "verification and participation rewards preparedness plus steady progress."
        )

    with tab3:
        st.write("The syllabus defines a common milestone system used across the two individual assignments and the group project.")
        milestone_df = pd.DataFrame(
            [{"Milestone": k, "Meaning": v} for k, v in MILESTONES.items()]
        )
        st.dataframe(milestone_df, use_container_width=True, hide_index=True)

        picked = st.select_slider(
            "Move through the milestone sequence",
            options=list(MILESTONES.keys()),
            value="3"
        )
        st.success(f"Milestone {picked}: {MILESTONES[picked]}")

elif page == "Grade Simulator":
    st.title("Grade Simulator")
    st.caption("A live model of the syllabus grading scheme with attendance penalty logic.")

    st.subheader("Enter your projected scores")
    col1, col2 = st.columns([1,1])

    inputs = {}
    with col1:
        inputs["Conceptual checkpoint #1"] = st.slider("CC #1", 0, 100, 85)
        inputs["Conceptual checkpoint #2"] = st.slider("CC #2", 0, 100, 88)
        inputs["Conceptual checkpoint #3"] = st.slider("CC #3", 0, 100, 90)
        inputs["Assignment 1 (Regression)"] = st.slider("Assignment 1", 0, 100, 87)

    with col2:
        inputs["Assignment 2 (Classification)"] = st.slider("Assignment 2", 0, 100, 89)
        inputs["Group project"] = st.slider("Group project", 0, 100, 92)
        inputs["Participation in class"] = st.slider("Participation", 0, 100, 94)

    raw = weighted_grade(inputs)

    st.subheader("Attendance / punctuality effects")
    c1, c2, c3 = st.columns(3)
    unexcused = c1.number_input("Net unexcused absences", min_value=0, max_value=10, value=0, step=1)
    lates = c2.number_input("Late arrivals", min_value=0, max_value=20, value=0, step=1)
    peer_factor = c3.slider("Group project peer factor", 0.50, 1.20, 1.00, 0.01)

    adjusted_inputs = inputs.copy()
    adjusted_inputs["Group project"] = min(100, inputs["Group project"] * peer_factor)
    adjusted_raw = weighted_grade(adjusted_inputs)
    final_score, attendance_penalty = apply_attendance_penalty(adjusted_raw, unexcused, lates)
    final_letter = letter_grade(final_score)

    a, b, c, d = st.columns(4)
    a.metric("Weighted score", f"{raw:.2f}")
    b.metric("After peer factor", f"{adjusted_raw:.2f}")
    c.metric("Attendance penalty", f"-{attendance_penalty:.2f}")
    d.metric("Projected final", f"{final_score:.2f} ({final_letter})")

    chart_df = pd.DataFrame({
        "Stage": ["Base weighted", "After peer factor", "After attendance"],
        "Score": [raw, adjusted_raw, final_score]
    })
    st.line_chart(chart_df.set_index("Stage"))

    st.subheader("What score do you need?")
    target = st.selectbox("Target letter grade", ["A", "A-", "B+", "B", "B-", "C+", "C"])
    targets = {"A":93, "A-":90, "B+":87, "B":83, "B-":80, "C+":77, "C":73}
    needed = targets[target]
    gap = needed - final_score
    if gap <= 0:
        st.success(f"You are currently on pace for at least a {target}.")
    else:
        st.warning(f"You are about {gap:.2f} points below a {target} right now.")

elif page == "Schedule Navigator":
    st.title("Schedule Navigator")
    st.caption("Explore the calendar by week, topic area, and milestone intensity.")

    df = pd.DataFrame(SCHEDULE_ROWS)
    df["has_milestone"] = df["milestone"].apply(lambda x: "Yes" if str(x).strip() else "No")
    df["kind"] = df["topic"].apply(
        lambda x: "Holiday / No class" if ("Holiday" in x or "NO CLASS" in x)
        else "Project / presentation" if ("Project" in x or "presentations" in x)
        else "Instruction"
    )

    c1, c2, c3 = st.columns(3)
    selected_weeks = c1.slider("Week range", 1, 15, (1, 15))
    selected_kind = c2.multiselect("Session type", sorted(df["kind"].unique()), default=sorted(df["kind"].unique()))
    milestone_only = c3.toggle("Show only rows with milestones or notes", value=False)

    filtered = df[(df["wk"] >= selected_weeks[0]) & (df["wk"] <= selected_weeks[1]) & (df["kind"].isin(selected_kind))]
    if milestone_only:
        filtered = filtered[(filtered["milestone"].str.strip() != "") | (filtered["notes"].str.strip() != "")]

    st.dataframe(
        filtered[["wk","session","day","date","topic","milestone","notes"]],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Timeline density")
    density = filtered.groupby("wk").size().reset_index(name="Sessions")
    st.bar_chart(density.set_index("wk"))

    st.subheader("Deadline radar")
    flagged = df[df["notes"].str.contains("due|revealed", case=False, na=False) | (df["milestone"].str.strip() != "")]
    for _, row in flagged.iterrows():
        with st.expander(f"Week {row['wk']} • {row['date']} • {row['topic']}"):
            st.write(f"**Milestone:** {row['milestone'] or '—'}")
            st.write(f"**Notes:** {row['notes'] or '—'}")

elif page == "Policy Scenarios":
    st.title("Policy Scenarios")
    st.caption("Turn passive policy reading into active judgment.")

    scenario = st.selectbox(
        "Choose a scenario",
        [
            "Late assignment",
            "Attendance risk",
            "Grade appeal",
            "Project contribution mismatch",
            "Participation expectations",
        ]
    )

    if scenario == "Late assignment":
        st.write("You submit an assignment 1.5 days late, and the instructor admits it.")
        days = st.slider("How many days late (or fraction thereof)?", 0.0, 4.0, 1.5, 0.5)
        penalty = math.ceil(days) * 25
        st.metric("Penalty applied", f"{penalty}%")
        original = st.slider("Original grade", 0, 100, 92)
        adjusted = max(0, original * (1 - penalty / 100))
        st.write(f"Final grade after penalty: **{adjusted:.1f}**")
        st.info("The syllabus states a 25% penalty per day late or fraction thereof, unless a harsher specific penalty applies.")

    elif scenario == "Attendance risk":
        st.write("Every net unexcused absence lowers the final course grade by 1%. Four unexcused absences can trigger being dropped.")
        absences = st.slider("Unexcused absences", 0, 6, 2)
        score = st.slider("Pre-penalty final grade", 0, 100, 88)
        final = max(0, score - absences)
        st.metric("Projected final score", f"{final:.1f}")
        if absences >= 4:
            st.error("At 4 unexcused absences, the syllabus says the student may be dropped from the course.")
        elif absences >= 2:
            st.warning("This is now materially affecting the course outcome.")
        else:
            st.success("Still recoverable, but the policy should be taken seriously.")

    elif scenario == "Grade appeal":
        st.write("You think a checkpoint was graded incorrectly.")
        elapsed = st.radio("How long has it been since the grade was formally returned?", ["1 business day", "2 business days", "4 business days"])
        if elapsed in ["1 business day", "2 business days"]:
            st.success("A written email request explaining all reasons for the revision can still be made.")
            st.write("The full work may be re-reviewed and the grade can go up, go down, or stay the same.")
        else:
            st.error("The syllabus says the request window has closed.")

    elif scenario == "Project contribution mismatch":
        st.write("The group project uses a peer assessment factor based on expected vs. assessed contribution.")
        team_grade = st.slider("Team project grade", 0, 100, 95)
        expected = st.number_input("Expected contribution %", value=33.0)
        actual = st.number_input("Peer-assessed contribution %", value=30.0)
        factor = actual / expected if expected else 0
        final = team_grade * factor
        st.metric("Peer factor", f"{factor:.2f}")
        st.metric("Individual project grade", f"{final:.1f}")

    elif scenario == "Participation expectations":
        st.write("Participation is not just speaking often; it combines preparedness, comment quality, and steady progress.")
        freq = st.select_slider("How often do you contribute?", options=["Rarely", "Sometimes", "Most classes", "Every class"], value="Most classes")
        quality = st.select_slider("Comment quality", options=["Low", "Medium", "Medium-high", "High"], value="Medium-high")
        progress = st.toggle("Evidence of early, steady, continuous progress", value=True)
        if freq == "Every class" and quality in ["Medium-high", "High"] and progress:
            st.success("This resembles the upper participation bands in the syllabus rubric.")
        elif progress and quality in ["Medium", "Medium-high", "High"]:
            st.info("This looks like a workable middle-to-strong participation profile.")
        else:
            st.warning("The syllabus makes clear that participation without preparation and visible progress is not enough.")

elif page == "Student Success Planner":
    st.title("Student Success Planner")
    st.caption("Translate the syllabus into an execution strategy.")

    st.subheader("Profile builder")
    c1, c2 = st.columns(2)
    background = c1.selectbox("Your strongest starting area", ["Programming", "Statistics", "Writing/communication", "None of these strongly"])
    risk = c2.selectbox("Your biggest likely risk", ["Falling behind", "Debugging bottlenecks", "Weak presentation/reporting", "Passive participation"])

    recommendations = []
    if background == "Programming":
        recommendations.append("Leverage your coding strength, but do not neglect interpretation and communication.")
    elif background == "Statistics":
        recommendations.append("Use your statistical intuition to choose models well, but plan extra time for implementation.")
    elif background == "Writing/communication":
        recommendations.append("You can likely excel in storytelling and reporting; protect time for model implementation practice.")
    else:
        recommendations.append("Start with software setup, textbook structure, and a strict weekly routine.")

    if risk == "Falling behind":
        recommendations.append("Treat milestones as binding internal deadlines and begin assignments early.")
    elif risk == "Debugging bottlenecks":
        recommendations.append("Build a debugging workflow: isolate errors, search documentation, use Stack Overflow, then ask focused questions.")
    elif risk == "Weak presentation/reporting":
        recommendations.append("Use every milestone review as a chance to improve clarity of charts, recommendations, and business framing.")
    else:
        recommendations.append("Prepare before class and bring at least one meaningful contribution or question each session.")

    for rec in recommendations:
        st.markdown(f"- {rec}")

    st.subheader("Weekly operating system")
    week_hours = st.slider("Planned hours per week for this course", 2, 20, 8)
    if week_hours < 5:
        st.error("For a course this dense, that is likely too low unless you already have strong prior preparation.")
    elif week_hours < 8:
        st.warning("Possible, but risky. You will need discipline and very early starts.")
    else:
        st.success("This is closer to the level of effort implied by the syllabus tone and workload.")

    st.subheader("Setup readiness")
    setup_items = {
        "R installed": False,
        "RStudio installed": False,
        "Keras/TensorFlow plan in place": False,
        "Textbook located": False,
        "Office-hour strategy ready": False,
    }
    ready_count = 0
    cols = st.columns(len(setup_items))
    for idx, item in enumerate(setup_items):
        checked = cols[idx].checkbox(item, key=f"setup_{idx}")
        ready_count += int(checked)

    st.metric("Readiness score", f"{ready_count}/{len(setup_items)}")
    if ready_count == len(setup_items):
        st.success("You are operationally ready.")
    else:
        st.info("The fastest early win is completing the software and support setup before workload compounds.")

    st.subheader("Export your notes")
    payload = {
        "onboarding_progress_percent": progress_pct(),
        "notes": st.session_state["notes"],
        "recommendations": recommendations,
    }
    st.download_button(
        "Download my planner notes as JSON",
        data=json.dumps(payload, indent=2),
        file_name="bat3305_syllabus_planner.json",
        mime="application/json",
    )

st.caption("Prototype built from the BAT 3305 syllabus.")
