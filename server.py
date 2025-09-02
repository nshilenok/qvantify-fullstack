import os
from flask import Flask, send_from_directory, request, jsonify, g
from flask_cors import CORS
import logging

# Import all your existing backend functionality
import openai
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone, timedelta
from llmInterface import LLM
import uuid
import json
import credentials
from database import DB
from topic import topicHandler
from conversationInterface import conversation
import platform

if platform.system() == 'Linux':
    from heartbeat import heartbeat

# Create Flask app that serves both frontend and backend
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
psycopg2.extras.register_uuid()

# Import all your existing functions from app.py
def check_if_user_exists():
    query = "SELECT id,project FROM respondents WHERE id=%s"
    query_params = (g.uuid,)
    results = g.db.query_database_one(query,query_params)
    parameters = (uuid.UUID(g.uuid),uuid.UUID(g.projectId))
    if parameters == results:
        app.logger.info('%s logged in successfully', g.uuid)
        pass
    else:
        app.logger.exception('User not found. Comparing: %s vs %s', parameters, results)
        raise Exception("Sorry, no user found for this project")

def check_if_project_exists():
    query = "SELECT id FROM projects WHERE id=%s"
    query_params = (g.projectId,)
    results = g.db.query_database_one(query,query_params)
    if results:
        app.logger.info('%s project found successfully', g.projectId)
        pass
    else:
        app.logger.exception('%s project not found', g.projectId)
        raise Exception("Sorry, no project found")

@app.before_request
def before_request():
    if request.path.startswith('/api/'):
        g.db = DB(credentials.db_config)
        try:
            g.uuid = request.headers.get('externalId')
            g.projectId = request.headers.get('projectId')
            if g.uuid and g.projectId:
                check_if_user_exists()
                check_if_project_exists()
        except Exception as e:
            return jsonify({'error': str(e)}), 401

# Frontend routes - serve React app
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path.startswith('api/'):
        return  # Let API routes handle this
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Backend API routes (with /api prefix)
@app.route('/api/respondent/', methods=['POST'])
def createRespondent():
    data = request.get_json()
    email = data.get('email')
    consent = data.get('consent')
    
    query = "INSERT INTO respondents (id, project, email, consent) VALUES (%s, %s, %s, %s)"
    query_params = (g.uuid, g.projectId, email, consent)
    g.db.query_database_insert(query, query_params)
    
    return jsonify({'success': True})

@app.route('/api/project/', methods=['GET'])
def getProject():
    query = "SELECT * FROM projects WHERE id = %s"
    query_params = (g.projectId,)
    result = g.db.query_database_one(query, query_params)
    return jsonify(result)

@app.route('/api/reply/', methods=['POST'])
def createReply():
    data = request.get_json()
    message = data.get('message')
    
    convo = conversation()
    response = convo.getReply(message)
    
    return jsonify({'reply': response})

@app.route('/api/interview/', methods=['GET'])
def startInterview():
    first_answer = request.args.get('first_answer')
    
    query = "INSERT INTO interviews (respondent, project, first_answer, timestamp) VALUES (%s, %s, %s, %s) RETURNING id"
    query_params = (g.uuid, g.projectId, first_answer, datetime.now(timezone.utc))
    interview_id = g.db.query_database_one(query, query_params)
    
    return jsonify({'interview_id': interview_id, 'status': 'started'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
