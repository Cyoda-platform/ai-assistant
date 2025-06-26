import asyncio
import json
import logging
import os
from pathlib import Path

from common.auth.cyoda_auth import CyodaAuthService
from common.config.config import config
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.utils.utils import send_cyoda_request
from common.workflow.converter.workflow_converter import convert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'

API_V_WORKFLOWS_ = "api/v1/workflows"


class CyodaInitService:
    def __init__(self, cyoda_repository: CyodaRepository, cyoda_auth_service: CyodaAuthService):
        self.cyoda_repository = cyoda_repository
        self.entity_dir = Path("outputs/import")
        self.API_V_WORKFLOWS_ = "api/v1/workflows"
        self.cyoda_auth_service = cyoda_auth_service

    async def initialize_service(self):
        await self.init_cyoda(token=self.cyoda_auth_service)

    async def init_cyoda(self, token: CyodaAuthService):
        await self.init_entities_schema(entity_dir=self.entity_dir, token=token)

    async def init_entities_schema(self, entity_dir, token: CyodaAuthService):
        for json_file in entity_dir.glob('*.json'):
            # Ensure the JSON file is in an immediate subdirectory
            try:
                dto = json.loads(json_file.read_text())
                dto_workflow_name = dto['workflow'][0]['name']
                workflows_response = await send_cyoda_request(cyoda_auth_service=token, method="get",
                                                              base_url=config.CYODA_API_URL,
                                                              path="platform-api/statemachine/workflows")
                if workflows_response['status'] != 200:
                    raise
                workflows = workflows_response['json']
                for workflow in workflows:
                    if workflow.get('name') and workflow['name'] == dto_workflow_name:
                        workflow['active']=False
                        deactivate_response = await send_cyoda_request(cyoda_auth_service=token, method="put",
                                                                       base_url=config.CYODA_API_URL,
                                                                       path=f"platform-api/statemachine/persisted/workflows/{workflow['id']}",
                                                                       data=json.dumps(workflow))
                        if deactivate_response['status'] != 200:
                            raise
                response = await send_cyoda_request(cyoda_auth_service=token, method="post", base_url=config.CYODA_API_URL,
                                                    path="platform-api/statemachine/import?needRewrite=true",
                                                    data=json.dumps(dto))
                print(response)
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
                logger.exception(e)




def main():
    # Initialize required services and repository
    cyoda_auth_service = CyodaAuthService()
    cyoda_repository = CyodaRepository(
        cyoda_auth_service=cyoda_auth_service)  # Make sure this can be instantiated or mocked appropriately

    # Create the CyodaInitService instance
    init_service = CyodaInitService(cyoda_repository, cyoda_auth_service)

    # Run the async start method using asyncio
    asyncio.run(init_service.initialize_service())


if __name__ == "__main__":
    main()