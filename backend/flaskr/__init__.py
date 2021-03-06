# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# ----------------------------------------------------------------------------#
# Questions Pagination.
# ----------------------------------------------------------------------------#


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
    # ----------------------------------------------------------------------------#
    # CORS Headers
    # ----------------------------------------------------------------------------#

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
    # ----------------------------------------------------------------------------#
    # GET Categories.
    # ----------------------------------------------------------------------------#

    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()

        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        formatted_categories = {}

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify(
            {
                "success": True,
                "categories": formatted_categories,
                "total_categories": len(selection),
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
    # ----------------------------------------------------------------------------#
    # GET questions.
    # ----------------------------------------------------------------------------#

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            if len(current_questions) == 0:
                abort(404)

            categories = Category.query.all()

            formatted_categories = {}

            for category in categories:
                formatted_categories[category.id] = category.type

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": formatted_categories[category.id],
                    "categories": formatted_categories,
                }
            )

        except:
            abort(404)

    """
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """
    # ----------------------------------------------------------------------------#
    # DELETE with question_id.
    # ----------------------------------------------------------------------------#

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:

            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    "deleted": question.id,
                    "message": "Successfully deleted!",
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
    # ----------------------------------------------------------------------------#
    # POST new question.
    # ----------------------------------------------------------------------------#

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = request.json.get("question")
        new_answer = request.json.get("answer")
        new_difficulty = request.json.get("difficulty")
        new_category = request.json.get("category")

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "message": "Successfully created",
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(405)

    """
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """
    # ----------------------------------------------------------------------------#
    # Search question with search term.
    # ----------------------------------------------------------------------------#

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()

        search = body.get("searchTerm", "")

        try:
            questions = Question.query.filter(
                Question.question.ilike("%{}%".format(search))
            ).all()

            if not questions:
                abort(404)

            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                }
            )

        except:
            abort(404)

    """
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """
    # ----------------------------------------------------------------------------#
    # GET questions with category_id.
    # ----------------------------------------------------------------------------#

    @app.route("/questions/<int:category_id>", methods=["GET"])
    def get_categories(category_id):
        body = request.get_json()

        try:

            questions = Question.query.filter(Question.category == str(category_id))

            current_questions = paginate_questions(request, questions)

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                    "current_category": category_id,
                }
            )

        except:
            abort(404)

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
    # ----------------------------------------------------------------------------#
    # POST random question within the given category.
    # ----------------------------------------------------------------------------#

    @app.route("/quizzes", methods=["POST"])
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
                print(quiz)

            selected = []

            for question in quiz:
                if question.id not in previous_questions:
                    selected.append(question.format())

            if len(selected) != 0:
                result = random.choice(selected)
                return jsonify({"success": True, "question": result})

            else:
                return jsonify({"question": False})

        except:
            abort(422)
            print(sys.exc_info())

    """
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 

  """
    # ----------------------------------------------------------------------------#
    # 404: Resource Not found
    # ----------------------------------------------------------------------------#

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource Not Found"}),
            404,
        )

    # ----------------------------------------------------------------------------#
    # 422: Unprocessable
    # ----------------------------------------------------------------------------#

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    # ----------------------------------------------------------------------------#
    # 400: Bad Request
    # ----------------------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400

    # ----------------------------------------------------------------------------#
    # 405: Method Not Allowed
    # ----------------------------------------------------------------------------#

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    return app
