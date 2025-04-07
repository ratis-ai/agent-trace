import time
from typing import Optional
import sys

from agent_trace.core.trace import start_run, trace
from agent_trace.logging.logger import file_logger
logger = file_logger("SIMPLE_EXAMPLE")

# Force flush stdout
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+

logger.info('='*100)
logger.info("NEW RUN OF SIMPLE EXAMPLE")  # Debug print
logger.info('='*100)

@trace
def read_pdf(path: str) -> str:
    """Simulate reading a PDF file."""
    time.sleep(0.1)  # Simulate file reading
    return "This is the content of the PDF file..."


@trace
def summarize_text(text: str, max_words: Optional[int] = None) -> str:
    """Simulate text summarization with an LLM."""
    time.sleep(0.3)  # Simulate LLM call
    return "This is a summary of the text..."


@trace
def send_email(to: str, body: str) -> bool:
    """Simulate sending an email."""
    time.sleep(0.1)  # Simulate email sending
    return True


def main():
    """Run an example agent pipeline with tracing."""
    with start_run(
        "simple_mock_example",
        metadata={"source": "example"}
    ):
        # Read the PDF
        text = read_pdf("report.pdf")
        
        # Generate summary
        summary = summarize_text(text, max_words=100)
        
        # Send email
        success = send_email("user@example.com", summary)
        
        logger.info("Pipeline completed successfully!" if success else "Failed to send email")
        print("Pipeline completed successfully!" if success else "Failed to send email")


if __name__ == "__main__":
    main() 