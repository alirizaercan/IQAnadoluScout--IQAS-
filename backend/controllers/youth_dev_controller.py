from flask import Blueprint, jsonify

youth_dev_controller = Blueprint('youth_dev_controller', __name__)

@youth_dev_controller.route('/physical-development', methods=['GET'])
def physical_development():
    return jsonify({'message': 'Physical Development Page'})

@youth_dev_controller.route('/conditional-development', methods=['GET'])
def conditional_development():
    return jsonify({'message': 'Conditional Development Page'})

@youth_dev_controller.route('/endurance-development', methods=['GET'])
def endurance_development():
    return jsonify({'message': 'Endurance Development Page'})
