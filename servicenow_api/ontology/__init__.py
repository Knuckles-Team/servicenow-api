"""ServiceNow ITSM ontology contribution (CONCEPT:KG-2.320).

Data-only subpackage: it carries ``servicenow.ttl`` (the ``owl:Ontology``
``http://knuckles.team/kg/servicenow`` module — incidents, changes, CMDB
configuration items and their relationships) which the agent-utilities hub
federates in via the ``agent_utilities.ontology_providers`` entry-point. It holds
no business logic and no heavy imports so the hub can resolve it cheaply.
"""
