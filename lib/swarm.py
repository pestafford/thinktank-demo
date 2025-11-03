"""
ThinkTank Demo - Swarm Orchestration
Parallel multi-agent deliberation system
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from lib.agent import Agent
from lib.config import SWARM_SIZE, PARALLEL_EXECUTION, MAX_WORKERS, AGENT_MAX_TOKENS, FOREPERSON_MAX_TOKENS


class Swarm:
    """
    Orchestrates multi-agent debate with parallel execution.
    """

    def __init__(self, personas, verbose=False, use_parallel=None):
        """
        Initialize swarm with personas.

        Args:
            personas: List of persona dicts (including foreperson)
            verbose: Print detailed progress
            use_parallel: Override parallel execution setting
        """
        self.verbose = verbose
        self.use_parallel = use_parallel if use_parallel is not None else PARALLEL_EXECUTION

        # Select agents per camp based on SWARM_SIZE
        selected = []
        for camp, count in SWARM_SIZE.items():
            camp_personas = [p for p in personas if p.get("camp") == camp]
            if len(camp_personas) >= count:
                selected += random.sample(camp_personas, count)
            else:
                selected += camp_personas  # Use all if not enough

        # Add Foreperson
        foreperson_personas = [p for p in personas if p.get("camp") == "Foreperson"]
        if foreperson_personas:
            selected += foreperson_personas[:1]

        # Create agents with labels
        self.agents = []
        self.agent_labels = []
        camp_counts = {camp: 0 for camp in SWARM_SIZE.keys()}

        for p in selected:
            camp = p.get("camp")
            if camp == "Foreperson":
                label = "Foreperson"
            else:
                camp_counts[camp] += 1
                label = f"{camp} {camp_counts[camp]}"

            self.agents.append(Agent(p, camp))
            self.agent_labels.append(label)

        if self.verbose:
            print(f"\n[Swarm] Initialized with {len(self.agents)} agents")
            print(f"[Swarm] Parallel execution: {self.use_parallel}")

    def run_single_phase(self, prompt, extension_context=None):
        """
        Run a single deliberation phase.

        Args:
            prompt: The question/task
            extension_context: Optional domain expertise

        Returns:
            str: Formatted debate output
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"SINGLE PHASE DELIBERATION")
            print(f"{'='*60}\n")

        start_time = time.time()

        # Run all agents (excluding foreperson in initial phase)
        responses = self._run_agents_parallel(
            "Opening Statements",
            prompt,
            extension_context=extension_context,
            exclude_foreperson=True
        )

        # Run foreperson to synthesize
        foreperson_response = self._run_foreperson(
            prompt,
            responses,
            extension_context=extension_context
        )

        elapsed = time.time() - start_time

        if self.verbose:
            print(f"\n[Swarm] Completed in {elapsed:.2f} seconds")

        return foreperson_response

    def run_multi_phase(self, prompt, phases=3, extension_context=None):
        """
        Run multi-phase deliberation.

        Args:
            prompt: The question/task
            phases: Number of debate phases
            extension_context: Optional domain expertise

        Returns:
            str: Final consensus report
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"MULTI-PHASE DELIBERATION ({phases} phases)")
            print(f"{'='*60}\n")

        start_time = time.time()
        all_responses = []

        # Phase 1: Opening Statements
        responses = self._run_agents_parallel(
            "Phase 1: Opening Statements",
            prompt,
            extension_context=extension_context,
            exclude_foreperson=True
        )
        all_responses.extend(responses)

        # Phase 2+: Rebuttal/Synthesis rounds
        for phase_num in range(2, phases + 1):
            phase_name = f"Phase {phase_num}: Rebuttal & Synthesis"

            # Build context from previous responses
            context = self._build_context(prompt, all_responses)

            responses = self._run_agents_parallel(
                phase_name,
                context,
                extension_context=extension_context,
                exclude_foreperson=True
            )
            all_responses.extend(responses)

        # Final: Foreperson synthesis
        consensus = self._run_foreperson(
            prompt,
            all_responses,
            extension_context=extension_context
        )

        elapsed = time.time() - start_time

        if self.verbose:
            print(f"\n[Swarm] Multi-phase deliberation completed in {elapsed:.2f} seconds")

        return consensus

    def _run_agents_parallel(self, phase_name, prompt, extension_context=None, exclude_foreperson=True):
        """Run agents in parallel"""
        if self.verbose:
            print(f"\n--- {phase_name} ---\n")

        def agent_task(idx):
            agent = self.agents[idx]
            label = self.agent_labels[idx]

            # Skip foreperson if requested
            if exclude_foreperson and agent.camp == "Foreperson":
                return None

            if self.verbose:
                print(f"[{label}] Thinking...", flush=True)

            response = agent.act(prompt, max_tokens=AGENT_MAX_TOKENS, extension_context=extension_context)

            if self.verbose:
                print(f"[{label}] Complete")

            return (label, response)

        results = []

        if self.use_parallel:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_idx = {
                    executor.submit(agent_task, idx): idx
                    for idx in range(len(self.agents))
                }

                for future in as_completed(future_to_idx):
                    result = future.result()
                    if result is not None:
                        results.append(result)
        else:
            # Sequential execution
            for idx in range(len(self.agents)):
                result = agent_task(idx)
                if result is not None:
                    results.append(result)

        return results

    def _run_foreperson(self, original_prompt, all_responses, extension_context=None):
        """Run foreperson to synthesize consensus"""
        if self.verbose:
            print(f"\n--- Foreperson Synthesis ---\n")

        # Find foreperson agent
        foreperson_idx = None
        for idx, agent in enumerate(self.agents):
            if agent.camp == "Foreperson":
                foreperson_idx = idx
                break

        if foreperson_idx is None:
            return "[Error: No foreperson agent found]"

        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(original_prompt, all_responses)

        # Query foreperson
        foreperson = self.agents[foreperson_idx]
        if self.verbose:
            print(f"[Foreperson] Synthesizing perspectives...", flush=True)

        consensus = foreperson.act(
            synthesis_prompt,
            max_tokens=FOREPERSON_MAX_TOKENS,
            extension_context=extension_context
        )

        if self.verbose:
            print(f"[Foreperson] Complete\n")

        return consensus

    def _build_context(self, original_prompt, responses):
        """Build context from previous responses"""
        context = f"Original question: {original_prompt}\n\nPrevious perspectives:\n\n"

        for label, response in responses[-len(self.agents)+1:]:  # Last round
            context += f"[{label}]: {response}\n\n"

        context += "\nConsidering these perspectives, provide your updated analysis:"

        return context

    def _build_synthesis_prompt(self, original_prompt, all_responses):
        """Build prompt for foreperson synthesis"""
        synthesis = f"""You are synthesizing a multi-agent deliberation on the following question:

{original_prompt}

The deliberation involved {len(all_responses)} agent responses from diverse perspectives:
"""

        # Group by agent for clarity
        agent_summaries = {}
        for label, response in all_responses:
            if label not in agent_summaries:
                agent_summaries[label] = []
            agent_summaries[label].append(response)

        for label, responses in agent_summaries.items():
            synthesis += f"\n[{label}] ({len(responses)} contribution(s)):\n"
            for resp in responses:
                synthesis += f"  - {resp[:200]}{'...' if len(resp) > 200 else ''}\n"

        synthesis += """

As Foreperson, provide a comprehensive consensus report with:
1. Executive Summary
2. Areas of Agreement
3. Areas of Disagreement (if any)
4. Key Insights and Analysis
5. Recommendations

Format your response as a structured report."""

        return synthesis
