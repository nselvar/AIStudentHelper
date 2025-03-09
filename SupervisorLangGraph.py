import langgraph
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from HomeworkHelper import HomeworkHelper
from LinkedinApply import LinkedinApply
from ReportGenerator import ReportGenerator
from VideoSummary import VideoSummary

# Initialize LLM
llm = ChatOpenAI()

# Define state
class AgentState:
    def __init__(self, user_input):
        self.user_input = user_input
        self.task = None
        self.response = None

# Supervisor Agent (Routes tasks)
def supervisor_agent(state):
    user_prompt = state["user_input"].lower()

    if "summarize pdf" in user_prompt:
        return {"task": "summarize_pdf"}
    elif "summarize youtube video" in user_prompt:
        return {"task": "summarize_youtube"}
    elif "apply for jobs" in user_prompt:
        return {"task": "apply_jobs"}
    elif "homeworkhelper" in user_prompt:  # ✅ Added Homework Helper task
        return {"task": "homework_helper"}
    else:
        return {"response": "Task not recognized."}

# Specialized Agents
def pdf_agent(state):
    pdf_name = input("📄 Enter the PDF file name with full path: ")
    report = ReportGenerator(pdf_name)
    report.generate_report()
    return {"response": f"Summarizing PDF: {pdf_name}"}

def youtube_agent(state):
    video_url = input("🎥 Enter the YouTube video link: ")
    report = VideoSummary(video_url)
    return {"response": f"Summarizing YouTube video: {video_url}"}

def job_agent(state):
    location = input("📍 Applying for jobs, make sure your linkedin username , password is configured in config.yml: ")
    report = LinkedinApply()
    return {"response": f"Applying for jobs in {location}"}

def homework_agent(state):
    """Handles Homework Help."""
    print("📚 Open your web browser and navigate to the URL provided by Streamlit (usually http://localhost:8501).Enter your homework question in the text area and press Get Help to see the answers. ")
    report = HomeworkHelper()

# Define Workflow Graph
workflow = StateGraph(dict)

# Add nodes (agents)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("summarize_pdf", pdf_agent)
workflow.add_node("summarize_youtube", youtube_agent)
workflow.add_node("apply_jobs", job_agent)
workflow.add_node("homework_helper", homework_agent)  # ✅ Added Homework Helper Node

# Task Routing with `add_conditional_edges()`
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["task"],
    {
        "summarize_pdf": "summarize_pdf",
        "summarize_youtube": "summarize_youtube",
        "apply_jobs": "apply_jobs",
        "homework_helper": "homework_helper",  # ✅ Added Homework Helper Routing
    }
)

# Set entry point & Compile Graph
workflow.set_entry_point("supervisor")
executor = workflow.compile()

# Run Multi-Agent System
user_prompt = input("📝 Enter your task (summarize pdf / summarize youtube video / apply for jobs / homeworkhelper): ")
result = executor.invoke({"user_input": user_prompt})
print("🤖 Agent Response:", result["response"])