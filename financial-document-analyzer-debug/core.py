from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Run the Crew pipeline and return the result object/dict.

    This is kept as a separate helper so workers can import it without importing
    the FastAPI app module.
    """
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )

    result = financial_crew.kickoff({"query": query})
    return result
