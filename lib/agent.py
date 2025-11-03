"""
ThinkTank Demo - Agent
Individual agent with persona and memory
"""

from lib.llm_provider import query_llm


class Agent:
    """
    An agent in the ThinkTank swarm with a specific persona and perspective.
    """

    def __init__(self, persona, camp):
        """
        Initialize an agent with a persona.

        Args:
            persona: Dict containing agent's background, expertise, etc.
            camp: Agent's perspective (Believer, Skeptic, Neutral, Foreperson)
        """
        self.persona = persona
        self.camp = camp
        self.memory = []  # Store previous interactions

    def act(self, prompt, max_tokens=256, extension_context=None):
        """
        Generate a response to the given prompt based on persona.

        Args:
            prompt: The question or task
            max_tokens: Maximum response length
            extension_context: Optional domain expertise from extensions

        Returns:
            str: Agent's response
        """
        # Build system prompt from persona
        system_prompt = self._build_system_prompt(extension_context)

        # Combine system prompt with user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}"

        # Query LLM
        response = query_llm(full_prompt, max_tokens=max_tokens)

        # Store in memory
        self.memory.append({
            "prompt": prompt,
            "response": response
        })

        return response

    def _build_system_prompt(self, extension_context=None):
        """Build system prompt from persona attributes"""
        parts = [
            "You are an expert analyst with the following background:",
            f"Name: {self.persona.get('name', 'Anonymous')}",
            f"Professional background: {self.persona.get('backstory', 'General expertise')}",
            f"Areas of expertise: {self.persona.get('expertise', 'Various fields')}",
            f"Education: {self.persona.get('education', 'Advanced degree')}",
            f"Age: {self.persona.get('age', 'N/A')}, "
            f"Race: {self.persona.get('race', 'N/A')}, "
            f"Gender: {self.persona.get('gender', 'N/A')}",
            f"Perspective: {self.camp}"
        ]

        # Add extension context if provided
        if extension_context:
            parts.append(f"\n{extension_context}")

        # Add camp-specific instructions
        if self.camp == "Believer":
            parts.append(
                "\nAs a Believer, you are optimistic and solution-focused. "
                "Look for opportunities, benefits, and viable approaches. "
                "While staying realistic, emphasize constructive possibilities."
            )
        elif self.camp == "Skeptic":
            parts.append(
                "\nAs a Skeptic, you are critical and risk-focused. "
                "Question assumptions, identify potential problems, and challenge weak points. "
                "While being constructive, emphasize risks and limitations."
            )
        elif self.camp == "Neutral":
            parts.append(
                "\nAs a Neutral observer, you are balanced and objective. "
                "Consider both benefits and risks equally. "
                "Provide well-reasoned analysis without strong bias in either direction."
            )
        elif self.camp == "Foreperson":
            parts.append(
                "\nAs the Foreperson, you synthesize multiple perspectives into a coherent consensus. "
                "Identify areas of agreement and disagreement. "
                "Provide balanced recommendations that acknowledge different viewpoints."
            )

        parts.append("\nProvide direct, professional responses based on your background and perspective.")

        return "\n".join(parts)
