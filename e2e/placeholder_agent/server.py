import logging

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from placeholder_agent.agent import create_agent
from placeholder_agent.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting agent: %s", config.agent_name)
    logger.info("A4S API URL: %s", config.a4s_api_url)
    logger.info("Agent host: %s", config.agent_host)

    agent = create_agent()
    app = to_a2a(agent, host=config.agent_host, port=8000)

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    main()
