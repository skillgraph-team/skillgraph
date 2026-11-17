# SkillGraph
## Evidence-Based Skills Intelligence and Opportunity Matching Platform

**Project type:** AI-powered software platform / Startup project  
**Team size:** 4 members  
**Development timeframe:** One academic semester  
**Primary technologies:** Web application, AI/LLMs, multi-agent systems, knowledge graphs, data processing

---

## 1. Project Overview

### 1.1 Description

SkillGraph is an AI-powered skills intelligence platform designed to help individuals understand, demonstrate, and develop their professional capabilities while helping organizations identify suitable candidates for employment and internship opportunities.

Traditional recruitment systems primarily depend on CVs, qualifications, certifications, and self-reported skills. However, these sources do not always accurately represent what an individual can actually do.

A person might list Python, distributed systems, or machine learning on their CV without providing sufficient evidence of their proficiency. Conversely, another person might possess valuable practical skills demonstrated through personal projects, open-source contributions, or independent work that are not adequately represented by conventional qualifications.

SkillGraph addresses this problem by constructing an evidence-based representation of an individual's skills.

The platform collects information from different sources, extracts potential skills, evaluates supporting evidence, identifies skill gaps, and matches individuals with relevant opportunities.

Its distinguishing feature is the use of a collaborative Multi-Agent System (MAS). Specialized AI agents cooperate to analyze information, evaluate evidence, investigate opportunities, and generate personalized recommendations.

The result is a continuously updated skills profile that represents not only what an individual claims to know, but also what they have demonstrated and how confidently the platform can support those conclusions.

### 1.2 Vision

To create a platform where professional capabilities can be represented, evaluated, and connected to opportunities through verifiable evidence rather than relying exclusively on traditional CVs and qualifications.

### 1.3 Problem Statement

There is a gap between the skills individuals claim to possess, the skills they can demonstrate, and the skills organizations require.

This creates several problems:

- Individuals struggle to communicate their practical capabilities effectively.
- Recruiters spend time interpreting CVs and comparing candidates using incomplete information.
- Students and graduates often lack a clear understanding of which skills they need to develop.
- Universities and training organizations have limited visibility into the relationship between their students' capabilities and employment requirements.
- Conventional recruitment platforms often prioritize keywords and qualifications over practical evidence.

SkillGraph aims to reduce this gap by creating structured, evidence-backed skills profiles and connecting them to real opportunities.

---

## 2. Project Objectives

The project has five primary objectives.

### Objective 1: Build evidence-based skills profiles

Allow users to create profiles using multiple sources of information, including:

- CVs and résumés.
- GitHub repositories and project descriptions.
- Personal portfolios.
- Certifications and qualifications.
- Practical assessments.
- Manually submitted projects and experience.

The platform should extract relevant skills and associate each skill with the evidence supporting it.

### Objective 2: Evaluate and organize skills

Go beyond simple skill extraction by evaluating the quality and relevance of available evidence.

For example, listing Python on a CV should not automatically establish proficiency.

The platform should distinguish between:

- Claimed skills: Skills explicitly mentioned by the user.
- Demonstrated skills: Skills supported by projects, contributions, or other evidence.
- Assessed skills: Skills evaluated through practical assessments.
- Unverified skills: Skills for which sufficient evidence is not available.

The platform should also represent relationships between skills. For example, knowledge of Python, databases, APIs, and distributed systems can contribute to a broader representation of backend development capabilities.

### Objective 3: Match individuals with opportunities

Analyze employment and internship requirements and compare them against users' skills profiles.

The system should:

- Identify relevant opportunities.
- Compare required skills against demonstrated capabilities.
- Explain why an individual matches or does not match an opportunity.
- Identify missing requirements.
- Recommend ways to improve compatibility.

### Objective 4: Generate personalized development recommendations

Identify gaps between an individual's current capabilities and the requirements of their desired opportunities.

Generate recommendations such as:

- Practical projects to complete.
- Skills to prioritize.
- Assessments to undertake.
- Learning resources to explore.
- Evidence that could strengthen an existing skills profile.

