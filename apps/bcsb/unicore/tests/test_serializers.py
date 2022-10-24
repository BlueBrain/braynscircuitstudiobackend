from bcsb.unicore.serializers import CreateJobSerializer


def test_dump_serializer():
    data = {
        "project": "proj3",
        "name": "My circuit",
        "have_client_stage_in": True,
        "tags": ["visualization"],
        "resources": {
            "queue": "prod",
            "nodes": 1,
            "runtime": "8h",
            "node_constraints": "cpu",
            "memory": "0",
            "exclusive": True,
        },
    }
    expected_output = {
        "Project": "proj3",
        "Name": "My circuit",
        "haveClientStageIn": True,
        "Tags": ["visualization"],
        "Resources": {
            "Queue": "prod",
            "Nodes": 1,
            "Runtime": "8h",
            "NodeConstraints": "cpu",
            "Memory": "0",
            "Exclusive": True,
        },
    }
    create_job_serializer = CreateJobSerializer(data)
    assert create_job_serializer.data == expected_output
