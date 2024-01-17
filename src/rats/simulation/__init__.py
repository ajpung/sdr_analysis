import os
from pathlib import Path
from threading import Thread
from typing import List, Any, Callable

try:
    import orekit
    from orekit.pyhelpers import setup_orekit_curdir
except ImportError:
    OREKIT_IMPORTED = False
else:
    OREKIT_IMPORTED = True


def _return_via_container(return_container: List[Any], func: Callable, *args) -> None:
    if len(return_container) != 1:
        raise ValueError("Return container must be a list of length 1")
    return_container[-1] = func(*args)


def safe_call(
    func: Callable, *args, check_exception: Callable | None = None, timeout: float = 5.0
) -> Any:
    """
    This method uses a thread to execute a function call so that it can safely
    detect when the call has failed to return in a reasonable amount of time. By
    providing an external exception check (see phase_base for example), it
    can recognize and alert the user when the job has thrown an exception.
    """
    # Use a shared-memory container to get results from Thread. It's a
    # shortcoming of the threading interface, but concurrent.futures
    # was hanging in the TimeoutError block, so this is more reliable
    dummy = object()  # Just need something in the list. Should be replaced
    response_container = [dummy]
    t = Thread(
        target=_return_via_container,
        args=(
            response_container,
            func,
        )
        + args,
        daemon=True,
    )
    t.start()
    t.join(timeout)
    if check_exception is not None:
        check_exception()
    if t.is_alive():
        raise TimeoutError(
            "Communication timed out but no exception was detected."
            " Consider increasing the timeout argument to wait longer."
        )
    result = response_container[-1]
    if result is dummy:
        raise ValueError(
            "The function call failed to update the container as expected."
        )
    return result


def get_or_init_orekit_vm(orekit_data_folder: str | Path = ""):
    if not OREKIT_IMPORTED:
        raise ValueError("Failed to import orekit. Unable to initialize the vm.")

    orekit_data_folder = orekit_data_folder or os.environ.get(
        "DW_OREKIT_DATA_PATH", "../../orekit-data/"
    )
    # Get the orekit jvm if it's already running. It should return almost
    # instantly, but sometimes it hangs, so give it a short timeout
    try:
        # Returns None if no VM exists
        vm = safe_call(orekit.getVMEnv, timeout=0.1)
    except TimeoutError:
        # Match the default in the event of a hanging process
        vm = None

    if vm is None:
        vm = orekit.initVM()
    setup_orekit_curdir(orekit_data_folder)
    return vm


from .asset import *
