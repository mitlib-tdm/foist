# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest
import requests
import xml.etree.ElementTree as ET

from foist import (create_container, parse_text_encoding_errors, Thesis,
                   transaction, upload_file, update_metadata)

from foist.namespaces import BIBO, DCTYPE, PCDM


def test_thesis(xml, text_errors):
    '''Thesis object should initialize with a name, mets, errors, and full
    text status.
    '''
    mets = ET.parse(xml).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, 'Department One',
               errors)

    assert t.name == 'thesis'
    assert t.mets == mets
    assert t.errors == errors
    assert t.departments == 'Department One'
    assert t.no_full_text is True


def test_thesis_with_all_metadata_fields_parses_correctly(xml, text_errors):
    '''Thesis object should create properties for all metadata fields.
    '''
    mets = ET.parse(xml).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, ['Department One', 'Department Two'],
               errors)

    assert t.abstract == 'Sample abstract.'
    assert t.advisor == ['Advisor One.', 'Advisor Two.']
    assert t.alt_title == ['Alternative Title.']
    assert t.author == ['Author One.', 'Author Two.']
    assert t.copyright_date == '2006'
    assert t.dc_type == DCTYPE.Text
    assert t.degree == ['S.M.', 'M.B.A.']
    assert t.degree_statement == ('Thesis (S.M. and M.B.A.)--Massachusetts '
                                  'Institute of Technology, Computation for '
                                  'Design and Optimization Program, 2006.')
    assert t.department == ['Department One', 'Department Two']
    assert t.encoded_text is True
    assert t.handle == 'http://hdl.handle.net/1721.1/39208'
    assert t.handle_part == '39208'
    assert t.issue_date == '2006'
    assert t.ligatures is None
    assert t.no_full_text is True
    assert t.notes == [('Thesis (S.M. and M.B.A.)--Massachusetts Institute of '
                        'Technology, Computation for Design and Optimization '
                        'Program, 2006.'),
                       'Includes bibliographical references (p. 1-2).',
                       'by Lei Zhang.']
    assert t.publisher == 'Massachusetts Institute of Technology'
    assert t.rdf_type == [BIBO.Thesis, PCDM.Object]
    assert t.rights_statement == ('MIT theses are protected by copyright. They'
                                  ' may be viewed, downloaded, or printed from'
                                  ' this source but further reproduction or '
                                  'distribution in any format is prohibited '
                                  'without written permission.')
    assert t.title == 'Sample Title.'


def test_set_thesis_full_text_property(xml, text_errors):
    mets = ET.parse(xml).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, ['Department One', 'Department Two'],
               errors)
    t.no_full_text = None

    assert t.no_full_text is None


def test_thesis_get_metadata_returns_turtle(xml, text_errors):
    mets = ET.parse(xml).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, ['Department One'],
               errors)
    m = t.get_metadata()

    # Check all prefix bindings
    assert b'@prefix bibo: <http://purl.org/ontology/bibo/> .' in m
    assert b'@prefix dcterms: <http://purl.org/dc/terms/> .' in m
    assert b'@prefix dctype: <http://purl.org/dc/dcmitype/> .' in m
    assert b'@prefix local: <http://example.com/> .' in m
    assert b'@prefix mods: <http://www.loc.gov/standards/mods/modsrdf/v1/#> .'\
        in m
    assert b'@prefix msl: <http://purl.org/montana-state/library/> .' in m
    assert b'@prefix pcdm: <http://pcdm.org/models#> .' in m
    assert b'@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .' in m
    assert b'@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .' in m
    assert b'@prefix xml: <http://www.w3.org/XML/1998/namespace> .' in m
    assert b'@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .' in m

    # Check a few metadata statements
    assert b'<>' in m
    assert b'a pcdm:Object' in m
    assert b'bibo:Thesis' in m
    assert b'dcterms:type dctype:Text' in m
    assert b'dcterms:title "Alternative Title."' in m
    assert b'local:encoded_text true' in m
    assert b'local:ligature_errors "None"' in m
    assert b'bibo:handle <http://hdl.handle.net/1721.1/39208>' in m
    assert b'msl:degreeGrantedForCompletion "M.B.A."' in m
    assert b'"S.M."' in m
    assert (b'local:degree_statement "Thesis (S.M. and M.B.A.)--Massachusetts '
            b'Institute of Technology, Computation for Design and Optimization'
            b' Program, 2006."' in m)
    assert (b'msl:associatedDepartment "Department One"' in m)
    assert b'local:handle_part "39208"' in m


