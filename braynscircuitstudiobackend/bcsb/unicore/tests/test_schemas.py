from bcsb.unicore.schemas import CreateJobSchema, dump_schema


def test_dump_schema():
    assert dump_schema(CreateJobSchema, {}) == {}

    data = {
        "project": "proj3",
        "name": "My circuit",
        "have_client_stage_in": True,
        "tags": ["visualization"],
        "resources": {
            "queue": "prod",
            "nodes": 1,
            "cpus_per_node": 72,
            "runtime": "8h",
            "node_constraints": "cpu",
            "memory": "128G",
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
            "CPUsPerNode": 72,
            "Runtime": "8h",
            "NodeConstraints": "cpu",
            "Memory": "128G",
            "Exclusive": True,
        },
    }
    assert dump_schema(CreateJobSchema, data) == expected_output
