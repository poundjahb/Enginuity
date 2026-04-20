import os
from abc import ABC, abstractmethod
from typing import TypedDict

from crewai import Agent, Crew, LLM, Task
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import AgentDefinition, TaskDefinition


class AgentDefinitionSpec(TypedDict):
    role: str
    goal: str
    backstory: str
    llm_model_override: str | None


class TaskSpec(TypedDict):
    description_template: str
    expected_output: str
    async_execution: bool


class BaseAgentError(RuntimeError):
    pass


class DBConfiguredAgent(ABC):
    @property
    @abstractmethod
    def agent_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def default_model(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def default_definition(self) -> AgentDefinitionSpec:
        raise NotImplementedError

    @abstractmethod
    def default_tasks(self) -> list[TaskSpec]:
        raise NotImplementedError

    def normalize_model_name(self, model_name: str) -> str:
        if model_name.startswith("ollama/"):
            return model_name.split("/", 1)[1]
        return model_name

    def build_llm(self, model_override: str | None = None) -> LLM:
        selected_model = model_override or self.default_model
        model_name = self.normalize_model_name(selected_model)
        routed_model_name = f"ollama/{model_name}"

        if settings.disable_openai:
            os.environ["OPENAI_API_KEY"] = "disabled"

        return LLM(
            model=routed_model_name,
            base_url=settings.ollama_base_url.rstrip("/"),
            timeout=self.timeout_seconds,
            temperature=0,
            max_tokens=220,
        )

    def _load_definition_from_db(self, db: Session) -> AgentDefinitionSpec | None:
        record = (
            db.query(AgentDefinition)
            .filter(AgentDefinition.agent_id == self.agent_id)
            .filter(AgentDefinition.is_active.is_(True))
            .first()
        )
        if not record:
            return None

        return {
            "role": str(record.role),
            "goal": str(record.goal),
            "backstory": str(record.backstory),
            "llm_model_override": str(record.llm_model_override) if record.llm_model_override else None,
        }

    def _load_tasks_from_db(self, db: Session) -> list[TaskSpec]:
        records = (
            db.query(TaskDefinition)
            .filter(TaskDefinition.agent_id == self.agent_id)
            .filter(TaskDefinition.is_active.is_(True))
            .order_by(TaskDefinition.execution_order.asc(), TaskDefinition.task_id.asc())
            .all()
        )

        return [
            {
                "description_template": str(item.description_template),
                "expected_output": str(item.expected_output),
                "async_execution": bool(item.async_execution),
            }
            for item in records
        ]

    def _render_task_description(self, description_template: str, context: dict[str, str]) -> str:
        return description_template.format(**context)

    def _resolve_definition_and_tasks(self) -> tuple[AgentDefinitionSpec, list[TaskSpec]]:
        definition = self.default_definition()
        task_specs = self.default_tasks()

        if settings.agent_definition_db_enabled:
            db = SessionLocal()
            try:
                db_definition = self._load_definition_from_db(db)
                if db_definition:
                    definition = db_definition
                elif not settings.agent_definition_fallback_enabled:
                    raise BaseAgentError(f"{self.agent_id} definition not found in database")

                db_tasks = self._load_tasks_from_db(db)
                if db_tasks:
                    task_specs = db_tasks
                elif not settings.agent_definition_fallback_enabled:
                    raise BaseAgentError(f"No active tasks found for agent {self.agent_id}")
            finally:
                db.close()

        return definition, task_specs

    def execute_tasks(self, context: dict[str, str]) -> str:
        definition, task_specs = self._resolve_definition_and_tasks()
        llm = self.build_llm(definition.get("llm_model_override"))

        runtime_agent = Agent(
            role=definition["role"],
            goal=definition["goal"],
            backstory=definition["backstory"],
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )

        tasks: list[Task] = []
        for task_spec in task_specs:
            task = Task(
                description=self._render_task_description(task_spec["description_template"], context),
                expected_output=task_spec["expected_output"],
                agent=runtime_agent,
                context=list(tasks) if tasks else None,
                async_execution=task_spec["async_execution"],
            )
            tasks.append(task)

        if not tasks:
            raise BaseAgentError(f"No tasks configured for agent {self.agent_id}")

        crew = Crew(agents=[runtime_agent], tasks=tasks, verbose=False)
        result = crew.kickoff()
        return getattr(result, "raw", None) or str(result)
