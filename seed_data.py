"""
Seed script to populate database with initial tasks and thinking drills
Run this after setting up your .env file
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import settings
import asyncio

# Connect to MongoDB
client = AsyncIOMotorClient(settings.mongodb_url)
db = client[settings.database_name]


async def seed_tasks():
    """Seed initial tasks for all roles"""
    
    tasks = [
        # Backend Engineer Tasks
        {
            "title": "Design a Rate Limiter",
            "description": "Design a scalable rate limiting system for an API",
            "role": "Backend Engineer",
            "difficulty": "intermediate",
            "estimated_time_minutes": 30,
            "scenario": """You're building a public API that needs to limit requests per user. 
            
Requirements:
- 100 requests per minute per user
- 1000 requests per hour per user
- Should be distributed across multiple servers
- Must handle 10,000 concurrent users
- Minimal latency impact (<5ms)

Your API currently handles 50,000 requests/second across 20 servers.""",
            "prompts": [
                "What storage mechanism will you use for tracking limits?",
                "How will you handle distributed rate limiting across servers?",
                "What happens when a user exceeds their limit?",
                "How will you prevent race conditions?",
                "What are the failure modes and how will you handle them?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Debug Production Incident",
            "description": "Investigate and resolve a sudden spike in API latency",
            "role": "Backend Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 45,
            "scenario": """Your API latency suddenly spiked from 50ms to 2000ms for 30% of requests.
            
Observations:
- Started 10 minutes ago
- Database queries look normal
- CPU and memory usage are fine
- Error rate hasn't increased
- Mostly affecting POST /orders endpoint
- GET requests are unaffected

