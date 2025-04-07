import io
import contextlib

from crewai import Crew
from functools import wraps
from agent_trace.logging.logger import console_logger, file_logger
logger = file_logger("CREW_CAPTURE")
# console_logger = console_logger("CREW_CAPTURE_OUT")

_stdout_buffer = {}


def get_stdout_for_crew(crew_id):
    return _stdout_buffer.get(crew_id, "")


def patch_crewai_capture():
    original_kickoff = Crew.kickoff

    @wraps(original_kickoff)
    def wrapped_kickoff(self, *args, **kwargs):
        crew_id = getattr(self, "id", "default")
        logger.info(f"Wrapping kickoff for crew {crew_id}")
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            result = original_kickoff(self, *args, **kwargs)
            _stdout_buffer[crew_id] = buf.getvalue()
            return result

    Crew.kickoff = wrapped_kickoff
    logger.info("Crew.kickoff has been patched to capture stdout")