from marshmallow import Schema, fields


class ResourcesSchema(Schema):
    queue = fields.String(data_key="Queue")
    nodes = fields.Integer(data_key="Nodes")
    cpus_per_node = fields.Integer(data_key="CPUsPerNode")
    runtime = fields.String(data_key="Runtime")
    node_constraints = fields.String(data_key="NodeConstraints")
    exclusive = fields.Boolean(data_key="Exclusive")
    memory = fields.String(data_key="Memory")


class CreateJobSchema(Schema):
    """
    {
        "Project": "proj3",
        "Name": "Visualization of circuit",
        "haveClientStageIn": True,
        "Resources": {
            "Queue": "prod",
            "Nodes": 1,
            "CPUsPerNode": 72,
            "Runtime": 600,  # 3600,
            "NodeConstraints": "cpu",
            "Memory": "128G",
        },
        "Tags": ["visualization"],
    }
    """

    project = fields.String(data_key="Project")
    name = fields.String(data_key="Name")
    have_client_stage_in = fields.Boolean(data_key="haveClientStageIn")
    resources = fields.Nested(ResourcesSchema(), data_key="Resources")
    tags = fields.List(fields.String(), data_key="Tags")
