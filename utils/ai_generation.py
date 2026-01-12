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


async def check_task_exists(db, title: str, role: str, difficulty: str) -> bool:
    """Check if a similar task already exists in the database.
    
    Args:
        db: Database connection
        title: Task title to check
        role: Engineering role
        difficulty: Task difficulty
    
    Returns:
        bool: True if a similar task exists, False otherwise
    """
    # Check for exact title match first
    existing = await db.tasks.find_one({
        "title": title,
        "role": role,
        "difficulty": difficulty
    })
    
    if existing:
        return True
    
    # Also check for similar titles (case-insensitive partial match)
    # This helps avoid generating near-duplicate tasks
    import re
    title_words = title.lower().split()
    # If more than 3 words, check for significant overlap
    if len(title_words) >= 3:
        # Create a regex pattern for the first 3 significant words
        significant_words = [w for w in title_words if len(w) > 3][:3]
        if significant_words:
            pattern = ".*".join(re.escape(w) for w in significant_words)
            existing = await db.tasks.find_one({
                "title": {"$regex": pattern, "$options": "i"},
                "role": role,
                "difficulty": difficulty
            })
            if existing:
                return True
    
    return False


async def generate_daily_tasks(db=None) -> List[Dict]:
    """Generate daily tasks for all engineering roles and all difficulties.
    
    Generates one task for each role-difficulty combination (12 tasks total).
    Skips generation if a similar task already exists to avoid duplicates.
    
    Args:
        db: Optional database connection for deduplication checks
    
    Returns:
        list: List of generated tasks (one per role per difficulty)
    """
    logger.info("Generating daily tasks for all roles and difficulties")
    
    # we have seven roles 
    roles = ["Backend Engineer", "Frontend Engineer", "Systems Engineer", "Data Engineer", "Fullstack Engineer", "DevOps Engineer", "Security Engineer"]
    difficulties = ["beginner", "intermediate", "advanced"]
    tasks = []
    skipped_count = 0
    
    for role in roles:
        for difficulty in difficulties:
            try:
                # Generate a task
                task = await generate_task_with_ai(role, difficulty)
                
                # Check for duplicates if database is provided
                if db is not None:
                    if await check_task_exists(db, task["title"], role, difficulty):
                        logger.info(f"Skipping duplicate task: '{task['title']}' for {role}/{difficulty}")
                        skipped_count += 1
                        
                        # Try regenerating up to 2 more times to get a unique task
                        retries = 2
                        unique_found = False
                        for _ in range(retries):
                            task = await generate_task_with_ai(role, difficulty)
                            if not await check_task_exists(db, task["title"], role, difficulty):
                                unique_found = True
                                break
                            logger.info(f"Retry also produced duplicate, trying again...")
                        
                        if not unique_found:
                            logger.warning(f"Could not generate unique task for {role}/{difficulty} after {retries} retries")
                            continue
                
                tasks.append(task)
                logger.info(f"Generated task for {role}/{difficulty}: {task['title']}")
                
            except Exception as e:
                logger.error(f"Failed to generate task for {role}/{difficulty}: {str(e)}")
    
    logger.info(f"Generated {len(tasks)} daily tasks, skipped {skipped_count} duplicates")
    return tasks
