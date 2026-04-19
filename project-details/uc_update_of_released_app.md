Yes. The model you defined is well-suited for updates and feature additions after alpha, as long as you treat every change as a new governed delivery cycle linked to the existing product baseline.

How it should work for your example (2 new features after alpha):

1. New change request intake
- Receptionist Agent creates a Change Request from the user prompt.
- It tags request type as feature addition, not net-new product.
- It links to current release baseline (alpha version, existing BRD, architecture, repo state).

2. Delta analysis instead of full re-analysis
- Analyst Agent produces Delta-BRD:
- business value of each new feature
- impacted existing flows
- revised acceptance criteria
- non-functional impact (performance, security, compliance)
- If ambiguity is high, it asks focused questions before proceeding.

3. Architecture impact assessment
- Architect Agent creates Delta-Architecture:
- components/services touched
- schema/API changes
- backward compatibility risks
- migration requirements
- Senior dev gate is triggered only if risk threshold is exceeded.

4. Re-planning and sequencing
- PM Agent splits each new feature into stories and dependencies.
- It can choose parallel streams if features are independent.
- It updates roadmap and release train (alpha+1, beta, patch, etc.).

5. Implementation and review
- Developer Agent works in feature branches.
- Reviewer Agent enforces regression tests plus new tests for added features.
- CI quality and security gates remain mandatory.

6. Controlled release
- Release Agent deploys to staging for feedback.
- Production gate applies by risk policy (auto for low-risk, manual for medium/high-risk).
- Learning Agent captures what changed and improves future estimations/prompts.

What to add to your architecture to make this robust:

1. Add explicit change states to the workflow
- Change_Request_Received
- Delta_BRD_Draft
- Delta_Architecture_Draft
- Regression_Test_Gate
- Incremental_Release

2. Add versioning discipline
- BRD versions (v1, v1.1, v1.2)
- ADR supersession tracking
- semantic app versioning tied to feature bundles

3. Add impact and risk scoring
- auto-calculate blast radius (files/modules/services touched)
- enforce stronger gates when critical modules are impacted

4. Add regression protection
- baseline test snapshot from alpha
- mandatory regression suite before any feature merge

So yes: your system can handle continuous feature evolution very well. The key is to run an incremental delta workflow, not restart the full lifecycle each time.

If you want, I can draft the exact “Feature Update Workflow” section you can append to your architecture doc, including state transitions and gate rules.