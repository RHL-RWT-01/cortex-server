"""AI integration using Google Gemini for feedback and scoring.

This module provides AI-powered features:
- Generate personalized feedback for user responses
- Calculate reasoning scores across multiple dimensions
- Use Gemini 2.0 Flash model for fast, accurate evaluations
"""

from utils.ai_client import gemini_ai
from logger import get_logger

logger = get_logger(__name__)

async def generate_ai_feedback(
    task_scenario: str,
    task_prompts: list,
    user_assumptions: str,
    user_architecture: str,
    user_tradeoffs: str,
    user_failures: str,
    architecture_image: str = None
) -> str:
    """Generate personalized AI feedback for a user's task response.
    
    Uses Gemini AI to provide constructive, mentor-like feedback that:
    - Analyzes the quality of assumptions and reasoning
    - Evaluates awareness of constraints and trade-offs
    - Assesses failure scenario planning
    - If architecture_image is provided, reviews the visual diagram
    - Asks follow-up questions to deepen thinking
    - Guides without providing complete solutions
    
    Args:
        task_scenario: The original task description
        task_prompts: List of guiding questions for the task
        user_assumptions: User's stated assumptions
        user_architecture: User's proposed architecture/solution
        user_tradeoffs: User's trade-off analysis
        user_failures: User's failure scenario analysis
        architecture_image: Base64 encoded PNG of the architecture diagram
    
    Returns:
        str: AI-generated feedback text
    """
    
    prompt = f"""You are an expert engineering mentor reviewing a software engineer's thinking process.
    
    If an architecture diagram image is provided, review it as the primary visual source of truth. 
    Cross-reference it with the user's written architecture description.

**Task Scenario:**
{task_scenario}

**Guiding Questions:**
{chr(10).join(f"- {p}" for p in task_prompts)}

**User's Response:**

**Assumptions:**
{user_assumptions}

**Architecture:**
{user_architecture}

**Trade-offs:**
{user_tradeoffs}

**Failure Scenarios:**
{user_failures}

---

**Your Job:**
Provide constructive feedback focusing on:
1. Quality of assumptions (are they explicit and reasonable?)
2. Awareness of constraints and requirements
3. Depth of trade-off analysis
4. Thoroughness in failure anticipation
5. Clarity and simplicity of thinking

Be encouraging but rigorous. Point out what was done well and what could be improved.
Ask 2-3 follow-up questions to deepen their thinking.

Do NOT provide a complete solution. Guide them to think deeper.
"""
    
    try:
        contents = [prompt]
        if architecture_image:
            # Handle base64 image data
            if "," in architecture_image:
                header, data = architecture_image.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
            else:
                data = architecture_image
                mime_type = "image/png"
            
            contents.append({
                "mime_type": mime_type,
                "data": data
            })

        # Generate feedback using singleton AI client
        response = gemini_ai.generate_content(contents)
        feedback = response.text
        
        logger.info("AI feedback generated successfully")
        return feedback
        
    except Exception as e:
        logger.error(f"Error generating AI feedback: {str(e)}")
        # Return fallback feedback
        return "Your response shows solid thinking. Consider exploring edge cases and scalability implications further."


async def calculate_reasoning_score(
    user_assumptions: str,
    user_architecture: str,
    user_tradeoffs: str,
    user_failures: str,
    architecture_image: str = None
) -> dict:
    """Calculate detailed reasoning scores across 5 dimensions using AI.
    
    Evaluates user responses on:
    1. Clarity - Well-structured, easy to understand thinking
    2. Constraints Awareness - Consideration of requirements and limits
    3. Trade-off Reasoning - Analysis of pros/cons of approaches
    4. Failure Anticipation - Thinking about what could go wrong
    5. Simplicity - Clear, non-over-complicated solutions
    
    Each dimension is scored 0-10, where:
    - 0-3: Needs significant improvement
    - 4-6: Developing skills
    - 7-8: Good understanding
    - 9-10: Excellent mastery
    
    Args:
        user_assumptions: User's stated assumptions
        user_architecture: User's proposed solution
        user_tradeoffs: User's trade-off analysis
        user_failures: User's failure scenario analysis
    
    Returns:
        dict: Score breakdown with keys: clarity, constraints_awareness,
              trade_off_reasoning, failure_anticipation, simplicity
    """
    
    prompt = f"""You are an expert evaluator of engineering thinking. Score the following response on these 5 dimensions (0-10 each):

1. **Clarity** - Are thoughts well-structured and easy to understand?
2. **Constraints Awareness** - Did they consider requirements, limits, and context?
3. **Trade-off Reasoning** - Did they analyze pros/cons of different approaches?
4. **Failure Anticipation** - Did they think about what could go wrong?
5. **Simplicity** - Is the thinking clear and not over-complicated?

**Response to evaluate:**

**Assumptions:**
{user_assumptions}

**Architecture:**
{user_architecture}

**Trade-offs:**
{user_tradeoffs}

**Failure Scenarios:**
{user_failures}

---

Provide ONLY a JSON response in this exact format:
{{
  "clarity": 7.5,
  "constraints_awareness": 8.0,
  "trade_off_reasoning": 6.5,
  "failure_anticipation": 7.0,
  "simplicity": 8.5
}}
"""
    
    try:
        contents = [prompt]
        if architecture_image:
            if "," in architecture_image:
                header, data = architecture_image.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
            else:
                data = architecture_image
                mime_type = "image/png"
            
            contents.append({
                "mime_type": mime_type,
                "data": data
            })

        # Calculate score using singleton AI client
        response = gemini_ai.generate_content(contents)
        import json
        
        result = response.text.strip()
        # Remove markdown code blocks if present
        if result.startswith('```json'):
            result = result.split('```json')[1].split('```')[0].strip()
        elif result.startswith('```'):
            result = result.split('```')[1].split('```')[0].strip()
        
        scores = json.loads(result)
        logger.info("Reasoning score calculated successfully")
        return scores
    except Exception as e:
        logger.error(f"Error calculating scores: {str(e)}")
        # Return default scores if AI fails
        return {
            "clarity": 5.0,
            "constraints_awareness": 5.0,
            "trade_off_reasoning": 5.0,
            "failure_anticipation": 5.0,
            "simplicity": 5.0
        }
