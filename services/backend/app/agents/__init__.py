"""Agents package.

To add a new DB-configured agent:
1. Subclass DBConfiguredAgent from app.agents.base_agent.
2. Implement agent_id, default_model, timeout_seconds, default_definition, and default_tasks.
3. Keep only domain-specific output parsing and business rules in the concrete agent.
"""

from app.agents.base_agent import AgentDefinitionSpec, BaseAgentError, DBConfiguredAgent, TaskSpec

__all__ = [
	"AgentDefinitionSpec",
	"BaseAgentError",
	"DBConfiguredAgent",
	"TaskSpec",
]
