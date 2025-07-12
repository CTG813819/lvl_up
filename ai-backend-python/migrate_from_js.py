#!/usr/bin/env python3
"""
Migration script from JavaScript backend to Python backend
"""

import asyncio
import motor.motor_asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import structlog
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logger = structlog.get_logger()


class BackendMigrator:
    """Migrate data from JavaScript backend to Python backend"""
    
    def __init__(self):
        self.js_mongodb_uri = os.getenv("JS_MONGODB_URI", "mongodb://localhost:27017")
        self.py_mongodb_uri = os.getenv("PY_MONGODB_URI", "mongodb://localhost:27017")
        self.js_db_name = os.getenv("JS_DATABASE_NAME", "ai_backend")
        self.py_db_name = os.getenv("PY_DATABASE_NAME", "ai_backend_python")
        
        # Initialize connections
        self.js_client = motor.motor_asyncio.AsyncIOMotorClient(self.js_mongodb_uri)
        self.py_client = motor.motor_asyncio.AsyncIOMotorClient(self.py_mongodb_uri)
        
        self.js_db = self.js_client[self.js_db_name]
        self.py_db = self.py_client[self.py_db_name]
    
    async def migrate_proposals(self) -> int:
        """Migrate proposals from JS to Python backend"""
        try:
            logger.info("Starting proposal migration")
            
            # Get all proposals from JS backend
            js_proposals = await self.js_db.proposals.find({}).to_list(None)
            
            if not js_proposals:
                logger.info("No proposals found in JS backend")
                return 0
            
            logger.info(f"Found {len(js_proposals)} proposals to migrate")
            
            # Transform and insert into Python backend
            migrated_count = 0
            for proposal in js_proposals:
                try:
                    # Transform field names to Python convention
                    py_proposal = self._transform_proposal(proposal)
                    
                    # Insert into Python backend
                    await self.py_db.proposals.insert_one(py_proposal)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating proposal {proposal.get('_id')}", error=str(e))
            
            logger.info(f"Successfully migrated {migrated_count} proposals")
            return migrated_count
            
        except Exception as e:
            logger.error("Error in proposal migration", error=str(e))
            return 0
    
    async def migrate_learning_data(self) -> int:
        """Migrate learning data from JS to Python backend"""
        try:
            logger.info("Starting learning data migration")
            
            # Get learning data from JS backend
            js_learning = await self.js_db.learning.find({}).to_list(None)
            
            if not js_learning:
                logger.info("No learning data found in JS backend")
                return 0
            
            logger.info(f"Found {len(js_learning)} learning entries to migrate")
            
            # Transform and insert into Python backend
            migrated_count = 0
            for learning_entry in js_learning:
                try:
                    # Transform field names
                    py_learning = self._transform_learning_entry(learning_entry)
                    
                    # Insert into Python backend
                    await self.py_db.learning.insert_one(py_learning)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating learning entry {learning_entry.get('_id')}", error=str(e))
            
            logger.info(f"Successfully migrated {migrated_count} learning entries")
            return migrated_count
            
        except Exception as e:
            logger.error("Error in learning data migration", error=str(e))
            return 0
    
    async def migrate_experiments(self) -> int:
        """Migrate experiments from JS to Python backend"""
        try:
            logger.info("Starting experiments migration")
            
            # Get experiments from JS backend
            js_experiments = await self.js_db.experiments.find({}).to_list(None)
            
            if not js_experiments:
                logger.info("No experiments found in JS backend")
                return 0
            
            logger.info(f"Found {len(js_experiments)} experiments to migrate")
            
            # Transform and insert into Python backend
            migrated_count = 0
            for experiment in js_experiments:
                try:
                    # Transform field names
                    py_experiment = self._transform_experiment(experiment)
                    
                    # Insert into Python backend
                    await self.py_db.experiments.insert_one(py_experiment)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating experiment {experiment.get('_id')}", error=str(e))
            
            logger.info(f"Successfully migrated {migrated_count} experiments")
            return migrated_count
            
        except Exception as e:
            logger.error("Error in experiments migration", error=str(e))
            return 0
    
    def _transform_proposal(self, js_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Transform proposal from JS format to Python format"""
        py_proposal = {
            "_id": js_proposal.get("_id"),
            "ai_type": js_proposal.get("aiType"),
            "file_path": js_proposal.get("filePath"),
            "code_before": js_proposal.get("codeBefore"),
            "code_after": js_proposal.get("codeAfter"),
            "status": js_proposal.get("status", "pending"),
            "result": js_proposal.get("result"),
            "user_feedback": js_proposal.get("userFeedback"),
            "test_status": js_proposal.get("testStatus", "not-run"),
            "test_output": js_proposal.get("testOutput"),
            
            # Advanced deduplication fields
            "code_hash": js_proposal.get("codeHash"),
            "semantic_hash": js_proposal.get("semanticHash"),
            "diff_score": js_proposal.get("diffScore"),
            "duplicate_of": js_proposal.get("duplicateOf"),
            
            # AI Learning fields
            "ai_reasoning": js_proposal.get("aiReasoning"),
            "learning_context": js_proposal.get("learningContext"),
            "mistake_pattern": js_proposal.get("mistakePattern"),
            "improvement_type": js_proposal.get("improvementType"),
            "confidence": js_proposal.get("confidence", 0.5),
            
            # Feedback and learning
            "user_feedback_reason": js_proposal.get("userFeedbackReason"),
            "ai_learning_applied": js_proposal.get("aiLearningApplied", False),
            "previous_mistakes_avoided": js_proposal.get("previousMistakesAvoided", []),
            
            # Timestamps
            "created_at": js_proposal.get("createdAt", datetime.utcnow()),
            "updated_at": js_proposal.get("updatedAt")
        }
        
        return py_proposal
    
    def _transform_learning_entry(self, js_learning: Dict[str, Any]) -> Dict[str, Any]:
        """Transform learning entry from JS format to Python format"""
        py_learning = {
            "_id": js_learning.get("_id"),
            "proposal_id": js_learning.get("proposalId"),
            "ai_type": js_learning.get("aiType"),
            "status": js_learning.get("status"),
            "feedback_reason": js_learning.get("feedbackReason"),
            "ml_analysis": js_learning.get("mlAnalysis", {}),
            "created_at": js_learning.get("createdAt", datetime.utcnow())
        }
        
        return py_learning
    
    def _transform_experiment(self, js_experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Transform experiment from JS format to Python format"""
        py_experiment = {
            "_id": js_experiment.get("_id"),
            "ai_type": js_experiment.get("aiType"),
            "status": js_experiment.get("status"),
            "result": js_experiment.get("result"),
            "created_at": js_experiment.get("createdAt", datetime.utcnow())
        }
        
        return py_experiment
    
    async def create_indexes(self):
        """Create indexes in Python backend"""
        try:
            logger.info("Creating indexes in Python backend")
            
            # Proposals indexes
            await self.py_db.proposals.create_index([("ai_type", 1), ("status", 1)])
            await self.py_db.proposals.create_index([("file_path", 1), ("ai_type", 1)])
            await self.py_db.proposals.create_index([("created_at", -1)])
            await self.py_db.proposals.create_index([("code_hash", 1), ("ai_type", 1)])
            await self.py_db.proposals.create_index([("semantic_hash", 1), ("ai_type", 1)])
            
            # Learning indexes
            await self.py_db.learning.create_index([("ai_type", 1), ("created_at", -1)])
            await self.py_db.learning.create_index([("proposal_id", 1)])
            
            # Experiments indexes
            await self.py_db.experiments.create_index([("ai_type", 1), ("status", 1)])
            await self.py_db.experiments.create_index([("created_at", -1)])
            
            logger.info("Indexes created successfully")
            
        except Exception as e:
            logger.error("Error creating indexes", error=str(e))
    
    async def run_migration(self):
        """Run complete migration"""
        try:
            logger.info("Starting migration from JavaScript to Python backend")
            
            # Test connections
            await self.js_client.admin.command('ping')
            await self.py_client.admin.command('ping')
            
            logger.info("Database connections successful")
            
            # Run migrations
            proposals_count = await self.migrate_proposals()
            learning_count = await self.migrate_learning_data()
            experiments_count = await self.migrate_experiments()
            
            # Create indexes
            await self.create_indexes()
            
            # Summary
            logger.info("Migration completed successfully", 
                       proposals_migrated=proposals_count,
                       learning_migrated=learning_count,
                       experiments_migrated=experiments_count)
            
            return {
                "proposals_migrated": proposals_count,
                "learning_migrated": learning_count,
                "experiments_migrated": experiments_count,
                "total_migrated": proposals_count + learning_count + experiments_count
            }
            
        except Exception as e:
            logger.error("Migration failed", error=str(e))
            raise
        finally:
            # Close connections
            self.js_client.close()
            self.py_client.close()


async def main():
    """Main migration function"""
    migrator = BackendMigrator()
    result = await migrator.run_migration()
    
    print(f"\nMigration Summary:")
    print(f"Proposals migrated: {result['proposals_migrated']}")
    print(f"Learning entries migrated: {result['learning_migrated']}")
    print(f"Experiments migrated: {result['experiments_migrated']}")
    print(f"Total records migrated: {result['total_migrated']}")


if __name__ == "__main__":
    asyncio.run(main()) 