import logging
from pathlib import Path
from common.config.config import config
from common.workflow.converter.workflow_converter import convert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'

API_V_WORKFLOWS_ = "api/v1/workflows"


def main():
    CONFIG_DIR = Path(__file__).resolve().parent / "config"
    OUTPUT_ROOT = Path(__file__).resolve().parent / "outputs"

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
        relative_path = file_path.relative_to(CONFIG_DIR)
        output_file = OUTPUT_ROOT / "config" / relative_path
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


if __name__ == "__main__":
    main()
