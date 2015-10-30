# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from comport.utils import flash_errors
from flask.ext.login import login_required
from comport.decorators import extractor_auth_required
from comport.department.models import Extractor
from comport.data.models import UseOfForceIncident, CitizenComplaint,OfficerInvolvedShooting
from comport.utils import parse_date, parse_int
import json
from datetime import datetime

blueprint = Blueprint("data", __name__, url_prefix='/data',
                      static_folder="../static")

@blueprint.route("/heartbeat", methods=['POST'])
@extractor_auth_required()
def heartbeat():
    username = request.authorization.username
    extractor = Extractor.query.filter_by(username=username).first()

    extractor.last_contact = datetime.now()
    extractor.save()

    if extractor.next_month and extractor.next_year:
        return json.dumps({"received":request.json, "nextMonth":extractor.next_month, "nextYear":extractor.next_year})

    return json.dumps({"received":request.json})

@blueprint.route("/UOF", methods=['POST'])
@extractor_auth_required()
def use_of_force():
    username = request.authorization.username
    extractor = Extractor.query.filter_by(username=username).first()
    j = request.json
    added_rows = 0
    updated_rows = 0

    for incident in j['data']:
        found_incident = UseOfForceIncident.query.filter_by(
            opaque_id=incident["opaqueId"],
            department_id=extractor.department_id,
            officer_identifier =incident["officerIdentifier"],
            officer_force_type =incident["officerForceType"]
            ).first()

        occured_date = parse_date(incident["occuredDate"])

        if not found_incident:
            found_incident = UseOfForceIncident.create(
                    department_id = extractor.department_id,
                    opaque_id = incident["opaqueId"],
                    occured_date = occured_date,
                    division = incident["division"],
                    precinct =incident["precinct"],
                    shift = incident["shift"],
                    beat =incident["beat"],
                    disposition =incident["disposition"],
                    census_tract = None,
                    officer_force_type =incident["officerForceType"],
                    use_of_force_reason =incident["useOfForceReason"],
                    service_type =incident["serviceType"],
                    arrest_made =incident["arrestMade"],
                    arrest_charges =incident["arrestCharges"],
                    resident_weapon_used =incident["residentWeaponUsed"],
                    resident_injured =incident["residentInjured"],
                    resident_hospitalized =incident["residentHospitalized"],
                    officer_injured =incident["officerInjured"],
                    officer_hospitalized =incident["officerHospitalized"],
                    resident_race =incident["residentRace"],
                    resident_sex =incident["residentSex"],
                    resident_age = incident["residentAge"],
                    resident_condition =incident["residentCondition"],
                    officer_identifier =incident["officerIdentifier"],
                    officer_race =incident["officerRace"],
                    officer_sex =incident["officerSex"],
                    officer_age = incident["officerAge"],
                    officer_years_of_service = incident["officerYearsOfService"],
                    officer_condition = incident["officerCondition"]
                    )
            added_rows += 1
            continue

        found_incident.department_id = extractor.department_id,
        found_incident.opaque_id = incident["opaqueId"],
        found_incident.occured_date = occured_date,
        found_incident.division = incident["division"],
        found_incident.precinct =incident["precinct"],
        found_incident.shift = incident["shift"],
        found_incident.beat =incident["beat"],
        found_incident.disposition =incident["disposition"],
        found_incident.census_tract = None,
        found_incident.officer_force_type =incident["officerForceType"],
        found_incident.use_of_force_reason =incident["useOfForceReason"],
        found_incident.service_type =incident["serviceType"],
        found_incident.arrest_made =incident["arrestMade"],
        found_incident.arrest_charges =incident["arrestCharges"],
        found_incident.resident_weapon_used =incident["residentWeaponUsed"],
        found_incident.resident_injured =incident["residentInjured"],
        found_incident.resident_hospitalized =incident["residentHospitalized"],
        found_incident.officer_injured =incident["officerInjured"],
        found_incident.officer_hospitalized =incident["officerHospitalized"],
        found_incident.resident_race =incident["residentRace"],
        found_incident.resident_sex =incident["residentSex"],
        found_incident.resident_age = incident["residentAge"],
        found_incident.resident_condition =incident["residentCondition"],
        found_incident.officer_identifier =incident["officerIdentifier"],
        found_incident.officer_race =incident["officerRace"],
        found_incident.officer_sex =incident["officerSex"],
        found_incident.officer_age = incident["officerAge"],
        found_incident.officer_years_of_service =incident["officerYearsOfService"],
        found_incident.officer_condition =incident["officerCondition"]
        found_incident.save()
        updated_rows += 1

    extractor.next_month = None
    extractor.next_year = None
    extractor.save()
    return json.dumps({"added": added_rows, "updated": updated_rows})

