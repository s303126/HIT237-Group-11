# HIT237-Group-11

**Group Contract Version:** 1.1 | **Last Updated:** 18/03/2026

# 1.0 Terms and Conditions
## 1.1 Group Allocation
All members should receive the same mark if they contribute the agreed upon workload (otherwise the group will proceed with steps outlined in Conflict Resolution). A fair contribution should be an amount of work that all team members agree, and should take up roughly 25% of the total time required by all students to finish the work.

## 1.2 Communication
MS Teams will be the primary source of communication. Replies are expected in 24 hours. If there is no reply within that time, team member/s will send messages through learnline and email. MS Teams should be installed on all phones so that team members can call eachother in case of emergency. (for example a small portion of code is missing, and there is only a few hours until a deadline is due)

Meetings will be held weekly on Mondays at 4pm (communication will be held by the end of each Sunday discussing if the meeting is needed). Meeting minutes will be recorded with a rotating schedule and confirmation on the accuracy of meeting minutes will be given by all team members.

## 1.3 Task Ownership
All team member's tasks will be assigned with full team discussion and unanimous decision. There will be agreed upon checkpoints for tasks to be completed, where all team members must report on their progress.
If a team member falls behind, they will first inform the group on if they believe they are able to catch up. The member will be assigned a buddy team member to assist. If they do not believe they are able to catch up on the work, a group meeting will be held and tasks reassigned. The Collaborative Learning Facilitator will be informed of the situation.
Team members must inform the rest of the team ASAP if they suspect they will be unable to complete a task before a given deadline

## 1.4 Diverse Working Styles
When scheduling meetings/deadlines/other events, all times must be sent in the Darwin time zone. If a team member has difficulty learning the material or reaching an internal deadline/checkpoint, they can request that the internal deadlines/checkpoints are moved, and/or ask other team members for help in understanding the material.

## 1.5 Conflict Resolution
All issues will be discussed openly, and effort will be made from each member involved to try and resolve the situation.
If team members agree that there is no foreseeable resolution to the issue, the Collaborative Learning Facilitator will be contacted with a written summary of steps already taken to resolve the issue within the team.

## 1.6 Academic Integrity and AI usage
All team members must uphold CDU's Academic Integrity policies throughout all assessments. Team members must genuinely understand and be able to explain all submitted work, no member will plagiarise from external sources.

AI coding assistants are permitted as per assessment specifications. Any significant AI contribution must have a corresponding ADR entry written in the contributing member's own words, demonstrating genuine understanding of the code not just a summary of the AI output. Where applicable, the ADR entry structure outlined in the Assessment 2 task sheet on Learnline should be followed.

## 1.7 Amending the Contract
It is expected that the Contract will frequently be amended as the team progresses through the assessments.
Any member may propose an amendment by posting in the group Microsoft Teams channel. The proposal must remain open for at least 24 hours to allow all members to respond. Amendments require agreement from at least three of four members. The amending member then updates the markdown file and the contract version and date, then commits with a message that includes the reason and section amended.


# 2.0 Provisional Milestones and Checkpoints
## 2.1 Key milestones with target dates for each assessment

(Milestone 1: Target Date - 23/03) Initial Assessment discussion, team member role assignment, expectations and requirements from the team.
Following project theme (5), assign design and development roles to team members for each part of the web app. completed tasks uploaded to GitHub to be merged. following code design and implementation requirements according to task (Django).

(Milestone 2: Target Date - 30/03) Follow up with team on individual task progression, discuss any barriers/blockers that might need to be addressed and propose resolutions and review code/design progress. Contribute to Architectural Decision Record (ADR) as well as update project plan and group contract (GitHub).

(Milestone 3: Target Date 7/04) Finalize project and merge pending changes with GitHub project. Perform testing prepare documentation to ensure there are no errors. Update ADR, project plan and group contract.

(Milestone 4: Target Date 14/04) Assessment 2 Submission. Meeting to reflect on deliverables, discuss and prepare initial requirements and scope for Assessment 4. Distribute tasks for team members

Submission includes:
    - The ADR as a Markdown (.md) file
    - The complete, runnable Django app
    - The updated project plan and contract as a Markdown (.md) file
    - Supplementary materials
    - The requirements.txt file

