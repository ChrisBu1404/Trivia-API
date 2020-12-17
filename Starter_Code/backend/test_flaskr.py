import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the best football team all over the place?',
            'answer': 'Borussia Dortmund',
            'category': 1,
            'difficulty': 1
        }

        self.new_question_wrong = {
            'question': 'What is the best football team all over the place??',
            'answer': 'Borussia Dortmund',
            'category': 1,
            'difficulty': 'Should be an integer'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()


    def test_get_questions_from_page_2(self):
        """Test if questions can be retrieved from page 2"""
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_questions_from_page_1000(self):
        """Test if questions can be retrieved from a page that does not exist"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'resource not found')


    def test_get_questions(self):
        """Test if questions can be retrieved"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))


    # def test_delete_question(self):
    #     """Test if question can be deleted"""
    #     res = self.client().delete('/questions/6')
    #     data = json.loads(res.data)

    #     question = Question.query.filter(Question.id == 6).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'], 6)
    #     self.assertTrue(data['total_questions'])
    #     self.assertTrue(len(data['questions']))
    #     self.assertEqual(question, None)

    def test_404_delete_if_question_does_not_exist(self):
        """Test if the question that is to deleted does not exist"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_create_new_question(self):
        """Test to create new question"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_if_question_creation_fails(self):
        """Test if question creation fails"""
        res = self.client().post('/questions', json=self.new_question_wrong)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_questions_search_with_results(self):
        """Test to get questions with search"""
        res = self.client().post('/questions', json={'searchTerm': 'World'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)

    def test_get_questions_search_without_results(self):
        """Test if search without results"""
        res = self.client().post('/questions', json={'searchTerm': 'blablabla'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)


    def test_get_questions_by_category(self):
        """Test to retrieve questions by category"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_invalid_category(self):
        """Test to retrieve questions by category"""
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)

    def test_get_quiz_questions(self):
        """Test quit questions can be retrieved"""
        res = self.client().post('/quizzes', json={'previous_questions': [3], 'quiz_category':{'type': 'Sports','id':"6"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))


    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()