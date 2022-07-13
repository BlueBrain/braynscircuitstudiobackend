from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.schema import GetSessionsResponseSchema


@CircuitStudioConsumer.register_method(response_schema=GetSessionsResponseSchema)
def get_sessions():
    return {
        "sessions": [],
    }
