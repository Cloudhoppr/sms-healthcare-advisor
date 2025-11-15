"""
Hugging Face LLM Model Integration for SMS Healthcare Advisor
"""
import os
from typing import Optional, List, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch


class HealthcareLLM:
    """
    A wrapper class for Hugging Face LLM models optimized for healthcare advice.
    """
    
    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-medium",
        device: Optional[str] = None,
        use_pipeline: bool = True
    ):
        """
        Initialize the Healthcare LLM model.
        
        Args:
            model_name: Hugging Face model identifier
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
            use_pipeline: Whether to use the transformers pipeline API
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.use_pipeline = use_pipeline
        
        print(f"Loading model: {model_name}")
        print(f"Using device: {self.device}")
        
        if use_pipeline:
            self._load_pipeline()
        else:
            self._load_model()
    
    def _load_pipeline(self):
        """Load model using the transformers pipeline API."""
        self.pipeline = pipeline(
            "text-generation",
            model=self.model_name,
            tokenizer=self.model_name,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        )
        self.tokenizer = self.pipeline.tokenizer
    
    def _load_model(self):
        """Load model and tokenizer separately."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        )
        
        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate(
        self,
        prompt: str,
        max_length: int = 200,
        temperature: float = 0.7,
        top_p: float = 0.9,
        num_return_sequences: int = 1,
        max_new_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
       
        # Pass max_new_tokens through kwargs if provided
        if max_new_tokens is not None:
            kwargs['max_new_tokens'] = max_new_tokens
            
        if self.use_pipeline:
            return self._generate_with_pipeline(
                prompt, max_length, temperature, top_p, num_return_sequences, **kwargs
            )
        else:
            return self._generate_with_model(
                prompt, max_length, temperature, top_p, num_return_sequences, **kwargs
            )
    
    def _generate_with_pipeline(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        top_p: float,
        num_return_sequences: int,
        **kwargs
    ) -> str:
        # Extract repetition_penalty and max_new_tokens from kwargs if provided
        repetition_penalty = kwargs.pop('repetition_penalty', 1.0)
        max_new_tokens = kwargs.pop('max_new_tokens', None)
        
        # Use max_new_tokens if provided, otherwise calculate from max_length
        if max_new_tokens is None:
            # Estimate tokens in prompt and use remaining for generation
            prompt_tokens = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            max_new_tokens = min(300, max(50, max_length - prompt_tokens))
        
        results = self.pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=repetition_penalty,
            truncation=True,
            **kwargs
        )
        
        if num_return_sequences == 1:
            generated_text = results[0]["generated_text"]
            # Remove the prompt from the response
            if generated_text.startswith(prompt):
                response = generated_text[len(prompt):].strip()
            else:
                # If prompt doesn't match exactly, try to find where the new content starts
                response = generated_text.strip()
            return response if response else "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        else:
            return [result["generated_text"][len(prompt):].strip() if result["generated_text"].startswith(prompt) else result["generated_text"].strip() for result in results]
    
    def _generate_with_model(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        top_p: float,
        num_return_sequences: int,
        **kwargs
    ) -> str:
        """Generate using model directly."""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = inputs.to(self.device)
        
        # Extract repetition_penalty and max_new_tokens from kwargs if provided
        repetition_penalty = kwargs.pop('repetition_penalty', 1.0)
        max_new_tokens = kwargs.pop('max_new_tokens', None)
        
        generate_kwargs = {
            'temperature': temperature,
            'top_p': top_p,
            'num_return_sequences': num_return_sequences,
            'do_sample': True,
            'pad_token_id': self.tokenizer.eos_token_id,
            'repetition_penalty': repetition_penalty,
        }
        
        # Use max_new_tokens if provided, otherwise use max_length
        if max_new_tokens is not None:
            generate_kwargs['max_new_tokens'] = max_new_tokens
        else:
            generate_kwargs['max_length'] = max_length
        
        generate_kwargs.update(kwargs)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                **generate_kwargs
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response
        if generated_text.startswith(prompt):
            response = generated_text[len(prompt):].strip()
        else:
            response = generated_text.strip()
        return response if response else "I apologize, but I couldn't generate a response. Please try rephrasing your question."


