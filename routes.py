import sys
import json

from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)

#point configuration property to sqlite db file 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ScheduleData.db'

db = SQLAlchemy(app)

#ORM data model for mapping to db columns
class Subject(db.Model):
    __tablename__ = 'Subjects'
    SubjectID = db.Column(db.Integer, primary_key = True)
    abbrev = db.Column(db.String(10))
    fullname = db.Column(db.String(20))


#ORM data model for mapping to db columns
class Department(db.Model):
    __tablename__ = 'Departments'
    departmentID = db.Column(db.Integer, primary_key = True)
    abbrev = db.Column(db.String(10))
    fullname = db.Column(db.String(20))


#ORM data model for mapping to db columns
class Section(db.Model):
    __tablename__ = 'Sections'
    sectionID = db.Column(db.Integer, primary_key = True)
    courseID = db.Column(db.String(10))
    department = db.Column(db.String(20))
    crn = db.Column(db.String(10))
    semester = db.Column(db.String(10))
    discipline = db.Column(db.String(15))
    courseNumber = db.Column(db.String(10))
    section = db.Column(db.String(10))
    type = db.Column(db.String(30))
    title = db.Column(db.String(30))
    hours = db.Column(db.String(30))
    days = db.Column(db.String(30))
    time = db.Column(db.String(30))
    location = db.Column(db.String(30))
    instructor = db.Column(db.String(30))
    maxEnrollments = db.Column(db.String(30))
    availSeats = db.Column(db.String(30))
    messages = db.Column(db.String(30))
    term = db.Column(db.String(30))
    feeTitle = db.Column(db.String(30))
    totalFees = db.Column(db.Float(9))
    perCourseOrPerCredit = db.Column(db.String(30))
    startDate = db.Column(db.String(30))
    endDate = db.Column(db.String(30))
    url = db.Column(db.String(30))



@app.route('/instructors', methods=['GET'])
def instructors():
    if request.method == 'GET':
        lim = request.args.get('limit',100)
        courseCode = request.args.get('courseCode','')

        d = {}
        json_results = []
        
        
        if(courseCode):
            if(courseCode == 'all'):
                results = Section.query.filter(Section.courseID.like("%")).all()
            else:
                results = Section.query.filter(Section.courseID.like(courseCode + "%")).all()
            
            result_set = []
            for result in results:
                if result.instructor not in result_set:
                    result_set.append(result.instructor)
            for instructor in result_set:
                d = {'instructor': instructor}
                json_results.append(d)
                json_results.sort()

        response = jsonify(json_results)
        response.headers.add('Access-Control-Allow-Origin', '*')
            
    return response
                
                

