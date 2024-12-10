from flask import Flask, render_template, request, redirect, url_for, jsonify
import textwrap
import yaml
import logging
from crewai import Agent, Task, Crew

# Pydantic and type handling
from pydantic import BaseModel, Field
from typing import List

# Environment and configuration
from dotenv import load_dotenv
import os

# Load environment variables and set up logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tools and AI configuration
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

class SocialMediaPost(BaseModel):
    platform: str = Field(..., description="Social media platform")
    content: str = Field(..., description="Post content")

class ContentOutput(BaseModel):
    article: str = Field(..., description="Generated article in markdown")
    social_media_posts: List[SocialMediaPost] = Field(..., description="Related social media posts")

# Initialize tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


# Flask app configuration
app = Flask(__name__)


#app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Load configurations safely
def load_yaml_config(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {file_path}: {e}")
        return {}

# Define file paths for YAML configurations
CONFIG_FILES = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

# Load configurations
configs = {config_type: load_yaml_config(file_path) 
           for config_type, file_path in CONFIG_FILES.items()}

# Validate API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")



# Home route

@app.route("/", methods=["GET", "POST"])

#@app.route('/')

def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500

if __name__ == '__main__':
    app.run(debug=True)

# Content creation route
@app.route('/create_content', methods=['POST'])
def create_content():
    try:
        # Input validation
        subject = request.form.get('subject')
        if not subject:
            return render_template('error.html', message="Subject is required"), 400

        # Initialize Agents with error checking
        try:
            agents_config = configs.get('agents', {})
            tasks_config = configs.get('tasks', {})

            news_retriever_agent = Agent(
                config=agents_config.get('news_retriever_agent', {}), 
                tools=[search_tool, scrape_tool], 
                llm="openai/gpt-4o"
            )
            summarizer_agent = Agent(
                config=agents_config.get('summarizer_agent', {}), 
                tools=[search_tool, scrape_tool], 
                llm="openai/gpt-4o"
            )
            content_creator_agent = Agent(
                config=agents_config.get('content_creator_agent', {}), 
                tools=[search_tool, scrape_tool], 
                llm="openai/gpt-4o"
            )
            socialpost_creator_agent = Agent(
                config=agents_config.get('social_media_posts_agent', {}), 
                tools=[search_tool, scrape_tool], 
                llm="openai/gpt-4o"
            )

            # Initialize Tasks
            retrieve_news_task = Task(
                config=tasks_config.get('retrieve_news', {}), 
                agent=news_retriever_agent
            )
            summarize_news_task = Task(
                config=tasks_config.get('summarize_news', {}), 
                agent=summarizer_agent
            )
            create_content_task = Task(
                config=tasks_config.get('create_content', {}), 
                agent=content_creator_agent
            )
            create_socialpost_task = Task(
                config=tasks_config.get('generate_social_media_posts', {}), 
                agent=socialpost_creator_agent
            )

            # Setup Crew to execute tasks
            content_creation_crew = Crew(
                agents=[
                    news_retriever_agent, 
                    summarizer_agent, 
                    content_creator_agent, 
                    socialpost_creator_agent
                ],
                tasks=[
                    retrieve_news_task, 
                    summarize_news_task, 
                    create_content_task, 
                    create_socialpost_task
                ],
                verbose=False  # Set to False in production
            )

            # Execute tasks
            result = content_creation_crew.kickoff(inputs={'subject': subject})

            # Process output
            article = result.get('article', 'No article generated')
            social_media_posts = result.get('social_media_posts', [])

            # Format posts
            formatted_posts = [
                {
                    'platform': post.get('platform', 'Unknown'),
                    'content': textwrap.fill(post.get('content', ''), width=50)
                } 
                for post in social_media_posts
            ]

            # Render result
            return render_template(
                'result.html', 
                article=article, 
                social_media_posts=formatted_posts
            )

        except Exception as agent_error:
            logger.error(f"Error in agent setup or execution: {agent_error}")
            return render_template('error.html', message="Failed to create content"), 500

    except Exception as e:
        logger.error(f"Unexpected error in content creation: {e}")
        return render_template('error.html', message="An unexpected error occurred"), 500

# Add error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    # Ensure this is only for local development
    if os.getenv('FLASK_ENV', 'development') == 'development':
        app.run(debug=False)  # Keep debug off even in development
    else:
        # In production, you'd use a WSGI server like gunicorn
        logger.warning("This script should not be run directly in production.")
