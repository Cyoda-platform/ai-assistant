import json


def process_file(input_file_path, output_dir):
    # Open the input file and process each line
    with open(input_file_path, 'r') as infile:
        for line_number, line in enumerate(infile, start=1):
            # Parse the JSON line
            data = json.loads(line.strip())

            # Define the output file path for this line
            output_file_path = f'{output_dir}input_{line_number}.txt'

            # Write the content of the line to the corresponding text file
            with open(output_file_path, 'w') as outfile:
                outfile.write(json.dumps(data))  # You can modify this line if you need a different format


def main():
    # Define the input and output paths
    input_file_path = '/home/kseniia/IdeaProjects/cyoda-ai-test/data/fine-tuning/v3/cyoda/05-02-25/cyoda_training_validationset.jsonl'
    output_dir = '/home/kseniia/IdeaProjects/cyoda-ai-test/data/rag/v2/cyoda/validation_data/'

    # Call the process_file function to process the input file
    process_file(input_file_path, output_dir)


if __name__ == "__main__":
    main()