@app.route('/sections', methods=['GET'])
def sections():
    if request.method == 'GET':
	    #number of elements in response
        lim = request.args.get('limit', 10)
		#number to skip
        off = request.args.get('offset', 0)
		#find=shape-cone   OR   find=<field>-<search string>
        find = request.args.get('find', "")
		#fields=id-description-url  OR  fields=<field1>-<field2>
        fields = request.args.get('fields',"")
        
        search = {}
        search['id'] = Section.sectionID
        search['courseID'] = Section.courseID
        search['department'] = Section.department
        search['crn'] = Section.crn
        search['semester'] = Section.semester
        search['discipline'] = Section.discipline
        search['courseNumber'] = Section.courseNumber
        search['section'] = Section.section
        search['type'] = Section.type
        search['title'] = Section.title
        search['hours'] = Section.hours
        search['days'] = Section.days
        search['time'] = Section.time
        search['location'] = Section.location
        search['instructor'] = Section.instructor
        search['maxEnrollments'] = Section.maxEnrollments
        search['availSeats'] = Section.availSeats
        search['messages'] = Section.messages
        search['term'] = Section.term
        search['feeTitle'] = Section.feeTitle
        search['totalFees'] = Section.totalFees
        search['perCourseOrPerCredit'] = Section.perCourseOrPerCredit
        search['startDate'] = Section.startDate
        search['endDate'] = Section.endDate
        search['page_url'] = Section.url

        #split find query string value
        find_arg = []
        find_arg = find.split('-')

        if(find):
            results = Section.query.filter(search[find_arg[0]].like('%'+find_arg[1]+'%')).limit(lim).offset(off).all()
        else:
            results = Section.query.limit(lim).offset(off).all()

        #split fields query string value
        fields_arg = []
        fields_arg = fields.split('-')

        d = {}#used for response data transfer object(dictionary)
        json_results = []#list of dictionaries of Sighting objects

        if(fields):
            section = Section()
            resp_fields = []

            for field in fields_arg:
                #introspect fields of sqlalchemy orm object (list of string)
                keys = section.__table__.columns._data.keys()
                #url returned optionally with url_for resource
                if field in keys:
                    resp_fields.append(str(field))
                if field in ['url','id','page_url']:
                    resp_fields.append(str(field))

            #create data shaped response
            for result in results:
                #result as dictionary to key into for values
                result_dict = result.__dict__
                for field in resp_fields:
                    if field == 'id' or field == 'sectionID':
                        d['id'] = result_dict['sectionID']
                    elif field == 'url':
                        d['url'] = url_for('section', id=result.sectionID)
                    elif field == 'page_url':
                        d['page_url'] = result_dict['url']
                    else:
                        d[str(field)] = result_dict[str(field)]
				#append a copy of the dictionary (otherwise all overwritten by last result) 
                json_results.append(d.copy())

            
        else:
            for result in results:
                d = {'url': url_for('section', id=result.sectionID),
                     'id': result.sectionID,
                     'courseID': result.courseID,
                     'department': result.department,
                     'crn': result.crn,
                     'semester': result.semester,
                     'discipline': result.discipline,
                     'courseNumber': result.courseNumber,
                     'section': result.section,
                     'type': result.type,
                     'title': result.title,
                     'hours': result.hours,
                     'days': result.days,
                     'time': result.time,
                     'location': result.location,
                     'instructor': result.instructor,
                     'maxEnrollments': result.maxEnrollments,
                     'availSeats': result.availSeats,
                     'messages': result.messages,
                     'term': result.term,
                     'feeTitle': result.feeTitle,
                     'totalFees': result.totalFees,
                     'perCourseOrPerCredit': result.perCourseOrPerCredit,
                     'startDate': result.startDate,
                     'endDate': result.endDate,
                     'page_url': result.url}
                json_results.append(d)

        response = jsonify(json_results)
        response.headers.add('Access-Control-Allow-Origin', '*')    
        
        return response


@app.route('/section/<int:id>', methods=['GET'])
def section(id):
    if request.method == 'GET':
        result = section.query.filter_by(sectionID=id).first()

        json_result = {'url': url_for('section', id=result.sectionID),
                     'id': result.sectionID,
                     'courseID': result.courseID,
                     'department': result.department,
                     'crn': result.crn,
                     'semester': result.semester,
                     'discipline': result.discipline,
                     'courseNumber': result.courseNumber,
                     'section': result.section,
                     'type': result.type,
                     'title': result.title,
                     'hours': result.hours,
                     'days': result.days,
                     'time': result.time,
                     'location': result.location,
                     'instructor': result.instructor,
                     'maxEnrollments': result.maxEnrollments,
                     'availSeats': result.availSeats,
                     'messages': result.messages,
                     'term': result.term,
                     'feeTitle': result.feeTitle,
                     'totalFees': result.totalFees,
                     'perCourseOrPerCredit': result.perCourseOrPerCredit,
                     'startDate': result.startDate,
                     'endDate': result.endDate,
                     'page_url': result.url}

        return jsonify(json_result)






