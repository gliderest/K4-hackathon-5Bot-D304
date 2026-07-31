# AI Tutor Architecture Design - Learning Agent Version

## Overview
This document describes the improved AI Tutor architecture that transforms the system from a Retrieval-Augmented Chatbot to a true AI Learning Agent, as requested. The design preserves the existing codebase and project structure while enhancing the internal workflow.

## Core Architecture Components

The improved architecture follows this flow:
```
User Input
    ↓
[Intent Detection] → Determines user's goal and question type
    ↓
[Planner] → Creates execution plan: what info is needed, which tools to call, sequence
    ↓
[Tool Calling Loop] → Executes tools dynamically based on plan
    ↓
[Context Builder] → Combines tool results into coherent context for LLM
    ↓
[LLM] → Generates initial response based on enriched context
    ↓
[Reflection] → Evaluates response for completeness, accuracy, and pedagogical value
    ↓
[Final Answer] → Refined response after reflection
    ↓
[Learning State Update] → Updates student model based on interaction
```

## Component Details

### 1. Intent Detection
**Purpose**: Understand what the student is trying to achieve
**Input**: Raw user query (text or transcribed speech)
**Output**: Intent classification with confidence score
**Capabilities**:
- Question type identification (explanation, summary, comparison, application, etc.)
- Topic/subject detection
- Difficulty level inference
- Emotional/engagement state detection (frustration, curiosity, confidence)
**Implementation**: 
- Lightweight classifier or LLM-based intent recognition
- Can be implemented as a specialized tool or pre-processing step

### 2. Planner
**Purpose**: Determine what information is needed and which tools to use
**Input**: User intent, current learning state, conversation history
**Output**: Execution plan with tool sequence and dependencies
**Capabilities**:
- Decides single vs. multiple tool usage
- Determines tool execution order based on dependencies
- Identifies when parallel execution is beneficial
- Plans for iterative refinement (if initial results insufficient)
**Implementation**:
- Rule-based planner for common patterns
- LLM-based planner for complex, novel requests
- Planning cache for frequent query patterns

### 3. Tool Calling Loop
**Purpose**: Dynamically execute tools based on the plan
**Input**: Execution plan from Planner
**Output**: Results from executed tools
**Capabilities**:
- Executes tools sequentially or in parallel as planned
- Handles tool dependencies (output of one tool as input to another)
- Dynamically adjusts plan based on intermediate results
- Continues until sufficient evidence is gathered or max iterations reached
- Implements retry mechanisms for failed tool calls
**Implementation**:
- Extends the existing `run_model_tool_loop` from lab04's chat.py
- Adds dynamic replanning capability based on intermediate results
- Maintains tool execution state and history

### 4. Context Builder
**Purpose**: Synthesize tool results into coherent context for LLM
**Input**: Results from executed tools
**Output**: Structured context package for LLM consumption
**Capabilities**:
- Removes redundancy from multiple tool outputs
- Resolves conflicts between different information sources
- Structures information by relevance and reliability
- Preserves citations and source attribution
- Formats context optimally for LLM consumption
**Implementation**:
- Separate module that processes tool results
- Uses techniques like retrieval-augmented generation (RAG) principles
- Implements citation tracking and formatting

### 5. LLM (Language Model)
**Purpose**: Generate initial response based on enriched context
**Input**: User query + built context + system prompts
**Output**: Initial response candidate
**Capabilities**:
- Leverages the educational context to generate accurate, pedagogical responses
- Follows instruction prompts for teaching style, tone, and approach
- Maintains awareness of learning objectives and student level
**Implementation**:
- Uses existing provider abstraction from lab04
- Enhanced with educational-specific system prompts
- Temperature and other parameters tuned for educational use

### 6. Reflection
**Purpose**: Evaluate and improve the initial response
**Input**: Initial response, original query, tool results, learning state
**Output**: Feedback on response quality and suggested improvements
**Capabilities**:
- Checks completeness: Did we answer all parts of the question?
- Verifies accuracy: Are claims supported by evidence from tools?
- Assesses pedagogical value: Is explanation clear and appropriate for level?
- Identifies gaps: What additional information might be needed?
- Determines if prerequisite knowledge should be mentioned
- Evaluates if follow-up suggestions or resources would be helpful
**Implementation**:
- Can be implemented as:
  a) Self-reflection by the same LLM with different prompt
  b) Specialized critic model
  c) Rule-based checker for common issues