What's your debugging approach?""",
            "prompts": [
                "What would you check first and why?",
                "What metrics and logs would you examine?",
                "What are your top 3 hypotheses?",
                "How would you verify each hypothesis?",
                "What immediate mitigation steps would you take?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Design Notification System",
            "description": "Design a system to send millions of push notifications",
            "role": "Backend Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 40,
            "scenario": """Build a notification system that sends:
- Email notifications
- Push notifications (mobile)
- SMS (for critical alerts)

Requirements:
- 5 million users
- Peak: 100,000 notifications/minute
- Delivery within 30 seconds
- Handle retries for failures
- Track delivery status
- Users can set preferences""",
            "prompts": [
                "What's your high-level architecture?",
                "How will you queue and process notifications?",
                "How will you handle different notification types?",
                "How will you retry failed deliveries?",
                "What happens if a third-party service (e.g., email provider) is down?"
            ],
            "created_at": datetime.utcnow()
        },
        
        # Frontend Engineer Tasks
        {
            "title": "Optimize React Performance",
            "description": "Improve performance of a slow dashboard component",
            "role": "Frontend Engineer",
            "difficulty": "intermediate",
            "estimated_time_minutes": 30,
            "scenario": """You have a dashboard that renders a table with 10,000 rows. 
            
Problems:
- Takes 3 seconds to render initially
- Scrolling is janky (low FPS)
- Filtering causes entire page to freeze for 2 seconds
- Each row has 10 columns with formatted data
- Users can sort, filter, and export data

Current implementation uses simple map() over all rows.""",
            "prompts": [
                "What performance issues do you identify?",
                "What optimization techniques would you apply?",
                "How would you implement virtualization?",
                "How would you handle filtering without blocking the UI?",
                "What trade-offs exist between different solutions?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Design Offline-First Mobile App",
            "description": "Design offline functionality for a note-taking app",
            "role": "Frontend Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 35,
            "scenario": """Build an offline-first note-taking app where:
- Users can create/edit notes without internet
- Changes sync when connection returns
- Multiple devices can edit the same note
- Conflicts must be resolved
- Should feel instant (no loading spinners)

Average user has 500 notes, each 1-5KB.""",
            "prompts": [
                "What local storage strategy will you use?",
                "How will you sync data when online?",
                "How will you handle conflicts?",
                "What's your data model for tracking changes?",
                "How will you handle the initial load and subsequent updates?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Build Real-Time Collaboration",
            "description": "Add real-time editing to a document editor",
            "role": "Frontend Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 40,
            "scenario": """Add Google Docs-style collaboration to your text editor:
- Multiple users can edit simultaneously
- See other users' cursors
- Changes appear instantly
- Handle conflicts
- Show who's viewing/editing
- Works with 100+ concurrent users per document""",
            "prompts": [
                "What protocol/technology will you use for real-time updates?",
                "How will you handle concurrent edits?",
                "What's your conflict resolution strategy?",
                "How will you optimize for low latency?",
                "What happens when a user disconnects?"
            ],
            "created_at": datetime.utcnow()
        },
        
        # Systems Engineer Tasks
        {
            "title": "Design Cache Strategy",
            "description": "Design a multi-layer caching strategy",
            "role": "Systems Engineer",
            "difficulty": "intermediate",
            "estimated_time_minutes": 30,
            "scenario": """Your e-commerce site needs caching:
- 1 million products
- Product data rarely changes
- User sessions need fast access
- High read-to-write ratio (1000:1)
- Global users (multiple regions)
- Current: Database can handle 5000 QPS, need 50,000 QPS""",
            "prompts": [
                "What layers of caching will you implement?",
                "What caching technology will you use for each layer?",
                "What's your cache invalidation strategy?",
                "How will you handle cache stampede?",
                "What metrics will you monitor?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Design Database Sharding",
            "description": "Shard a growing PostgreSQL database",
            "role": "Systems Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 45,
            "scenario": """Your single PostgreSQL database is at 2TB and growing:
- User table: 50M rows
- Orders table: 500M rows
- Products table: 5M rows
- Write queries are getting slow
- Some joins across tables are needed
- Zero-downtime migration required""",
            "prompts": [
                "What sharding strategy will you use?",
                "What's your shard key and why?",
                "How will you handle cross-shard queries?",
                "What's your migration plan?",
                "How will you rebalance shards as data grows?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Handle Traffic Spike",
            "description": "Prepare infrastructure for 10x traffic surge",
            "role": "Systems Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 35,
            "scenario": """Your app will be featured on national TV in 3 days:
- Current: 10,000 requests/second
- Expected: 100,000 requests/second spike for 2 hours
- Must maintain <200ms response time
- Current setup: 10 app servers, 2 DB replicas, 1 Redis instance
- Budget: $5000 for scaling""",
            "prompts": [
                "What components are likely bottlenecks?",
                "How will you scale each layer?",
                "What auto-scaling policies will you set?",
                "What's your fallback plan if things fail?",
                "How will you test this before the event?"
            ],
            "created_at": datetime.utcnow()
        },
        
        # Data Engineer Tasks
        {
            "title": "Design Data Pipeline",
            "description": "Build a real-time analytics pipeline",
            "role": "Data Engineer",
            "difficulty": "intermediate",
            "estimated_time_minutes": 35,
            "scenario": """Build a pipeline for real-time user behavior analytics:
- Ingest: 50,000 events/second
- Process: Aggregate by user, session, page
- Store: Query latency < 100ms
- Retention: Raw data for 30 days, aggregates for 1 year
- Use cases: Dashboards, user segmentation, A/B testing""",
            "prompts": [
                "What technologies will you use for ingestion?",
                "How will you process and transform the data?",
                "What storage solutions will you use?",
                "How will you handle late-arriving data?",
                "What's your strategy for schema evolution?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Optimize Slow Query",
            "description": "Fix a dashboard query taking 30 seconds",
            "role": "Data Engineer",
            "difficulty": "intermediate",
            "estimated_time_minutes": 30,
            "scenario": """A dashboard query takes 30 seconds to run:
```sql
SELECT 
    date,
    COUNT(DISTINCT user_id) as users,
    SUM(revenue) as revenue,
    AVG(session_duration) as avg_duration
FROM events
WHERE date >= '2024-01-01'
    AND event_type IN ('purchase', 'view')
GROUP BY date, country, device_type
ORDER BY date DESC
```
Table has 10 billion rows, growing by 50M/day.""",
            "prompts": [
                "What's causing the slow performance?",
                "What indexes would help?",
                "Would partitioning help? How would you partition?",
                "Should you pre-aggregate some data?",
                "What trade-offs exist in your solution?"
            ],
            "created_at": datetime.utcnow()
        },
        {
            "title": "Build Data Quality System",
            "description": "Ensure data quality in your pipeline",
            "role": "Data Engineer",
            "difficulty": "advanced",
            "estimated_time_minutes": 35,
            "scenario": """Your data pipeline has quality issues:
- Duplicate records appearing
- Missing required fields
- Invalid data formats
- Schema mismatches between sources
- Downstream teams losing trust in data

Need to implement data quality checks.""",
            "prompts": [
                "What quality checks will you implement?",
                "Where in the pipeline will you add validation?",
                "How will you handle data that fails validation?",
                "How will you monitor and alert on quality issues?",
                "What's your strategy for fixing historical bad data?"
            ],
            "created_at": datetime.utcnow()
        }
    ]
    
    # Clear existing tasks
    await db.tasks.delete_many({})
    
    # Insert new tasks
    result = await db.tasks.insert_many(tasks)
    print(f"✅ Inserted {len(result.inserted_ids)} tasks")


async def seed_drills():
    """Seed thinking drills"""
    
    drills = [
        # Spot Assumptions
        {
            "title": "API Design Assumptions",
            "drill_type": "spot_assumptions",
            "question": """A developer says: "We'll use REST API because it's the standard."
            
What assumption is being made?""",
            "options": [
                "REST is always the best choice",
                "The use case fits REST well",
                "The team knows REST",
                "All of the above"
            ],
            "correct_answer": "All of the above",
            "explanation": "The developer assumes REST is suitable without evaluating if GraphQL, gRPC, or WebSockets might be better for the specific use case. They also assume team familiarity and that 'standard' means 'best'.",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Database Choice",
            "drill_type": "spot_assumptions",
            "question": """Team decides: "Let's use MongoDB because we need to scale."
            
What's the flawed assumption?""",
            "options": [
                "NoSQL automatically scales better",
                "Relational databases can't scale",
                "Scaling is only about database choice",
                "All of the above"
            ],
            "correct_answer": "All of the above",
            "explanation": "This assumes NoSQL is always more scalable, ignores that relational databases can scale horizontally, and oversimplifies scaling to just database choice when architecture matters more.",
            "created_at": datetime.utcnow()
        },
        
        # Rank Failures
        {
            "title": "Payment System Failures",
            "drill_type": "rank_failures",
            "question": """Rank these failure modes for a payment system from MOST to LEAST critical:
            
A) User charged twice
B) Slow checkout (5 seconds)
C) Payment successful but order not created
D) Payment gateway timeout""",
            "options": [
                "C, A, D, B",
                "A, C, D, B",
                "D, C, A, B",
                "B, D, A, C"
            ],
            "correct_answer": "C, A, D, B",
            "explanation": "C is worst (money taken, no order = angry customers + refunds). A is bad (financial loss + trust issues). D is recoverable with retry. B is annoying but not critical.",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Social Media Feed Failures",
            "drill_type": "rank_failures",
            "question": """Rank these issues for a social media feed from MOST to LEAST critical:
            
A) Feed loads slowly (3 seconds)
B) Same post shown multiple times
C) User's own posts not visible
D) Can't refresh feed (temporary)""",
            "options": [
                "C, B, A, D",
                "D, C, B, A",
                "C, D, A, B",
                "B, C, D, A"
            ],
            "correct_answer": "C, D, A, B",
            "explanation": "C breaks core value (seeing your content). D prevents refreshing but cached content works. A annoys but works. B is a UX issue but feed functions.",
            "created_at": datetime.utcnow()
        },
        
        # Predict Scaling
        {
            "title": "Session Storage Scaling",
            "drill_type": "predict_scaling",
            "question": """You store user sessions in memory on each server. Current: 10,000 users, 5 servers. What breaks first when you hit 1M users?""",
            "options": [
                "Memory on each server",
                "Session inconsistency across servers",
                "CPU from session lookups",
                "Network bandwidth"
            ],
            "correct_answer": "Session inconsistency across servers",
            "explanation": "With in-memory sessions, a user can be routed to different servers, losing their session. This breaks before memory limits. You need sticky sessions or centralized session storage (Redis).",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Notification Queue",
            "drill_type": "predict_scaling",
            "question": """You use a single-threaded worker to send email notifications. Currently 1000 emails/hour. What happens at 100,000 emails/hour?""",
            "options": [
                "Memory overflow from queue",
                "Emails delayed by hours",
                "Database connection exhaustion",
                "Email provider blocks you"
            ],
            "correct_answer": "Emails delayed by hours",
            "explanation": "A single worker can only process so fast. At 100x load, the queue grows faster than it's processed, causing hour-long delays. You need multiple workers or a better queuing system.",
            "created_at": datetime.utcnow()
        },
        
        # Trade-offs
        {
            "title": "Cache Trade-off",
            "drill_type": "choose_tradeoffs",
            "question": """For caching product prices, what's the best trade-off?
            
A) Cache for 1 hour (fast, might show stale prices)
B) Cache for 1 minute (slower, more accurate)
C) No cache (always accurate, slow)
D) Cache forever, invalidate on update (complex)""",
            "options": [
                "A - Speed over accuracy",
                "B - Balanced approach",
                "C - Accuracy over speed",
                "D - Best of both worlds"
            ],
            "correct_answer": "B - Balanced approach",
            "explanation": "1-minute cache is best for most e-commerce. Prices don't change often, so staleness is minimal. 1 hour risks showing wrong prices during sales. No cache overloads DB. Option D adds complexity that's usually not worth it.",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Consistency vs Availability",
            "drill_type": "choose_tradeoffs",
            "question": """For a social media 'like' counter, which trade-off makes sense?""",
            "options": [
                "Strong consistency - Exact count always",
                "Eventual consistency - Approximate count, high availability",
                "Weak consistency - Cached count, may be very stale",
                "No counting - Too complex"
            ],
            "correct_answer": "Eventual consistency - Approximate count, high availability",
            "explanation": "Like counts don't need to be exact. Users won't notice if 1,234 likes shows as 1,230 temporarily. Eventual consistency allows high availability and scale. Strong consistency would be too expensive for this feature.",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Clear existing drills
    await db.drills.delete_many({})
    
    # Insert new drills
    result = await db.drills.insert_many(drills)
    print(f"✅ Inserted {len(result.inserted_ids)} thinking drills")


async def main():
    print("🌱 Seeding database...")
    await seed_tasks()
    await seed_drills()
    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
    client.close()
