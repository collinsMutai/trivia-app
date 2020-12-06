import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# categories
def paginate_categories(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    categories = [category.format() for category in selection]
    current_categories = categories[start:end]

    return current_categories

    # questions


#  INSERT INTO questions (question, answer, category, difficulty) VALUES ('QUIZ 1', 'ANSWER TO QUIZ 1', 'SCIENCE', '1');


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
  
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  """
    # curl -X GET http://127.0.0.1:5000/categories?page=1000
    @app.route("/categories")
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = paginate_categories(request, selection)

        if len(current_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": current_categories,
                "total_categories": len(Category.query.all()),
            }
        )

    """
    
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  """
    # curl -X GET http://127.0.0.1:5000/questions?page=1000
    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
            }
        )

    """
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """
    # curl -X DELETE http://127.0.0.1:5000/questions/1
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  """
    # curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":"Question 3", "answer":"Answer to quiz 3", "category": "Tech", "difficulty":"3"}'
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """
    # curl http://localhost:5000/questions/search -X POST  -H "Content-Type: application/json"  -d '{"query" : { "category": "Tech" }}'
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()

        search = body.get("search", None)

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.category.ilike("%{}%".format(search))
            )

            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """
    # curl -X GET http://127.0.0.1:5000/categories -H "Content-Type: application/json"  -d  '{"query" : { "category": "2" }}'
    @app.route("/questions/<int:category_id>", methods=["GET"])
    def get_categories(category_id):
        body = request.get_json()

        try:

            selection = Question.query.filter(
                Question.category == str(category_id)
            ).all()

            if selection is None:
                abort(404)

            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "categories": current_questions,
                    "total_categories": len(Category.query.all()),
                }
            )

        except:
            abort(400)

    """
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  """

    @app.route("/quizzes", methods=["GET"])
    def play_quiz():
        body = request.get_json()

        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get("quiz_category", None)

        try:
            if quiz_category:
                if quiz_category["id"] == 0:
                    quiz = Question.query.all()
                else:
                    quiz = Question.query.filter_by(category=quiz_category["id"]).all()
            if not quiz:
                return abort(422)
            selected = []
            for question in quiz:
                if question.id not in previous_questions:
                    selected.append(question.format())
            if len(selected) != 0:
                result = random.choice(selected)
                return jsonify({"question": result})
            else:
                return jsonify({"question": False})
        except:
            abort(404)

    """
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  
  """
    # 404 Not found
    # curl -X GET http://127.0.0.1:5000/questions?page=10
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource Not found"}),
            404,
        )

    # 422 Unprocessable

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    # 400 Bad Request
    # curl -X GET http://127.0.0.1:5000/categories/2
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400

    # 405 Method Not Allowed
    # curl http://127.0.0.1:5000/questions/7 -X POST -H "Content-Type: application/json" -d '{"question":"Question 5", "answer":"Answer to quiz 5", "category": "Travel", "difficulty":"8"}'
    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    return app
