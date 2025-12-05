# agents/pipeline_agent.py

import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

# Import your two existing agents
from .disease_profile import disease_profile_agent
from .synthea_module import synthea_module_generator_agent

logger = logging.getLogger(__name__)


class DiseaseToSyntheaFlowAgent(BaseAgent):
    """
    Custom agent that orchestrates:
      1) Disease profile generation (PubMed / ClinicalTrials)
      2) Synthea GMF module generation from that profile
    """

    # Pydantic field declarations (same pattern as docs)
    disease_profile_agent: LlmAgent
    synthea_module_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        disease_profile_agent: LlmAgent,
        synthea_module_agent: LlmAgent,
    ):
        # Tell ADK which sub-agents we orchestrate
        sub_agents = [disease_profile_agent, synthea_module_agent]

        super().__init__(
            name=name,
            disease_profile_agent=disease_profile_agent,
            synthea_module_agent=synthea_module_agent,
            sub_agents=sub_agents,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        1) Run disease_profile_agent → capture its final text as disease_profile
        2) Put that into ctx.session.state["disease_profile"]
        3) Run synthea_module_agent, which reads {disease_profile} from state
        """
        logger.info(f"[{self.name}] Starting Disease → Synthea pipeline")

        # -------------------------
        # STEP 1: DISEASE PROFILE
        # -------------------------
        logger.info(f"[{self.name}] Running DiseaseProfileAgent...")
        disease_profile_text = None

        async for event in self.disease_profile_agent.run_async(ctx):
            # Stream everything up to the runner (so you still see profile text if you want)
            yield event

            # Capture the final response text as the disease profile
            if event.is_final_response() and event.content and event.content.parts:
                # Concatenate all text parts, just in case
                parts_text = [
                    getattr(p, "text", "") or "" for p in event.content.parts
                ]
                disease_profile_text = "\n".join(parts_text).strip()

        if not disease_profile_text:
            # Fallback: maybe the agent already wrote to state under some key
            disease_profile_text = (
                ctx.session.state.get("disease_profile")
                or ctx.session.state.get("disease_profile_text")
            )

        if not disease_profile_text:
            logger.error(
                f"[{self.name}] No disease profile text produced. Aborting pipeline."
            )
            return

        # Store final profile into state under a standard key so the Synthea agent
        # can use {disease_profile} in its instruction template.
        ctx.session.state["disease_profile"] = disease_profile_text
        logger.info(
            f"[{self.name}] Stored disease_profile in session.state['disease_profile'] "
            f"(length={len(disease_profile_text)} chars)"
        )

        # -------------------------
        # STEP 2: SYNTHEA MODULE
        # -------------------------
        logger.info(f"[{self.name}] Running SyntheaModuleGeneratorAgent...")
        async for event in self.synthea_module_agent.run_async(ctx):
            # Just pass all events through; the final JSON module will appear
            # as the final LLM response from this agent.
            yield event

        logger.info(f"[{self.name}] Pipeline completed.")


# Instantiate a single root agent you can mount in runner or agent_loader
root_agent = DiseaseToSyntheaFlowAgent(
    name="DiseaseToSyntheaPipeline",
    disease_profile_agent=disease_profile_agent,
    synthea_module_agent=synthea_module_generator_agent,
)
