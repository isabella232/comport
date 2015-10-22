#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Shell, Server, prompt_bool, prompt_pass
from flask_migrate import MigrateCommand, upgrade


from comport.app import create_app
from comport.user.models import User, Role
from comport.department.models import Department, Extractor
from comport.content.models import Link
from comport.settings import DevConfig, ProdConfig, Config
from comport.database import db
from comport.utils import random_string, parse_date, diff_month, parse_csv_date, parse_int
from comport.data.models import UseOfForceIncident, CitizenComplaint
from tests.factories import UseOfForceIncidentFactory, DenominatorValueFactory, CitizenComplaintFactory
import json
import glob
import csv
import hashlib
from datetime import datetime

if os.environ.get("COMPORT_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User, 'Department': Department, 'Extractor': Extractor, 'UseOfForceIncident': UseOfForceIncident, "CitizenComplaint": CitizenComplaint}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '-x', '--verbose'])
    return exit_code


@manager.command
def make_admin_user():
    password = prompt_pass("Password")
    user = User.create(username="admin", email="email@example.com",password=password,active=True)
    admin_role = Role(name='admin')
    admin_role.save()
    user.roles.append(admin_role)
    user.save()

@manager.command
def load_test_data():
    department = Department.query.filter_by(name="IMPD").first()
    if not department:
        department = Department.create(name="IMPD")
    if not User.query.filter_by(username="user").first():
        User.create(username="user", email="email2@example.com",password="password",active=True, department_id=department.id)

    for filename in glob.glob('data/testdata/complaints/complaints.csv'):
        with open(filename, 'rt') as f:
            reader = csv.DictReader(f)
            for complaint in reader:
                officer_identifier = hashlib.md5((complaint.get("OFFNUM", None) + Config.SECRET_KEY).encode('UTF-8')).hexdigest()
                opaque_id = hashlib.md5((complaint.get("INCNUM", None) + Config.SECRET_KEY).encode('UTF-8')).hexdigest()

                CitizenComplaint.create(
                    opaque_id = opaque_id,
                    department_id = department.id,
                    occured_date = parse_csv_date(complaint.get("OCCURRED_DT", None)),
                    division = complaint.get("UDTEXT24A", None),
                    precinct = complaint.get("UDTEXT24B", None),
                    shift = complaint.get("UDTEXT24C", None),
                    beat = complaint.get("UDTEXT24D", None),
                    disposition = complaint.get("FINDING", None),
                    allegation_type = complaint.get("ALG_CLASS", None),
                    allegation = complaint.get("ALLEGATION", None),
                    census_tract = None,
                    resident_race = complaint.get("RACE", None),
                    officer_race = complaint.get("OFF_RACE", None),
                    resident_sex = complaint.get("SEX", None),
                    officer_sex = complaint.get("OFF_SEX", None),
                    officer_identifier = officer_identifier,
                    officer_years_of_service = complaint.get("OFF_YR_EMPLOY", None),
                    officer_age = complaint.get("OFF_AGE", None),
                    resident_age = complaint.get("CIT_AGE", None)
                )


@manager.command
def make_test_data():
    department = Department.query.filter_by(name="Busy Town Public Safety").first()
    if not department:
        department = Department.create(name="Busy Town Public Safety")
        Link.create(title="The Department's Policy on Force", url="www.example.com/policy/force.pdf", department_id=department.id, type="policy")
        Link.create(title="The Department's Training Policy on Force", url="www.example.com/training/force.pdf", department_id=department.id, type="training")
        Link.create(title="The Department's Outreach Strategy", url="www.example.com/outreach.pdf", department_id=department.id, type="outreach")

    if not User.query.filter_by(username="user").first():
        User.create(username="user", email="email2@example.com",password="password",active=True, department_id=department.id)

    for _ in range(100):
        incident = UseOfForceIncidentFactory()
        incident.department_id = department.id
        incident.save()

    for _ in range(100):
        complaint = CitizenComplaintFactory()
        complaint.department_id = department.id
        complaint.save()

    for _ in range(diff_month(datetime.now(),datetime(2012,1,1))):
        denominator_value = DenominatorValueFactory()
        denominator_value.department_id = department.id
        denominator_value.save()


@manager.command
def delete_everything():
   db.reflect()
   db.drop_all()
   upgrade()



manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
