from dataclasses import dataclass

import psutil

from ..service import Component, EndpointRegistry


@dataclass
class VirtualMemory:
    total: int
    available: int
    percent: float
    used: int
    free: int
    active: int
    inactive: int
    cached: int
    shared: int


@dataclass
class SwapMemory:
    total: int
    used: int
    free: int
    percent: float
    sin: int
    sout: int


@dataclass
class MemoryInfoResult:
    virtual_memory: VirtualMemory
    swap_memory: SwapMemory


class Memory(Component):
    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add("get-memory-info", self.info, "Available system memory")

    async def info(self) -> MemoryInfoResult:
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryInfoResult(
            VirtualMemory(
                total=virtual.total,
                available=virtual.available,
                percent=virtual.percent,
                used=virtual.used,
                free=virtual.free,
                active=virtual.active,
                inactive=virtual.inactive,
                cached=virtual.cached,
                shared=virtual.shared,
            ),
            SwapMemory(
                total=swap.total,
                used=swap.used,
                free=swap.free,
                percent=swap.percent,
                sin=swap.sin,
                sout=swap.sout,
            ),
        )
