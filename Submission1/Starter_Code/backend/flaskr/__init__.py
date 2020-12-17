import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from random import choice

from models import setup_db, Question, Category

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"*": {"origins": '*'}}) 

  

  def paginate_questions(request, selection):
    QUESTIONS_PER_PAGE = 10
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    #response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response



  @app.route('/questions/<int:page>', methods=['GET'])
  def retrieve_specific_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.id).all()
    formated_categories = {category.id: category.type for category in categories}

    if len(current_questions) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': formated_categories,
        'current_category': None
    })

  @app.route('/questions', methods=['GET'])
  def retrieve_questions():

    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.id).all()
    formated_categories = {category.id: category.type for category in categories}

    if len(current_questions) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': formated_categories,
        'current_category': None
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
          'success': True,
          'deleted': question_id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty',None)
    search = body.get('searchTerm', None)

    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        current_questions =paginate_questions(request,selection)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection.all()),
          'current_category': None
        })


      else:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })

    except:
      abort(422)

  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def retrieve_questions_by_category(cat_id):
    selection = Question.query.filter(Question.category == cat_id).all()
    current_questions = paginate_questions(request, selection)
    category = Category.query.filter(Category.id == cat_id).first()
    formated_category = {category.id: category.type}

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'current_category': formated_category
      })

  @app.route('/categories', methods=['GET'])
  def retrieve_categories():

    categories = Category.query.order_by(Category.id).all()
    formated_categories = {category.id: category.type for category in categories}


    if len(categories) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'categories': formated_categories
    })

  @app.route('/quizzes', methods=['POST'])
  def retrieve_quiz():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    print(quiz_category)
    i=0
    for previous_question in previous_questions:
      previous_questions[i] = str(previous_question)
      i += 1


    if not previous_questions:
      if quiz_category['id'] == 0:
        question = choice(Question.query.all())
      else:
        question = choice(Question.query.filter(Question.category == quiz_category['id']).all())
    else:
      if quiz_category['id'] == 0:
        question = choice(Question.query.filter(~Question.id.in_(previous_questions)).all())
      else:
        question = choice(Question.query.filter(Question.category == quiz_category['id']).filter(~Question.id.in_(previous_questions)).all())

    formated_question = question.format()

    if len(formated_question) == 0:
        abort(404)

    return jsonify({
      'success': True,
      'category': quiz_category,
      'question': formated_question,
      'previousQuestions': previous_questions
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "bad request"
      }), 400

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False, 
          "error": 500,
          "message": "internal server error"
      }), 500



  return app

    