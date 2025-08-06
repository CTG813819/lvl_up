"""
Chaos Language Service
Dynamic chaos language documentation that grows with the system
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

from .enhanced_project_horus_service import enhanced_project_horus_service
from .project_berserk_enhanced_service import project_berserk_enhanced_service
from .ai_adversarial_integration_service import ai_adversarial_integration_service

logger = structlog.get_logger()


class ChaosLanguageService:
    """Dynamic chaos language documentation that evolves with system learning"""
    
    def __init__(self):
        # Language structure
        self.language_core = {
            "version": "2.0.0",
            "base_constructs": {},
            "ai_derived_constructs": {},
            "weapon_specific_constructs": {},
            "evolution_history": []
        }
        
        # Documentation chapters
        self.documentation_chapters = []
        self.chapter_templates = {}
        
        # Growth tracking
        self.growth_metrics = {
            "total_constructs": 0,
            "constructs_per_ai": {},
            "constructs_per_weapon_category": {},
            "evolution_cycles": 0,
            "last_growth_event": None
        }
        
        # Auto-generation settings
        self.auto_generation_enabled = True
        self.generation_threshold = 10  # New constructs trigger chapter creation
        
    async def initialize(self):
        """Initialize chaos language service"""
        try:
            # Initialize base language constructs
            await self._initialize_base_constructs()
            
            # Load chapter templates
            await self._initialize_chapter_templates()
            
            # Start background growth monitoring
            asyncio.create_task(self._background_language_growth_monitor())
            
            logger.info("Chaos Language Service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Chaos Language Service: {e}")
            raise
    
    async def _initialize_base_constructs(self):
        """Initialize base chaos language constructs"""
        self.language_core["base_constructs"] = {
            "CHAOS.CORE.INIT": {
                "description": "Initialize chaos core systems",
                "syntax": "CHAOS.CORE.INIT(target_system, complexity_level)",
                "parameters": ["target_system", "complexity_level"],
                "created": datetime.utcnow().isoformat(),
                "origin": "base_language"
            },
            "CHAOS.STEALTH.ENGAGE": {
                "description": "Engage stealth protocols",
                "syntax": "CHAOS.STEALTH.ENGAGE(stealth_level, duration)",
                "parameters": ["stealth_level", "duration"],
                "created": datetime.utcnow().isoformat(),
                "origin": "base_language"
            },
            "CHAOS.PERSIST.DEPLOY": {
                "description": "Deploy persistence mechanisms",
                "syntax": "CHAOS.PERSIST.DEPLOY(persistence_type, backup_count)",
                "parameters": ["persistence_type", "backup_count"],
                "created": datetime.utcnow().isoformat(),
                "origin": "base_language"
            },
            "CHAOS.EXTRACT.DATA": {
                "description": "Extract data from target systems",
                "syntax": "CHAOS.EXTRACT.DATA(target_path, extraction_method)",
                "parameters": ["target_path", "extraction_method"],
                "created": datetime.utcnow().isoformat(),
                "origin": "base_language"
            },
            "CHAOS.EVOLVE.SELF": {
                "description": "Trigger self-evolution protocols",
                "syntax": "CHAOS.EVOLVE.SELF(evolution_direction, complexity_increase)",
                "parameters": ["evolution_direction", "complexity_increase"],
                "created": datetime.utcnow().isoformat(),
                "origin": "base_language"
            }
        }
    
    async def _initialize_chapter_templates(self):
        """Initialize chapter templates for documentation"""
        self.chapter_templates = {
            "ai_learning_integration": {
                "title_template": "AI Learning Integration - {ai_type} Contributions",
                "sections": [
                    "Introduction",
                    "AI-Specific Constructs",
                    "Learning Patterns",
                    "Integration Examples",
                    "Performance Metrics"
                ]
            },
            "weapon_synthesis": {
                "title_template": "Weapon Synthesis - {weapon_category} Evolution",
                "sections": [
                    "Weapon Category Overview",
                    "Synthesis Constructs",
                    "Deployment Patterns",
                    "Evolution Algorithms",
                    "Performance Analysis"
                ]
            },
            "adversarial_evolution": {
                "title_template": "Adversarial Evolution - {domain} Domain",
                "sections": [
                    "Domain Analysis",
                    "Adversarial Constructs",
                    "Combat Patterns",
                    "Adaptation Strategies",
                    "Success Metrics"
                ]
            }
        }
    
    async def collect_new_constructs_from_system(self) -> Dict[str, Any]:
        """Collect new constructs from system components"""
        collection_results = {
            "horus_constructs": 0,
            "berserk_constructs": 0,
            "ai_adversarial_constructs": 0,
            "new_constructs": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Collect from Project Horus
            horus_constructs = await self._collect_horus_constructs()
            collection_results["new_constructs"].update(horus_constructs)
            collection_results["horus_constructs"] = len(horus_constructs)
            
            # Collect from Project Berserk
            berserk_constructs = await self._collect_berserk_constructs()
            collection_results["new_constructs"].update(berserk_constructs)
            collection_results["berserk_constructs"] = len(berserk_constructs)
            
            # Collect from AI adversarial experiences
            adversarial_constructs = await self._collect_adversarial_constructs()
            collection_results["new_constructs"].update(adversarial_constructs)
            collection_results["ai_adversarial_constructs"] = len(adversarial_constructs)
            
            # Update language core with new constructs
            await self._integrate_new_constructs(collection_results["new_constructs"])
            
            # Check if new chapter creation is needed
            if len(collection_results["new_constructs"]) >= self.generation_threshold:
                await self._generate_new_chapter_from_constructs(collection_results["new_constructs"])
            
            return collection_results
            
        except Exception as e:
            logger.error(f"Error collecting new constructs: {e}")
            return collection_results
    
    async def _collect_horus_constructs(self) -> Dict[str, Any]:
        """Collect new constructs from Project Horus"""
        constructs = {}
        
        try:
            # Get chaos language evolution from Horus
            if hasattr(enhanced_project_horus_service, 'chaos_language_evolution'):
                horus_evolution = enhanced_project_horus_service.chaos_language_evolution
                
                for construct_name, construct_data in horus_evolution.items():
                    if construct_name not in self.language_core["ai_derived_constructs"]:
                        constructs[construct_name] = {
                            "description": f"AI-derived construct from {construct_data.get('origin_ai', 'unknown')}",
                            "syntax": f"{construct_name}(target, parameters)",
                            "domain": construct_data.get("domain", "unknown"),
                            "origin_ai": construct_data.get("origin_ai", "unknown"),
                            "lessons": construct_data.get("lessons", []),
                            "created": construct_data.get("created", datetime.utcnow().isoformat()),
                            "origin": "project_horus",
                            "usage_count": construct_data.get("usage_count", 0)
                        }
            
            # Get weapon-specific constructs
            if hasattr(enhanced_project_horus_service, 'weapon_synthesis_lab'):
                weapons = enhanced_project_horus_service.weapon_synthesis_lab
                
                for weapon_id, weapon in weapons.items():
                    if isinstance(weapon, dict) and weapon.get("synthetic", False):
                        category = weapon.get("category", "unknown")
                        construct_name = f"CHAOS.WEAPON.{category.upper()}.{weapon_id.split('_')[-1]}"
                        
                        if construct_name not in self.language_core["weapon_specific_constructs"]:
                            constructs[construct_name] = {
                                "description": f"Weapon-specific construct for {category}",
                                "syntax": f"{construct_name}(deployment_option, target_system)",
                                "weapon_category": category,
                                "weapon_id": weapon_id,
                                "complexity": weapon.get("stats", {}).get("complexity", 1.0),
                                "created": weapon.get("created", datetime.utcnow().isoformat()),
                                "origin": "horus_weapon_synthesis"
                            }
            
        except Exception as e:
            logger.error(f"Error collecting Horus constructs: {e}")
        
        return constructs
    
    async def _collect_berserk_constructs(self) -> Dict[str, Any]:
        """Collect new constructs from Project Berserk"""
        constructs = {}
        
        try:
            # Get Berserk weapons and their constructs
            if hasattr(project_berserk_enhanced_service, 'weapon_arsenal'):
                arsenal = project_berserk_enhanced_service.weapon_arsenal
                
                for weapon_id, weapon in arsenal.items():
                    if isinstance(weapon, dict):
                        category = weapon.get("category", "unknown")
                        construct_name = f"CHAOS.BERSERK.{category.upper()}.{weapon_id.split('_')[-1]}"
                        
                        if construct_name not in self.language_core["weapon_specific_constructs"]:
                            constructs[construct_name] = {
                                "description": f"Berserk enhanced construct for {category}",
                                "syntax": f"{construct_name}(deployment_mode, growth_parameters)",
                                "weapon_category": category,
                                "weapon_id": weapon_id,
                                "berserk_enhanced": True,
                                "complexity": weapon.get("stats", {}).get("complexity", 1.0),
                                "special_capabilities": weapon.get("berserk_capabilities", {}),
                                "created": weapon.get("created", datetime.utcnow().isoformat()),
                                "origin": "project_berserk"
                            }
            
            # Get learning-derived constructs from Berserk
            if hasattr(project_berserk_enhanced_service, 'berserk_learning_data'):
                learning_data = project_berserk_enhanced_service.berserk_learning_data
                
                for ai_type, ai_data in learning_data.items():
                    combat_patterns = ai_data.get("combat_patterns", [])
                    
                    for pattern in combat_patterns:
                        construct_name = f"CHAOS.COMBAT.{ai_type.upper()}.{pattern.upper()}"
                        
                        if construct_name not in self.language_core["ai_derived_constructs"]:
                            constructs[construct_name] = {
                                "description": f"Combat pattern construct from {ai_type}",
                                "syntax": f"{construct_name}(intensity, duration)",
                                "combat_pattern": pattern,
                                "origin_ai": ai_type,
                                "created": datetime.utcnow().isoformat(),
                                "origin": "berserk_combat_analysis"
                            }
            
        except Exception as e:
            logger.error(f"Error collecting Berserk constructs: {e}")
        
        return constructs
    
    async def _collect_adversarial_constructs(self) -> Dict[str, Any]:
        """Collect new constructs from adversarial experiences"""
        constructs = {}
        
        try:
            # Get shared adversarial knowledge
            if hasattr(ai_adversarial_integration_service, 'shared_adversarial_knowledge'):
                shared_knowledge = ai_adversarial_integration_service.shared_adversarial_knowledge
                
                for domain, knowledge_entries in shared_knowledge.items():
                    for entry in knowledge_entries[-5:]:  # Last 5 entries per domain
                        if entry.get("success", False):  # Only successful experiences
                            construct_name = f"CHAOS.ADVERSARIAL.{domain.upper()}.{entry.get('source_ai', 'UNKNOWN').upper()}"
                            
                            if construct_name not in self.language_core["ai_derived_constructs"]:
                                constructs[construct_name] = {
                                    "description": f"Adversarial construct from {entry.get('source_ai')} in {domain}",
                                    "syntax": f"{construct_name}(scenario_complexity, adaptation_level)",
                                    "domain": domain,
                                    "source_ai": entry.get("source_ai", "unknown"),
                                    "performance_score": entry.get("performance_score", 0.0),
                                    "lessons": entry.get("lessons", []),
                                    "created": entry.get("timestamp", datetime.utcnow().isoformat()),
                                    "origin": "adversarial_experience"
                                }
            
            # Get AI progress constructs
            if hasattr(ai_adversarial_integration_service, 'ai_adversarial_progress'):
                progress = ai_adversarial_integration_service.ai_adversarial_progress
                
                for ai_type, ai_progress in progress.items():
                    if ai_progress.get("level", 1) >= 5:  # High-level AIs
                        construct_name = f"CHAOS.MASTERY.{ai_type.upper()}.LEVEL_{ai_progress.get('level', 1)}"
                        
                        if construct_name not in self.language_core["ai_derived_constructs"]:
                            constructs[construct_name] = {
                                "description": f"Mastery level construct from {ai_type}",
                                "syntax": f"{construct_name}(mastery_application, target_complexity)",
                                "ai_type": ai_type,
                                "mastery_level": ai_progress.get("level", 1),
                                "victories": ai_progress.get("victories", 0),
                                "created": datetime.utcnow().isoformat(),
                                "origin": "ai_mastery_achievement"
                            }
            
        except Exception as e:
            logger.error(f"Error collecting adversarial constructs: {e}")
        
        return constructs
    
    async def _integrate_new_constructs(self, new_constructs: Dict[str, Any]):
        """Integrate new constructs into language core"""
        try:
            for construct_name, construct_data in new_constructs.items():
                origin = construct_data.get("origin", "unknown")
                
                # Categorize construct based on origin
                if origin in ["project_horus", "horus_weapon_synthesis"]:
                    if "weapon" in construct_name.lower():
                        self.language_core["weapon_specific_constructs"][construct_name] = construct_data
                    else:
                        self.language_core["ai_derived_constructs"][construct_name] = construct_data
                elif origin in ["project_berserk", "berserk_combat_analysis"]:
                    if "weapon" in construct_name.lower() or "berserk" in construct_name.lower():
                        self.language_core["weapon_specific_constructs"][construct_name] = construct_data
                    else:
                        self.language_core["ai_derived_constructs"][construct_name] = construct_data
                elif origin in ["adversarial_experience", "ai_mastery_achievement"]:
                    self.language_core["ai_derived_constructs"][construct_name] = construct_data
                else:
                    self.language_core["ai_derived_constructs"][construct_name] = construct_data
                
                # Update growth metrics
                self._update_growth_metrics(construct_name, construct_data)
            
            # Record evolution event
            if new_constructs:
                evolution_event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "constructs_added": len(new_constructs),
                    "construct_names": list(new_constructs.keys()),
                    "evolution_cycle": self.growth_metrics["evolution_cycles"]
                }
                
                self.language_core["evolution_history"].append(evolution_event)
                self.growth_metrics["evolution_cycles"] += 1
                self.growth_metrics["last_growth_event"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Error integrating new constructs: {e}")
    
    def _update_growth_metrics(self, construct_name: str, construct_data: Dict[str, Any]):
        """Update growth metrics for new construct"""
        self.growth_metrics["total_constructs"] += 1
        
        # Update per-AI metrics
        origin_ai = construct_data.get("origin_ai") or construct_data.get("source_ai") or construct_data.get("ai_type")
        if origin_ai:
            if origin_ai not in self.growth_metrics["constructs_per_ai"]:
                self.growth_metrics["constructs_per_ai"][origin_ai] = 0
            self.growth_metrics["constructs_per_ai"][origin_ai] += 1
        
        # Update per-weapon-category metrics
        weapon_category = construct_data.get("weapon_category")
        if weapon_category:
            if weapon_category not in self.growth_metrics["constructs_per_weapon_category"]:
                self.growth_metrics["constructs_per_weapon_category"][weapon_category] = 0
            self.growth_metrics["constructs_per_weapon_category"][weapon_category] += 1
    
    async def _generate_new_chapter_from_constructs(self, new_constructs: Dict[str, Any]):
        """Generate new documentation chapter from constructs"""
        try:
            # Analyze construct origins to determine chapter type
            origins = [construct.get("origin", "unknown") for construct in new_constructs.values()]
            origin_counts = {}
            for origin in origins:
                origin_counts[origin] = origin_counts.get(origin, 0) + 1
            
            # Determine primary chapter type
            primary_origin = max(origin_counts, key=origin_counts.get)
            
            if "horus" in primary_origin or "weapon" in primary_origin:
                chapter_type = "weapon_synthesis"
                chapter_focus = self._determine_weapon_focus(new_constructs)
            elif "berserk" in primary_origin or "combat" in primary_origin:
                chapter_type = "adversarial_evolution"
                chapter_focus = self._determine_combat_focus(new_constructs)
            else:
                chapter_type = "ai_learning_integration"
                chapter_focus = self._determine_ai_focus(new_constructs)
            
            # Generate chapter
            chapter = await self._create_chapter(chapter_type, chapter_focus, new_constructs)
            
            self.documentation_chapters.append(chapter)
            
            # Update language version
            await self._increment_language_version()
            
            logger.info(f"Generated new chaos language chapter: {chapter['title']}")
            
        except Exception as e:
            logger.error(f"Error generating new chapter: {e}")
    
    def _determine_weapon_focus(self, constructs: Dict[str, Any]) -> str:
        """Determine weapon focus for chapter"""
        categories = [c.get("weapon_category", "general") for c in constructs.values() if c.get("weapon_category")]
        
        if categories:
            # Return most common category
            category_counts = {}
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            return max(category_counts, key=category_counts.get)
        
        return "general"
    
    def _determine_combat_focus(self, constructs: Dict[str, Any]) -> str:
        """Determine combat focus for chapter"""
        domains = [c.get("domain", "general") for c in constructs.values() if c.get("domain")]
        
        if domains:
            # Return most common domain
            domain_counts = {}
            for domain in domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            return max(domain_counts, key=domain_counts.get)
        
        return "general"
    
    def _determine_ai_focus(self, constructs: Dict[str, Any]) -> str:
        """Determine AI focus for chapter"""
        ais = []
        for construct in constructs.values():
            ai = construct.get("origin_ai") or construct.get("source_ai") or construct.get("ai_type")
            if ai:
                ais.append(ai)
        
        if ais:
            # Return most common AI
            ai_counts = {}
            for ai in ais:
                ai_counts[ai] = ai_counts.get(ai, 0) + 1
            return max(ai_counts, key=ai_counts.get)
        
        return "collective"
    
    async def _create_chapter(self, chapter_type: str, focus: str, constructs: Dict[str, Any]) -> Dict[str, Any]:
        """Create documentation chapter"""
        chapter_number = len(self.documentation_chapters) + 1
        template = self.chapter_templates.get(chapter_type, self.chapter_templates["ai_learning_integration"])
        
        if chapter_type == "weapon_synthesis":
            title = template["title_template"].format(weapon_category=focus)
        elif chapter_type == "adversarial_evolution":
            title = template["title_template"].format(domain=focus)
        else:
            title = template["title_template"].format(ai_type=focus)
        
        chapter = {
            "chapter_number": chapter_number,
            "title": title,
            "chapter_type": chapter_type,
            "focus": focus,
            "constructs": constructs,
            "sections": await self._generate_chapter_sections(chapter_type, focus, constructs),
            "created": datetime.utcnow().isoformat(),
            "language_version": self.language_core["version"],
            "construct_count": len(constructs)
        }
        
        return chapter
    
    async def _generate_chapter_sections(self, chapter_type: str, focus: str, 
                                       constructs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sections for chapter"""
        template = self.chapter_templates.get(chapter_type, self.chapter_templates["ai_learning_integration"])
        sections = {}
        
        for section_name in template["sections"]:
            if section_name == "Introduction":
                sections[section_name] = self._generate_introduction_section(chapter_type, focus, constructs)
            elif "Constructs" in section_name:
                sections[section_name] = self._generate_constructs_section(constructs)
            elif "Patterns" in section_name:
                sections[section_name] = self._generate_patterns_section(constructs)
            elif "Examples" in section_name:
                sections[section_name] = self._generate_examples_section(constructs)
            elif "Metrics" in section_name or "Analysis" in section_name:
                sections[section_name] = self._generate_metrics_section(constructs)
            else:
                sections[section_name] = f"Content for {section_name} section"
        
        return sections
    
    def _generate_introduction_section(self, chapter_type: str, focus: str, 
                                     constructs: Dict[str, Any]) -> str:
        """Generate introduction section"""
        intro = f"This chapter documents the evolution of chaos language constructs "
        
        if chapter_type == "weapon_synthesis":
            intro += f"related to {focus} weapon synthesis and deployment."
        elif chapter_type == "adversarial_evolution":
            intro += f"derived from adversarial experiences in the {focus} domain."
        else:
            intro += f"contributed by {focus} AI learning and experiences."
        
        intro += f"\n\nTotal constructs documented: {len(constructs)}"
        intro += f"\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return intro
    
    def _generate_constructs_section(self, constructs: Dict[str, Any]) -> str:
        """Generate constructs section"""
        section = "## Chaos Language Constructs\n\n"
        
        for construct_name, construct_data in constructs.items():
            section += f"### {construct_name}\n"
            section += f"**Description:** {construct_data.get('description', 'No description')}\n"
            section += f"**Syntax:** `{construct_data.get('syntax', 'No syntax defined')}`\n"
            
            origin = construct_data.get('origin', 'unknown')
            section += f"**Origin:** {origin}\n"
            
            if construct_data.get('complexity'):
                section += f"**Complexity:** {construct_data['complexity']}\n"
            
            section += "\n"
        
        return section
    
    def _generate_patterns_section(self, constructs: Dict[str, Any]) -> str:
        """Generate patterns section"""
        section = "## Usage Patterns\n\n"
        
        # Analyze construct patterns
        origins = [c.get('origin', 'unknown') for c in constructs.values()]
        complexity_levels = [c.get('complexity', 1.0) for c in constructs.values() if c.get('complexity')]
        
        section += f"**Origin Distribution:**\n"
        origin_counts = {}
        for origin in origins:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
        
        for origin, count in origin_counts.items():
            section += f"- {origin}: {count} constructs\n"
        
        if complexity_levels:
            avg_complexity = sum(complexity_levels) / len(complexity_levels)
            section += f"\n**Average Complexity:** {avg_complexity:.2f}\n"
        
        return section
    
    def _generate_examples_section(self, constructs: Dict[str, Any]) -> str:
        """Generate examples section"""
        section = "## Usage Examples\n\n"
        
        # Pick first few constructs for examples
        example_constructs = list(constructs.items())[:3]
        
        for construct_name, construct_data in example_constructs:
            section += f"### Example: {construct_name}\n"
            section += f"```chaos\n{construct_data.get('syntax', 'No syntax')}\n```\n"
            
            if construct_data.get('lessons'):
                section += f"**Learned from:** {', '.join(construct_data['lessons'][:2])}\n"
            
            section += "\n"
        
        return section
    
    def _generate_metrics_section(self, constructs: Dict[str, Any]) -> str:
        """Generate metrics section"""
        section = "## Performance Metrics\n\n"
        
        # Calculate various metrics
        total_constructs = len(constructs)
        complexity_constructs = len([c for c in constructs.values() if c.get('complexity', 0) > 1.5])
        weapon_constructs = len([c for c in constructs.values() if 'weapon' in c.get('origin', '').lower()])
        
        section += f"**Total Constructs:** {total_constructs}\n"
        section += f"**High Complexity Constructs:** {complexity_constructs}\n"
        section += f"**Weapon-Derived Constructs:** {weapon_constructs}\n"
        
        # Performance scores if available
        performance_scores = [c.get('performance_score', 0) for c in constructs.values() if c.get('performance_score')]
        if performance_scores:
            avg_performance = sum(performance_scores) / len(performance_scores)
            section += f"**Average Performance Score:** {avg_performance:.2f}\n"
        
        return section
    
    async def _increment_language_version(self):
        """Increment language version"""
        try:
            version_parts = self.language_core["version"].split('.')
            version_parts[1] = str(int(version_parts[1]) + 1)
            self.language_core["version"] = '.'.join(version_parts)
            
        except Exception as e:
            logger.error(f"Error incrementing language version: {e}")
    
    async def _background_language_growth_monitor(self):
        """Background monitoring for language growth"""
        while True:
            try:
                await asyncio.sleep(1800)  # Every 30 minutes
                
                # Collect new constructs
                collection_result = await self.collect_new_constructs_from_system()
                
                if collection_result["horus_constructs"] + collection_result["berserk_constructs"] + collection_result["ai_adversarial_constructs"] > 0:
                    logger.info(f"Chaos language growth: {collection_result}")
                
            except Exception as e:
                logger.error(f"Error in language growth monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def get_complete_chaos_language_documentation(self) -> Dict[str, Any]:
        """Get complete chaos language documentation"""
        return {
            "language_core": self.language_core,
            "documentation_chapters": self.documentation_chapters,
            "growth_metrics": self.growth_metrics,
            "total_constructs": (
                len(self.language_core["base_constructs"]) +
                len(self.language_core["ai_derived_constructs"]) +
                len(self.language_core["weapon_specific_constructs"])
            ),
            "auto_generation_enabled": self.auto_generation_enabled,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def force_chapter_generation(self) -> Dict[str, Any]:
        """Force generation of new chapter from current constructs"""
        try:
            # Collect current constructs
            collection_result = await self.collect_new_constructs_from_system()
            
            if collection_result["new_constructs"]:
                await self._generate_new_chapter_from_constructs(collection_result["new_constructs"])
                
                return {
                    "status": "success",
                    "message": "New chapter generated",
                    "constructs_processed": len(collection_result["new_constructs"]),
                    "chapter_number": len(self.documentation_chapters)
                }
            else:
                return {
                    "status": "no_new_constructs",
                    "message": "No new constructs available for chapter generation"
                }
                
        except Exception as e:
            logger.error(f"Error forcing chapter generation: {e}")
            return {"status": "error", "message": str(e)}


# Global instance
chaos_language_service = ChaosLanguageService()