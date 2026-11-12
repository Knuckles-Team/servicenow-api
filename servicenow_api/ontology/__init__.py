"""ServiceNow ITSM ontology contribution (CONCEPT:AU-KG.ontology.federation-provider-leg).

Data-only subpackage: it carries ``servicenow.ttl`` (the ``owl:Ontology``
``https://knuckles-team.github.io/ontology/connector/servicenow`` module — incidents, changes, CMDB
configuration items and their relationships) which the Arbora hub
federates in via the ``scion_sdk.ontology_providers`` entry-point. It holds
no business logic and no heavy imports so the hub can resolve it cheaply.
"""
