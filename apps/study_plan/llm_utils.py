import os
import google.generativeai as genai
from django.conf import settings
import traceback

def initialize_gemini():
    """Initialize Gemini API and models."""
    if not settings.GOOGLE_API_KEY:
        error_msg = "GOOGLE_API_KEY is not set in environment variables. Please add it to your .env file."
        print(error_msg)
        raise ValueError(error_msg)

    try:
        print("Configuring Gemini API...")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        print("Initializing Gemini models...")
        study_model = genai.GenerativeModel('gemini-2.0-flash')
        chatbot_model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
        
        return study_model, chatbot_model
    except Exception as e:
        print(f"Error initializing Gemini: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise

# Initialize models
try:
    study_model, chatbot_model = initialize_gemini()
except Exception as e:
    print(f"Failed to initialize Gemini models: {str(e)}")
    study_model = None
    chatbot_model = None

def generate_study_plan(subject, days, hours, level):
    """Generate a study plan using Gemini model."""
    if not study_model:
        error_msg = "Study plan model not initialized. Check your API key configuration."
        print(error_msg)
        return error_msg

    if not subject or not days or not hours:
        error_msg = "Error: Missing required parameters (subject, days, or hours)"
        print(error_msg)
        return error_msg

    prompts = {
        "beginner": f"You are a helpful study planner for {subject}. Create a beginner plan for {days} days at {hours} hrs/day.",
        "intermediate": f"You are a study planner. Create an intermediate study plan for {subject} over {days} days, {hours} hrs/day.",
        "expert": f"You are a study planner. Create an expert revision plan for {subject} within {days} days, {hours} hrs/day."
    }

    prompt = prompts.get(level.lower(), prompts["beginner"])
    
    try:
        print(f"Generating study plan for subject: {subject}")
        print(f"Parameters - Days: {days}, Hours: {hours}, Level: {level}")
        print(f"Using prompt template for level: {level.lower()}")
        
        response = study_model.generate_content(prompt)
        
        if not response:
            error_msg = "Error: No response received from the model"
            print(error_msg)
            return error_msg
            
        if not hasattr(response, 'text'):
            error_msg = "Error: Invalid response format from the model"
            print(error_msg)
            return error_msg
            
        if not response.text:
            error_msg = "Error: Empty response from the model"
            print(error_msg)
            return error_msg
            
        print(f"Successfully generated study plan: {response.text[:100]}...")
        return response.text
        
    except Exception as e:
        error_msg = f"Error generating study plan: {str(e)}"
        print(error_msg)
        print("Full traceback:")
        print(traceback.format_exc())
        return error_msg

def get_chat_response(user_message, chat_history=None):
    """Get a response from the chatbot using Gemini model."""
    if not chatbot_model:
        error_msg = "Chat model not initialized. Check your API key configuration."
        print(error_msg)
        return error_msg

    try:
        if not user_message:
            error_msg = "Error: Empty message received"
            print(error_msg)
            return error_msg

        print(f"Processing chat message: {user_message[:100]}...")
        
        response = chatbot_model.generate_content(user_message)
        
        if not response:
            error_msg = "Error: No response received from the model"
            print(error_msg)
            return error_msg
            
        if not hasattr(response, 'text'):
            error_msg = "Error: Invalid response format from the model"
            print(error_msg)
            return error_msg
            
        if not response.text:
            error_msg = "Error: Empty response from the model"
            print(error_msg)
            return error_msg
            
        print(f"Successfully generated response: {response.text[:100]}...")
        return response.text
            
    except Exception as e:
        error_msg = f"Error in chat response: {str(e)}"
        print(error_msg)
        print("Full traceback:")
        print(traceback.format_exc())
        return error_msg 