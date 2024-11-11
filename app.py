from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import openai
from fastapi.middleware.cors import CORSMiddleware

# Replace with your actual OpenAI API key
openai.api_key = "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" # Replace with a valid key

app = FastAPI()

# CORS middleware to allow cross-origin requests from any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoryRequest(BaseModel):
    stories: List[str]

# Global list to store individual responses
individual_responses = []

def get_individual_story_analysis(stories: List[str]) -> List[str]:
    """Processes each story individually, stores the result, and returns separate conversational rewrites."""
    analyses = []
    for story in stories:
        prompt = f"I’ve written a short story: \"{story}\". Please help me rewrite it in a way that feels like I'm telling it in my own words. Keep it natural, personal, and conversational, as if I'm explaining it to someone in a relaxed way."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly assistant helping someone express their thoughts in a personal, conversational style."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500 
            )
            analysis = response.choices[0].message['content']
            analyses.append(analysis)
            individual_responses.append(analysis)  # Store each individual analysis
        except Exception as e:
            print("Error:", e)
            analyses.append("An error occurred while processing the story.")

    return analyses

def get_book_story_analysis() -> str:
    """Merges all stored individual responses and generates a single book-like output."""
    merged_story = " ".join(individual_responses)  # Combine all stored responses into a single text
    prompt = f"I've gathered a collection of stories that I'd like to turn into a cohesive book. Here's the collection: \"{merged_story}\". Please rewrite it in a structured, book-like format that flows naturally from beginning to end."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled writer helping to turn a collection of stories into a well-structured book."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        book_analysis = response.choices[0].message['content']
        return book_analysis
    except Exception as e:
        print("Error:", e)
        return "An error occurred while generating the story book."

def detect_book_request(stories: List[str]) -> bool:
    """Checks if the user's input requests a book generation."""
    book_keywords = ["give me the book", "make it a book", "story book", "create a book", "combine", "merge all"]
    # Check if any story entry matches the book request keywords
    for story in stories:
        if any(keyword in story.lower() for keyword in book_keywords):
            return True
    return False

@app.post("/analyze_story")
async def analyze_story(request: StoryRequest):
    """API endpoint to analyze stories based on detected mode."""
    user_stories = request.stories

    # Detect if the user wants a book based on keywords
    if detect_book_request(user_stories):
        # If book mode is detected, use the stored responses to create a book
        if not individual_responses:
            raise HTTPException(status_code=400, detail="No individual stories found to create a book.")
        book_analysis = get_book_story_analysis()
        return {"book": book_analysis}

    # Otherwise, process stories individually and store each response
    analyses = get_individual_story_analysis(user_stories)
    return {"analyses": analyses}
