# Batch Search and Replace Tool

A powerful, safe, and configurable tool for performing batch search-and-replace operations on text files. Perfect for codebase refactoring, configuration updates, and bulk text transformations.

## Features

- **Safe Operation**: Creates mirrored output folder, leaves original files untouched
- **Intelligent File Detection**: Automatically identifies text files and skips binary files
- **Multiple Replacement Rules**: Single or batch operations via JSON/YAML configuration
- **Environment Awareness**: Environment-specific replacements (dev/staging/prod)
- **Regex Support**: Both exact string matching and regular expressions
- **Flexible Filtering**: Include specific file types or ignore directories
- **Dry Run Mode**: Preview changes before applying them
- **Comprehensive Logging**: Console and file logging with colored output
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourdepartment/batch-replace-tool.git
cd batch-replace-tool

# Install in development mode
pip install -e .

# Or install with dependencies
pip install -r requirements.txt

Usage
##Basic Usage
Replace "old" with "new" in all text files:

bash
batch-replace --source ./myproject --destination ./output --pattern "old" --replace "new"


## With File Type Filtering
Only process specific file types:

bash
batch-replace --source ./src --destination ./out --pattern "localhost" --replace "127.0.0.1" --file-types .html,.js,.css

##Using Regular Expressions
bash
batch-replace --source ./src --destination ./out --pattern "\b\d{3}-\d{4}\b" --replace "[PHONE]" --regex

##Dry Run Mode
Preview changes without writing files:

bash
batch-replace --source ./src --destination ./out --pattern "old" --replace "new" --dry-run

##Using a Rules File
Multiple replacements in one run:

bash
batch-replace --source ./src --destination ./out --rules-file rules.json

e.g
{
  "rules": [
    {"pattern": "old-domain.com", "replace": "new-domain.com"},
    {"pattern": "\\d{3}-\\d{4}", "replace": "[PHONE]", "regex": true},
    {"pattern": "password\\s*=\\s*['\"](.*?)['\"]", "replace": "password=\"[REDACTED]\"", "regex": true}
  ]
}

##Environment-Aware Replacements
batch-replace --source ./config --destination ./output --rules-file rules.json --env dev --env-config env_config.json
Example env_config.json:

json
{
  "environments": {
    "dev": {
      "API_URL": "http://localhost:8000",
      "DB_HOST": "localhost"
    },
    "prod": {
      "API_URL": "https://api.example.com",
      "DB_HOST": "prod-db.example.com"
    }
  }
}

Then in your rules, use ${VAR_NAME} placeholders:

json
{
  "rules": [
    {"pattern": "api.example.com", "replace": "${API_URL}"},
    {"pattern": "localhost:5432", "replace": "${DB_HOST}:5432"}
  ]
}

##Ignoring Directories
Skip specific directories:

bash
batch-replace --source ./src --destination ./out --pattern "old" --replace "new" --ignore-dirs .git,node_modules,dist,__pycache__


##Preserve Timestamps
Keep original file timestamps:

bash
batch-replace --source ./src --destination ./out --pattern "old" --replace "new" --preserve-timestamps


Command Line Arguments
Argument	Description	Required
--source	Source folder to process	Yes
--destination	Output folder for modified copies	Yes
--pattern	String or regex pattern to search for	Conditional*
--replace	Replacement string	Conditional*
--rules-file	JSON/YAML file with multiple rules	Conditional*
--regex	Treat pattern as regular expression	No
--file-types	Comma-separated file extensions to process	No
--ignore-dirs	Directories to skip (default: .git,node_modules,pycache,dist,build,.idea,.vscode)	No
--dry-run	Preview changes without writing	No
--env	Environment name (dev, prod, staging)	No
--env-config	Environment configuration file	No
--preserve-timestamps	Preserve original file timestamps	No
--verbose	Enable verbose logging	No
--log-file	Path to log file	No
*Either --pattern+--replace or --rules-file must be provided


##Rules File Format
The rules file can be in JSON or YAML format and should contain either:

Single Rule
json
{
  "pattern": "search text",
  "replace": "replacement text",
  "regex": false
}

##Multiple Rules
json
{
  "rules": [
    {"pattern": "text1", "replace": "text2", "regex": false},
    {"pattern": "\\d+", "replace": "[NUMBER]", "regex": true}
  ]
}

Or as a list:

json
[
  {"pattern": "text1", "replace": "text2"},
  {"pattern": "\\d+", "replace": "[NUMBER]", "regex": true}
]
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=batch_replace tests/


##Example 1: Update API endpoints
bash
batch-replace \
  --source ./src \
  --destination ./src-updated \
  --pattern "https://old-api.example.com" \
  --replace "https://new-api.example.com" \
  --file-types .js,.ts,.html

  ##Example 2: Remove debug code for production
bash
batch-replace \
  --source ./src \
  --destination ./dist \
  --rules-file remove-debug.json \
  --env prod \
  --env-config env_config.json

  ##remove-debug.json:

json
{
  "rules": [
    {"pattern": "console\\.log\\(.*?\\);?", "replace": "", "regex": true},
    {"pattern": "debugger;", "replace": "", "regex": false}
  ]
}

##Example 3: Mask sensitive data
bash
batch-replace \
  --source ./logs \
  --destination ./logs-sanitized \
  --pattern "\\b\\d{16}\\b" \
  --replace "[CREDIT_CARD]" \
  --regex \
  --dry-run

  License
MIT License - See LICENSE file for details

Contributing
Fork the repository

Create a feature branch

Add tests for new features

Ensure all tests pass

Submit a pull request

Support
For issues or questions, please open an issue on the GitHub repository.

text

### `requirements.txt`

```txt
# Core dependencies
chardet>=5.0.0

# Optional dependencies
pyyaml>=6.0  # For YAML support
colorama>=0.4.6  # For colored console output on Windows
rich>=13.0.0  # Enhanced console output

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0

