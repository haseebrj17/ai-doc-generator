#!/usr/bin/env python3
"""
Command-line interface for AI Documentation Generator.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from .config import Config
from .doc_generator import DocumentationGenerator


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate documentation for Python projects using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate documentation for current directory
  ai-doc-gen

  # Generate with custom config
  ai-doc-gen --config my-config.json

  # Force full regeneration
  ai-doc-gen --full

  # Specify output directory
  ai-doc-gen --output docs/api

  # Use specific OpenAI model
  ai-doc-gen --model gpt-4o-mini
        """
    )

    # Required arguments
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python project (default: current directory)"
    )

    # Optional arguments
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for documentation (default: docs/generated)"
    )

    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Force full documentation regeneration"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (overrides OPENAI_API_KEY env var)"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo-preview"],
        help="OpenAI model to use"
    )

    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files in documentation"
    )

    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Additional directories to exclude"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be documented without generating"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Load configuration
    try:
        if args.config:
            config = Config.from_file(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        else:
            config = Config()

        # Override with command-line arguments
        config.project_root = Path(args.path).resolve()

        if args.output:
            config.output_dir = Path(args.output)

        if args.api_key:
            config.openai_api_key = args.api_key

        if args.model:
            config.model = args.model

        if args.include_tests:
            config.include_tests = True

        if args.exclude:
            config.exclude_dirs.extend(args.exclude)

        # Validate configuration
        errors = config.validate()
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)

        # Dry run mode
        if args.dry_run:
            from .file_scanner import FileScanner
            scanner = FileScanner(config)
            files = scanner.scan_all_files()
            
            print(f"\nProject: {config.project_root}")
            print(f"Output: {config.output_dir}")
            print(f"Model: {config.model}")
            print(f"\nWould document {len(files)} files:")
            
            for file in sorted(files)[:20]:  # Show first 20
                print(f"  - {file.relative_to(config.project_root)}")
            
            if len(files) > 20:
                print(f"  ... and {len(files) - 20} more files")
            
            sys.exit(0)

        # Create and run generator
        logger.info(f"Starting documentation generation for {config.project_root}")
        generator = DocumentationGenerator(config)
        generator.generate_documentation(force_full=args.full)
        
        logger.info(f"Documentation generated successfully in {config.output_dir}")

    except KeyboardInterrupt:
        logger.info("Documentation generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()