(Milestone 5: Target Date 21/04) Follow up with team on individual task progression, discuss any barriers/blockers that might need to be addressed and propose resolutions and review code/design progress. Include supplementary materials.

(Milestone X: Target Date 28/05) Assessment 4 Submission. Meeting to reflect on deliverables and overall team work.

Submission includes:
    - The ADR as a Markdown (.md) file
    - The complete, runnable Django app
    - The updated project plan and contract as a Markdown (.md) file
    - Supplementary materials
    - The requirements.txt file


## 2.2 Task breakdowns showing how the assessed topics will be tackled and by whom

To ensure balanced contributions and clear responsibility throughout the project, the work for the Django application will be divided into the following roles and responsibilities: 

### Backend Architecture and Data Modelling - Jack Manning
    -	Design Django models representing species recordings, locations and observations
    -	Use Django ORM to implement relationships between entities
    -	Use Django QuerySet APIs to retrieve and filter biodiversity data
    -	Produce ER diagrams showing data relationships

### Application Logic and Views - Isaac Jessen 
    -	Implement application logic using Django class-based views
    -	Handle requests for audio recording submission and view of species data
    -	Ensure views interact correctly with models and templates
    -	Apply Django design philosophies

### User interface and Templates - Aaron Madelo
    -	Develop front-end interface using Django templates
    -	Implement pages for recording submission and viewing timelines of observations
    -	Integrate Django Template Language (DTL) variables
    -	Build templates and UI, and maintain for consistency and usability

### QuerySet APIs, Data Managemnet and Documentation - Melanie Bardoux
    -	Write and manage all QuerySet APIs across the project
    -	Manage and maintain project data including sourcing and importing species data
    -	Create and maintain the ERD and supplementary materials including class diagrams
    -	Set up and maintain the ADR, ensuring all entries follow the correct structure and required information

### Architectural Decision Records (ADR) and Documentation:
    -	All members participate in coding, testing and debugging
    -	All members contribute to the ADR; entries demonstrate understanding of all implemented features, including AI-assisted code 
    -	Contributions are managed with Git branches and pull requests 
    -	All entries must include context, alternatives, decision rationale and code references
    -	All members must document decisions related to their work 


## 2.3 Internal checkpoints or review points where the team will assess progress

| Date | Topic                                                                                                                                                                                                                           | Method  |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| 23/3 | Weekly Chekup                                                                                                                                                                                                                   | Meeting |
| 30/3 | Weekly Checkup                                                                                                                                                                                                                  | Meeting |
| 6/4  | Weekly Checkup                                                                                                                                                                                                                  | Meeting |
| 10/4 | All team members confirm if any last tasks are on track to be completed before 14/4                                                                                                                                             | Meeting |
| 13/4 | No meeting as the assignment is due the following day, so any problems should already have been shared via message.   Team members confirm that all tasks have been completed and that the assignment is ready to be submitted. | Message |
| 20/4 | Discuss steps toward planning assessment 4                                                                                                                                                                                      | Meeting |
| n/a  | Team members create post when they’ve completed a task or encounter any roadblocks (this can then be resolved either in the next meeting or immediately depending on urgency)                                                   | Message |
| n/a  | Weekly meetings will continue once plans are made from the 20/4 meeting                                                                                                                                                         |         |


## 2.4 Integration Points
At each weekly Monday meeting the team will assess individual progress and agree on an integration point date, which will be recorded in the meeting minutes. Team members work on their individual tasks until the agreed date, at which point work is merged into the main branch. Members then have 48 hours to test and review the combined codebase, raising and resolving any conflicts via the Microsoft Teams group chat. Integration must occur at least fortnightly to ensure conflicts and issues are identified and resolved early.

# Contributors
| Name            | Student-id | email                       |
|-----------------|------------|-----------------------------|
| Isaac Jessen    | s388590    | isaac.b.jessen@gmail.com    |
| Melanie Bardoux | s329560    | s329560@students.cdu.edu.au |
| Jack Manning    | s303126    | s303126@students.cdu.edu.au |
| Aaron Madelo    | s389992    | s389992@students.cdu.edu.au |
