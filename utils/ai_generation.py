"""AI-powered task and drill generation utilities.

Uses Google Gemini to automatically generate engineering tasks and thinking drills.
"""

from typing import List, Dict
from utils.ai_client import gemini_ai
from logger import get_logger
import json

logger = get_logger(__name__)


async def generate_task_with_ai(role: str, difficulty: str) -> Dict:
    """Generate an engineering task using AI.
    
    Args:
        role: Engineering role (Backend Engineer, Frontend Engineer, etc.)
        difficulty: Task difficulty (beginner, intermediate, advanced)
    
    Returns:
        dict: Generated task with title, description, scenario, prompts
    """
    logger.info(f"Generating AI task for role: {role}, difficulty: {difficulty}")
    
    prompt = f"""Generate a realistic SOFTWARE ENGINEERING task for a {role} at {difficulty} difficulty level.

IMPORTANT: This MUST be about SOFTWARE ENGINEERING ONLY. Focus on:
- Web applications, APIs, microservices
- Distributed systems, databases, caching
- Frontend architecture, state management, performance
- Data pipelines, ETL, real-time processing
- Cloud infrastructure, deployment, scalability

DO NOT generate tasks about:
- Hardware, embedded systems, IoT devices
- Medical devices, industrial equipment
- Mobile apps (unless web-based)
- Physical products or electronics

Return a JSON object with this exact structure:
{{
    "title": "Clear, concise task title",
    "description": "Detailed task description (3-4 sentences)",
    "role": "{role}",
    "difficulty": "{difficulty}",
    "estimated_time_minutes": 45,
    "scenario": "Detailed scenario description with background information and constraints (3-4 sentences)",
    "prompts": ["Question 1 to guide thinking", "Question 2 about approach", "Question 3 about tradeoffs", "Question 4 about edge cases"]
}}

Examples of good SOFTWARE ENGINEERING tasks:
- Backend: "Design a rate limiting system for a REST API", "Build a distributed job queue", "Design an authentication service"
- Frontend: "Optimize a React dashboard with 10,000 rows", "Implement infinite scroll with virtual rendering"
- Systems: "Design a distributed caching layer for an e-commerce site", "Build a CDN architecture for global users"
- Data: "Design a real-time analytics pipeline for clickstream data", "Build an ETL system for data warehouse"

Make it practical, relevant to modern web/cloud engineering, and thought-provoking. Focus on SOFTWARE system design and architecture."""

    try:
        response = gemini_ai.generate_content(prompt)
        
        # Extract JSON from response
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text.split('```json')[1].split('```')[0].strip()
        elif text.startswith('```'):
            text = text.split('```')[1].split('```')[0].strip()
        
        task_data = json.loads(text)
        
        logger.info(f"Successfully generated task: {task_data['title']}")
        return task_data
        
    except Exception as e:
        logger.error(f"Error generating task with AI: {str(e)}")
        # Fallback task
        return {
            "title": f"System Design Challenge for {role}",
            "description": f"Design a scalable solution for a {difficulty} level challenge relevant to {role}.",
            "role": role,
            "difficulty": difficulty,
            "estimated_time_minutes": 45,
            "scenario": "You need to design a system that handles high traffic and provides reliable service. Consider scalability, reliability, and maintainability in your design.",
            "prompts": ["What are your key assumptions?", "How would you architect this system?", "What are the main tradeoffs?", "What failure scenarios should you consider?"]
        }


async def generate_drill_with_ai(drill_type: str) -> Dict:
    """Generate a thinking drill using AI.
    
    Args:
        drill_type: Type of drill (spot_assumptions, rank_failures, etc.)
    
    Returns:
        dict: Generated drill with question, options, answer, explanation
    """
    logger.info(f"Generating AI drill of type: {drill_type}")
    
    drill_descriptions = {
        "spot_assumptions": "Identify hidden assumptions in a SOFTWARE ENGINEERING scenario",
        "rank_failures": "Rank potential failure modes in a WEB/CLOUD system by severity/likelihood",
        "predict_scaling": "Predict scaling bottlenecks in a SOFTWARE system",
        "choose_tradeoffs": "Choose the best tradeoff for a SOFTWARE ENGINEERING constraint"
    }
    
    prompt = f"""Generate a thinking drill for SOFTWARE ENGINEERS: {drill_descriptions.get(drill_type, drill_type)}

IMPORTANT: This MUST be about SOFTWARE ENGINEERING ONLY. Focus on:
- Web APIs, microservices, distributed systems
- Database design, caching strategies, message queues
- Frontend performance, state management, rendering
- Cloud infrastructure, deployment, CI/CD
- Scalability, reliability, security

DO NOT use scenarios about:
- Hardware, embedded systems, IoT
- Medical devices, physical products
- Battery life, power consumption
- Industrial equipment or robotics

Return a JSON object with this exact structure:
{{
    "title": "Brief drill title",
    "drill_type": "{drill_type}",
    "question": "Clear SOFTWARE ENGINEERING question or scenario (2-3 sentences)",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Detailed explanation of why this answer is correct and others aren't (3-4 sentences)"
}}

Examples of good SOFTWARE ENGINEERING drill scenarios:
- "Your API is experiencing high latency. Choose the best caching strategy..."
- "A React component is re-rendering too often. Which optimization approach..."
- "Your database queries are slow. Rank these indexing strategies..."
- "You need to handle 1M concurrent WebSocket connections. What tradeoff..."

Make it:
- Realistic and practical for SOFTWARE ENGINEERS
- Educational with clear learning points
- Challenging but fair
- Relevant to modern web/cloud engineering practices"""

    try:
        response = gemini_ai.generate_content(prompt)
        
        # Extract JSON from response
        text = response.text.strip()
        if text.startswith('```json'):
            text = text.split('```json')[1].split('```')[0].strip()
        elif text.startswith('```'):
            text = text.split('```')[1].split('```')[0].strip()
        
        drill_data = json.loads(text)
        
        logger.info(f"Successfully generated drill: {drill_data['title']}")
        return drill_data
        
    except Exception as e:
        logger.error(f"Error generating drill with AI: {str(e)}")
        # Fallback drill
        return {
            "title": "Engineering Thinking Challenge",
            "drill_type": drill_type,
            "question": "Evaluate the given engineering scenario and select the best option.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This option best addresses the constraints and requirements."
        }


async def generate_daily_tasks() -> List[Dict]:
    """Generate daily tasks for all engineering roles.
    
    Returns:
        list: List of generated tasks (one per role at varying difficulties)
    """
    logger.info("Generating daily tasks for all roles")
    
    roles = ["Backend Engineer", "Frontend Engineer", "Systems Engineer", "Data Engineer"]
    difficulties = ["beginner", "intermediate", "advanced"]
    tasks = []
    
    for role in roles:
        # Rotate difficulty for variety
        difficulty = difficulties[len(tasks) % len(difficulties)]
        
        try:
            task = await generate_task_with_ai(role, difficulty)
            tasks.append(task)
        except Exception as e:
            logger.error(f"Failed to generate task for {role}: {str(e)}")
    
    logger.info(f"Generated {len(tasks)} daily tasks")
    return tasks
