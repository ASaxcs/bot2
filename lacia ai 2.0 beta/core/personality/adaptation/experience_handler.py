"""
Experience Handler untuk sistem adaptasi Lacia AI
Menangani pengalaman dan pembelajaran dari interaksi
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Experience:
    """Struktur data untuk menyimpan pengalaman"""
    timestamp: str
    interaction_type: str
    context: Dict[str, Any]
    user_input: str
    ai_response: str
    user_feedback: Optional[str] = None
    emotion_state: Optional[str] = None
    success_rate: float = 0.0
    learning_points: List[str] = None
    # Note: id akan di-generate otomatis, tidak diterima sebagai parameter

    def __post_init__(self):
        if self.learning_points is None:
            self.learning_points = []

class ExperienceHandler:
    """Menangani penyimpanan dan analisis pengalaman untuk pembelajaran"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with config dictionary instead of direct path"""
        # Extract data path from config or use default
        data_config = config.get("data", {})
        data_path = data_config.get("experiences_path", "data/experiences.json")
        
        self.data_path = Path(data_path)
        self.config = config
        self.experiences: List[Experience] = []
        self.load_experiences()
    
    def load_experiences(self):
        """Memuat pengalaman dari file"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Safe experience loading - remove 'id' if present
                    safe_experiences = []
                    for exp in data:
                        # Remove 'id' key if it exists
                        exp_copy = exp.copy()
                        exp_copy.pop('id', None)  # Remove id safely
                        safe_experiences.append(Experience(**exp_copy))
                    self.experiences = safe_experiences
                print(f"✅ Loaded {len(self.experiences)} experiences from {self.data_path}")
            else:
                print(f"📝 No existing experiences file found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading experiences: {e}")
            self.experiences = []
    
    def save_experiences(self):
        """Menyimpan pengalaman ke file"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(exp) for exp in self.experiences], f, 
                         indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving experiences: {e}")
    
    def record_experience(self, experience_data: Dict[str, Any]) -> Experience:
        """Record a new experience from interaction data"""
        # Extract relevant information from experience_data
        user_input = experience_data.get('input', '')
        ai_response = experience_data.get('response', '')
        context = experience_data.get('context', {})
        
        # Determine interaction type based on input analysis
        interaction_type = self._determine_interaction_type(user_input)
        
        # Extract emotion state if available
        emotion_state = None
        if 'emotion' in context:
            emotion_data = context['emotion']
            emotion_state = emotion_data.get('current_mood', 'neutral')
        
        # Calculate success rate (simplified for now)
        success_rate = self._calculate_success_rate(user_input, ai_response, context)
        
        return self.add_experience(
            interaction_type=interaction_type,
            context=context,
            user_input=user_input,
            ai_response=ai_response,
            emotion_state=emotion_state,
            success_rate=success_rate
        )
    
    def _determine_interaction_type(self, user_input: str) -> str:
        """Determine the type of interaction based on user input"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['?', 'what', 'how', 'why', 'when', 'where']):
            return "question_answer"
        elif any(word in user_input_lower for word in ['create', 'write', 'generate', 'make']):
            return "creative_task"
        elif any(word in user_input_lower for word in ['help', 'assist', 'support']):
            return "assistance_request"
        elif any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'goodbye', 'bye']):
            return "greeting"
        else:
            return "general_conversation"
    
    def _calculate_success_rate(self, user_input: str, ai_response: str, context: Dict[str, Any]) -> float:
        """Calculate a basic success rate for the interaction"""
        # Simple heuristic based on response length and context
        base_score = 0.5
        
        # Longer responses might indicate more detailed help
        if len(ai_response) > 100:
            base_score += 0.2
        
        # If response contains helpful keywords
        helpful_keywords = ['here', 'help', 'solution', 'answer', 'explain']
        if any(keyword in ai_response.lower() for keyword in helpful_keywords):
            base_score += 0.2
        
        # If emotional state is positive
        if context.get('emotion', {}).get('current_mood') in ['joy', 'excitement']:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def add_experience(self, interaction_type: str, context: Dict[str, Any],
                      user_input: str, ai_response: str, 
                      user_feedback: Optional[str] = None,
                      emotion_state: Optional[str] = None,
                      success_rate: float = 0.0) -> Experience:
        """Menambah pengalaman baru"""
        experience = Experience(
            timestamp=datetime.datetime.now().isoformat(),
            interaction_type=interaction_type,
            context=context,
            user_input=user_input,
            ai_response=ai_response,
            user_feedback=user_feedback,
            emotion_state=emotion_state,
            success_rate=success_rate
        )
        
        # Ekstrak poin pembelajaran
        experience.learning_points = self._extract_learning_points(experience)
        
        self.experiences.append(experience)
        
        # Save periodically (every 10 experiences) to avoid too frequent I/O
        if len(self.experiences) % 10 == 0:
            self.save_experiences()
        
        return experience
    
    def _extract_learning_points(self, experience: Experience) -> List[str]:
        """Ekstrak poin pembelajaran dari pengalaman"""
        learning_points = []
        
        # Analisis berdasarkan feedback
        if experience.user_feedback:
            if any(word in experience.user_feedback.lower() for word in ["bagus", "good", "great", "excellent"]):
                learning_points.append("positive_response_pattern")
            elif any(word in experience.user_feedback.lower() for word in ["buruk", "bad", "poor", "wrong"]):
                learning_points.append("negative_response_pattern")
        
        # Analisis berdasarkan tipe interaksi
        learning_points.append(f"{experience.interaction_type}_interaction")
        
        # Analisis berdasarkan success rate
        if experience.success_rate > 0.8:
            learning_points.append("high_success_pattern")
        elif experience.success_rate < 0.4:
            learning_points.append("low_success_pattern")
        
        # Analisis berdasarkan emotion state
        if experience.emotion_state:
            learning_points.append(f"emotion_{experience.emotion_state}")
        
        # Analisis berdasarkan panjang respons
        if len(experience.ai_response) > 200:
            learning_points.append("detailed_response")
        elif len(experience.ai_response) < 50:
            learning_points.append("brief_response")
        
        return learning_points
    
    def get_similar_experiences(self, context: Dict[str, Any], 
                              limit: int = 10) -> List[Experience]:
        """Mendapatkan pengalaman serupa berdasarkan konteks"""
        similar = []
        
        for exp in self.experiences:
            similarity_score = self._calculate_similarity(context, exp.context)
            if similarity_score > 0.3:  # Lower threshold for better matching
                similar.append((exp, similarity_score))
        
        # Sort berdasarkan similarity dan ambil yang terbaik
        similar.sort(key=lambda x: x[1], reverse=True)
        return [exp for exp, _ in similar[:limit]]
    
    def _calculate_similarity(self, context1: Dict[str, Any], 
                            context2: Dict[str, Any]) -> float:
        """Menghitung similarity score antara dua konteks"""
        if not context1 or not context2:
            return 0.0
        
        # Compare personality traits if available
        personality_similarity = 0.0
        if 'personality' in context1 and 'personality' in context2:
            p1 = context1['personality']
            p2 = context2['personality']
            common_traits = set(p1.keys()) & set(p2.keys())
            if common_traits:
                trait_matches = sum(1 for trait in common_traits 
                                  if abs(p1[trait] - p2[trait]) < 0.3)
                personality_similarity = trait_matches / len(common_traits)
        
        # Compare emotion states if available
        emotion_similarity = 0.0
        if ('emotion' in context1 and 'emotion' in context2 and
            context1['emotion'].get('current_mood') == context2['emotion'].get('current_mood')):
            emotion_similarity = 1.0
        
        # Combine similarities
        total_similarity = (personality_similarity + emotion_similarity) / 2
        return total_similarity
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Mendapatkan insights dari pengalaman untuk pembelajaran"""
        if not self.experiences:
            return {
                "total_experiences": 0,
                "message": "No experiences recorded yet"
            }
        
        insights = {
            "total_experiences": len(self.experiences),
            "interaction_types": {},
            "success_patterns": {},
            "common_learning_points": {},
            "recent_trends": [],
            "avg_success_rate": 0.0
        }
        
        total_success = 0
        
        # Analisis tipe interaksi
        for exp in self.experiences:
            interaction_type = exp.interaction_type
            if interaction_type not in insights["interaction_types"]:
                insights["interaction_types"][interaction_type] = {
                    "count": 0,
                    "avg_success": 0.0,
                    "total_success": 0.0
                }
            
            insights["interaction_types"][interaction_type]["count"] += 1
            insights["interaction_types"][interaction_type]["total_success"] += exp.success_rate
            total_success += exp.success_rate
        
        # Hitung rata-rata success rate
        for interaction_type in insights["interaction_types"]:
            data = insights["interaction_types"][interaction_type]
            data["avg_success"] = data["total_success"] / data["count"]
            # Remove total_success as it's not needed in final output
            del data["total_success"]
        
        # Overall average success rate
        insights["avg_success_rate"] = total_success / len(self.experiences)
        
        # Analisis learning points
        for exp in self.experiences:
            for point in exp.learning_points:
                if point not in insights["common_learning_points"]:
                    insights["common_learning_points"][point] = 0
                insights["common_learning_points"][point] += 1
        
        # Get recent trends (last 10 experiences)
        recent_experiences = self.experiences[-10:] if len(self.experiences) >= 10 else self.experiences
        recent_success_rates = [exp.success_rate for exp in recent_experiences]
        if recent_success_rates:
            insights["recent_trends"] = {
                "recent_avg_success": sum(recent_success_rates) / len(recent_success_rates),
                "trend": "improving" if len(recent_success_rates) > 1 and 
                        recent_success_rates[-1] > recent_success_rates[0] else "stable"
            }
        
        return insights
    
    def get_experience_count(self) -> int:
        """Get total number of recorded experiences"""
        return len(self.experiences)
    
    def cleanup_old_experiences(self, days_to_keep: int = 30):
        """Membersihkan pengalaman lama"""
        if not self.experiences:
            return
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        original_count = len(self.experiences)
        
        self.experiences = [
            exp for exp in self.experiences 
            if datetime.datetime.fromisoformat(exp.timestamp.replace('Z', '+00:00').replace('+00:00', '')) > cutoff_date
        ]
        
        cleaned_count = original_count - len(self.experiences)
        if cleaned_count > 0:
            print(f"🧹 Cleaned up {cleaned_count} old experiences")
            self.save_experiences()
    
    def __del__(self):
        """Save experiences when object is destroyed"""
        try:
            self.save_experiences()
        except:
            pass  # Ignore errors during cleanup