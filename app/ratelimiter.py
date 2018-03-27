# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
import asyncio
from typing import Callable, Any


class RateLimiter:
    class EventGroup:
        def __init__(self, call_time: float, delay: float):
            self.next_call_time = call_time + delay
            self.calls_left = 1

        def add_call(self, delay):
            self.next_call_time += delay
            self.calls_left += 1

        def remove_call(self):
            self.calls_left -= 1

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.event_groups = {}
        self.event_loop = event_loop

    async def remove_group(self, group: 'RateLimiter.EventGroup', token: str, delay: float):
        if group.calls_left == 0:
            await asyncio.sleep(delay)
            if group.calls_left == 0 and group.next_call_time < self.event_loop.time() and token in self.event_groups:
                if self.event_groups[token] is group:
                    del self.event_groups[token]

    async def wait_before_request(self, token: str, delay: float):
        time = self.event_loop.time()
        if token in self.event_groups:
            group = self.event_groups[token]
            delay_before_call = group.next_call_time - time
            group.add_call(delay)
            await asyncio.sleep(delay_before_call)
        else:
            group = self.EventGroup(time, delay)
            self.event_groups[token] = group
        group.remove_call()
        self.event_loop.create_task(self.remove_group(group, token, delay))