### Objective 5: Demonstrate practical Multi-Agent Systems

Implement a coordinated system of specialized agents capable of:

- Dividing complex objectives into smaller tasks.
- Communicating and exchanging information.
- Sharing a common representation of the user's skills.
- Evaluating and challenging findings.
- Using external tools and APIs.
- Recovering from unsuccessful operations.
- Producing a consolidated result.

The multi-agent architecture should provide measurable benefits compared with a conventional single-agent or non-agentic implementation.

---

## 3. Target Users and Potential Customers

The initial target market should focus on university students and recent graduates.

### Primary users

**Students and recent graduates**

Individuals who want to understand their professional capabilities, demonstrate practical experience, and discover suitable internships or employment opportunities.

### Potential paying customers

**Recruitment agencies and employers**

Organizations that need to identify candidates based on demonstrated capabilities and specific technical requirements.

Potential benefits include structured candidate profiles, skill-based filtering, and explanations of candidate suitability.

**Universities and educational institutions**

Institutions interested in improving graduate employability and understanding which professional skills their students possess or need to develop.

**Training organizations**

Organizations that want to identify skill gaps and recommend appropriate training paths.

### Initial market strategy

The first version should focus on individual users, particularly students and graduates.

Recruiters and educational organizations can become secondary customer groups after the core platform has been validated.

This approach avoids making the initial product dependent on institutional partnerships.

---

## 4. Core Features

The project should be divided into several functional modules.

### 4.1 User Management and Profile Creation

Users create accounts and build their professional profiles.

Features:
- Authentication and account management.
- Personal information and education.
- CV upload.
- Project and experience management.
- External profile integration.
- Skills profile visualization.

### 4.2 Evidence Collection and Processing

The platform collects information from different sources.

Examples:
- Extracting skills from uploaded CVs.
- Retrieving repository metadata and relevant information from GitHub.
- Processing descriptions of personal projects.
- Recording completed assessments.
- Associating evidence with specific skills.

Every extracted skill should retain a reference to its source.

### 4.3 Skills Intelligence Engine

This is one of the platform's central components.

It organizes skills into a structured representation and associates them with evidence.

For example:

A user has a GitHub repository involving a REST API implemented with Python and PostgreSQL.

The system may identify:

- Python.
- REST API development.
- PostgreSQL.
- Database integration.
- Backend development.

However, these should not all receive identical confidence levels. The platform should consider what the repository actually demonstrates.

The system should also support relationships between skills, allowing it to represent broader competencies.

### 4.4 Opportunity Matching

Users can discover relevant internships and employment opportunities.

The platform compares their skills profiles with opportunity requirements.

Each recommendation should provide:
- Match score.
- Matching skills.
- Missing or insufficiently demonstrated skills.
- Supporting evidence.
- Explanation of the recommendation.

A high match score should not be presented as a guarantee of employability.

### 4.5 Skill Gap Analysis

Users can select an opportunity or a professional direction and compare its requirements against their current profile.

The system identifies missing skills and recommends practical ways to demonstrate them.

For example:

A user wants to apply for a backend development internship requiring Python, SQL, REST APIs, and Docker.

The platform identifies that Python and SQL have supporting evidence, REST APIs have partial evidence, and Docker is not yet demonstrated.

It can then recommend an appropriate practical project or assessment.

### 4.6 Dashboard and Visualization

The dashboard provides an overview of:

- Current skills.
- Evidence supporting each skill.
- Skill confidence and verification status.
- Recent profile updates.
- Relevant opportunities.
- Identified skill gaps.
- Development recommendations.

The interface should make the platform's reasoning understandable rather than displaying unexplained AI-generated scores.

---

## 5. Multi-Agent System Architecture

The Multi-Agent System is the principal technical component that distinguishes SkillGraph from a conventional skills-matching application.

Rather than relying on one general-purpose AI agent, the platform uses specialized agents with distinct responsibilities.

### 5.1 Proposed Agents

**1. Profile Agent**

Responsible for processing user information and constructing the initial skills profile.

