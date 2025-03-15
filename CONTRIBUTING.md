# Contributing to Mumble

Thank you for your interest in contributing to Mumble! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug in the application, please create an issue on GitHub with the following information:

1. A clear, descriptive title
2. Steps to reproduce the bug
3. Expected behavior
4. Actual behavior
5. Screenshots (if applicable)
6. Your environment (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue on GitHub with:

1. A clear, descriptive title
2. A detailed description of the proposed feature
3. Any relevant mockups or examples
4. Why this feature would be useful to the project

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mumble.git
   cd mumble
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt  # Will be created in the future
   ```

## Coding Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Write unit tests for new functionality

## Testing

Run the tests with:
```bash
python -m unittest discover tests
```

## Documentation

- Update documentation when changing functionality
- Document new features thoroughly
- Keep the README.md up to date

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in the present tense (e.g., "Add feature" not "Added feature")
- Reference issue numbers when applicable

## Review Process

1. All pull requests will be reviewed by a maintainer
2. Feedback may be given for changes or improvements
3. Once approved, your pull request will be merged

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license. 