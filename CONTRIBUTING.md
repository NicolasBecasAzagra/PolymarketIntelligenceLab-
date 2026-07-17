# Contributing to Polymarket Intelligence Lab

We follow a strict **Gitflow** branching model and commit conventions to maintain a clean history and ensure that multiple features can be developed concurrently without breaking the main branch.

## Branching Strategy

- **`main`**: The production-ready state. Only receives merges from `develop` or hotfixes.
- **`develop`**: The integration branch for features. This is the default branch for ongoing development.
- **`feature/<feature-name>`**: Branches for developing new features. Must branch off from `develop` and merge back into `develop`.
- **`bugfix/<bug-name>`**: Branches for fixing bugs in the development environment.
- **`hotfix/<hotfix-name>`**: Emergency fixes that branch directly off `main` and merge back into both `main` and `develop`.

## Workflow

1. Update your local repository: `git checkout develop && git pull origin develop`
2. Create a new branch: `git checkout -b feature/my-awesome-feature`
3. Develop your feature, ensuring that you update the `.ai/` tracking files as you progress.
4. Run tests and linters locally (`make test`, `make lint`).
5. Commit your changes using Conventional Commits.
6. Push your branch to the remote repository.
7. Open a Pull Request against `develop`.

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` for new features.
- `fix:` for bug fixes.
- `docs:` for documentation changes (including `.ai/` files).
- `refactor:` for code changes that neither fix a bug nor add a feature.
- `test:` for adding or modifying tests.
- `chore:` for updating build tasks, package manager configs, etc.

*Example:* `feat: implement bronze layer ingestion for polymarket orderbook`
