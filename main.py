import requests
import json
import flask
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class lesson:
    subject_name: str
    lesson_period: int
    lesson_room: str
    lesson_teacher: str

# Create Flask app at module level
app = flask.Flask(__name__)

class ClassChartsAPI:
    def __init__(self):
        # Defines some constants for the API
        # My student details
        self.STUDENT_ID = '7303971'
        self.STUDENT_FNAME = 'Pietro'
        self.STUDENT_LNAME = 'Kaye'
        self.STUDENT_FULLNAME = f"{self.STUDENT_FNAME} {self.STUDENT_LNAME}"
        self.STUDENT_LOGIN_CODE = 'MWT5QMWA3U'
        self.STUDENT_DOB = '2011-12-03' # Date of birth in YYYY-MM-DD format
        self.student_Authcode = "" # Will be entered on login

    def login(self):
        # Make a request to the API to get the auth code
        response = requests.post(
            'https://www.classcharts.com/apiv2student/login',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'code': self.STUDENT_LOGIN_CODE,
                'remember': 'true',
                'recaptcha-token': 'no-token-available',
                'dob': self.STUDENT_DOB
            }
)
        if response.status_code == 200:
            print(response.json())
            self.student_Authcode = response.json()["meta"]["session_id"]
            return True
        else:
            return False

    def logged_in(self):
        return self.student_Authcode != ""

    def get_timetable_cur_date(self):
        if not self.logged_in():
            return flask.jsonify({'error': 'Not logged in'}), 401
        
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Make a request to the API to get the timetable for the current date
        response = requests.get(f'https://www.classcharts.com/apiv2student/timetable/{self.STUDENT_ID}?date={current_date}', headers={'Authorization': f'Basic {self.student_Authcode}'})
        if response.status_code == 200:
            lessons = self.parse_lesson_data(response.json())
            print([lesson.__dict__ for lesson in lessons])
            return flask.jsonify([lesson.__dict__ for lesson in lessons]), 200
        else:
            return flask.jsonify({'error': 'Failed to retrieve timetable'}), response.status_code
    
    def parse_lesson_data(self, data: dict) -> List[lesson]:
        """
        Parse lesson data from the API response and return a list of lesson objects.
        
        Args:
            data: The JSON response from the ClassCharts API containing lesson information
            
        Returns:
            A list of lesson objects populated with the API data
        """
        lessons = []
        
        # Extract the data array from the response
        if 'data' not in data or not isinstance(data['data'], list):
            return lessons
        
        # Parse each lesson in the data array
        for lesson_data in data['data']:
            try:
                parsed_lesson = lesson(
                    subject_name=lesson_data.get('subject_name', ''),
                    lesson_period=int(lesson_data.get('period_number', 0)),
                    lesson_room=lesson_data.get('room_name', ''),
                    lesson_teacher=lesson_data.get('teacher_name', '')
                )
                lessons.append(parsed_lesson)
            except (ValueError, KeyError) as e:
                # Skip lessons with invalid data
                continue
        
        if not lessons:
            return "No lessons found for the current date."
        else:
            return lessons
    
@app.route('/api/timetable_cur_date', methods=['GET'])
def timetable_cur_date():
    return api.get_timetable_cur_date()

    

if __name__ == '__main__':
    api = ClassChartsAPI()
    if api.login():
        print("Logged in successfully!")
        app.run(debug=True)
    else:
        print("Failed to log in. Please check your credentials.")