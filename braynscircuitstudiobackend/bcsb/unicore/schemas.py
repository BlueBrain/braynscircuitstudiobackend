from marshmallow import Schema, fields, EXCLUDE


def dump_schema(schema: type(Schema), data: dict):
    return schema().dump(data)


def load_schema(schema: type(Schema), raw_data):
    return schema().load(raw_data)


class ResourcesSchema(Schema):
    queue = fields.String(data_key="Queue")
    nodes = fields.Integer(data_key="Nodes")
    cpus_per_node = fields.Integer(data_key="CPUsPerNode")
    runtime = fields.String(data_key="Runtime")
    node_constraints = fields.String(data_key="NodeConstraints")
    exclusive = fields.Boolean(data_key="Exclusive")
    memory = fields.String(data_key="Memory")


class JobListResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    jobs = fields.List(fields.String())


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


class SubmissionPreferencesSchema(Schema):
    UC_OAUTH_BEARER_TOKEN = fields.List(fields.String())


class JobStatusResponseSchema(Schema):
    """
    {
        "owner": "CN=naskret, O=Ecole polytechnique federale de Lausanne (EPFL), L=Lausanne, ST=Vaud, C=CH",
        "submissionPreferences": {
            "UC_OAUTH_BEARER_TOKEN": [
                "ey...JQ"
            ]
        },
        "log": [
            "Mon Jan 24 16:07:26 CET 2022: Created with ID fb82eb95-04eb-4fca-9b7e-2650c499ca45",
            "Mon Jan 24 16:07:26 CET 2022: Created with type 'JSDL'",
            "Mon Jan 24 16:07:26 CET 2022: Client: Name: CN=naskret,O=Ecole polytechnique federale de Lausanne (EPFL),L=Lausanne,ST=Vaud,C=CH\nXlogin: uid: [naskret], gids: [addingOSgroups: true]\nRole: user: role from attribute source\nSecurity tokens: User name: CN=naskret,O=Ecole polytechnique federale de Lausanne (EPFL),L=Lausanne,ST=Vaud,C=CH\nDelegation to consignor status: true, core delegation status: false\nMessage signature status: UNCHECKED\nClient's original IP: 128.179.254.207",
            "Mon Jan 24 16:07:27 CET 2022: Using default execution environment.",
            "Mon Jan 24 16:07:27 CET 2022: No staging in needed.",
            "Mon Jan 24 16:07:27 CET 2022: Status set to READY.",
            "Mon Jan 24 16:07:27 CET 2022: Status set to PENDING.",
            "Mon Jan 24 16:07:27 CET 2022: No application to execute, changing action status to POSTPROCESSING",
            "Mon Jan 24 16:07:27 CET 2022: Status set to DONE.",
            "Mon Jan 24 16:07:27 CET 2022: Result: Success.",
            "Mon Jan 24 16:07:27 CET 2022: Total: 0.28 sec., Stage-in: 0.00 sec., Stage-out: 0.00 sec., Datamovement: 1 %"
        ],
        "_links": {
            "action:start": {
                "description": "Start",
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/start"
            },
            "action:restart": {
                "description": "Restart",
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/restart"
            },
            "workingDirectory": {
                "description": "Working directory",
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/storages/fb82eb95-04eb-4fca-9b7e-2650c499ca45-uspace"
            },
            "self": {
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45"
            },
            "action:abort": {
                "description": "Abort",
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/abort"
            },
            "parentTSS": {
                "description": "Parent TSS",
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/sites/800e4953-0c70-4e86-a331-c8515f463df1"
            }
        },
        "acl": [],
        "submissionTime": "2022-01-24T16:07:27+0100",
        "statusMessage": "",
        "tags": [],
        "currentTime": "2022-01-24T16:07:48+0100",
        "resourceStatus": "READY",
        "terminationTime": "2022-02-23T16:07:26+0100",
        "name": "UNICORE_Job",
        "queue": "N/A",
        "status": "SUCCESSFUL"
    }
    """

    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    queue = fields.String()
    status = fields.String()
    resource_status = fields.String()
    status_message = fields.String(data_key="statusMessage")
    owner = fields.String()
    current_time = fields.DateTime(data_key="currentTime")
    termination_time = fields.DateTime(data_key="terminationTime")
    submission_time = fields.DateTime(data_key="submissionTime")
    submission_preferences = fields.Nested(
        SubmissionPreferencesSchema(), data_key="submissionPreferences"
    )
    log = fields.List(fields.String())