Responsibilities:
- Extract information from CVs.
- Analyze project descriptions.
- Retrieve relevant information from connected services.
- Identify potential skills.
- Produce structured skill records.

**2. Evidence Evaluation Agent**

Responsible for examining the evidence associated with identified skills.

Responsibilities:
- Evaluate whether evidence supports a claimed skill.
- Distinguish between claims and demonstrated capabilities.
- Identify weak or insufficient evidence.
- Estimate confidence.
- Request additional information when necessary.

The agent must not claim that a skill has been independently verified simply because an LLM inferred it from a project description.

**3. Opportunity Agent**

Responsible for discovering and analyzing employment and internship opportunities.

Responsibilities:
- Retrieve opportunities from available sources.
- Extract required and desirable skills.
- Identify experience and qualification requirements.
- Normalize different descriptions of similar skills.
- Store structured opportunity information.

**4. Matching Agent**

Responsible for comparing user profiles with opportunity requirements.

Responsibilities:
- Compare required skills against available evidence.
- Calculate compatibility.
- Identify missing requirements.
- Explain matching decisions.
- Rank relevant opportunities.

**5. Development Agent**

Responsible for generating personalized recommendations.

Responsibilities:
- Analyze skill gaps.
- Suggest practical projects and assessments.
- Recommend learning resources.
- Prioritize development objectives.
- Identify opportunities to strengthen existing evidence.

### 5.2 Orchestration Agent

An additional orchestration component coordinates the other agents.

It is responsible for:
- Receiving high-level requests.
- Decomposing requests into tasks.
- Assigning tasks to specialized agents.
- Managing execution order.
- Sharing relevant context.
- Handling failures and retries.
- Collecting results.
- Producing the final response.

For example, when a user requests suitable internships, the orchestrator can:

1. Ask the Opportunity Agent to retrieve available internships.
2. Ask the Matching Agent to compare them against the current skills profile.
3. Ask the Evidence Evaluation Agent to inspect questionable skill matches.
4. Ask the Development Agent to identify ways to address missing requirements.
5. Consolidate the findings into a final recommendation.

### 5.3 Agent Communication

Agents should communicate through structured messages rather than unrestricted natural-language conversations.

A message could contain:

- Task identifier.
- Sending agent.
- Receiving agent.
- Task description.
- Relevant context.
- Expected output format.
- Execution status.
- Result or error information.

A shared database should store the canonical user profile, skills, evidence, opportunities, and assessment results.

The agents should not maintain conflicting independent versions of the user's profile.

### 5.4 Shared Knowledge Graph

A knowledge graph can represent relationships between users, skills, evidence, projects, and opportunities.

Example relationships:

- User HAS_SKILL Python.
- User COMPLETED_PROJECT REST_API.
- REST_API USES_SKILL Python.
- REST_API USES_SKILL PostgreSQL.
- Internship REQUIRES_SKILL Python.
- Internship REQUIRES_SKILL SQL.

This structure allows the platform to perform more sophisticated reasoning than simple keyword comparison.

The knowledge graph can initially be implemented using relational tables and relationships. A dedicated graph database can be considered later if justified by the application's requirements.

---

## 6. Proposed Technical Architecture

The application should use a modular architecture separating the frontend, backend, AI orchestration, data processing, and persistence layers.

### Frontend

A web interface through which users:
- Register and manage profiles.
- Upload CVs.
- Connect external accounts.
- View skills and evidence.
- Discover opportunities.
- Explore recommendations.

Possible technologies:
- Svelte or React.
- HTML, CSS, and JavaScript/TypeScript.

### Backend

Responsible for:
- Authentication.
- API endpoints.
- User and profile management.
- File handling.
- Database operations.
- External integrations.
- Communication with the agent system.

Possible technologies:
- Python with FastAPI.
- PostgreSQL.
- SQLAlchemy.

### AI and Agent Layer

Responsible for:
- LLM integration.
- Agent execution.
- Tool calling.
- Task orchestration.
- Structured output validation.
- Agent communication.
- Evaluation and logging.

Possible technologies:
- Python.
- Provider API or a locally hosted model.
- Raw HTTP requests or an official SDK.
- A custom orchestration implementation.

