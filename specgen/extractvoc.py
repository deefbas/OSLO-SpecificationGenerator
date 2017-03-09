# =================================================================
# Copyrighted 2016 by Laurens De Vocht - iMinds - UGent
# All rights reserved
# =================================================================

import rdflib
import os
import re
import json
import datetime

PREFIXES = """prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix dcat: <http://www.w3.org/ns/dcat#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix prov: <http://www.w3.org/ns/prov#>
prefix content: <http://www.w3.org/2011/content#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix locn: <http://www.w3.org/ns/locn#>
prefix gsp: <http://www.opengis.net/ont/geosparql#>
prefix geo: <https://www.iana.org/assignments/media-types/application/vnd.geo+>
prefix schema: <http://schema.org/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix adms: <http://www.w3.org/ns/adms#>
prefix iso: <http://def.seegrid.csiro.au/isotc211/iso19115/2003/metadata#>
prefix cc: <http://creativecommons.org/ns#>
prefix rec: <http://www.w3.org/2001/02pd/rec54#>
prefix vann: <http://purl.org/vocab/vann/>
prefix wdsr: <http://www.w3.org/2007/05/powder-s#>
"""


def convert(rdf):
    g = rdflib.Graph()
    if rdf.endswith('.xml'):
        g.parse(os.path.realpath(rdf),
                format='xml')
    else:
        g.parse(os.path.realpath(rdf),
                format=rdflib.util.guess_format(os.path.realpath(rdf)))

    result = ""

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              ?v a owl:Ontology .
              OPTIONAL { ?v vann:preferredNamespacePrefix ?prefix } .
              OPTIONAL { ?v vann:preferredNamespaceUri ?pUri } .
              OPTIONAL { ?v rdfs:label ?label . FILTER(LANG(?label) = "" || LANGMATCHES(LANG(?label), "en")) } .
              OPTIONAL { ?v dcterms:abstract ?abstract . FILTER(LANG(?abstract) = "" || LANGMATCHES(LANG(?abstract), "en")) } .
              OPTIONAL { ?v cc:attributionName ?attribution } .
              OPTIONAL { ?v cc:attributionUrl ?attributionUrl } .
              OPTIONAL { ?v dcterms:issued ?issued } .
              OPTIONAL { ?v dcterms:modified ?modified } .
              OPTIONAL { ?v dcterms:rights ?rights } .
              OPTIONAL { ?v dcterms:title ?title } .
              OPTIONAL {
                ?v dcterms:mediator ?m .
                ?m foaf:homepage ?mhomepage .
                ?m foaf:mbox ?mmbox .
                ?m foaf:name ?mname .
              } .
           } LIMIT 1""")

    result += "[metadata]\n"

    for row in qres:
        if row['v'] is not None:
            result += "uri=%s\n" % row['v']
        if row['prefix'] is not None:
            result += "prefix=%s\n" % row['prefix']
        if row['pUri'] is not None:
            result += "prefUri=%s\n" % row['pUri']
        if row['label'] is not None:
            result += "label=%s\n" % row['label']
        if row['title'] is not None:
            result += "title=%s\n" % row['title']
        if row['abstract'] is not None:
            result += "abstract=%s\n" % re.sub(r'\n', ' ', row['abstract'])
        if row['issued'] is not None:
            result += "issued=%s\n" % row['issued']
        if row['modified'] is not None:
            result += "modified=%s\n" % row['modified']
        if row['rights'] is not None:
            result += "rights=%s\n" % row['rights']
        if row['m'] is not None:
            if row['mname'] is not None:
                result += "mname=%s\n" % row['mname']
            if row['mhomepage'] is not None:
                result += "mhomepage=%s\n" % row['mhomepage']
            if row['mmbox'] is not None:
                result += "mmbox=%s\n" % row['mmbox']

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              ?v a owl:Ontology .
              ?v rec:editor ?e .
              OPTIONAL { ?e schema:affiliation ?affiliation .
                         ?affiliation foaf:homepage ?ahomepage .
                         ?affiliation foaf:name ?aName } .
              OPTIONAL { ?e foaf:homepage ?mhomepage } .
              OPTIONAL { ?e foaf:mbox ?mmbox } .
              OPTIONAL { ?e foaf:name ?mname } .
           }""")

    editors = []

    for row in qres:
        if row['e'] is not None:
            editors.append(row['e'])
            result += '\n[editor:%s]\n' % row['e']
            if row['mname'] is not None:
                result += "mname=%s\n" % row['mname']
            if row['mhomepage'] is not None:
                result += "mhomepage=%s\n" % row['mhomepage']
            if row['mmbox'] is not None:
                result += "mmbox=%s\n" % row['mmbox']
            if row['affiliation'] is not None:
                result += "aName=%s\n" % row['aName']
                result += "ahomepage=%s\n" % row['ahomepage']

    if len(editors) > 0:
        result += '\n[editors]\n'
        result += 'list=%s\n' % ','.join(editors)

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              ?v a owl:Ontology .
              ?v foaf:maker ?m .
              OPTIONAL { ?m schema:affiliation ?affiliation . ?affiliation foaf:homepage ?ahomepage . ?affiliation foaf:name ?aName } .
              OPTIONAL { ?m foaf:homepage ?mhomepage }.
              OPTIONAL { ?m foaf:mbox ?mmbox }.
              OPTIONAL { ?m foaf:name ?mname }.
           }""")

    makers = []

    for row in qres:
        if row['m'] is not None:
            makers.append(row['m'])
            result += '\n[maker:%s]\n' % row['m']
            if row['mname'] is not None:
                result += "mname=%s\n" % row['mname']
            if row['mhomepage'] is not None:
                result += "mhomepage=%s\n" % row['mhomepage']
            if row['mmbox'] is not None:
                result += "mmbox=%s\n" % row['mmbox']
            if row['affiliation'] is not None:
                result += "aname=%s\n" % row['aName']
                result += "ahomepage=%s\n" % row['ahomepage']

    if len(makers) > 0:
        result += '\n[makers]\n'
        result += 'list=%s\n' % ','.join(makers)

    result += "\n[glance]\n"

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { ?class a owl:Class } UNION { ?class a rdfs:Class } .
              ?class rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "en"))
           }""")

    classes = []
    class_uris = []

    for row in qres:
        if row['class'] is not None:
            classes.append(row['label'])
            class_uris.append(row['class'])

    result += "classes=%s\n" % ",".join(classes)

    result += "class_uris=%s\n" % ",".join(class_uris)

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { ?class a owl:Class } UNION { ?class a rdfs:Class } .
              ?class rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "nl"))
           }""")

    classes = []
    class_uris = []

    for row in qres:
        if row['class'] is not None:
            classes.append(row['label'])
            class_uris.append(row['class'])

    result += "classes_nl=%s\n" % ",".join(classes)

    result += "class_uris_nl=%s\n" % ",".join(class_uris)

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { { ?p a owl:ObjectProperty } UNION { ?p a owl:DatatypePoperty } } UNION { ?p a rdf:Property } .
              ?p rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "en"))
           }""")

    properties = []
    prop_uris = []

    for row in qres:
        if row['p'] is not None:
            properties.append(row['label'])
            prop_uris.append(row['p'])

    result += "properties=%s\n" % ",".join(properties)

    result += "prop_uris=%s\n" % ",".join(prop_uris)

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { { ?p a owl:ObjectProperty } UNION { ?p a owl:DatatypePoperty } } UNION { ?p a rdf:Property } .
              ?p rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "nl"))
           }""")

    properties = []
    prop_uris = []

    for row in qres:
        if row['p'] is not None:
            properties.append(row['label'])
            prop_uris.append(row['p'])

    result += "properties_nl=%s\n" % ",".join(properties)

    result += "prop_uris_nl=%s\n" % ",".join(prop_uris)

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { ?class a owl:Class } UNION { ?class a rdfs:Class } .
              ?class rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "en")) .
              OPTIONAL { ?class dcterms:identifier ?identifier } .
              ?class rdfs:comment ?comment .
              FILTER(LANGMATCHES(LANG(?comment), "en")) .
              OPTIONAL { ?class vann:usageNote ?usageNote } .
              OPTIONAL { ?class rdfs:isDefinedBy ?definedBy } .
              OPTIONAL { ?class wdsr:describedBy ?describedBy } .
           }""")

    for row in qres:
        if row['class'] is not None:
            result += '\n[class:%s]\n' % row['class']
            if row['label'] is not None:
                result += "label=%s\n" % row['label']
            if row['identifier'] is not None:
                result += "identifier=%s\n" % row['identifier']
            if row['comment'] is not None:
                result += "comment=%s\n" % re.sub(r'\n', ' ', row['comment'])
            if row['usageNote'] is not None:
                result += "usageNote=%s\n" % re.sub(r'\n', ' ', row['usageNote'])
            if row['definedBy'] is not None:
                result += "definedBy=%s\n" % row['definedBy']
            if row['describedBy'] is not None:
                result += "describedBy=%s\n" % row['describedBy']

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { ?class a owl:Class } UNION { ?class a rdfs:Class } .
              ?class rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "nl")) .
              OPTIONAL { ?class dcterms:identifier ?identifier } .
              ?class rdfs:comment ?comment .
              FILTER(LANGMATCHES(LANG(?comment), "nl")) .
              OPTIONAL { ?class vann:usageNote ?usageNote } .
              OPTIONAL { ?class rdfs:isDefinedBy ?definedBy } .
              OPTIONAL { ?class wdsr:describedBy ?describedBy } .
           }""")

    for row in qres:
        if row['class'] is not None:
            result += '\n[class_nl:%s]\n' % row['class']
            if row['label'] is not None:
                result += "label=%s\n" % row['label']
            if row['identifier'] is not None:
                result += "identifier=%s\n" % row['identifier']
            if row['comment'] is not None:
                result += "comment=%s\n" % re.sub(r'\n', ' ', row['comment'])
            if row['usageNote'] is not None:
                result += "usageNote=%s\n" % re.sub(r'\n', ' ',
                                                    row['usageNote'])
            if row['definedBy'] is not None:
                result += "definedBy=%s\n" % row['definedBy']
            if row['describedBy'] is not None:
                result += "describedBy=%s\n" % row['describedBy']

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { { ?p a owl:ObjectProperty } UNION { ?p a owl:DatatypePoperty } } UNION { ?p a rdf:Property } .
              ?p rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "en")) .
              OPTIONAL { ?p dcterms:identifier ?identifier } .
              ?p rdfs:comment ?comment .
              FILTER(LANGMATCHES(LANG(?comment), "en")) .
              OPTIONAL { ?p rdfs:domain ?domain } .
              OPTIONAL { ?p rdfs:range ?range } .
              OPTIONAL { ?p vann:usageNote ?usageNote } .
              OPTIONAL { ?p rdfs:isDefinedBy ?definedBy } .
              OPTIONAL { ?p wdsr:describedBy ?describedBy } .
           }""")

    for row in qres:
        if row['p'] is not None:
            result += '\n[property:%s]\n' % row['p']
            if row['label'] is not None:
                result += "label=%s\n" % row['label']
            if row['identifier'] is not None:
                result += "identifier=%s\n" % row['identifier']
            if row['domain'] is not None:
                result += "domain=%s\n" % row['domain']
            if row['range'] is not None:
                result += "range=%s\n" % row['range']
            if row['comment'] is not None:
                result += "comment=%s\n" % re.sub(r'\n', ' ', row['comment'])
            if row['usageNote'] is not None:
                result += "usageNote=%s\n" % re.sub(r'\n', ' ', row['usageNote'])
            if row['definedBy'] is not None:
                result += "definedBy=%s\n" % row['definedBy']
            if row['describedBy'] is not None:
                result += "describedBy=%s\n" % row['describedBy']

    qres = g.query(  # Mandatory -> required; Optional -> OPTIONAL
        PREFIXES +
        """SELECT DISTINCT *
           WHERE {
              { { ?p a owl:ObjectProperty } UNION { ?p a owl:DatatypePoperty } } UNION { ?p a rdf:Property } .
              ?p rdfs:label ?label .
              FILTER(LANGMATCHES(LANG(?label), "nl")) .
              OPTIONAL { ?p dcterms:identifier ?identifier } .
              ?p rdfs:comment ?comment .
              FILTER(LANGMATCHES(LANG(?comment), "nl")) .
              OPTIONAL { ?p rdfs:domain ?domain } .
              OPTIONAL { ?p rdfs:range ?range } .
              OPTIONAL { ?p vann:usageNote ?usageNote } .
              OPTIONAL { ?p rdfs:isDefinedBy ?definedBy } .
              OPTIONAL { ?p wdsr:describedBy ?describedBy } .
           }""")

    for row in qres:
        if row['p'] is not None:
            result += '\n[property_nl:%s]\n' % row['p']
            if row['label'] is not None:
                result += "label=%s\n" % row['label']
            if row['identifier'] is not None:
                result += "identifier=%s\n" % row['identifier']
            if row['domain'] is not None:
                result += "domain=%s\n" % row['domain']
            if row['range'] is not None:
                result += "range=%s\n" % row['range']
            if row['comment'] is not None:
                result += "comment=%s\n" % re.sub(r'\n', ' ', row['comment'])
            if row['usageNote'] is not None:
                result += "usageNote=%s\n" % re.sub(r'\n', ' ',
                                                    row['usageNote'])
            if row['definedBy'] is not None:
                result += "definedBy=%s\n" % row['definedBy']
            if row['describedBy'] is not None:
                result += "describedBy=%s\n" % row['describedBy']

    print(result)
    return result
