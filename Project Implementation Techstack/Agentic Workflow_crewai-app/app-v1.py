import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from crewai import Crew, Agent, Task, Process
#from langchain.llms import OpenAI
from langchain_openai import OpenAI

#from langchain_community import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI
llm = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY', ''),
    temperature=0.7
)

class NewsProcessingCrew:
    def __init__(self, topic):
        self.topic = topic
        self.setup_agents()
        self.setup_tasks()
        self.create_crew()

    def setup_agents(self):
        # News Retriever Agent
        self.news_retriever = Agent(
            role='News Retriever',
            goal=f'Find the most recent and relevant news articles about {self.topic}',
            backstory='An expert researcher skilled at finding credible news sources',
            verbose=True,
            llm=llm
        )

        # News Summarizer Agent
        self.news_summarizer = Agent(
            role='News Summarizer',
            goal='Create concise and informative summaries of retrieved news articles',
            backstory='A linguistic expert who can distill complex news into clear, digestible summaries',
            verbose=True,
            llm=llm
        )

        # Content Creator Agent
        self.content_creator = Agent(
            role='Content Creator',
            goal='Generate engaging and well-structured news content',
            backstory='A creative writer who transforms news summaries into compelling narratives',
            verbose=True,
            llm=llm
        )

    def setup_tasks(self):
        # Task to retrieve news
        self.retrieve_news_task = Task(
            description=f'Research and retrieve the latest news articles about {self.topic}',
            agent=self.news_retriever,
            expected_output='A comprehensive list of recent news articles with titles, sources, and key details'
        )

        # Task to summarize news
        self.summarize_news_task = Task(
            description='Summarize the retrieved news articles, highlighting key points and insights',
            agent=self.news_summarizer,
            expected_output='Concise summaries of each news article, capturing the essential information'
        )

        # Task to create content
        self.create_content_task = Task(
            description='Create an engaging and informative article based on the news summaries',
            agent=self.content_creator,
            expected_output='A well-written, comprehensive article that provides context and insight'
        )

    def create_crew(self):
        # Create the crew with sequential process
        self.crew = Crew(
            agents=[
                self.news_retriever, 
                self.news_summarizer, 
                self.content_creator
            ],
            tasks=[
                self.retrieve_news_task, 
                self.summarize_news_task, 
                self.create_content_task
            ],
            verbose=2,
            process=Process.sequential
        )

    def process(self):
        # Run the crew and return results
        return self.crew.kickoff()

@app.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/process_news', methods=['POST'])
def process_news():
    """Process news for a given topic"""
    try:
        # Get topic from form submission
        topic = request.form.get('topic', '')
        
        if not topic:
            return jsonify({
                'error': 'No topic provided',
                'status': 'error'
            }), 400
        
        # Create and run the news processing crew
        news_crew = NewsProcessingCrew(topic)
        results = news_crew.process()
        
        return jsonify({
            'status': 'success',
            'topic': topic,
            'results': results
        })
    
    except Exception as e:
        app.logger.error(f"Error processing news: {str(e)}")
        return jsonify({
            'error': 'Failed to process news',
            'details': str(e),
            'status': 'error'
        }), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """API endpoint to retrieve news for a given topic"""
    topic = request.args.get('topic', '')
    
    if not topic:
        return jsonify({
            'error': 'No topic provided',
            'status': 'error'
        }), 400
    
    try:
        # Create and run the news processing crew
        news_crew = NewsProcessingCrew(topic)
        results = news_crew.process()
        
        return jsonify({
            'status': 'success',
            'topic': topic,
            'results': results
        })
    except Exception as e:
        app.logger.error(f"Error retrieving news: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve news',
            'details': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
