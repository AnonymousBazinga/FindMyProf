from flask import Flask, render_template, request, redirect, url_for
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
        result = {
            'course_title': course_title,
            'instructor_info': f"Instructor's name is: {instructor_name}"
        }
    else:
        result = {'course_title': course_title, 'instructor_info': "Instructor information not available."}

    return result


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


def extract_first_last_names(full_name):
    #convert to a name
    print("BEFORE: ", full_name, " WITH ", full_name.index(":"))
    full_name = full_name[full_name.index(":")+1:]
    print("AFTER: ", full_name)

    # Split the full name by spaces and extract the first and last names
    names = full_name.split()
    if len(names) >= 2:
        first_name = names[0]
        last_name = names[-1]
    else:
        # If there are not enough parts, use the full name
        first_name = full_name
        last_name = full_name
    print("FINAL: ", first_name, last_name)
    return first_name, last_name

@app.route('/rate_my_professor/<professor_info>')
def rate_my_professor(professor_info):
    # Extract first and last names
    first_name, last_name = extract_first_last_names(professor_info)

    # Open a new tab searching for the first and last names on Rate My Professor
    search_url = f'https://www.ratemyprofessors.com/search/professors?q={first_name}%20{last_name}'
    print(search_url)
    return redirect(search_url)

if __name__ == '__main__':
    app.run(debug=True)
