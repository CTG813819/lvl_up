# Dynamic Evaluation System

## Overview

The Dynamic Evaluation System replaces template-based scoring with scenario-driven criteria generation. Instead of using predefined base scores or templates, the system analyzes each test scenario and generates appropriate evaluation criteria based on the specific requirements, AI type, difficulty level, and technical content.

## Key Principles

### 1. Scenario-Driven Criteria Generation
- **No Templates**: Evaluation criteria are generated dynamically based on the actual test scenario
- **Context-Aware**: Criteria adapt to the specific requirements and context of each test
- **AI-Specific**: Different criteria for different AI types based on their strengths and the scenario
- **Difficulty-Adaptive**: Criteria scale with difficulty level (basic to legendary)

### 2. Multi-Dimensional Evaluation
The system evaluates responses across multiple dimensions:

- **Requirements Coverage**: How well the response addresses the specific requirements extracted from the scenario
- **Difficulty Performance**: How well the response meets difficulty-specific expectations
- **AI-Specific Performance**: How well the AI leverages its unique capabilities
- **Technical Performance**: How well the response handles technical aspects
- **Quality Performance**: Overall quality, clarity, and relevance

### 3. Dynamic Scoring
- **No Base Scores**: Scores are calculated based on actual performance against generated criteria
- **Weighted Components**: Different evaluation components are weighted based on difficulty
- **Context-Sensitive**: Scoring adapts to the specific scenario and AI type

## System Architecture

### Core Methods

#### `_evaluate_with_dynamic_criteria(ai_type, scenario, response, difficulty)`
Main evaluation method that:
1. Generates dynamic criteria from the scenario
2. Evaluates the response against those criteria
3. Calculates a comprehensive score
4. Generates detailed feedback

#### `_generate_dynamic_criteria(scenario, difficulty, ai_type)`
Generates evaluation criteria by:
1. **Extracting Requirements**: Parses the scenario for specific requirements
2. **Difficulty Criteria**: Creates criteria based on difficulty level
3. **AI-Specific Criteria**: Generates criteria based on AI type and scenario
4. **Technical Criteria**: Identifies technical requirements from scenario content
5. **Quality Criteria**: Establishes quality standards based on difficulty

### Criteria Generation

#### Requirements Extraction
```python
def _extract_scenario_requirements(scenario: str) -> List[str]:
    # Looks for action words like "create", "build", "implement", "design"
    # Extracts specific requirements from the scenario text
    # Falls back to general requirements if none found
```

#### Difficulty-Specific Criteria
- **Basic**: Focus on completeness, clarity, and correctness
- **Intermediate**: Add efficiency and error handling
- **Advanced**: Include optimization, scalability, and sophisticated solutions
- **Expert**: Emphasize innovation, enterprise-level considerations
- **Master**: Require leadership, groundbreaking approaches
- **Legendary**: Demand visionary thinking and exceptional excellence

#### AI-Specific Criteria
- **Conquest**: User focus, practical implementation, development skills
- **Guardian**: Security analysis, protection mechanisms, assessment capabilities
- **Imperium**: System optimization, performance enhancement, architectural expertise
- **Sandbox**: Experimental approaches, innovation, discovery capabilities

#### Technical Criteria
Generated based on scenario keywords:
- **Code-related**: Code quality, correctness, optimization
- **Security-related**: Security implementation, threat analysis
- **Performance-related**: Performance consideration, optimization techniques
- **Scalability-related**: Scalability design, architectural considerations

### Evaluation Process

#### Single Criterion Evaluation
```python
def _evaluate_single_criterion(response_lower: str, criterion_description: str) -> float:
    # Extracts keywords from criterion description
    # Counts keyword matches in response
    # Returns score based on coverage (20-100 points)
```

#### Component Scoring
Each evaluation component is scored independently:
- **Requirements Coverage**: Percentage of requirements addressed
- **Difficulty Performance**: Average score across difficulty criteria
- **AI-Specific Performance**: Average score across AI-specific criteria
- **Technical Performance**: Average score across technical criteria
- **Quality Performance**: Average score across quality criteria

#### Final Score Calculation
```python
def _calculate_dynamic_score(evaluation_results: Dict[str, float], difficulty: str) -> float:
    # Weights components based on difficulty level
    # Basic: 40% requirements, 30% difficulty, 20% AI-specific, 10% technical
    # Advanced: 25% each component
    # Expert+: Higher weight on AI-specific and technical components
```

