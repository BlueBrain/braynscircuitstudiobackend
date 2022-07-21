from rest_framework import serializers


class ResourcesSerializer(serializers.Serializer):
    Queue = serializers.CharField(source="queue")
    Nodes = serializers.IntegerField(source="nodes")
    Runtime = serializers.CharField(source="runtime")
    NodeConstraints = serializers.CharField(source="node_constraints")
    Exclusive = serializers.BooleanField(source="exclusive")
    Memory = serializers.CharField(source="memory")
    Comment = serializers.CharField(
        source="comment",
        required=False,
    )


class JobListResponseSerializer(serializers.Serializer):
    jobs = serializers.ListField(child=serializers.CharField())


class CreateJobSerializer(serializers.Serializer):
    Project = serializers.CharField(
        source="project",
    )
    Stdin = serializers.CharField(
        source="stdin",
        required=False,
    )
    Executable = serializers.CharField(
        source="executable",
        required=False,
    )
    Name = serializers.CharField(
        source="name",
    )
    haveClientStageIn = serializers.BooleanField(
        source="have_client_stage_in",
    )
    Resources = ResourcesSerializer(
        source="resources",
    )
    Tags = serializers.ListField(
        child=serializers.CharField(),
        source="tags",
    )


class SubmissionPreferencesSerializer(serializers.Serializer):
    UC_OAUTH_BEARER_TOKEN = serializers.ListField(child=serializers.CharField())


class JobStatusResponseSerializer(serializers.Serializer):
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

    name = serializers.CharField()
    queue = serializers.CharField()
    status = serializers.CharField()
    resourceStatus = serializers.CharField(source="resource_status")
    statusMessage = serializers.CharField(
        source="status_message",
        allow_blank=True,
    )
    owner = serializers.CharField()
    currentTime = serializers.DateTimeField(source="current_time")
    terminationTime = serializers.DateTimeField(source="termination_time")
    submissionTime = serializers.DateTimeField(source="submission_time")
    submissionPreferences = SubmissionPreferencesSerializer(source="submission_preferences")
    log = serializers.ListField(child=serializers.CharField())


class UnicoreDirContentItemSerializer(serializers.Serializer):
    owner = serializers.CharField()
    size = serializers.IntegerField()
    last_accessed = serializers.DateTimeField(source="lastAccessed")
    is_directory = serializers.BooleanField(source="isDirectory")
    group = serializers.CharField()


class UnicoreStorageResponseSerializer(serializers.Serializer):
    owner = serializers.CharField()
    children = serializers.ListField(child=serializers.CharField())
    content = serializers.DictField(child=UnicoreDirContentItemSerializer())
