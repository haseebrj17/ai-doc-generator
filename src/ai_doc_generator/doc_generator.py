#!/usr/bin/env python3
"""
Main documentation generator for the RainMakerz Document Processing project.
Generates comprehensive documentation using OpenAI's API.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from openai import OpenAI
from tqdm import tqdm

from .file_scanner import FileScanner
from .code_analyzer import CodeAnalyzer
from .change_tracker import ChangeTracker
from .doc_builder import DocumentationBuilder
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Main class for generating project documentation using LLM."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        self.file_scanner = FileScanner(config)
        self.code_analyzer = CodeAnalyzer()
        self.change_tracker = ChangeTracker(config)
        self.doc_builder = DocumentationBuilder(config)

    def generate_documentation(self, force_full: bool = False) -> None:
        """
        Generate documentation for the project.

        Args:
            force_full: If True, regenerate all documentation regardless of changes
        """
        logger.info("Starting documentation generation...")

        # Determine which files need documentation
        if force_full or not self.change_tracker.has_previous_run():
            logger.info("Performing full documentation generation...")
            files_to_document = self.file_scanner.scan_all_files()
            is_full_run = True
        else:
            logger.info("Checking for changes since last run...")
            files_to_document = self.change_tracker.get_changed_files()
            is_full_run = False

        if not files_to_document:
            logger.info("No files need documentation.")
            return

        logger.info(f"Found {len(files_to_document)} files to document.")

        # Load existing documentation if incremental
        if not is_full_run:
            self.doc_builder.load_existing_documentation()

        # Process each file
        documented_files = []
        with tqdm(total=len(files_to_document), desc="Documenting files") as pbar:
            for file_path in files_to_document:
                try:
                    doc_content = self._document_file(file_path)
                    if doc_content:
                        self.doc_builder.add_file_documentation(file_path, doc_content)
                        documented_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error documenting {file_path}: {str(e)}")
                finally:
                    pbar.update(1)

        # Build the final documentation
        logger.info("Building final documentation structure...")
        self.doc_builder.build_documentation()

        # Update the change tracker
        self.change_tracker.update_state(documented_files)

        logger.info("Documentation generation complete!")

    def _document_file(self, file_path: Path) -> Optional[Dict]:
        """
        Generate documentation for a single file.

        Args:
            file_path: Path to the file to document

        Returns:
            Dictionary containing documentation content
        """
        logger.debug(f"Documenting {file_path}")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read {file_path}: {str(e)}")
            return None

        # Analyze the code
        analysis = self.code_analyzer.analyze_file(file_path, content)

        # Prepare the prompt for the LLM
        prompt = self._create_documentation_prompt(file_path, content, analysis)

        # Get documentation from LLM
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            doc_content = response.choices[0].message.content

            return {
                "path": str(file_path),
                "analysis": analysis,
                "documentation": doc_content,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"LLM error for {file_path}: {str(e)}")
            return None

    def _create_documentation_prompt(self, file_path: Path, content: str, analysis: Dict) -> str:
        """Create a prompt for the LLM to generate documentation."""

        # Truncate content if too long
        max_content_length = 10000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n... (truncated)"

        prompt = f"""Please generate comprehensive documentation for the following Python file.

File Path: {file_path}
File Type: {file_path.suffix}

Code Analysis:
- Classes: {len(analysis.get('classes', []))}
- Functions: {len(analysis.get('functions', []))}
- Imports: {len(analysis.get('imports', []))}
- Lines of Code: {analysis.get('loc', 0)}

File Content:
```python
{content}
```

Please provide:
1. A brief overview of the file's purpose
2. Detailed description of each class (purpose, key methods, relationships)
3. Detailed description of each function (purpose, parameters, return values, exceptions)
4. Key dependencies and imports
5. Usage examples where applicable
6. Any important notes or considerations

Format the documentation in clean Markdown with appropriate headers and sections."""

        return prompt


def main() -> None:
    """Main entry point for the documentation generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate project documentation using AI")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--full", action="store_true", help="Force full documentation regeneration")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (overrides config)")
    parser.add_argument("--output", type=str, help="Output directory for documentation")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = Config()

    # Override settings from command line
    if args.api_key:
        config.openai_api_key = args.api_key
    if args.output:
        config.output_dir = Path(args.output)

    # Validate API key
    if not config.openai_api_key:
        logger.error("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Create and run generator
    generator = DocumentationGenerator(config)
    generator.generate_documentation(force_full=args.full)


if __name__ == "__main__":
    main()