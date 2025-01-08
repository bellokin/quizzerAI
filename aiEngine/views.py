import os
import json
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List

# Load environment variables from .env file
load_dotenv()

# Define the Pydantic model for the expected JSON structure
class GeneratedQuestions(BaseModel):
    questions: List[str]

# Initialize Groq LLM (LLaMA via ChatGroq)
groq_llama3_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=os.environ.get("GROQ_API_KEY"),
)

# Define the output parser using the Pydantic model
parser = JsonOutputParser(pydantic_object=GeneratedQuestions)

# Create a prompt template for generating multiple-choice questions
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Generate 10 multiple-choice questions based on the article below in JSON format. "
     "The JSON should have a single field 'questions', which contains a list of dictionaries. "
     "Each dictionary should represent a question with the following keys: "
     "- 'question': The question text. "
     "- 'choices': A list of strings representing the choices (e.g., ['A) option1', 'B) option2', ...]). "
     "- 'correct_answer': The correct answer choice as a letter (e.g., 'A', 'B', 'C', 'D')."
     "Ensure that all questions follow this format and the answers are clearly indicated."
    ),
    ("user", "{input}")
])


# Create the chain that guarantees JSON output
chain = prompt | groq_llama3_llm | parser

# Example index view
def index(request):
    return JsonResponse({'message': 'AI Load App is working!'})

# View to take in an article and generate questions
@csrf_exempt
 
def take_in_article(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data for the article
            data = json.loads(request.body)
            article = data.get('article', '')

            if not article:
                return JsonResponse({'error': 'Article content is required.'}, status=400)

            # Use Groq to generate questions based on the article
            result_raw = chain.invoke({"input": article})

            # Validate and parse the output
            if isinstance(result_raw, dict) and 'questions' in result_raw:
                generated_questions = result_raw['questions']
            else:
                return JsonResponse({
                    'error': 'Invalid JSON output from LLM. Missing "questions" key.',
                    'details': result_raw,  # Include the raw result for debugging
                }, status=500)

            # Return the generated questions
            return JsonResponse({'generated_questions': generated_questions}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request.'}, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'details': 'There was an issue processing your request.',
            }, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)