def test_thesis_handles_missing_metadata_fields(xml_missing_fields,
                                                text_errors):
    mets = ET.parse(xml_missing_fields).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis-02')
    t = Thesis('thesis-02', mets, ['Test department'], errors)

    assert t.abstract is None
    assert t.advisor is None
    assert t.copyright_date is None
    assert t.degree is None
    assert t.degree_statement is None
    assert t.department == ['Test department']
    assert t.encoded_text is None
    assert t.handle is None
    assert t.handle_part is None
    assert t.issue_date is None
    assert t.ligatures is None
    assert t.no_full_text is None
    assert t.notes is None
    assert t.title is None


def test_thesis_create_file_sparql_update_is_correct(xml, text_errors):
    mets = ET.parse(xml).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, errors)

    s = t.create_file_sparql_update('.pdf')
    assert s == ('PREFIX dcterms: <http://purl.org/dc/terms/> PREFIX pcdm: '
                 '<http://pcdm.org/models#> PREFIX ebucore: '
                 '<http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#> '
                 'INSERT { <> a pcdm:File ; dcterms:language "eng" ; '
                 'dcterms:extent "109 p." . } WHERE { }')

    s = t.create_file_sparql_update('.txt')
    assert s == ('PREFIX dcterms: <http://purl.org/dc/terms/> PREFIX pcdm: '
                 '<http://pcdm.org/models#> PREFIX ebucore: '
                 '<http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#> '
                 'INSERT { <> a pcdm:File ; dcterms:language "eng" ; '
                 'ebucore:hasEncodingFormat "utf-8" . } WHERE { }')


def test_thesis_create_file_sparql_update_missing_fields(xml_missing_fields,
                                                         text_errors):
    mets = ET.parse(xml_missing_fields).getroot()
    errors = parse_text_encoding_errors(text_errors).get('thesis')
    t = Thesis('thesis', mets, errors)

    s = t.create_file_sparql_update('.pdf')
    assert s == ('PREFIX dcterms: <http://purl.org/dc/terms/> PREFIX pcdm: '
                 '<http://pcdm.org/models#> PREFIX ebucore: '
                 '<http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#> '
                 'INSERT { <> a pcdm:File . } WHERE { }')


def test_parse_text_encoding_errors_creates_dict(text_errors):
    d = parse_text_encoding_errors(text_errors)
    assert type(d) == dict
    assert d['thesis']['Encoded text old file'] == '1'


def test_transaction_commits(fedora):
    with transaction('mock://example.com/rest/') as t:
        assert t == 'mock://example.com/rest/tx:123456789'


def test_transaction_with_error_raises_exception(fedora):
    with pytest.raises(RuntimeError):
        with transaction('mock://example.com/rest/'):
            raise


def test_transaction_commit_fail_raises_exception(fedora_errors):
    with pytest.raises(requests.exceptions.HTTPError):
        with transaction('mock://example.com/rest/'):
            pass


def test_create_container_is_successful(fedora, turtle):
    r = None
    with transaction('mock://example.com/rest/') as t:
        uri = t + '/theses/thesis'
        r = create_container(uri, turtle)
    assert r.status_code == 201


def test_create_container_failure_raises_error(fedora_errors, turtle):
    with pytest.raises(requests.exceptions.HTTPError):
        uri = 'mock://example.com/rest/tx:error/theses/thesis'
        create_container(uri, turtle)


def test_upload_file_is_successful(fedora, pdf):
    r = None
    with transaction('mock://example.com/rest/') as t:
        uri = t + '/theses/thesis/thesis.pdf/'
        r = upload_file(uri, pdf, 'application/pdf')
    assert r == 201


def test_upload_file_failure_raises_error(fedora_errors, pdf):
    with pytest.raises(requests.exceptions.HTTPError):
        uri = 'mock://example.com/rest/tx:error/theses/thesis/thesis.pdf'
        upload_file(uri, pdf, 'application/pdf')


def test_add_file_metadata_is_successful(fedora, sparql, auth=None):
    r = None
    with transaction('mock://example.com/rest/') as t:
        uri = t + '/theses/thesis/thesis.pdf/fcr:metadata'
        r = update_metadata(uri, sparql)
    assert r == 204


def test_add_file_metadata_failure_raises_error(fedora_errors, sparql,
                                                auth=None):
    with pytest.raises(requests.exceptions.HTTPError):
        uri = ('mock://example.com/rest/tx:error/theses/thesis/thesis.pdf/'
               'fcr:metadata')
        update_metadata(uri, sparql)