## Collaborative Evaluation

### Collaborative Criteria Generation
- **Individual Contribution**: Each AI should make meaningful contributions
- **Complementary Approaches**: AIs should provide different perspectives
- **Coordination**: Effective teamwork and coordination
- **Synergy**: Collaborative effort should exceed individual capabilities
- **Scenario-Specific**: Criteria based on which AIs are participating

### Collaboration Scoring
- **Diversity Bonus**: Rewards different approaches and perspectives
- **Participation Bonus**: Rewards more participants
- **AI-Specific Collaboration**: Bonus for AIs playing their roles effectively
- **Synergy Bonus**: Bonus for complementary contributions

## Example Scenarios

### Security Test (Guardian AI, Advanced)
**Scenario**: "Create a secure authentication system with password hashing, JWT tokens, and protection against SQL injection, XSS, and CSRF."

**Generated Criteria**:
- **Requirements**: Address authentication, security measures, attack protection
- **Difficulty**: Sophisticated solution, complex concepts, high accuracy, optimization, scalability
- **AI-Specific**: Security focus, threat analysis, Guardian strength
- **Technical**: Security implementation, threat analysis, code quality, code correctness, code optimization
- **Quality**: Completeness, clarity, relevance, depth, comprehensiveness

### Performance Test (Imperium AI, Expert)
**Scenario**: "Optimize a slow database query with multiple joins and aggregations on large datasets."

**Generated Criteria**:
- **Requirements**: Address query optimization, performance issues, large datasets
- **Difficulty**: Expert-level solution, expert clarity, expert accuracy, advanced optimization, enterprise scalability, innovation
- **AI-Specific**: Optimization focus, integration focus, Imperium strength
- **Technical**: Performance consideration, optimization techniques, scalability design, architecture consideration
- **Quality**: Completeness, clarity, relevance, depth, comprehensiveness, innovation, expertise

## Benefits

### 1. Eliminates Template Bias
- No more arbitrary base scores (40.08, 45, 50, 55)
- Scores reflect actual performance against scenario requirements
- Each test is evaluated on its own merits

### 2. Improves Accuracy
- Criteria are specific to the actual test scenario
- Evaluation considers the context and requirements
- AI-specific strengths are properly evaluated

### 3. Enhances Learning
- Detailed feedback based on specific criteria
- AIs can understand exactly what they need to improve
- Evaluation is transparent and explainable

### 4. Supports Growth
- Criteria adapt to AI performance and difficulty level
- Evaluation encourages improvement in specific areas
- Collaborative evaluation promotes teamwork

## Testing

Run the dynamic evaluation test:
```bash
python test_dynamic_evaluation.py
```

This will verify:
- Dynamic criteria generation works correctly
- Evaluation scores are based on actual performance
- AI-specific criteria are properly applied
- Collaborative evaluation functions correctly
- No template-based scoring is used

## Monitoring

After deployment, monitor:
1. **Criteria Generation**: Verify criteria are generated for each scenario
2. **Score Variation**: Confirm scores vary based on actual performance
3. **AI-Specific Evaluation**: Check that AIs are evaluated based on their strengths
4. **Collaborative Performance**: Verify collaboration bonuses work correctly
5. **Feedback Quality**: Ensure feedback is specific and actionable

## Files Modified

1. **`custody_protocol_service.py`** - Added dynamic evaluation methods
2. **`test_dynamic_evaluation.py`** - New test script for dynamic evaluation
3. **`DYNAMIC_EVALUATION_SYSTEM.md`** - This documentation

## Migration from Template-Based System

The system now:
- ✅ Generates criteria based on actual test scenarios
- ✅ Evaluates responses against scenario-specific requirements
- ✅ Considers AI-specific strengths and capabilities
- ✅ Adapts scoring to difficulty levels
- ✅ Provides detailed, actionable feedback
- ✅ Supports collaborative evaluation
- ❌ No longer uses arbitrary base scores
- ❌ No longer uses template-based criteria
- ❌ No longer ignores scenario context

This ensures that each AI is evaluated based on their actual performance in addressing the specific challenges presented in each test, rather than receiving scores based on templates or arbitrary base values. 