@app.route('/subjects', methods=['GET'])
def subjects():
    if request.method == 'GET':
	    #number of elements in response
        lim = request.args.get('limit', 10)
		#number to skip
        off = request.args.get('offset', 0)
		#find=shape-cone   OR   find=<field>-<search string>
        find = request.args.get('find', "")
		#fields=id-description-url  OR  fields=<field1>-<field2>
        fields = request.args.get('fields',"")
        
        search = {}
        search['id'] = Subject.SubjectID
        search['abbrev'] = Subject.abbrev
        search['fullname'] = Subject.fullname

        #split find query string value
        find_arg = []
        find_arg = find.split('-')

        if(find):
            results = Subject.query.filter(search[find_arg[0]].like('%'+find_arg[1]+'%')).limit(lim).offset(off).all()
        else:
            results = Subject.query.limit(lim).offset(off).all()

        #split fields query string value
        fields_arg = []
        fields_arg = fields.split('-')

        d = {}#used for response data transfer object(dictionary)
        json_results = []#list of dictionaries of Sighting objects

        if(fields):
            subject = Subject()
            resp_fields = []

            for field in fields_arg:
                #introspect fields of sqlalchemy orm object (list of string)
                keys = subject.__table__.columns._data.keys()
                #url returned optionally with url_for resource
                if field in ['url','id']:
                    resp_fields.append(str(field))
                if field in keys:
                    resp_fields.append(str(field))

            #create data shaped response
            for result in results:
                #result as dictionary to key into for values
                result_dict = result.__dict__
                for field in resp_fields:
                    if field == 'url':
                        d['url'] = url_for('subject', SubjectID=result.SubjectID)
                    if field == 'id' or field == 'SubjectID':
                        d['id'] = result_dict['SubjectID']
                    else:
                        d[str(field)] = result_dict[str(field)]
				#append a copy of the dictionary (otherwise all overwritten by last result) 
                json_results.append(d.copy())

            
        else:
            for result in results:
                d = {'url': url_for('subject', id=result.SubjectID),
                     'id': result.SubjectID,
                     'abbrev': result.abbrev,
                     'fullname': result.fullname}
                json_results.append(d)
        
        return jsonify(json_results)


@app.route('/subject/<int:id>', methods=['GET'])
def subject(id):
    if request.method == 'GET':
        result = Subject.query.filter_by(SubjectID=id).first()

        json_result = {'id': result.SubjectID,
                       'abbrev': result.abbrev,
                       'fullname': result.fullname}

        return jsonify(json_result)





@app.route('/departments', methods=['GET'])
def departments():
    if request.method == 'GET':
	    #number of elements in response
        lim = request.args.get('limit', 10)
		#number to skip
        off = request.args.get('offset', 0)
		#find=shape-cone   OR   find=<field>-<search string>
        find = request.args.get('find', "")
		#fields=id-description-url  OR  fields=<field1>-<field2>
        fields = request.args.get('fields',"")
        
        search = {}
        search['departmentID'] = Department.departmentID
        search['abbrev'] = Department.abbrev
        search['fullname'] = Department.fullname

        #split find query string value
        find_arg = []
        find_arg = find.split('-')

        if(find):
            results = Department.query.filter(search[find_arg[0]].like('%'+find_arg[1]+'%')).limit(lim).offset(off).all()
        else:
            results = Department.query.limit(lim).offset(off).all()

        #split fields query string value
        fields_arg = []
        fields_arg = fields.split('-')

        d = {}#used for response data transfer object(dictionary)
        json_results = []#list of dictionaries of Sighting objects

        if(fields):
            department = Department()
            resp_fields = []

            for field in fields_arg:
                #introspect fields of sqlalchemy orm object (list of string)
                keys = department.__table__.columns._data.keys()
                #url returned optionally with url_for resource
                if field in ['url','id']:
                    resp_fields.append(str(field))
                if field in keys:
                    resp_fields.append(str(field))

            #create data shaped response
            for result in results:
                #result as dictionary to key into for values
                result_dict = result.__dict__
                for field in resp_fields:
                    if field == 'url':
                        d['url'] = url_for('department', departmentID=result.departmentID)
                    if field == 'id' or field == 'departmentID':
                        d['id'] = result_dict['departmentID']
                    else:
                        d[str(field)] = result_dict[str(field)]
				#append a copy of the dictionary (otherwise all overwritten by last result) 
                json_results.append(d.copy())

            
        else:
            for result in results:
                d = {'url': url_for('department', id=result.departmentID),
                     'id': result.departmentID,
                     'abbrev': result.abbrev,
                     'fullname': result.fullname}
                json_results.append(d)
        response = jsonify(json_results)
        response.headers.add('Access-Control-Allow-Origin', '*')    
        
        return response


@app.route('/department/<int:id>', methods=['GET'])
def department(id):
    if request.method == 'GET':
        result = Department.query.filter_by(departmentID=id).first()

        json_result = {'id': result.departmentID,
                       'abbrev': result.abbrev,
                       'fullname': result.fullname}

        return jsonify(json_result)


if __name__ == '__main__':
    app.run(debug=True)
