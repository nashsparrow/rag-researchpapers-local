import argparse

from app.pipelines import (
    execute_indexing_pipeline,
    execute_query_pipeline,
    execute_test_pipeline,
)
from config import PDF_DATA_PATH, PROCESSED_DATA_PATH


class CLIApplication:
    def __init__(self):
        self.parser = self.build_parser()

    def build_parser(self):
        parser = argparse.ArgumentParser(
            description="Research Paper RAG Assistant"
        )

        parser.add_argument(
            "command",
            choices=["index", "test", "run"],
        )

        return parser

    def run(self):
        args = self.parser.parse_args()

        if args.command == "index":
            execute_indexing_pipeline(
                pdf_path=PDF_DATA_PATH,
                txt_path=PROCESSED_DATA_PATH,
            )

        elif args.command == "test":
            execute_test_pipeline()

        elif args.command == "run":
            execute_query_pipeline()


if __name__ == "__main__":
    print("Welcome to Research RAG! \n")
    CLIApplication().run()