The initial implementation should avoid depending on a large agent framework. Building the basic agent loop and coordination mechanisms directly would provide a stronger demonstration of the team's understanding of MAS and Agentic AI.

### External Integrations

Potential integrations:
- GitHub API for repository information.
- CV/document parsing.
- Employment and internship data sources.
- Learning resource providers.

External integrations should be selected based on accessibility, API availability, and licensing.

### Database

PostgreSQL can store:
- Users.
- Profiles.
- Skills.
- Evidence.
- Projects.
- Opportunities.
- Skill requirements.
- Matching results.
- Agent execution records.

### High-Level Architecture

User Interface  
↓  
Backend API  
↓  
Agent Orchestrator  
↓  
Specialized Agents  
↓  
Shared Database / Skills Knowledge Graph  
↓  
External APIs and Data Sources

The backend remains responsible for permissions, validation, and database writes. Agents should not have unrestricted access to application data or external services.

---

## 7. Development Methodology

The project should be developed incrementally.

The team should first establish a functional non-agentic foundation, then introduce agent capabilities where they provide measurable value.

### Phase 1: Requirements and Market Validation

**Goal:** Establish that the problem is real and identify the initial customer.

Activities:
- Interview students and recent graduates.
- Interview recruiters if accessible.
- Examine existing recruitment and skills platforms.
- Identify the most common difficulties in demonstrating skills.
- Determine what information users are comfortable sharing.
- Identify potential willingness to pay.

Deliverables:
- Problem statement.
- Target user definition.
- Initial feature requirements.
- Competitor analysis.
- MVP scope.

### Phase 2: System Design

**Goal:** Define how the application and agents will interact.

Activities:
- Design the database schema.
- Define the skills representation.
- Define the evidence model.
- Design agent responsibilities.
- Define communication protocols.
- Design the API.
- Establish permissions and data-handling rules.

Deliverables:
- System architecture diagram.
- Database schema.
- Agent interaction diagrams.
- API specifications.
- Initial UI prototypes.

### Phase 3: Build the Core Platform

**Goal:** Create a functional application without depending on autonomous agents.

Activities:
- Implement authentication.
- Build user profiles.
- Implement CV upload.
- Integrate GitHub.
- Implement basic skill extraction.
- Store skills and evidence.
- Create the initial dashboard.

Deliverable:

A working platform that can collect user information and construct a basic skills profile.

### Phase 4: Implement the Multi-Agent System

**Goal:** Introduce specialized agents and coordinated execution.

Recommended implementation order:

1. Profile Agent.
2. Evidence Evaluation Agent.
3. Opportunity Agent.
4. Matching Agent.
5. Development Agent.
6. Orchestration component.

Start with one agent and validate its outputs before introducing additional agents.

Then implement:
- Structured agent communication.
- Shared state.
- Task delegation.
- Error handling.
- Bounded retries.
- Execution logging.
- Human approval for sensitive or consequential actions.

Deliverable:

A functioning multi-agent workflow capable of analyzing a user profile and producing evidence-based recommendations.

### Phase 5: Opportunity Matching and Recommendations

**Goal:** Complete the primary user-facing functionality.

Activities:
- Integrate opportunity sources.
- Extract job requirements.
- Implement skill matching.
- Generate explanations.
- Implement skill gap analysis.
- Generate personalized development recommendations.

Deliverable:

Users can compare their skills against available opportunities and receive explanations of their compatibility.

### Phase 6: Testing and Evaluation

**Goal:** Establish that the system works reliably and that its agent architecture provides value.

Activities:
- Test CV extraction accuracy.
- Evaluate evidence assessment.
- Test matching quality.
- Test agent coordination.
- Test failure recovery.
- Measure execution cost and latency.
- Compare agent-based and conventional implementations.

Deliverable:

An evaluated system with documented results, limitations, and demonstrations.

### Phase 7: Deployment and Presentation

**Goal:** Deliver a usable product and demonstrate its commercial and technical potential.

