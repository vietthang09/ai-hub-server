from flask import Blueprint, request, jsonify
import google.generativeai as genai

# Configure Gemini API key (replace with your actual key or use env variable)
GENAI_API_KEY = "AIzaSyDEA-O194a5vkYGFV1Q-DdqQTL041-L2cg"
genai.configure(api_key=GENAI_API_KEY)

gemini_bp = Blueprint('gemini', __name__)

def build_prompt(title):
	return f"""
You are an expert news content strategist. Given the news title: '{title}', suggest:
1. Meta description (max 160 chars)
2. Keywords (comma separated)
3. Tags (comma separated)
4. Categories (comma separated)
5. Content framework: Return this as HTML suitable for SunEditor in React, but do NOT include a full HTML structure. Only use <h2>, <h3>, <h4>, <p>, <ul>, <li> tags as appropriate. Do not include <html>, <body>, <head>, or <h1> tags. Focus on section headings and content blocks for the article outline.
Return your answer in JSON format with keys: meta_description, keywords, tags, categories, content_framework.
"""

@gemini_bp.route('/seo/suggestions', methods=['POST'])
def gemini_suggestions():
	data = request.get_json()
	title = data.get('title')
	if not title:
		return jsonify({'error': 'Missing title'}), 400
	prompt = build_prompt(title)
	try:
		model = genai.GenerativeModel('models/gemini-1.5-flash')
		response = model.generate_content(prompt)
		# Try to extract JSON from response
		import re, json
		match = re.search(r'\{.*\}', response.text, re.DOTALL)
		if match:
			suggestions = json.loads(match.group())
			return jsonify(suggestions)
		else:
			return jsonify({'error': 'Could not parse Gemini response', 'raw': response.text}), 500
	except Exception as e:
		return jsonify({'error': str(e)}), 500
