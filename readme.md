# Engineering Operations Hub (EOH)

Engineering Operations Hub (EOH) is an on-prem, agentic software engineering system designed to transform unstructured business requests into working software with minimal human effort.  
It combines specialized AI agents, deterministic workflow orchestration, and GitHub-native delivery to automate analysis, architecture, planning, coding, review, and staged deployment.

EOH is built for organizations that need:
- Data privacy (local model inference)
- Human-in-the-loop governance (approvals and feedback)
- End-to-end traceability (request to deployment)
- Fast iterative delivery with controlled autonomy

## What EOH Does

EOH accepts software requests in natural language and runs a structured delivery lifecycle:

1. Intake and Clarification  
- Receive requests via unified portal (and channel adapters like email/chat)
- Detect missing information and ask targeted clarification questions

2. Analysis and Design  
- Draft BRD and system architecture artifacts
- Route mandatory approvals at defined gates

3. Planning and Execution  
- Generate backlog and implementation tasks
- Create branches/PRs and produce code with tests

4. Review and Delivery  
- Run automated review and CI checks
- Deploy to staging for human feedback

5. Learning and Iteration  
- Capture outcomes, trace decisions, and improve future runs
- Support change requests and feature additions after initial releases

## Core Architecture

EOH separates interaction from orchestration:

- Engineering Operations Hub (EOH) UI:
- Request intake
- Project visibility
- Agent activity monitoring
- Human task inbox (approvals, clarifications, feedback)
- Basic operational controls (pause/resume/retry)

- Agentic Backend:
- CrewAI agent roles and collaboration
- LangGraph stateful orchestration with checkpoints
- Policy and gate enforcement
- Artifact and workflow state persistence
- GitHub integration (issues, branches, PR, CI/deploy)

- Model Runtime (Remote):
- Ollama hosted on a separate machine (PC1)
- Private LAN connectivity from project host to PC1

## Agent Roles

EOH uses specialized agents with role-aligned models:

- Receptionist: intake classification, clarification prompts
- Analyst: BRD and requirements synthesis
- Architect: architecture and ADR reasoning
- PM: backlog decomposition and dependency planning
- Developer: code and test generation
- Reviewer: code review and targeted fix guidance
- Release: release checklist and status orchestration
- Learning: post-run summaries and improvement signals

## Human-in-the-Loop by Design

EOH is autonomous where possible and supervised where necessary.  
Humans remain responsible for high-impact decisions through explicit gates:

- BRD approval
- Architecture approval
- Release approval (per policy/risk)

Asynchronous interaction is first-class:
- Users can respond later via portal/email/chat
- LangGraph workflows pause in waiting states and resume from checkpoints

## Configuration Philosophy

EOH is configuration-driven through the portal:
- All modifiable runtime parameters are managed in EOH
- Static files are reserved for hard technical constraints only
- Configuration changes are RBAC-controlled, auditable, and rollback-capable

## Prototype Scope (15-Day MVP)

The MVP focuses on proving the full path from request to staging deployment under constrained hardware and controlled concurrency.

Included:
- Unified portal baseline
- Core workflow and approvals
- GitHub PR/CI integration
- Staging delivery and feedback loop
- Traceability artifacts across lifecycle

Deferred:
- Advanced compliance automation
- Full production auto-release
- Enterprise-scale observability and portfolio controls

## Runtime Constraints (Current Profile)

Current execution profile is optimized for limited local resources:
- Project host: low-resource WSL environment
- Worker profile: capped concurrency (Profile S)
- Remote model inference on PC1 to reduce local load

## Vision

EOH aims to reduce developer effort in repetitive analysis and coding cycles while improving delivery speed, consistency, and governance.  
The long-term goal is controlled autonomy: AI agents do most delivery work, while humans provide strategic direction, approvals, and feedback.