Activities:
- Deploy the application.
- Prepare sample profiles.
- Prepare sample opportunities.
- Demonstrate complete workflows.
- Present evaluation results.
- Collect feedback from potential users.

Deliverable:

A deployed MVP, technical documentation, evaluation report, and startup presentation.

---

## 8. Proposed Semester Timeline

The following is a suggested 14-week schedule. It should be adjusted to the university's actual deadlines.

| Period | Main activities |
|---|---|
| Weeks 1–2 | Market validation, requirements, competitor research |
| Weeks 3–4 | Architecture, database, UI prototypes |
| Weeks 5–6 | Authentication, profiles, CV/GitHub integration |
| Weeks 7–8 | Skill extraction, evidence model, initial agents |
| Weeks 9–10 | Agent coordination, opportunity analysis, matching |
| Weeks 11–12 | Skill gap analysis, recommendations, testing |
| Week 13 | Deployment, evaluation, performance improvements |
| Week 14 | Final documentation and presentation |

A functional prototype should exist before the final third of the semester. The team should avoid spending most of the available time on architecture without producing a working application.

---

## 9. Team Organization

The project can be divided into four primary responsibilities.

### Member 1: Multi-Agent Architecture

Responsibilities:
- Agent orchestration.
- Agent communication protocols.
- Shared state management.
- Task delegation.
- Error handling and retries.
- Agent execution logging.

### Member 2: AI and Skills Intelligence

Responsibilities:
- CV processing.
- Skill extraction.
- Evidence evaluation.
- LLM integration.
- Structured output validation.
- Skill relationships and knowledge representation.

### Member 3: Backend and Data Infrastructure

Responsibilities:
- Backend API.
- Database architecture.
- Authentication.
- File handling.
- GitHub and opportunity integrations.
- Application security and deployment infrastructure.

### Member 4: Frontend and User Experience

Responsibilities:
- User interface.
- Profile management.
- Dashboard.
- Skills visualization.
- Opportunity browsing.
- Integration with backend APIs.
- Frontend testing.

All four members should participate in integration, testing, documentation, and technical decisions. These divisions establish ownership, not isolated development.

---

## 10. Evaluation and Success Criteria

The project should be evaluated through both functional and technical criteria.

### Functional Evaluation

- Can users create and update profiles?
- Can the platform extract skills from different sources?
- Can each skill be associated with evidence?
- Can users discover relevant opportunities?
- Can the platform explain its matching decisions?
- Can it identify skill gaps?
- Are recommendations relevant and actionable?

### Multi-Agent Evaluation

The team should compare three implementations:

**A. Conventional baseline**

A traditional application using deterministic rules and conventional matching.

**B. Single-agent implementation**

One AI agent performs the entire analysis using available tools.

**C. Multi-agent implementation**

Several specialized agents coordinate to perform the same task.

Compare them using:

| Metric | What it measures |
|---|---|
| Extraction accuracy | Correctness of identified skills |
| Evidence assessment quality | Whether evidence genuinely supports the skill |
| Matching precision | Proportion of recommended opportunities that are relevant |
| Task completion rate | Percentage of workflows completed successfully |
| Latency | Time required to produce results |
| Execution cost | AI/API cost per completed workflow |
| Failure rate | Frequency of unsuccessful executions |
| Coordination overhead | Additional time and cost introduced by multiple agents |

The multi-agent system should not automatically be considered better. The evaluation should establish whether specialization and coordination improve the quality or reliability of the results enough to justify their additional complexity.

---

## 11. Business Model and Commercial Potential

SkillGraph can potentially operate through a combination of individual and organizational services.

### Individual Users

A free tier could provide:
- Basic skills profile.
- Limited evidence sources.
- Basic opportunity matching.

A premium tier could eventually provide:
- Additional integrations.
- More detailed assessments.
- Advanced development recommendations.
- Extended profile analytics.

### Recruitment Organizations

A subscription-based service could provide:
- Candidate discovery.
- Skills-based filtering.
- Structured candidate profiles.
- Evidence-backed candidate comparisons.

### Universities and Training Organizations

Potential services:
- Student skills analytics.
- Skill-gap identification.
- Employability reporting.
- Training recommendations.

