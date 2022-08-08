import logging

from bcsb.allocations.models import Allocation
from bcsb.brayns.serializers import (
    StartBraynsRequestSerializer,
    StartBraynsResponseSerializer,
)
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.sessions.session_service import make_session_service
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class StartNewSessionMethod(JSONRPCMethod):
    """
    Starts a full new Brayns/BCSS session on a new node.
    """

    request_serializer_class = StartBraynsRequestSerializer
    response_serializer_class = StartBraynsResponseSerializer

    async def run(self):
        session_service = await make_session_service(
            user=self.request.user,
            token=self.request.token,
        )
        params = self.request.params
        progress_notifier = ProgressNotifier(self.request)
        allocation: Allocation = await session_service.start(
            progress_notifier=progress_notifier,
            project=params["project"],
        )

        return {
            "host": allocation.hostname,
            "allocation_id": allocation.id,
        }
