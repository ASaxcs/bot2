"""
Cognition Processor for Lacia AI
Handles cognitive processing, context analysis, and memory integration
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import threading


def safe_memory_slice(memory_data, slice_obj=None, start=None, end=None):
    """Safe memory slicing to prevent index errors"""
    if not isinstance(memory_data, (list, tuple)):
        return []
    
    try:
        if slice_obj is not None:
            if isinstance(slice_obj, slice):
                return list(memory_data[slice_obj])
            elif isinstance(slice_obj, int):
                return [memory_data[slice_obj]] if 0 <= slice_obj < len(memory_data) else []
            else:
                return []
        
        # Handle start/end parameters
        if start is not None or end is not None:
            start = start if isinstance(start, int) else 0
            end = end if isinstance(end, int) else len(memory_data)
            return list(memory_data[start:end])
        
        return list(memory_data)
    except Exception as e:
        print(f"Memory slice error handled: {e}")
        return []

def safe_memory_retrieve(memory_list, limit=None):
    """Safely retrieve memory without slice errors"""
    if not isinstance(memory_list, (list, tuple)):
        return []
    
    if limit is None:
        return list(memory_list)
    
    try:
        if isinstance(limit, int) and limit > 0:
            return list(memory_list[-limit:])  # Get last N items safely
        return list(memory_list)
    except Exception as e:
        print(f"Memory retrieval error handled: {e}")
        return []

class CognitionProcessor:
    """Main cognitive processing engine"""
    
    def __init__(self, short_term_memory, long_term_memory, config: Dict[str, Any]):
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.config = config
        self.cognition_config = config.get("cognition", {})
        self.logger = logging.getLogger(__name__)
        
        # Processing parameters
        self.processing_depth = self.cognition_config.get("processing_depth", 3)
        self.context_window = self.cognition_config.get("context_window", 10)
        self.analysis_timeout = self.cognition_config.get("analysis_timeout", 30)
        
        # Processing state
        self.current_context = {}
        self.processing_lock = threading.Lock()
        
        self.logger.info("Cognition Processor initialized")
    
    def get_context_for_query(self, query: str, depth: int = None) -> Dict[str, Any]:
        """Get comprehensive context for a query"""
        try:
            with self.processing_lock:
                depth = depth or self.processing_depth
                
                context = {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "short_term_memories": self._get_relevant_short_term(query),
                    "long_term_memories": self._get_relevant_long_term(query),
                    "contextual_analysis": self._analyze_context(query, depth),
                    "relevance_scores": {},
                    "processing_metadata": {
                        "depth": depth,
                        "processing_time": None,
                        "context_quality": 0.0
                    }
                }
                
                # Calculate relevance scores
                context["relevance_scores"] = self._calculate_relevance_scores(context)
                
                # Assess context quality
                context["processing_metadata"]["context_quality"] = self._assess_context_quality(context)
                
                return context
                
        except Exception as e:
            self.logger.error(f"Context generation error: {e}")
            return self._get_fallback_context(query)
    
    def _get_relevant_short_term(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get relevant short-term memories with safe slicing"""
        try:
            limit = limit or self.context_window
            
            if not hasattr(self.short_term_memory, 'get_relevant_memories'):
                # Fallback with safe memory retrieval
                recent_memories = getattr(self.short_term_memory, 'memories', [])
                return safe_memory_retrieve(recent_memories, limit)
            
            return self.short_term_memory.get_relevant_memories(query, limit)
            
        except Exception as e:
            self.logger.error(f"Short-term memory retrieval error: {e}")
            return []
    
    def _get_relevant_long_term(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant long-term memories"""
        try:
            if not hasattr(self.long_term_memory, 'search_memories'):
                # Fallback if method doesn't exist
                return []
            
            return self.long_term_memory.search_memories(query, limit)
            
        except Exception as e:
            self.logger.error(f"Long-term memory retrieval error: {e}")
            return []
    
    def _analyze_context(self, query: str, depth: int) -> Dict[str, Any]:
        """Perform contextual analysis of the query"""
        try:
            analysis = {
                "query_type": self._classify_query_type(query),
                "intent": self._detect_intent(query),
                "entities": self._extract_entities(query),
                "sentiment": self._analyze_sentiment(query),
                "complexity": self._assess_complexity(query),
                "topics": self._extract_topics(query),
                "temporal_context": self._analyze_temporal_context(query)
            }
            
            # Deep analysis for higher depth levels
            if depth > 1:
                analysis["semantic_analysis"] = self._semantic_analysis(query)
            
            if depth > 2:
                analysis["conceptual_mapping"] = self._conceptual_mapping(query)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Context analysis error: {e}")
            return {"error": str(e)}
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower().strip()
        
        # Question indicators
        question_words = ["what", "who", "where", "when", "why", "how", "which", "whose"]
        if any(query_lower.startswith(word) for word in question_words) or query.endswith("?"):
            return "question"
        
        # Command indicators
        command_words = ["do", "make", "create", "generate", "write", "calculate", "find"]
        if any(query_lower.startswith(word) for word in command_words):
            return "command"
        
        # Request indicators
        request_words = ["please", "can you", "could you", "would you", "help me"]
        if any(phrase in query_lower for phrase in request_words):
            return "request"
        
        # Conversation indicators
        conversation_starters = ["hello", "hi", "hey", "good morning", "good evening"]
        if any(query_lower.startswith(starter) for starter in conversation_starters):
            return "greeting"
        
        return "statement"
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        # Information seeking
        info_indicators = ["what is", "tell me about", "explain", "describe", "information"]
        if any(indicator in query_lower for indicator in info_indicators):
            return "information_seeking"
        
        # Task completion
        task_indicators = ["create", "make", "build", "generate", "write", "calculate"]
        if any(indicator in query_lower for indicator in task_indicators):
            return "task_completion"
        
        # Problem solving
        problem_indicators = ["help", "solve", "fix", "troubleshoot", "issue", "problem"]
        if any(indicator in query_lower for indicator in problem_indicators):
            return "problem_solving"
        
        # Social interaction
        social_indicators = ["hello", "how are you", "thank you", "goodbye", "chat"]
        if any(indicator in query_lower for indicator in social_indicators):
            return "social_interaction"
        
        return "general"
    
    def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """Extract entities from query (simplified NER)"""
        entities = []
        
        # Simple pattern matching for common entities
        import re
        
        # Dates
        date_patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": "date",
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Numbers
        number_pattern = r'\b\d+(\.\d+)?\b'
        matches = re.finditer(number_pattern, query)
        for match in matches:
            entities.append({
                "text": match.group(),
                "type": "number",
                "start": match.start(),
                "end": match.end()
            })
        
        # Simple name detection (capitalized words)
        name_pattern = r'\b[A-Z][a-z]+\b'
        matches = re.finditer(name_pattern, query)
        for match in matches:
            # Skip common words that are often capitalized
            common_words = ["I", "The", "This", "That", "What", "Who", "Where", "When", "Why", "How"]
            if match.group() not in common_words:
                entities.append({
                    "text": match.group(),
                    "type": "name",
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
    
    def _analyze_sentiment(self, query: str) -> Dict[str, Any]:
        """Analyze sentiment of query (simplified)"""
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "enjoy", "happy", "pleased", "satisfied", "perfect"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "angry", "sad", "frustrated", "annoyed", "disappointed", "upset"
        ]
        
        query_lower = query.lower()
        
        positive_count = sum(1 for word in positive_words if word in query_lower)
        negative_count = sum(1 for word in negative_words if word in query_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
    
    def _assess_complexity(self, query: str) -> Dict[str, Any]:
        """Assess query complexity"""
        # Basic complexity metrics
        word_count = len(query.split())
        char_count = len(query)
        sentence_count = len([s for s in query.split('.') if s.strip()])
        
        # Technical indicators
        technical_words = [
            "algorithm", "function", "variable", "database", "system", "process",
            "implementation", "architecture", "framework", "protocol", "interface"
        ]
        
        technical_count = sum(1 for word in technical_words if word.lower() in query.lower())
        
        # Calculate complexity score
        complexity_score = 0.0
        
        if word_count > 20:
            complexity_score += 0.3
        elif word_count > 10:
            complexity_score += 0.1
        
        if sentence_count > 2:
            complexity_score += 0.2
        
        if technical_count > 0:
            complexity_score += min(0.4, technical_count * 0.1)
        
        # Question complexity
        if "?" in query:
            nested_questions = query.count("?")
            if nested_questions > 1:
                complexity_score += 0.2
        
        complexity_score = min(1.0, complexity_score)
        
        if complexity_score < 0.3:
            level = "simple"
        elif complexity_score < 0.7:
            level = "moderate"
        else:
            level = "complex"
        
        return {
            "level": level,
            "score": complexity_score,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "technical_indicators": technical_count
        }
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract topics from query"""
        # Simplified topic extraction using keyword matching
        topic_keywords = {
            "technology": ["computer", "software", "programming", "AI", "tech", "digital"],
            "science": ["research", "study", "experiment", "theory", "analysis", "data"],
            "health": ["medical", "health", "doctor", "medicine", "treatment", "symptoms"],
            "business": ["company", "market", "sales", "profit", "business", "finance"],
            "education": ["learn", "study", "school", "university", "course", "education"],
            "entertainment": ["movie", "music", "game", "fun", "entertainment", "show"],
            "personal": ["personal", "life", "family", "relationship", "feeling", "emotion"]
        }
        
        query_lower = query.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics if detected_topics else ["general"]
    
    def _analyze_temporal_context(self, query: str) -> Dict[str, Any]:
        """Analyze temporal context of query"""
        temporal_indicators = {
            "past": ["was", "were", "did", "had", "yesterday", "ago", "before", "previously"],
            "present": ["is", "are", "am", "do", "does", "now", "today", "currently"],
            "future": ["will", "shall", "going to", "tomorrow", "later", "next", "soon"]
        }
        
        query_lower = query.lower()
        temporal_context = {"past": 0, "present": 0, "future": 0}
        
        for tense, indicators in temporal_indicators.items():
            count = sum(1 for indicator in indicators if indicator in query_lower)
            temporal_context[tense] = count
        
        # Determine primary temporal focus
        primary_tense = max(temporal_context, key=temporal_context.get)
        if temporal_context[primary_tense] == 0:
            primary_tense = "present"  # default
        
        return {
            "primary_tense": primary_tense,
            "temporal_indicators": temporal_context,
            "has_temporal_reference": any(count > 0 for count in temporal_context.values())
        }
    
    def _semantic_analysis(self, query: str) -> Dict[str, Any]:
        """Perform semantic analysis (simplified)"""
        return {
            "semantic_similarity": 0.5,  # Placeholder
            "conceptual_density": len(set(query.lower().split())) / len(query.split()) if query.split() else 0,
            "information_density": len(query.replace(" ", "")) / len(query.split()) if query.split() else 0
        }
    
    def _conceptual_mapping(self, query: str) -> Dict[str, Any]:
        """Create conceptual mapping (simplified)"""
        return {
            "concept_graph": {},  # Placeholder for concept relationships
            "abstraction_level": "medium",  # Placeholder
            "domain_mapping": self._extract_topics(query)
        }
    
    def _calculate_relevance_scores(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate relevance scores for context elements"""
        scores = {}
        
        # Score short-term memories
        short_term_memories = context.get("short_term_memories", [])
        if short_term_memories:
            scores["short_term_relevance"] = len(short_term_memories) / self.context_window
        else:
            scores["short_term_relevance"] = 0.0
        
        # Score long-term memories
        long_term_memories = context.get("long_term_memories", [])
        scores["long_term_relevance"] = min(1.0, len(long_term_memories) / 5)
        
        # Score contextual analysis quality
        analysis = context.get("contextual_analysis", {})
        scores["analysis_completeness"] = len([k for k, v in analysis.items() if v]) / 7  # 7 main analysis components
        
        return scores
    
    def _assess_context_quality(self, context: Dict[str, Any]) -> float:
        """Assess overall context quality"""
        relevance_scores = context.get("relevance_scores", {})
        
        if not relevance_scores:
            return 0.0
        
        # Weight different aspects
        weights = {
            "short_term_relevance": 0.3,
            "long_term_relevance": 0.3,
            "analysis_completeness": 0.4
        }
        
        quality_score = 0.0
        for metric, score in relevance_scores.items():
            weight = weights.get(metric, 0.1)
            quality_score += score * weight
        
        return min(1.0, quality_score)
    
    def _get_fallback_context(self, query: str) -> Dict[str, Any]:
        """Get fallback context when processing fails"""
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "short_term_memories": [],
            "long_term_memories": [],
            "contextual_analysis": {
                "query_type": "unknown",
                "intent": "general",
                "entities": [],
                "sentiment": {"sentiment": "neutral", "confidence": 0.5},
                "complexity": {"level": "unknown", "score": 0.5},
                "topics": ["general"],
                "temporal_context": {"primary_tense": "present"}
            },
            "relevance_scores": {"fallback": 0.1},
            "processing_metadata": {
                "depth": 1,
                "processing_time": None,
                "context_quality": 0.1,
                "fallback": True
            }
        }
    
    def process_with_timeout(self, query: str, timeout: int = None) -> Dict[str, Any]:
        """Process query with timeout"""
        timeout = timeout or self.analysis_timeout
        
        try:
            # Use threading for timeout
            result = [None]
            exception = [None]
            
            def process_target():
                try:
                    result[0] = self.get_context_for_query(query)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=process_target)
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive():
                self.logger.warning(f"Query processing timed out after {timeout}s")
                return self._get_fallback_context(query)
            
            if exception[0]:
                raise exception[0]
            
            return result[0] if result[0] else self._get_fallback_context(query)
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return self._get_fallback_context(query)
    def detect_task_intent(self, user_input: str) -> bool:
        """Detect if user wants to create/manage tasks"""
        task_keywords = [
            "add task", "create task", "schedule", "remind", "todo",
            "tomorrow", "later", "work", "appointment", "meeting",
            "day later", "afternoon", "morning", "evening",
            "deadline", "due", "plan", "organize"
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in task_keywords)
    
    def extract_task_details(self, user_input: str) -> Dict[str, Any]:
        """Extract task details from natural language"""
        import re
        
        task_data = {
            "name": "",
            "description": user_input,
            "due_date": "unspecified",
            "priority": "medium",
            "category": "general"
        }
        
        user_lower = user_input.lower()
        
        # Extract time references
        time_patterns = {
            "tomorrow": "tomorrow",
            "today": "today", 
            "later": "later today",
            "afternoon": "this afternoon",
            "morning": "tomorrow morning",
            "evening": "this evening"
        }
        
        for pattern, time_ref in time_patterns.items():
            if pattern in user_lower:
                task_data["due_date"] = time_ref
                break
        
        # Extract work/task type
        if "work" in user_lower:
            task_data["category"] = "work"
            task_data["name"] = "Work task"
        elif "meeting" in user_lower:
            task_data["category"] = "meeting"
            task_data["name"] = "Meeting"
        elif "home" in user_lower:
            task_data["category"] = "personal"
            task_data["name"] = "Home task"
        else:
            # Try to extract meaningful task name
            words = user_input.split()
            if len(words) > 2:
                task_data["name"] = " ".join(words[:3])
            else:
                task_data["name"] = "New task"
        
        return task_data
    
    def format_task_response(self, task_data: Dict[str, Any]) -> str:
        """Format a concise task creation response"""
        name = task_data.get("name", "Task")
        due_date = task_data.get("due_date", "unspecified")
        
        responses = [
            f"✅ Got it! I'll help you remember: {name}",
            f"📝 Task noted: {name}",
            f"✅ Added to your list: {name}"
        ]
        
        import random
        response = random.choice(responses)
        
        if due_date != "unspecified":
            response += f" (due: {due_date})"
        
        return response + "."