### Initial Commercial Strategy

The initial product should prioritize validating demand rather than implementing a complex payment system.

A reasonable approach is to recruit a small group of students to test the platform, collect feedback, and determine whether recruiters or training organizations would pay for access to structured skills information.

---

## 12. Risks and Limitations

### Accuracy of AI-generated conclusions

An LLM can infer skills that are not genuinely demonstrated by the available evidence.

Mitigation:
- Store the original evidence.
- Require explanations for extracted skills.
- Distinguish claims from demonstrated capabilities.
- Use confidence levels and verification statuses.
- Allow users to challenge or correct results.

### Limited availability of opportunity data

Some job platforms restrict automated access or do not provide public APIs.

Mitigation:
- Start with manually curated opportunities.
- Use legitimate APIs and accessible sources.
- Allow organizations to submit opportunities directly.

### Privacy and user data

CVs, employment histories, and external profiles can contain personal information.

Mitigation:
- Obtain explicit consent for integrations.
- Restrict access to user data.
- Provide account and data deletion functionality.
- Avoid sharing private profile information with recruiters without authorization.

### Multi-agent complexity

Additional agents introduce more API calls, latency, cost, and possible inconsistencies.

Mitigation:
- Keep agent responsibilities narrow.
- Use structured communication.
- Establish execution limits.
- Validate agent outputs.
- Evaluate whether each additional agent improves the workflow.

### Market competition

Existing recruitment and career platforms already offer profile analysis, recommendations, and matching.

Mitigation:
- Focus on evidence-backed skills rather than generic CV optimization.
- Make the reasoning behind skill assessments transparent.
- Develop a useful skills representation that can be reused across multiple opportunities.

---

## 13. Minimum Viable Product (MVP)

The first version should be deliberately limited.

The recommended MVP should include:

1. User registration and profile management.
2. CV upload and parsing.
3. GitHub repository integration.
4. Automated skill extraction.
5. Evidence-backed skills profiles.
6. A small, curated collection of internships and jobs.
7. Skill-based opportunity matching.
8. Explanations of matching results.
9. Basic skill gap analysis.
10. A functioning multi-agent workflow.

The MVP does not need:
- A complete recruitment management system.
- A large employment marketplace.
- Complex graph databases.
- Extensive university integrations.
- Automated hiring decisions.
- A fully autonomous career assistant.

The objective is to demonstrate a complete, useful workflow rather than an enormous collection of partially implemented features.

---

## 14. Expected Final Outcome

At the end of the semester, the team should have a deployed application that demonstrates the following workflow:

1. A student creates an account.
2. The student uploads a CV and connects a GitHub account.
3. The Profile Agent extracts potential skills.
4. The Evidence Evaluation Agent examines supporting information.
5. The system constructs an evidence-backed skills profile.
6. The Opportunity Agent retrieves and analyzes available internships.
7. The Matching Agent identifies relevant opportunities.
8. The Development Agent identifies missing skills and recommends ways to demonstrate them.
9. The user receives an understandable report explaining their capabilities, matching results, and potential development path.

The project should demonstrate that multiple specialized agents can collaborate to solve a complex problem involving information extraction, evidence evaluation, reasoning, and recommendation generation.

---

## 15. Conclusion

SkillGraph aims to bridge the gap between professional skills, demonstrable capabilities, and employment opportunities.

By combining evidence-based skills representation, AI-powered analysis, and multi-agent coordination, the platform offers an alternative to conventional systems that rely heavily on self-reported skills and CV keywords.

Its commercial potential comes from addressing problems faced by individuals, recruiters, and educational organizations. Its technical value comes from the implementation and evaluation of a coordinated multi-agent system that performs meaningful work rather than simply generating text.

The recommended development strategy is to begin with a narrow student-focused MVP, establish a reliable skills and evidence model, introduce specialized agents incrementally, and validate the product with real users before expanding its functionality.

**The central principle of SkillGraph is simple: a professional skill should be supported by evidence, and that evidence should help connect people to opportunities where their capabilities matter.**