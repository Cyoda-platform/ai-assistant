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




def main(import_workflows: bool):

    CONFIG_DIR = Path("config")
    OUTPUT_ROOT = Path("outputs")

    for file_path in CONFIG_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        # model_name is the name of the folder directly under config/
        # e.g. config/scheduler/foo.json -> scheduler
        try:
            # file_path.relative_to(CONFIG_DIR) == scheduler/foo.json
            model_name = file_path.relative_to(CONFIG_DIR).parts[-2]
        except IndexError:
            # fallback, though .rglob under CONFIG_DIR always has at least one part
            model_name = file_path.parent.name

        input_file = str(file_path)

        # Build the output path under outputs/ preserving subdirs
        output_file = OUTPUT_ROOT / file_path
        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        workflow_name = file_path.relative_to(CONFIG_DIR).parts[-1].split(".")[0]
        # Set the AI flag
        ai = True
        # Call your conversion
        convert(
            input_file_path=input_file,
            output_file_path=str(output_file),
            calculation_node_tags=config.GRPC_PROCESSOR_TAG,
            model_name=model_name,
            model_version=int(config.ENTITY_VERSION),
            workflow_name=workflow_name,
            ai=ai
        )

        print(f"Conversion completed. Result saved to {output_file}")
    print(f"Conversion completed.")
    if import_workflows:
        # Initialize required services and repository
        cyoda_auth_service = CyodaAuthService()
        cyoda_repository = CyodaRepository(
            cyoda_auth_service=cyoda_auth_service)  # Make sure this can be instantiated or mocked appropriately

        # Create the CyodaInitService instance
        init_service = CyodaInitService(cyoda_repository, cyoda_auth_service)

        # Run the async start method using asyncio
        asyncio.run(init_service.initialize_service())


if __name__ == "__main__":
    IMPORT_WORKFLOWS = True
    main(import_workflows=IMPORT_WORKFLOWS)