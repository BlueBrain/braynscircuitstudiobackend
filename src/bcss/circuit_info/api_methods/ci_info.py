from bcss.circuit_info.schemas.ci_info import (
    CircuitInfoGeneralInfoRequestSchema,
    CircuitInfoGeneralInfoResponseSchema,
)
from bcss.consumer import BCSSConsumer


@BCSSConsumer.register_method(
    request_schema=CircuitInfoGeneralInfoRequestSchema,
    response_schema=CircuitInfoGeneralInfoResponseSchema,
)
def ci_get_general_info():
    raise NotImplementedError
