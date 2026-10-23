## Project Organization
Bugs and changes are tracked with github issues.
Issues are automatically linked to the project's kanboard board.
Any webdev team member may claim an issue to pick up and work on on their own time.

New feature requests should be added to the kanban board as issues and prioritized by the team.
If a feature request is considerable in scope, it should be broken down into smaller sub-issues that can be completed in a reasonable amount of time.

## Branch Management
The website currently does not run off of major deployments. Instead, the main branch is always intended to be in a deployable state. The main branch is protected and cannot be directly pushed to.
Instead, all changes must be made through pull requests before being merged into the main branch.
- All changes should be organized into short-lived feature branches based off of main.
- When ready to merge a feature branch into main, a pull request should be created and reviewed by at least one other team member before being merged.
- After merging, the feature branch should be deleted.

*In the future, a PR template may be introduced and may include a checklist of items to be completed before merging, such as testing, documentation, and migrations.*

## CI/CD
### Continuous Integration
*Not Currently Implemented*
The following should be run on every PR:
- Code linting (ruff, djlint, markdownlint)
- Unit tests (pytest-django)
- `manage.py check --deploy` and `manage.py makemigrations --check`
- Dependency audit (pip-audit)
- Possible performance/accessibility checks?

### Continuous Deployment
*Not Currently Implemented*
The following should be run on every merge to main:
- Build and tag docker image
- Push docker image to container registry
- Pre-deploy backup of production database
- Run database migrations
- Collect static files
- Deploy to production server and restart services
- Run health checks

### Scheduled Jobs
*Not Currently Implemented*
The following should be run on a schedule:
- Database backups
- Dependency updates (via Dependabot)
- Uptime monitoring and alerting
- TLS certificate renewal
- Domain name renewal
- Unattended OS security updates

## Dependency Management
*Not Currently Implemented*
Dependabot for automated update PRs for python packages and docker base images.
New dependencies should be added to the project with care.
Keep all dependencies up to date and remove unused dependencies.

## Backups
Automated backups of the production database should be taken on a regular schedule and stored in a secure location. (currently not stored in a secure location, but should be)

## Deployment
We desire to automate deployment with github CD and docker.
In addition, updates to the production server should be automated and require minimal manual intervention. (the website does not require perfect uptime, so some downtime is acceptable during updates)
Manual deployment should be as simple as possible, ideally a single command to run on the server. (docker/podman compose)
Deployment should run uptime checks on regular intervals and alert the team if the website is down.

## Documentation
Documentation is extremely important for this project as team members may come and go over time. All documentation should be kept up to date and easily accessible to all team members.
All documentation can be found in the Documentation folder of the project repository.
- Project Charter
- Logs of important decisions
- Transition Material
- Software Engineering Practices
- Tech Stack
- Contribution Guidelines
- Runbooks
  - Development Environment Setup
  - Production Deployment Instructions
  - CI/CD Instructions
  - Backup Instructions
  - Domain and Hosting Instructions
  - Server Maintenance Instructions
  - Standard Changes and Updates Instructions
