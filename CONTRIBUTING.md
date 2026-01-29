# Contributing to Smart Coach Pose Estimation

Thank you for your interest in contributing to Smart Coach Pose Estimation! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Virtual environment tool (venv, conda, etc.)

### Installation

**Quick Setup (Recommended):**
```bash
# One-command setup
bash scripts/tools/setup.sh
```

**Manual Setup:**

1. Clone the repository:
   ```bash
   git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
   cd Smart_Coach_Pose_Estimation
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv mediapipe_env
   source mediapipe_env/bin/activate  # On Windows: mediapipe_env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. Download model files:
   ```bash
   python scripts/tools/download_models.py
   ```

6. Verify setup:
   ```bash
   python scripts/tools/verify_setup.py
   ```

**For detailed setup instructions, see [SETUP.md](docs/guides/SETUP.md).**

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/your-feature-name` for new features
- `fix/issue-description` for bug fixes
- `docs/documentation-update` for documentation changes
- `refactor/component-name` for refactoring

### Commit Messages

Write clear, concise commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when relevant

Example:
```
Add hand tracking smoothing algorithm

- Implement exponential moving average for landmark positions
- Add configuration parameters for smoothing factor
- Update tests to cover new functionality

Fixes #123
```

## Submitting Changes

### Before Submitting

1. **Test your changes**: Ensure all existing tests pass and add new tests for your changes
2. **Update documentation**: Update relevant documentation, including docstrings and README
3. **Check code style**: Follow the project's coding standards (see below)
4. **Verify paths**: Ensure all file paths follow the new repository structure

### Pull Request Process

1. Update the README.md or relevant documentation with details of changes if applicable
2. Ensure your code follows the project's coding standards
3. Include a clear description of the changes and their purpose
4. Reference any related issues in the PR description
5. Be prepared to address feedback and make revisions

### Pull Request Template

When submitting a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add docstrings to functions and classes
- Use type hints where appropriate

### File Organization

Follow the project structure:
```
smart_coach/          # Core library code
scripts/              # Executable scripts
  ├── processing/     # Main processing scripts
  └── tools/          # Utility scripts
data/                 # Data files (gitignored)
config/               # Configuration files
tests/                # Unit tests
docs/                 # Documentation
```

### Path Management

- Always use the new directory structure
- Model paths: `data/models/`
- Input paths: `data/input/`
- Output paths: `data/output/`
- Config paths: `config/`

### Testing

- Write unit tests for new functionality
- Place tests in the `tests/` directory
- Use descriptive test names
- Aim for good code coverage

### Documentation

- Update docstrings when modifying functions
- Keep README.md current
- Document breaking changes clearly
- Update migration guides if changing structure

## Questions?

If you have questions or need help:
- Open an issue with the `question` label
- Reach out to maintainers
- Check existing issues and documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

Thank you for contributing to Smart Coach Pose Estimation! 🎯
