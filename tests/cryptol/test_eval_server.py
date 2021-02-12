import os
from pathlib import Path
import signal
import subprocess
import time
import unittest
from distutils.spawn import find_executable
import argo_client.connection as argo


class CryptolEvalServerTests(unittest.TestCase):
    # Connection to cryptol
    c = None
    # process running the server
    p = None

    @classmethod
    def setUpClass(self):
        dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
        cryptol_path = dir_path.joinpath('data')
        env = os.environ.copy()
        env['CRYPTOLPATH'] = cryptol_path
        
        if find_executable("cryptol-eval-server"):
            p = subprocess.Popen(
                ["cryptol-eval-server", "http", "/", "--port", "50005", "--module", "M"],
                stdout=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=env)
        else:
            raise RuntimeError('Failed to find cryptol-eval-server executable in PATH')
        time.sleep(3)
        assert(p is not None)
        poll_result = p.poll()
        if poll_result is not None:
            print(poll_result)
            print(p.stdout.read())
            print(p.stderr.read())
        assert(poll_result is None)

        self.p = p
        self.c = argo.ServerConnection(argo.HttpProcess('http://localhost:50005/'))


    @classmethod
    def tearDownClass(self):
        os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
        super().tearDownClass()


    @classmethod
    def test_eval_server(self):
        c = self.c
        mid = c.send_query("evaluate expression", {"expression": {"expression":"call","function":"f","arguments":[{"expression":"bits","encoding":"hex","data":"ff","width":8}]}, "state": None})
        reply = c.wait_for_reply_to(mid)
        assert('result' in reply)
        assert('answer' in reply['result'])
        assert('value' in reply['result']['answer'])
        assert(reply['result']['answer']['value'] ==
            {'data': [{'data': 'ff', 'width': 8, 'expression': 'bits', 'encoding': 'hex'},
                        {'data': 'ff', 'width': 8, 'expression': 'bits', 'encoding': 'hex'}],
                'expression': 'sequence'})


if __name__ == "__main__":
    unittest.main()
