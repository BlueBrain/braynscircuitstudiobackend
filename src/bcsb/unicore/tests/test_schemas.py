from bcsb.unicore.schemas import CreateJobSchema
from common.utils.schemas import dump_schema


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
    assert dump_schema(CreateJobSchema, data) == expected_output