- Triggers additional tool calls if deficiencies found

### 7. Final Answer Generation
**Purpose**: Produce the refined response incorporating reflection feedback
**Input**: Initial response + reflection feedback
**Output**: Final response to present to user
**Capabilities**:
- Incorporates suggested improvements from reflection
- Adds missing information if needed
- Adjusts tone, clarity, and pedagogical approach
- Ensures proper citation formatting
- Includes proactive learning suggestions when appropriate
**Implementation**:
- Another LLM call with reflective feedback incorporated
- Or direct modification of initial response based on critique

### 8. Learning State Update
**Purpose**: Update the student model based on this interaction
**Input**: Interaction summary, final response, student actions/feedback
**Output**: Updated learning model
**Capabilities**:
- Tracks concept mastery based on question complexity and correctness
- Identifies misconceptions from student questions or mistakes
- Updates knowledge progression (completed, current, upcoming topics)
- Adjusts recommended difficulty and pacing
- Records effective explanations and examples for future use
- Notes preferred learning modalities (visual, verbal, examples, etc.)
**Implementation**:
- Separate Learning State Tool (as requested in requirements)
- Persistent storage (file-based or simple database)
- Updates happen asynchronously to not block response

## Tool Design (As Requested)

All tools follow the lab04 tool interface pattern but are enhanced for educational purposes:

### 1. Course Knowledge Tool
**Capabilities**:
- Search across slides, transcripts, and chat history
- Implements knowledge priority: current lesson → current transcript → other lessons → other transcripts → chat history → conversation memory → uploaded documents
- Returns ranked results with citations
- Specialized query understanding for educational concepts

### 2. Conversation Memory Tool
**Capabilities**:
- Retrieve previous conversations by student, topic, or time
- Summarize conversation history
- Recall specific explanations or examples given before
- Identify recurring questions or problem areas
- Track conversation patterns

### 3. Learning State Tool
**Capabilities**:
- Maintain current lesson, completed lessons, visited lessons
- Track weak concepts, strong concepts, frequently asked concepts
- Record quiz performance and trends
- Store preferred explanation style and learning pace
- Generate recommended review topics
- Update mastery estimates based on interactions

### 4. Rewrite Tool
**Capabilities**:
- Summarize, simplify, expand, rephrase content
- Convert to bullet points, study notes, or flashcards
- Adapt complexity level based on learning state
- Generate multiple representations of same concept

### 5. Quiz Tool
**Capabilities**:
- Generate MCQ, True/False, Short Answer questions
- Adjust difficulty based on learning state
- Create concept-check questions vs. application problems
- Provide hints and explanations for answers
- Track question effectiveness over time

### 6. Recommendation Tool
**Capabilities**:
- Recommend prerequisite review when needed
- Suggest next logical topics based on current mastery
- Identify related concepts for interdisciplinary connections
- Generate personalized review schedules
- Suggest alternative explanations when struggling

### 7. Citation Tool
**Capabilities**:
- Extract and format transcript markers [Txx-NNN]
- Reference slide numbers and lesson IDs
- Create bibliography-style references
- Ensure proper attribution in all responses
- Cross-reference between different content types

### 8. External Learning Tool
**Capabilities**:
- Process uploaded PDF, DOCX, PPTX, TXT, Markdown files
- Extract text and semantic meaning
- Integrate with course knowledge temporarily (higher priority than uploaded docs but lower than official course materials)
- Prevent overwriting or corrupting official course knowledge
- Clean up temporary knowledge after session or timeout

### 9. Speech Tool
**Capabilities**:
- Speech-to-Text for voice input
- Text-to-Speech for voice output
- Support for multiple languages (Vietnamese, English)
- Voice interaction controls (speed, tone, etc.)
- Pronunciation assistance for technical terms

## Knowledge Priority Implementation

