#!/usr/bin/env python3.11
"""
Web interface for UT Registration Checker
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# File to store course configuration
CONFIG_FILE = 'courses.json'

def load_courses():
    """Load course configuration from file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"semester": "", "courses": []}

def save_courses(semester, courses):
    """Save course configuration to file."""
    config = {
        "semester": semester,
        "courses": courses,
        "last_updated": datetime.now().isoformat()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    return config

@app.route('/')
def index():
    """Main page."""
    config = load_courses()
    return render_template('index.html', 
                         semester=config.get('semester', ''),
                         courses=config.get('courses', []))

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get current course configuration."""
    config = load_courses()
    return jsonify(config)

@app.route('/api/courses', methods=['POST'])
def update_courses():
    """Update course configuration."""
    data = request.json
    semester = data.get('semester', '').strip()
    courses = [c.strip() for c in data.get('courses', []) if c.strip()]
    
    if not semester:
        return jsonify({"error": "Semester code is required"}), 400
    
    if not courses:
        return jsonify({"error": "At least one course code is required"}), 400
    
    config = save_courses(semester, courses)
    return jsonify({"success": True, "config": config})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get monitoring status."""
    # This would integrate with the actual monitoring script
    # For now, return a placeholder
    return jsonify({
        "monitoring": False,
        "last_check": None,
        "courses": []
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)

