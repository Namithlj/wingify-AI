## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.agents import Agent

from tools import search_tool, FinancialDocumentTool

# No LLM integration for debug run; set to None
llm = None


# Creating a sensible, safety-minded Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze the provided financial document and produce an objective, compliance-minded summary and recommendations relevant to the query.",
    verbose=False,
    memory=True,
    backstory=(
        "Experienced financial analyst focused on factual, regulation-aware analysis."
    ),
    tool=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=True
)

# Document verifier: validate uploaded files and flag non-financial content
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify whether the uploaded file is a financial document and extract metadata (tables, figures, statements). Flag unsupported formats.",
    verbose=False,
    memory=False,
    backstory=("Responsible for verifying file format and basic structure of financial reports."),
    llm=llm,
    max_iter=1,
    max_rpm=10,
    allow_delegation=False
)


investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide objective, risk-disclosed investment suggestions when appropriate, based strictly on analyzed data and user query.",
    verbose=False,
    backstory=("Offers evidence-backed recommendations and highlights associated risks."),
    llm=llm,
    max_iter=1,
    max_rpm=10,
    allow_delegation=False
)


risk_assessor = Agent(
    role="Risk Assessor",
    goal="Assess and summarize risks found in the financial document and recommend mitigations with clear assumptions.",
    verbose=False,
    backstory=("Focuses on objective risk factors and clear explanations."),
    llm=llm,
    max_iter=1,
    max_rpm=10,
    allow_delegation=False
)
