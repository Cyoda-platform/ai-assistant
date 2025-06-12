import logging
from pathlib import Path
from common.config.config import config
from common.workflow.converter.utils import write_json_file, read_json_file
from common.workflow.converter.workflow_converter import WorkflowConverter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CONFIG_DIR = Path("/home/kseniia/PycharmProjects/ai_assistant/common/workflow/config")
OUTPUT_ROOT = Path("/home/kseniia/PycharmProjects/ai_assistant/common/workflow/outputs")
CALCULATION_NODE_TAGS = config.GRPC_PROCESSOR_TAG
ENTITY_VERSION = int(config.ENTITY_VERSION)


def main():
    logger.info("Starting workflow conversion...")
    try:
        for input_path in CONFIG_DIR.rglob("*"):
            if not input_path.is_file() or input_path.suffix.lower() != ".json":
                continue

            # Derive model name and workflow name
            try:
                model_name = input_path.relative_to(CONFIG_DIR).parts[-2]
            except IndexError:
                model_name = input_path.parent.name
            workflow_name = input_path.stem

            # Construct output path and ensure directory exists
            output_path = OUTPUT_ROOT / input_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Read input JSON
            try:
                input_json = read_json_file(input_path)
            except Exception as e:
                logger.error(f"Failed to read {input_path}: {e}")
                continue

            # Build DTO using WorkflowConverter
            try:
                converter = WorkflowConverter(
                    model_name=model_name,
                    model_version=ENTITY_VERSION,
                    workflow_name=workflow_name,
                    calculation_node_tags=CALCULATION_NODE_TAGS,
                    ai=True
                )
                dto = converter.build(input_json)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Error converting workflow for {input_path}: {e}")
                continue

            # Write output JSON
            try:
                write_json_file(output_path, dto)
                logger.info(f"Conversion complete: {output_path}")
            except Exception as e:
                logger.error(f"Failed to write output to {output_path}: {e}")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
