# app/services/gemini.py
import google.generativeai as genai
from typing import List, Dict, Optional
from app.config import settings
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    def generate_epics(self, project_context: Dict) -> List[Dict]:
        """Generate epic suggestions based on project context"""
        prompt = f"""
        You are an expert product owner. Based on the following project details, 
        suggest 5-8 epics that would be essential for this application.
        
        Project Type: {project_context.get('app_type')}
        Project Name: {project_context.get('name')}
        Description: {project_context.get('description')}
        Context: {project_context.get('context')}
        
        Return ONLY a JSON array of epics with this structure:
        [
            {{
                "title": "Epic title",
                "description": "Brief description of what this epic covers",
                "suggested_stories": ["Story 1 title", "Story 2 title", "Story 3 title"]
            }}
        ]
        
        Focus on core functionality for a {project_context.get('app_type')} application.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean the response and parse JSON
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Error generating epics: {e}")
            return []
    
    def generate_user_story(self, context: Dict) -> Dict:
        """Generate a detailed user story"""
        prompt = f"""
        You are an expert product owner. Create a detailed user story based on:
        
        Project Type: {context.get('app_type')}
        Project Context: {context.get('project_context')}
        Epic: {context.get('epic_title')}
        Story Title: {context.get('story_title')}
        Additional Context: {context.get('additional_context', '')}
        
        Return ONLY a JSON object with this structure:
        {{
            "user_story": "As a [user type], I want [functionality] so that [benefit]",
            "acceptance_criteria": [
                "Given [context], When [action], Then [outcome]",
                "Additional criteria..."
            ],
            "technical_notes": "Any technical considerations",
            "priority": "high|medium|low",
            "estimated_points": 1-13
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Error generating user story: {e}")
            return {}
    
    def refine_user_story(self, story_data: Dict, feedback: str) -> Dict:
        """Refine an existing user story based on feedback"""
        prompt = f"""
        You are an expert product owner. Refine this user story based on the feedback:
        
        Current User Story: {story_data.get('user_story')}
        Current Acceptance Criteria: {json.dumps(story_data.get('acceptance_criteria'))}
        
        Feedback/Changes Requested: {feedback}
        
        Project Context: {story_data.get('project_context')}
        
        Return ONLY a JSON object with the updated story in the same format:
        {{
            "user_story": "Updated user story...",
            "acceptance_criteria": ["Updated criteria..."],
            "technical_notes": "Updated notes",
            "priority": "high|medium|low",
            "estimated_points": 1-13
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Error refining user story: {e}")
            return {}
        
    async def generate_user_stories(self, epic_title: str, epic_description: str, project_context: str, app_type: str):
        """Generate user stories for a specific epic"""
        
        prompt = f"""
        Create detailed user stories for the following epic in a {app_type} application.
        
        Project Context: {project_context}
        
        Epic: {epic_title}
        Description: {epic_description}
        
        Generate 3-5 user stories that break down this epic into actionable development tasks.
        Each user story should follow the format: "As a [user type], I want [functionality] so that [benefit]"
        
        Return the response as a JSON array with this exact structure:
        [
            {{
                "title": "Brief descriptive title",
                "user_story": "As a [user type], I want [functionality] so that [benefit]",
                "acceptance_criteria": [
                    "Given [context], when [action], then [outcome]",
                    "Given [context], when [action], then [outcome]",
                    "Given [context], when [action], then [outcome]"
                ],
                "priority": "High|Medium|Low",
                "story_points": 1-13
            }}
        ]
        
        Make sure:
        - User stories are specific and actionable
        - Acceptance criteria use Given-When-Then format
        - Story points follow Fibonacci sequence (1, 2, 3, 5, 8, 13)
        - Priority reflects business value and dependencies
        - Stories cover different aspects of the epic
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean up the response text
            response_text = response.text.strip()
            
            # Remove markdown code block markers if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            stories = json.loads(response_text)
            
            return stories
            
        except Exception as e:
            print(f"Error generating user stories: {e}")
            # Return fallback stories if AI generation fails
            return [
                {
                    "title": "Basic Implementation",
                    "user_story": f"As a user, I want to use the {epic_title.lower()} functionality so that I can achieve my goals",
                    "acceptance_criteria": [
                        "Given I am on the application, when I access this feature, then it should work correctly",
                        "Given valid input, when I use this feature, then I should get expected results"
                    ],
                    "priority": "Medium",
                    "story_points": 5
                }
            ]
    
    def test_connection(self) -> bool:
        """Test if Gemini API is working"""
        try:
            response = self.model.generate_content("Say 'API Connected' and nothing else")
            return "Connected" in response.text
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        

# Singleton instance
gemini_service = GeminiService()