@blueprint.route("/OIS", methods=['POST'])
@extractor_auth_required()
def officer_involved_shooting():
    username = request.authorization.username
    extractor = Extractor.query.filter_by(username=username).first()
    j = request.json
    added_rows = 0
    updated_rows = 0

    for incident in j['data']:
        found_incident = OfficerInvolvedShooting.query.filter_by(opaque_id=incident["opaqueId"],department_id=extractor.department_id).first()

        occured_date = parse_date(incident["occuredDate"])

        if not found_incident:
            found_incident = OfficerInvolvedShooting.create(
                    department_id = extractor.department_id,
                    opaque_id = incident["opaqueId"],
                    service_type =incident["serviceType"],
                    occured_date = occured_date,
                    division = incident["division"],
                    precinct =incident["precinct"],
                    shift = incident["shift"],
                    beat =incident["beat"],
                    disposition =incident["disposition"],
                    resident_sex =incident["residentSex"],
                    resident_race =incident["residentRace"],
                    resident_age = incident["residentAge"],
                    resident_weapon_used =incident["residentWeaponUsed"],
                    resident_condition =incident["residentCondition"],
                    officer_identifier =incident["officerIdentifier"],
                    officer_force_type =incident["officerForceType"],
                    officer_race =incident["officerRace"],
                    officer_sex =incident["officerSex"],
                    officer_age = incident["officerAge"],
                    officer_years_of_service =parse_int(incident["officerYearsOfService"]),
                    officer_condition =incident["officerCondition"],
                    census_tract = None
                    )
            added_rows += 1
            continue

        found_incident.department_id = extractor.department_id,
        found_incident.opaque_id = incident["opaqueId"],
        found_incident.service_type =incident["serviceType"],
        found_incident.occured_date = occured_date,
        found_incident.division = incident["division"],
        found_incident.precinct =incident["precinct"],
        found_incident.shift = incident["shift"],
        found_incident.beat =incident["beat"],
        found_incident.disposition =incident["disposition"],
        found_incident.resident_sex =incident["residentSex"],
        found_incident.resident_race =incident["residentRace"],
        found_incident.resident_age = incident["residentAge"],
        found_incident.resident_weapon_used =incident["residentWeaponUsed"],
        found_incident.resident_condition =incident["residentCondition"],
        found_incident.officer_identifier =incident["officerIdentifier"],
        found_incident.officer_force_type =incident["officerForceType"],
        found_incident.officer_race =incident["officerRace"],
        found_incident.officer_sex =incident["officerSex"],
        found_incident.officer_age = incident["officerAge"],
        found_incident.officer_years_of_service =parse_int(incident["officerYearsOfService"]),
        found_incident.officer_condition =incident["officerCondition"],
        found_incident.census_tract = None
        found_incident.save()
        updated_rows += 1

    extractor.next_month = None
    extractor.next_year = None
    extractor.save()
    return json.dumps({"added": added_rows, "updated": updated_rows})

@blueprint.route("/complaints", methods=['POST'])
@extractor_auth_required()
def complaints():
    username = request.authorization.username
    extractor = Extractor.query.filter_by(username=username).first()
    j = request.json
    added_rows = 0
    updated_rows = 0

    for incident in j['data']:
        found_incident = CitizenComplaint.query.filter_by(
            opaque_id=incident["opaqueId"],
            allegation_type = incident["allegationType"],
            allegation = incident["allegation"],
            officer_identifier =incident["officerIdentifier"],
            department_id=extractor.department_id).first()

        occured_date = parse_date(incident["occuredDate"])

        if not found_incident:
            found_incident = CitizenComplaint.create(
                    department_id = extractor.department_id,
                    opaque_id = incident["opaqueId"],
                    occured_date = occured_date,
                    service_type = incident["serviceType"],
                    source = incident["source"],
                    division = incident["division"],
                    precinct =incident["precinct"],
                    shift = incident["shift"],
                    beat =incident["beat"],
                    allegation_type = incident["allegationType"],
                    allegation = incident["allegation"],
                    disposition =incident["disposition"],
                    resident_race =incident["residentRace"],
                    resident_sex =incident["residentSex"],
                    resident_age = incident["residentAge"],
                    officer_identifier =incident["officerIdentifier"],
                    officer_race =incident["officerRace"],
                    officer_sex =incident["officerSex"],
                    officer_age = incident["officerAge"],
                    officer_years_of_service =incident["officerYearsOfService"],
                    census_tract = None
                    )

            added_rows += 1
            continue

        # found_incident.department_id = extractor.department_id,
        # found_incident.opaque_id = incident["opaqueId"],
        # found_incident.occured_date = occured_date,
        # found_incident.division = incident["division"],
        # found_incident.precinct =incident["precinct"],
        # found_incident.shift = incident["shift"],
        # found_incident.beat =incident["beat"],
        # found_incident.allegation_type = incident["allegationType"],
        # found_incident.allegation = incident["allegation"],
        # found_incident.disposition =incident["disposition"],
        # found_incident.resident_race =incident["residentRace"],
        # found_incident.resident_sex =incident["residentSex"],
        # found_incident.resident_age = incident["residentAge"],
        # found_incident.officer_identifier =incident["officerIdentifier"],
        # found_incident.officer_race =incident["officerRace"],
        # found_incident.officer_sex =incident["officerSex"],
        # found_incident.officer_age = incident["officerAge"],
        # found_incident.officer_years_of_service =incident["officerYearsOfService"],
        # found_incident.census_tract = None
        # found_incident.save()
        # updated_rows += 1

    extractor.next_month = None
    extractor.next_year = None
    extractor.save()
    return json.dumps({"added": added_rows, "updated": updated_rows})