class HealthcareAdvisor:
    """
    Healthcare advisor that uses an LLM to provide medical advice via SMS.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the healthcare advisor.
        
        Args:
            model_name: Hugging Face model name (defaults to a suitable model)
            system_prompt: System prompt to guide the model's responses
        """
        # Default to a model suitable for conversational healthcare advice
        if model_name is None:
            # Using a general conversational model - you can change this
            model_name = "microsoft/DialoGPT-medium"
        
        self.llm = HealthcareLLM(model_name=model_name)
        
        # Default system prompt for healthcare advisor
        # Simplified for DialoGPT which works better with conversational prompts
        self.system_prompt = system_prompt or (
            "You are a helpful healthcare advisor. Provide detailed, informative answers about health topics. "
            "When asked about symptoms, list them clearly. Be specific and helpful."
        )
        
        # Knowledge base for common healthcare questions
        self.knowledge_base = {
            'cold': {
                'symptoms': [
                    'Runny or stuffy nose',
                    'Sneezing',
                    'Sore throat',
                    'Coughing',
                    'Congestion',
                    'Mild headache',
                    'Fatigue or tiredness',
                    'Mild body aches',
                    'Low-grade fever (sometimes)'
                ],
                'description': 'A common cold is a viral infection of your upper respiratory tract (nose and throat).',
                'keywords': ['runny nose', 'stuffy nose', 'sneezing', 'sore throat', 'cough', 'congestion', 'mild headache', 'fatigue', 'tired', 'body ache', 'low fever'],
                'next_steps': [
                    'Rest and stay hydrated',
                    'Use over-the-counter cold medications for symptom relief',
                    'Gargle with warm salt water for sore throat',
                    'Use a humidifier to ease congestion',
                    'Get plenty of sleep',
                    'Wash hands frequently to prevent spreading',
                    'See a doctor if symptoms worsen or persist beyond 10 days'
                ]
            },
            'flu': {
                'symptoms': [
                    'Fever or feeling feverish/chills',
                    'Cough',
                    'Sore throat',
                    'Runny or stuffy nose',
                    'Muscle or body aches',
                    'Headaches',
                    'Fatigue (tiredness)',
                    'Some people may have vomiting and diarrhea (more common in children)'
                ],
                'description': 'Influenza (flu) is a contagious respiratory illness caused by influenza viruses.',
                'keywords': ['fever', 'chills', 'cough', 'sore throat', 'body ache', 'muscle ache', 'headache', 'fatigue', 'vomiting', 'diarrhea', 'nausea'],
                'next_steps': [
                    'Rest and stay home to avoid spreading the virus',
                    'Stay hydrated - drink plenty of fluids',
                    'Take over-the-counter medications for fever and pain (acetaminophen or ibuprofen)',
                    'Consider antiviral medications if started within 48 hours of symptoms',
                    'Monitor for severe symptoms like difficulty breathing',
                    'Seek immediate medical attention if you have trouble breathing, chest pain, or severe dehydration',
                    'Get annual flu vaccination to prevent future infections'
                ]
            },
            'headache': {
                'relief': [
                    'Rest in a quiet, dark room',
                    'Apply a cold or warm compress to your forehead or neck',
                    'Stay hydrated - drink plenty of water',
                    'Take over-the-counter pain relievers (if appropriate for you)',
                    'Practice relaxation techniques',
                    'Get adequate sleep',
                    'Avoid triggers like bright lights, loud noises, or strong smells'
                ],
                'note': 'If headaches are severe, frequent, or accompanied by other symptoms, consult a healthcare professional.',
                'keywords': ['headache', 'head pain', 'migraine', 'throbbing', 'pressure'],
                'next_steps': [
                    'Identify and avoid triggers (stress, certain foods, lack of sleep)',
                    'Apply cold or warm compress',
                    'Take over-the-counter pain relievers as directed',
                    'Practice relaxation techniques or meditation',
                    'Ensure adequate hydration and sleep',
                    'See a doctor if headaches are severe, frequent, or accompanied by vision changes, fever, or neck stiffness'
                ]
            },
            'sleep': {
                'tips': [
                    'Maintain a regular sleep schedule - go to bed and wake up at the same time',
                    'Create a relaxing bedtime routine',
                    'Keep your bedroom cool, dark, and quiet',
                    'Avoid screens (phone, TV, computer) at least 1 hour before bed',
                    'Limit caffeine and alcohol, especially in the evening',
                    'Exercise regularly, but not too close to bedtime',
                    'Avoid large meals before bed',
                    'Manage stress through meditation or relaxation techniques'
                ],
                'description': 'Good sleep hygiene is essential for overall health and well-being.',
                'keywords': ['sleep', 'insomnia', 'sleepless', 'tired', 'fatigue'],
                'next_steps': [
                    'Establish a consistent sleep schedule',
                    'Create a relaxing bedtime routine',
                    'Make your bedroom sleep-friendly (cool, dark, quiet)',
                    'Avoid screens and stimulants before bed',
                    'Consider speaking with a healthcare provider if sleep problems persist'
                ]
            },
            'allergies': {
                'symptoms': [
                    'Sneezing',
                    'Runny or stuffy nose',
                    'Itchy, watery eyes',
                    'Itchy throat or ears',
                    'Postnasal drip',
                    'Coughing'
                ],
                'description': 'Allergies occur when your immune system reacts to a foreign substance.',
                'keywords': ['sneezing', 'itchy eyes', 'watery eyes', 'runny nose', 'stuffy nose', 'allergy', 'allergic', 'pollen', 'dust'],
                'next_steps': [
                    'Avoid known allergens when possible',
                    'Use over-the-counter antihistamines',
                    'Use nasal sprays for congestion',
                    'Consider allergy testing to identify triggers',
                    'Keep windows closed during high pollen seasons',
                    'Use air purifiers in your home',
                    'See an allergist if symptoms are severe or persistent'
                ]
            },
            'stomach_flu': {
                'symptoms': [
                    'Nausea',
                    'Vomiting',
                    'Diarrhea',
                    'Stomach cramps',
                    'Low-grade fever',
                    'Fatigue'
                ],
                'description': 'Gastroenteritis (stomach flu) is inflammation of the stomach and intestines.',
                'keywords': ['nausea', 'nauseous', 'vomiting', 'vomit', 'diarrhea', 'stomach ache', 'stomach pain', 'abdominal pain', 'cramps', 'upset stomach', 'belly ache'],
                'next_steps': [
                    'Stay hydrated with water, clear broths, or electrolyte solutions',
                    'Avoid solid foods until vomiting stops',
                    'Gradually reintroduce bland foods (bananas, rice, applesauce, toast)',
                    'Avoid dairy, caffeine, and alcohol',
                    'Rest as much as possible',
                    'Wash hands frequently to prevent spreading',
                    'Seek medical attention if you have signs of dehydration, severe pain, or symptoms last more than 2-3 days'
                ]
            }
        }
        
        # Conversation context to track symptoms
        self.conversation_context = []
    
    def _extract_symptoms(self, user_message: str) -> List[str]:
        """
        Extract symptoms mentioned in the user's message.
        
        Args:
            user_message: The user's message
            
        Returns:
            List of symptoms mentioned
        """
        message_lower = user_message.lower()
        symptoms = []
        
        # Common symptom keywords
        symptom_keywords = {
            'fever': ['fever', 'temperature', 'hot', 'chills'],
            'cough': ['cough', 'coughing'],
            'sore throat': ['sore throat', 'throat pain', 'throat hurts'],
            'runny nose': ['runny nose', 'dripping nose'],
            'stuffy nose': ['stuffy nose', 'congested', 'congestion', 'blocked nose'],
            'sneezing': ['sneezing', 'sneeze'],
            'headache': ['headache', 'head pain', 'migraine'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak'],
            'body aches': ['body ache', 'muscle ache', 'body pain', 'muscle pain'],
            'nausea': ['nausea', 'nauseous', 'queasy'],
            'vomiting': ['vomiting', 'vomit', 'throwing up'],
            'diarrhea': ['diarrhea', 'loose stools'],
            'stomach pain': ['stomach pain', 'stomach ache', 'abdominal pain', 'belly ache'],
            'itchy eyes': ['itchy eyes', 'watery eyes', 'eye irritation']
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                symptoms.append(symptom)
        
        return symptoms
    
    def _match_symptoms_to_condition(self, symptoms: List[str]) -> Optional[Dict]:
        """
        Match collected symptoms to a condition in the knowledge base.
        
        Args:
            symptoms: List of symptoms mentioned
            
        Returns:
            Dictionary with condition name and match score, or None
        """
        if not symptoms:
            return None
        
        best_match = None
        best_score = 0
        
        for condition_name, condition_data in self.knowledge_base.items():
            if 'keywords' not in condition_data:
                continue
                
            # Count how many symptoms match this condition
            match_count = 0
            condition_keywords = [kw.lower() for kw in condition_data['keywords']]
            
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                # Check if symptom matches any keyword
                # For stomach_flu, prioritize it over flu when GI symptoms are present
                if condition_name == 'stomach_flu':
                    # Stomach flu should match strongly on GI symptoms
                    gi_keywords = ['nausea', 'vomiting', 'diarrhea', 'stomach', 'abdominal', 'cramps']
                    if any(gi_kw in symptom_lower for gi_kw in gi_keywords):
                        match_count += 2  # Give extra weight to GI symptoms for stomach flu
                elif condition_name == 'flu':
                    # Flu should not match strongly on GI symptoms alone
                    gi_keywords = ['nausea', 'vomiting', 'diarrhea', 'stomach', 'abdominal']
                    if any(gi_kw in symptom_lower for gi_kw in gi_keywords):
                        match_count += 0.5  # Reduce weight for GI symptoms in flu
                
                if any(keyword in symptom_lower or symptom_lower in keyword for keyword in condition_keywords):
                    match_count += 1
            
            # Calculate match score (percentage of symptoms that match)
            score = match_count / len(symptoms) if symptoms else 0
            
            # Also consider total number of matches
            if match_count > 0 and (score > best_score or (score == best_score and match_count > best_match.get('match_count', 0) if best_match else True)):
                best_match = {
                    'condition': condition_name,
                    'score': score,
                    'match_count': match_count,
                    'data': condition_data
                }
                best_score = score
        
        # Only return if we have a reasonable match (at least 2 symptoms match or 50% match)
        if best_match and (best_match['match_count'] >= 2 or best_match['score'] >= 0.5):
            return best_match
        
        return None
    
    def _check_knowledge_base(self, user_message: str) -> Optional[str]:
        """
        Check if the user's question matches a topic in our knowledge base.
        
        Args:
            user_message: The user's question
            
        Returns:
            Formatted response from knowledge base, or None if no match
        """
        message_lower = user_message.lower()
        
        # Check for cold-related questions
        if any(word in message_lower for word in ['cold', 'common cold']):
            if any(word in message_lower for word in ['symptom', 'symptoms', 'sign', 'what are']):
                kb = self.knowledge_base['cold']
                response = f"{kb['description']}\n\nCommon symptoms include:\n"
                response += "\n".join(f"- {symptom}" for symptom in kb['symptoms'])
                response += "\n\nNote: If symptoms are severe or persist, please consult a healthcare professional."
                return response
        
        # Check for flu-related questions
        if any(word in message_lower for word in ['flu', 'influenza']):
            if any(word in message_lower for word in ['symptom', 'symptoms', 'sign', 'what are']):
                kb = self.knowledge_base['flu']
                response = f"{kb['description']}\n\nCommon symptoms include:\n"
                response += "\n".join(f"- {symptom}" for symptom in kb['symptoms'])
                response += "\n\nNote: The flu can be serious. If you suspect you have the flu, consult a healthcare professional."
                return response
        
        # Check for headache questions
        if 'headache' in message_lower:
            if any(word in message_lower for word in ['what should', 'what can', 'how to', 'help', 'relief', 'do']):
                kb = self.knowledge_base['headache']
                response = "Here are some ways to help relieve a headache:\n\n"
                response += "\n".join(f"- {tip}" for tip in kb['relief'])
                response += f"\n\n{kb['note']}"
                return response
        
        # Check for sleep questions
        if any(word in message_lower for word in ['sleep', 'insomnia', 'sleepless']):
            if any(word in message_lower for word in ['improve', 'better', 'how', 'tips', 'help']):
                kb = self.knowledge_base['sleep']
                response = f"{kb['description']}\n\nTips to improve your sleep:\n\n"
                response += "\n".join(f"- {tip}" for tip in kb['tips'])
                return response
        
        return None
    
    def get_advice(self, user_message: str, context: Optional[List[str]] = None) -> str:
        """
        Get healthcare advice for a user message.
        
        Args:
            user_message: The user's question or concern
            context: Optional conversation history
            
        Returns:
            Healthcare advice response
        """
        # Update conversation context
        if context is None:
            context = self.conversation_context
        else:
            self.conversation_context = context.copy()
        
        # Add current message to context
        self.conversation_context.append(user_message)
        # Keep only last 5 messages
        if len(self.conversation_context) > 5:
            self.conversation_context = self.conversation_context[-5:]
        
        # First, check if we have a knowledge base answer (for general questions)
        kb_response = self._check_knowledge_base(user_message)
        if kb_response:
            return kb_response
        
        # Extract symptoms from current message and context
        # Only do this if the message seems to be describing symptoms (not asking questions)
        message_lower = user_message.lower()
        is_question = any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', 'tell me', 'explain'])
        
        if not is_question:
            all_symptoms = []
            for msg in self.conversation_context:
                all_symptoms.extend(self._extract_symptoms(msg))
            
            # Remove duplicates while preserving order
            unique_symptoms = []
            seen = set()
            for symptom in all_symptoms:
                if symptom not in seen:
                    unique_symptoms.append(symptom)
                    seen.add(symptom)
            
            # Try to match symptoms to a condition for diagnosis
            if len(unique_symptoms) >= 2:  # Need at least 2 symptoms for diagnosis
                diagnosis_match = self._match_symptoms_to_condition(unique_symptoms)
                
                if diagnosis_match:
                    condition_name = diagnosis_match['condition']
                    condition_data = diagnosis_match['data']
                    
                    # Build diagnosis response
                    response = f"Based on your symptoms ({', '.join(unique_symptoms)}), "
                    response += f"this may indicate a **{condition_name.replace('_', ' ').title()}**.\n\n"
                    response += f"{condition_data['description']}\n\n"
                    
                    if 'symptoms' in condition_data:
                        response += "Your reported symptoms align with:\n"
                        matching_symptoms = [s for s in condition_data['symptoms'] 
                                           if any(kw in s.lower() for kw in [sym.lower() for sym in unique_symptoms])]
                        for symptom in matching_symptoms[:5]:  # Show top 5 matching
                            response += f"- {symptom}\n"
                        response += "\n"
                    
                    if 'next_steps' in condition_data:
                        response += "**Recommended Next Steps:**\n\n"
                        for i, step in enumerate(condition_data['next_steps'], 1):
                            response += f"{i}. {step}\n"
                        response += "\n"
                    
                    response += "**IMPORTANT:** This is not a medical diagnosis. Please consult with a healthcare professional for proper evaluation and treatment, especially if symptoms are severe, worsening, or persist."
                    
                    return response
            
            # If not enough symptoms for diagnosis, check if user is describing symptoms
            if unique_symptoms:
                response = f"I've noted your symptoms: {', '.join(unique_symptoms)}.\n\n"
                response += "To help provide a better assessment, could you tell me:\n"
                response += "- How long have you been experiencing these symptoms?\n"
                response += "- Are there any other symptoms you're experiencing?\n"
                response += "- How severe are these symptoms (mild, moderate, severe)?\n\n"
                response += "With more information, I can provide a more accurate assessment and next steps."
                return response
        
        # If no knowledge base match, use the LLM
        # Build prompt in a format DialoGPT understands better
        # DialoGPT was trained on Reddit conversations, so use a simple conversational format
        prompt_parts = []
        
        # Add system context at the start (but keep it brief)
        prompt_parts.append(self.system_prompt)
        
        # Add conversation history if provided
        if context:
            for msg in context[-3:]:
                prompt_parts.append(f"User: {msg}")
                prompt_parts.append("Assistant: [provides helpful health information]")
        
        # Add current question with a more direct prompt
        prompt_parts.append(f"User: {user_message}")
        
        # For questions about symptoms/conditions, add a hint
        if any(word in user_message.lower() for word in ['symptom', 'symptoms', 'sign', 'signs', 'what are', 'tell me about']):
            prompt_parts.append("Assistant: Common symptoms include:")
        else:
            prompt_parts.append("Assistant:")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate with parameters optimized for longer, more descriptive responses
        response = self.llm.generate(
            prompt,
            max_length=600,
            max_new_tokens=250,
            temperature=0.8,  # Higher temperature for more varied, natural responses
            top_p=0.95,      # Higher top_p for better coverage
            repetition_penalty=1.15
        )
        
        # Clean up the response
        response = response.strip()
        
        # If response is still too short, try one more time with even more permissive settings
        if len(response) < 30:
            response = self.llm.generate(
                prompt,
                max_length=600,
                max_new_tokens=200,
                temperature=0.9,
                top_p=0.98,
                repetition_penalty=1.1
            ).strip()
        
        # Final fallback if LLM still fails
        if not response or len(response) < 20:
            return "I understand you're asking about health information. For detailed medical advice, please consult with a healthcare professional. If you have questions about common conditions like colds, flu, headaches, or sleep, I can provide general information."
        
        return response
    
    def process_sms(self, sms_text: str) -> str:
        """
        Process an SMS message and return healthcare advice.
        
        Args:
            sms_text: The SMS message content
            
        Returns:
            Healthcare advice response suitable for SMS
        """
        # Get detailed advice
        response = self.get_advice(sms_text)
        
        # For SMS, we want descriptive but still manageable length
        # Modern SMS can handle longer messages, but keep it reasonable
        # Truncate only if extremely long (SMS can be up to 1600 chars, but we'll cap at 500)
        if len(response) > 500:
            # Try to truncate at a sentence boundary
            truncated = response[:497]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            cut_point = max(last_period, last_newline)
            if cut_point > 400:  # Only use sentence boundary if it's not too short
                response = truncated[:cut_point + 1] + "..."
            else:
                response = truncated + "..."
        
        return response


if __name__ == "__main__":
    # Example usage
    print("Initializing Healthcare Advisor...")
    advisor = HealthcareAdvisor()
    
    print("\n" + "="*70)
    print("Healthcare Advisor - Diagnosis & Next Steps Demo")
    print("="*70 + "\n")
    
    # Demo 1: Conversation flow with symptoms leading to diagnosis
    print("=" * 70)
    print("DEMO 1: Symptom-based Diagnosis")
    print("=" * 70 + "\n")
    
    conversation1 = [
        "I've been feeling really tired and have a runny nose",
        "I also have a cough and my throat is sore",
        "I think I might have a fever too"
    ]
    
    for i, query in enumerate(conversation1, 1):
        print(f"User (Message {i}): {query}")
        response = advisor.get_advice(query)
        print(f"\nAdvisor: {response}\n")
        print("-" * 70 + "\n")
    
    # Reset for next demo
    advisor.conversation_context = []
    
    # Demo 2: Another conversation flow
    print("\n" + "=" * 70)
    print("DEMO 2: Stomach Flu Symptoms")
    print("=" * 70 + "\n")
    
    conversation2 = [
        "I've been feeling nauseous",
        "I've been vomiting and have diarrhea",
        "My stomach really hurts"
    ]
    
    for i, query in enumerate(conversation2, 1):
        print(f"User (Message {i}): {query}")
        response = advisor.get_advice(query)
        print(f"\nAdvisor: {response}\n")
        print("-" * 70 + "\n")
    
    # Reset for next demo
    advisor.conversation_context = []
    
    # Demo 3: Single symptom (not enough for diagnosis)
    print("\n" + "=" * 70)
    print("DEMO 3: Single Symptom (Asks for More Info)")
    print("=" * 70 + "\n")
    
    print("User: I have a headache")
    response = advisor.get_advice("I have a headache")
    print(f"\nAdvisor: {response}\n")
    print("-" * 70 + "\n")
    
    # Demo 4: Traditional queries still work
    print("\n" + "=" * 70)
    print("DEMO 4: General Health Questions")
    print("=" * 70 + "\n")
    
    test_queries = [
        "What are the symptoms of a cold?",
        "How can I improve my sleep?"
    ]
    
    for query in test_queries:
        print(f"User: {query}")
        response = advisor.process_sms(query)
        print(f"\nAdvisor: {response}\n")
        print("-" * 70 + "\n")

