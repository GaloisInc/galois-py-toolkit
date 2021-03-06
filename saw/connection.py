from __future__ import annotations
import os
import signal
from distutils.spawn import find_executable
from argo_client.connection import ServerConnection, DynamicSocketProcess, StdIOProcess, HttpProcess
from argo_client.interaction import Interaction, Command
from .commands import *

from typing import Optional, Union, Any, List

# FIXME cryptol_path isn't always used...?
def connect(command: Union[str, ServerConnection, None] = None,
            *,
            cryptol_path: Optional[str] = None,
            persist: bool = False,
            url : Optional[str] = None) -> SAWConnection:
    """
    Connect to a (possibly new) Saw server process.

    :param command: A command to launch a new Saw server in socket mode (if provided).

    :param url: A URL at which to connect to an already running SAW 
    HTTP server.

    If no parameters are provided, the following are attempted in order:

    1. If the environment variable ``SAW_SERVER`` is set and referse to an executable,
    it is assumed to be a SAW server and will be used for a new ``socket`` connection.

    2. If the environment variable ``SAW_SERVER_URL`` is set, it is assumed to be
    the URL for a running SAW server in ``http`` mode and will be connected to.

    3. If an executable ``saw-remote-api`` is available on the ``PATH``
    it is assumed to be a SAW server and will be used for a new ``socket`` connection.

    """
    if command is not None:
        if url is not None:
            raise ValueError("A SAW server URL cannot be specified with a command currently.")
        return SAWConnection(command)
    elif url is not None:
        return SAWConnection(ServerConnection(HttpProcess(url)))
    elif (command := os.getenv('SAW_SERVER')) is not None and (command := find_executable(command)) is not None:
        return SAWConnection(command+" socket") # SAWConnection(ServerConnection(StdIOProcess(command+" stdio")))
    elif (url := os.getenv('SAW_SERVER_URL')) is not None:
        return SAWConnection(ServerConnection(HttpProcess(url)))
    elif (command := find_executable('saw-remote-api')) is not None:
        return SAWConnection(command+" socket")
    else:
        raise ValueError(
            """saw.connection.connect requires one of the following:",
            1) a command to launch a SAW server is the first positional argument,
            2) a URL to connect to a running SAW server is provided via the `url` keyword argument,
            3) the environment variable `SAW_SERVER` must refer to a valid server executable, or
            4) the environment variable `SAW_SERVER_URL` must refer to the URL of a running SAW server.""")

    return SAWConnection(command, persist=persist)


class SAWConnection:
    """A representation of a current user state in a session with SAW."""

    most_recent_result: Optional[Interaction]

    def __init__(self,
                 command_or_connection: Union[str, ServerConnection],
                 *, persist: bool = False) -> None:
        self.most_recent_result = None
        self.persist = persist
        if isinstance(command_or_connection, str):
            self.proc = DynamicSocketProcess(command_or_connection, persist=self.persist)
            self.server_connection = ServerConnection(self.proc)
        else:
            self.server_connection = command_or_connection

    def disconnect(self) -> None:
        if not self.persist:
            if self.proc and (pid := self.proc.pid()):
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            del self.server_connection
        

    def pid(self) -> Optional[int]:
        """Return the PID of the running server process."""
        return self.proc.pid()

    def running(self) -> bool:
        """Return whether the underlying server process is still running."""
        return self.proc.running()

    def snapshot(self) -> SAWConnection:
        """Return a ``SAWConnection`` that has the same process and state as
        the current connection. The new connection's state will be
        independent of the current state.
        """
        copy = SAWConnection(self.server_connection)
        copy.most_recent_result = self.most_recent_result
        return copy

    def protocol_state(self) -> Any:
        if self.most_recent_result is None:
            return None
        else:
            return self.most_recent_result.state()

    # Protocol messages
    def cryptol_load_file(self, filename: str) -> Command:
        self.most_recent_result = CryptolLoadFile(self, filename)
        return self.most_recent_result

    def llvm_load_module(self, name: str, bitcode_file: str)  -> Command:
        self.most_recent_result = LLVMLoadModule(self, name, bitcode_file)
        return self.most_recent_result

    def llvm_verify(self,
                    module: str,
                    function: str,
                    lemmas: List[str],
                    check_sat: bool,
                    contract: Any,
                    script: Any,
                    lemma_name: str) -> Command:
        self.most_recent_result = \
            LLVMVerify(self, module, function, lemmas, check_sat, contract, script, lemma_name)
        return self.most_recent_result

    def llvm_assume(self,
                    module: str,
                    function: str,
                    contract: Any,
                    lemma_name: str) -> Command:
        self.most_recent_result = \
            LLVMAssume(self, module, function, contract, lemma_name)
        return self.most_recent_result