The system strictly follows this knowledge retrieval priority:
1. Current lesson (based on student's current learning context)
2. Current transcript (specific to current lesson)
3. Other lessons (different topics in course)
4. Other transcripts (different lectures)
5. Chat history (historical tutor-student interactions as expert demonstration)
6. Conversation memory (this student's personal history)
7. Uploaded documents (temporary, session-only knowledge)

Each tool implementation respects this hierarchy when searching and ranking results.

## Chat History as Tutor Experience

Rather than treating chat history as simple memory, the system leverages it as expert demonstration data:
- Identifies effective explanation patterns from high-rated tutor responses
- Learns common student misconceptions from confusing questions
- Extracts effective follow-up questions that promote deeper understanding
- Recognizes successful teaching strategies for different concept types
- Applies these learned patterns when generating new responses

This is implemented through:
- Specialized analysis of chat history during system preparation
- Pattern matching when generating explanations
- Retrieval of similar historical Q&A pairs as examples
- Weighting of responses based on historical effectiveness metrics

## Proactive AI Capabilities

The system initiates helpful interactions without waiting for explicit requests:
- **Stuck Detection**: If student stays on same lesson > threshold time, offers summary
- **Repetition Detection**: If same topic asked repeatedly, offers flashcards/quiz/study notes
- **Prerequisite Checking**: If attempting advanced topic without basics, recommends review
- **Performance-Based Adaptation**: Poor quiz scores trigger alternative learning paths
- **Engagement Monitoring**: Drops in interaction frequency trigger re-engagement prompts
- **Mastery Celebration**: When concepts are mastered, suggests advancing or applying knowledge

## Implementation Approach Preserving Existing Codebase

To preserve the current structure while implementing these enhancements:

1. **Minimal Core Changes**:
   - Keep the basic `ResearchAgent`, `Provider`, and tool interface unchanged
   - Enhance `run_model_tool_loop` to support dynamic replanning
   - Add new educational-specific tools following existing patterns

2. **New Modules to Add**:
   - `intent_detector.py` - Intent detection logic
   - `planner.py` - Planning component
   - `context_builder.py` - Context synthesis
   - `reflection_engine.py` - Response evaluation
   - `learning_state_manager.py` - Student model (enhanced from basic concept)
   - `proactive_engine.py` - Initiative behaviors

3. **Enhanced Existing Components**:
   - Extend `agent.py` with new workflow orchestration
   - Enhance tool implementations with educational capabilities
   - Improve `chat.py` to handle the new workflow stages

4. **Configuration Approach**:
   - Use existing YAML-based tool configuration
   - Add educational-specific configuration for prompts and parameters
   - Maintain backward compatibility with existing tools

## Data Flow Example

Let's trace through a sample interaction: "Explain gradient descent like I'm 5"

1. **Input**: Student speaks: "Giải thích gradient descent như tôi có 5 tuổi đi" (Vietnamese)
2. **Speech-to-Text Tool**: Converts to text: "Explain gradient descent like I'm 5"
3. **Intent Detection**: Identifies intent as "simple explanation" with concept "gradient descent"
4. **Planner**: Decides to use Course Knowledge Tool (for gradient descent info) + Rewrite Tool (to simplify)
5. **Tool Calling Loop**: 
   - Calls Course Knowledge Tool → gets technical explanation from slides/transcripts
   - Passes result to Rewrite Tool → gets simplified analogy-based explanation
6. **Context Builder**: Combines technical source with simplified version, preserves citations
7. **LLM**: Generates initial child-friendly explanation using the simplified content
8. **Reflection**: Checks if explanation is truly simple enough, if analogies are appropriate, if core concept preserved
9. **Final Answer**: Refines explanation based on feedback, adds engaging elements for 5-year-old level
10. **Learning State Update**: Records that student requested beginner-level explanation of optimization concepts
11. **Proactive Check**: Notices this is first request on optimization topic, considers if prerequisite info needed

## Benefits of This Approach

1. **True Learning Agent Behavior**: Actively reasons, plans, and reflects rather than just retrieving
2. **Personalization**: Continuously adapts to individual student needs
3. **Pedagogical Quality**: Ensures explanations are educationally sound, not just factually correct
4. **Efficiency**: Uses tools strategically rather than exhaustively
5. **Initiative**: Helps students even when they don't know what to ask for
6. **Transparency**: Maintains clear reasoning trace and citation trail
7. **Scalability**: Modular components can be improved independently
8. **Preservation**: Builds upon existing solid foundation rather than replacing it

This design transforms the system from a passive question-answerer to an active learning partner that understands not just what students ask, but what they need to learn effectively.