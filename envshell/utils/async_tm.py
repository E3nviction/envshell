import concurrent
import time
import asyncio
import threading
from concurrent.futures import Future as ConcurrentFuture
from typing import Any

"""
Thanks to @kaipark for the following code.
"""

def create_background_task(target, interval, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}

    def loop_wrapper():
        if interval > 0:
            while True:
                target(*args, **kwargs)
                time.sleep(interval)
        else:
            target(*args, **kwargs)

    thread = threading.Thread(target=loop_wrapper, daemon=True)
    return thread

class AsyncTaskManager:
    _event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    _running_tasks: set = set()

    def __init__(self) -> None:
        """_summary_
        """
        # Start the asyncio event loop in a background thread
        event_loop_thread = threading.Thread(
            target=self._event_loop_worker,
            args=(self._event_loop,),
            daemon=True,
        )
        event_loop_thread.start()

    def _event_loop_worker(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def __del__(self) -> None:
        for task in self._running_tasks:
            task.cancel()

    def run(self, coroutine: Any) -> ConcurrentFuture: # Type Any is just a fallback
        # This callback will be called when the coroutine is done.
        def done(future: ConcurrentFuture) -> None:
            exception = future.exception()
            if exception:
                raise exception
            self._running_tasks.remove(future)

        # Run coroutine in bg
        future = asyncio.run_coroutine_threadsafe(coroutine, self._event_loop)
        future.add_done_callback(done)
        self._running_tasks.add(future) # we keep a pointer to the running task for __del__ handling
        return future


async def run_cmd_async(cmd, return_stderr: bool = False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    if return_stderr:
        return stdout, stderr
    else:
        return stdout