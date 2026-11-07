"""The host model chooses a category and words the final prompt."""
from typing import Literal

Category = Literal["resume", "application", "portfolio", "website", "coding", "security", "writing", "research", "other"]
Mode = Literal["create", "improve"]

# Every choice can be replaced with a free-text answer.
TOPICS = {
    "resume": (
        ("Which role should this resume target?", ["A specific job posting", "A role family", "A general resume"]),
        ("What evidence can the writer use?", ["My existing resume", "Notes on projects and experience", "Both"]),
        ("What should the final draft prioritize?", ["One-page ATS resume", "Tailored bullet points", "Skills and keyword gaps"]),
        "Use only supplied experience, skills and metrics. For a job posting, use relevant terms only when evidence supports them."
    ),
    "application": (
        ("What application material do you need?", ["Cover letter", "Referral request", "Application answer"]),
        ("Who will read it?", ["Recruiter", "Hiring manager", "Potential referrer"]),
        ("What evidence should anchor the message?", ["Resume and job posting", "A project example", "Details I will provide"]),
        "Tie each claim to the supplied evidence. Use placeholders for missing names or role details."
    ),
    "portfolio": (
        ("Who should the portfolio help you reach?", ["Recruiters", "Technical hiring managers", "Clients"]),
        ("What proof should it feature?", ["Project case studies", "Live demos", "Code and technical write-ups"]),
        ("What should the AI deliver?", ["Working website", "Portfolio copy", "Site structure and design"]),
        "Connect each featured project to a contribution, a concrete artifact and an outcome. Ask for missing evidence."
    ),
    "website": (
        ("What should visitors do?", ["Contact me", "Try a product", "Find information"]),
        ("What should the AI produce?", ["Runnable website", "Design brief", "Copy and page structure"]),
        ("What constraints apply?", ["Use my existing stack", "Keep setup simple", "Match a reference design"]),
        "Specify the main user flow, responsive layout, accessibility and an observable completion check."
    ),
    "coding": (
        ("What kind of help do you need?", ["Implement a feature", "Debug a failure", "Review or refactor"]),
        ("What can you provide?", ["Existing code", "An error or reproduction", "Requirements only"]),
        ("What output is most useful?", ["Patch and verification steps", "Runnable example", "Explanation and tradeoffs"]),
        "Name the inputs, expected behavior and how to verify it. Distinguish executed tests from suggested tests."
    ),
    "security": (
        ("What is the security task?", ["Threat modeling", "Defensive engineering", "Authorized lab testing"]),
        ("What scope should it cover?", ["A local lab", "My cloud environment", "A supplied architecture"]),
        ("What should the result contain?", ["Findings and mitigations", "A reproducible walkthrough", "Detection logic and validation"]),
        "Keep actions within the supplied scope. Distinguish observed evidence from hypotheses and include validation steps."
    ),
    "writing": (
        ("What are you writing?", ["Email or message", "Article or post", "Report or document"]),
        ("Who is the audience?", ["Professional contact", "General readers", "Specialists"]),
        ("What should the reader do?", ["Take action", "Understand an idea", "Make a decision"]),
        "Match tone and length to the reader. Preserve source facts and make the requested action clear."
    ),
    "research": (
        ("How will you use the research?", ["Choose between options", "Learn a topic", "Evaluate a claim"]),
        ("Which sources matter?", ["Primary sources", "Recent sources", "Only material I provide"]),
        ("What format will help?", ["Comparison table", "Brief with citations", "Detailed explanation"]),
        "Cite accessible evidence, flag uncertainty and never invent references. State if current sources cannot be checked."
    ),
    "other": (
        ("What outcome do you need?", ["Make something", "Understand something", "Make a decision"]),
        ("Who will use the result?", ["Just me", "A specific audience", "A general audience"]),
        ("What would make it successful?", ["Ready to use", "Easy to follow", "Supported by evidence"]),
        "Translate the goal into a concrete deliverable and an observable success condition."
    ),
}

IMPROVE = ("What should change in your existing prompt?", ["Make the instructions clearer", "Specify the output more precisely", "Add missing constraints"])

def questions(category: Category, mode: Mode):
    rows = list(TOPICS[category][:3])
    if mode == "improve":
        rows[-1] = IMPROVE
    return [{"question": title, "choices": options, "custom_answer_allowed": True} for title, options in rows]

def build_brief(source: str, mode: Mode, category: Category, answers: list[str], preferences: dict):
    if not source.strip() or len(source) > 24000:
        raise ValueError("Provide an idea or prompt between 1 and 24,000 characters.")
    quiz = questions(category, mode)
    if len(answers) != len(quiz) or any(not a.strip() or len(a) > 4000 for a in answers):
        raise ValueError("Provide one non-empty answer of at most 4,000 characters per quiz question.")
    instruction = (
        "Rewrite the original prompt as one coherent, self-contained replacement. Preserve its intent, "
        "facts and explicit constraints. Apply the selected improvement. Resolve conflicting requirements "
        "with the user when necessary."
        if mode == "improve" else
        "Turn the idea into a self-contained prompt that directly requests the chosen deliverable."
    )
    return {
        "editor_instruction": instruction + " Return one copyable prompt in the user's language. "
            "Incorporate the answers naturally, keep it proportional to the task, use placeholders for "
            "missing source material, and specify how to recognize a successful result. "
            "Write the prompt without executing the underlying task.",
        "category_guidance": TOPICS[category][3],
        "source": source,
        "quiz_answers": [{"question": q["question"], "answer": a.strip()} for q,a in zip(quiz, answers)],
        "style_defaults": preferences,
    }
