## Vision
A simple, durable, chapter-owned website that serves active members and alumni for years, survives frequent turnover in its maintainers, and shows the chapter as a group of capable engineers.
## Goals
- Longevity
	- Because:
		- This website will be used for upwards of the next 10 years
		- The development team and webmaster will transfer between people very often
		- Modern web development standards change often
		- Our beginner developers need a solid learning experience
		- Our infrastructure may be forced to change
	- We should have:
		- Architecture which uses long-term support technology
		- Simple administration (content separate from code)
		- Well-documented code
		- Backups
		- Understandable codebase and development practices
		- Chapter-Controlled Accounts (hosting, github, administration)
		- A strong handover plan
- Simplicity
	- Because:
		- People with a large variety of skill levels will work on the website
		- We should leave room for expansion of features
		- A well-built site presents a strong image of us as engineers
	- We should have:
		- A tech stack which relies on few components
		- A consistent, clean, and beautiful design
		- Fast optimization and simple navigation
- Chapter Ownership
	- Follow the needs and requests of the active and alumni chapters
	- Chapter Owned Infrastructure
- Learning Experience
	- The web dev team should use technologies which will prepare its members to complete web development work in the real world
	- The web dev team should use standard recognized software engineering practices when appropriate
## Measures of Success
- A webmaster can complete any standard change in less than 2 minutes (add a profile, change a link, edit the banner image, change member roles)
- A new member of the development team can launch a development instance in less than an hour with only documentation
- A website backup can be restored within 5 minutes by anyone on the development team
- Core pages meet a performance target (to be set later)
- All required credentials for management are stored such that any member of exec can access them
- A webmaster can spin up a new production instance within one hour from documentation alone
- Backups include all content in a portable format
- Website must have a bus factor of at least 3
- All dependencies are up-to-date and under developer support
- All pages can be accessed within 3 clicks
- All page elements are build from a shared component set with minimal one-off styling or CSS unless absolutely necessary
- The active and alumni chapters confirm satisfaction with the website
- All members of the web development team are provided the resources to submit a change that follows good software engineering and documentation practices
## Roles
| Role             | Responsibility                                            |
| ---------------- | --------------------------------------------------------- |
| Chapter          | Sets scope, priorities, and oversees major changes        |
| Webmaster        | Day-to-day ownership, reviews changes, keeps docs current |
| Development Team | Builds features, follows the contribution guidelines      |
| Alumni Chapter   | Represents alumni needs, advises on long-term direction   |
## Risks
| Risk                                          | Mitigation                                                        |
| --------------------------------------------- | ----------------------------------------------------------------- |
| Webmaster leaves with knowledge or access     | Handoff checklist, shared custodians, thorough docs               |
| Chosen tool is abandoned or changes licensing | LTS-prefered, yearly review, keep content in portable formats     |
| Stack grows too complex for beginners         | Dependency justification rule, simplicity review for new features |
| Backups silently fail                         | Automated alerts and scheduled restore tests                      |
| Hosting or domain lapses                      | Chapter-owned billing, renewal reminders, multiple admins         |
| Contributors push low-quality changes         | Branch protection, code review, contribution guide                |
