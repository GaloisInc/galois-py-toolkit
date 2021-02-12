import saw
from saw.llvm import Contract, void
from saw.llvm_types import i32

import os
import unittest
import os.path


class Swap(Contract):
    def __init__(self) -> None:
        super().__init__()
        self.ty = i32

    def specification(self) -> None:
        x = self.fresh_var(self.ty, "x")
        y = self.fresh_var(self.ty, "y")
        x_ptr = self.alloc(self.ty, points_to=x)
        y_ptr = self.alloc(self.ty, points_to=y)

        self.execute_func(x_ptr, y_ptr)

        self.points_to(x_ptr, y)
        self.points_to(y_ptr, x)
        self.returns(void)


class SwapEasyTest(unittest.TestCase):
    def test_swap(self):
        saw.connect(saw.find_saw_server() + " socket")
        if __name__ == "__main__": saw.view(saw.LogResults())

        dir_path = os.path.dirname(os.path.realpath(__file__))
        swap_bc = os.path.join(dir_path, 'swap.bc')

        mod = saw.llvm_load_module(swap_bc)

        result = saw.llvm_verify(mod, 'swap', Swap())
        self.assertIs(result.is_success(), True)
        saw.disconnect()


if __name__ == "__main__":
    unittest.main()
