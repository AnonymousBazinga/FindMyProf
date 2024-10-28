from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_url_path='/static')

def getProfName(department, course_number, section):
    url = f'https://ws.admin.washington.edu/student/v5/course/2024,winter,{department},{course_number}/{section}'
    headers = {'Authorization': 'Bearer 9919BCA8-9DCC-4BEC-B3F3-E0EFDE2F608E'}

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
            'instructor_info': instructor_name
        }
    else:
        result = {'course_title': course_title, 'instructor_info': "Instructor information is unavailable."}

    return result


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/process', methods=['POST'])
def process():
    class_info = courseSplitter(request.form['class'])
    section = request.form['section']
    # term = request.form['term']

    # Validate class_info and section or add additional error checking if needed
    if len(class_info) != 2 or not section:
        error_message = "Please enter a valid class in the format 'DEPARTMENT,COURSE_NUMBER' and provide a section."
        return render_template('index.html', error_message=error_message)

    department, course_number = class_info
    result = getProfName(department, course_number, section)
    return render_template('result.html', result=result)

def courseSplitter(nameOfClass):
    #Check this - does strip return a value or not?
    nameOfClass = nameOfClass.strip()
    if (nameOfClass.find(",") != -1):
        return nameOfClass.split(",")
    else:
        pos = -1
        for i in nameOfClass:
            pos+=1

            try:
                i = int(i)
            except Exception as e:
                continue
            else:
                break
        return [nameOfClass[0:pos].strip(), nameOfClass[pos:].strip()]

def extract_first_last_names(full_name):
    if full_name.find(":") != -1:
        #convert to a name
        full_name = full_name[full_name.index(":")+1:]

    # Split the full name by spaces and extract the first and last names
    names = full_name.split()
    if len(names) >= 2:
        first_name = names[0]
        last_name = names[-1]
    else:
        # If there are not enough parts, use the full name
        first_name = full_name
        last_name = full_name
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
