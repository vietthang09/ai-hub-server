from flask import Blueprint
from src.controllers.reviews_controller import ReviewsController

reviews_bp = Blueprint('reviews', __name__)
reviews_controller = ReviewsController()

@reviews_bp.route('/pull', methods=['POST'])
def pull_reviews():
    return reviews_controller.pull_reviews()

@reviews_bp.route('/', methods=['GET'])
def get_reviews():
    return reviews_controller.get_reviews()