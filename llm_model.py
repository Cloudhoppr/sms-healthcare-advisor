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
        **kwargs
    ) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature (lower = more focused)
            top_p: Nucleus sampling parameter
            num_return_sequences: Number of sequences to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
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
        """Generate using pipeline API."""
        results = self.pipeline(
            prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            **kwargs
        )
        
        if num_return_sequences == 1:
            generated_text = results[0]["generated_text"]
            # Remove the prompt from the response
            if generated_text.startswith(prompt):
                return generated_text[len(prompt):].strip()
            return generated_text.strip()
        else:
            return [result["generated_text"][len(prompt):].strip() for result in results]
    
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
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
        return generated_text.strip()


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
        self.system_prompt = system_prompt or (
            "You are a helpful healthcare advisor providing general health information. "
            "Always remind users to consult with healthcare professionals for serious concerns. "
            "Be empathetic, clear, and concise in your responses."
        )
    
    def get_advice(self, user_message: str, context: Optional[List[str]] = None) -> str:
        """
        Get healthcare advice for a user message.
        
        Args:
            user_message: The user's question or concern
            context: Optional conversation history
            
        Returns:
            Healthcare advice response
        """
        # Build the prompt with system context
        prompt = f"{self.system_prompt}\n\n"
        
        # Add conversation history if provided
        if context:
            for msg in context[-3:]:  # Keep last 3 messages for context
                prompt += f"User: {msg}\n"
        
        prompt += f"User: {user_message}\nAssistant:"
        
        # Generate response
        response = self.llm.generate(
            prompt,
            max_length=300,
            temperature=0.7,
            top_p=0.9
        )
        
        return response.strip()
    
    def process_sms(self, sms_text: str) -> str:
        """
        Process an SMS message and return healthcare advice.
        
        Args:
            sms_text: The SMS message content
            
        Returns:
            Healthcare advice response suitable for SMS
        """
        # Keep SMS responses concise
        response = self.get_advice(sms_text)
        
        # Truncate if too long for SMS (typically 160 characters per message)
        if len(response) > 300:
            response = response[:297] + "..."
        
        return response


if __name__ == "__main__":
    # Example usage
    print("Initializing Healthcare Advisor...")
    advisor = HealthcareAdvisor()
    
    # Example queries
    test_queries = [
        "I have a headache, what should I do?",
        "What are the symptoms of a cold?",
        "How can I improve my sleep?"
    ]
    
    print("\n" + "="*50)
    print("Healthcare Advisor - Example Queries")
    print("="*50 + "\n")
    
    for query in test_queries:
        print(f"User: {query}")
        response = advisor.process_sms(query)
        print(f"Advisor: {response}\n")
        print("-" * 50 + "\n")

