# agent/agent.py
from google.adk.agents import SequentialAgent

from .synthea_module import synthea_module_generator_agent
from .disease_profile import disease_profile_agent  # or wherever you defined it

root_agent = SequentialAgent(
    name="DiseaseToSyntheaPipeline",
    sub_agents=[
        disease_profile_agent,           # Step 1: build disease_profile JSON
        synthea_module_generator_agent,  # Step 2: turn it into Synthea GMF module
    ],
)
