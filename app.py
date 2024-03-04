from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_url_path='/static')

def getProfName(department, course_number, section):
    url = f'https://ws.admin.washington.edu/student/v5/course/2024,spring,{department},{course_number}/{section}'
    headers = {'Authorization': 'Bearer 7F3A58DB-4847-44B9-85B3-E73CE883E974'}

    # Make the API call
    response = requests.get(url, headers=headers)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract relevant information
    course_title = soup.find('span', {'class': 'CourseTitle'}).text.strip()
    instructor_name_element = soup.find('ul', {'class': 'Instructors'})

    if instructor_name_element:
        instructor_name = instructor_name_element.find('span', {'class': 'name'}).text.strip()
        return f"Course Title: {course_title}\nInstructor's name is: {instructor_name}"
    else:
        return "Instructor information not available."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    class_info = request.form['class'].split(',')
    section = request.form['section']
    
    # Validate class_info and section or add additional error checking if needed
    if len(class_info) != 2 or not section:
        error_message = "Please enter a valid class in the format 'DEPARTMENT,COURSE_NUMBER' and provide a section."
        return render_template('index.html', error_message=error_message)

    department, course_number = class_info
    result = getProfName(department, course_number, section)
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
