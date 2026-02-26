## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

## Task: Analyze a financial document based on the user's query
analyze_financial_document = Task(
    description="Read the provided financial document and produce an objective summary relevant to {query}. Extract key statements, important figures, and tables. Provide clear findings and actionable recommendations with assumptions and confidence levels.",

    expected_output="""Structured response with:
- Summary: concise 3-5 sentence overview of document
- Key Figures: list of important numbers (revenue, profit, margins, etc.) and page references
- Findings: 3-6 bullet points explaining what the numbers imply
- Recommendations: 2-3 actionable suggestions with rationale and risk notes
- Confidence: short statement of confidence and any missing data required for higher certainty""",

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Investment analysis task (uses investment advisor)
investment_analysis = Task(
    description="Given extracted data from the financial document and the user's query, provide objective investment options with risk disclosures and rationale.",

    expected_output="""Response should include:
- Top investment ideas (1-3) with clear rationale tied to document data
- Risks and potential downside for each idea
- Suggested time horizon and suitability
- Data points from the document used in reasoning""",

    agent=investment_advisor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Risk assessment task (uses risk assessor)
risk_assessment = Task(
    description="Assess material risks identified in the document and provide mitigations and monitoring suggestions.",

    expected_output="""Response should include:
- List of identified risks with severity (low/medium/high)
- Evidence from document for each risk
- Recommended mitigations and monitoring cadence""",

    agent=risk_assessor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Verification task
verification = Task(
    description="Verify that the uploaded file is a financial document (e.g., contains balance sheet, income statement, cash flow) and return structured metadata (pages, tables).",

    expected_output="""Response should state whether the file is a financial document with reasons, list found financial sections, and provide any parsing errors encountered.""",

    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)