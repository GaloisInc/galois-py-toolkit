import os
import os.path
import unittest
from saw import *
from saw.llvm import Contract, SetupVal, FreshVar, cryptol, struct, LLVMType, void
import saw.llvm_types as ty


def ptr_to_fresh(c : Contract, ty : LLVMType, name : Optional[str] = None) -> Tuple[FreshVar, SetupVal]:
    """Add to``Contract`` ``c`` an allocation of a pointer of type ``ty`` initialized to an unknown fresh value.
    
    :returns A fresh variable bound to the pointers initial value and the newly allocated pointer. (The fresh
             variable will be assigned ``name`` if provided/available.)"""
    var = c.fresh_var(ty, name)
    ptr = c.alloc(ty, points_to = var)
    return (var, ptr)


class SetContract(Contract):
    def specification(self):
        (_, x_p) = ptr_to_fresh(self, ty.array(2, ty.i32), "x")
        p = self.alloc(ty.alias('struct.s'), points_to=struct(x_p))

        self.execute_func(p)

        self.points_to(p, struct(x_p))
        self.points_to(x_p, cryptol('[0, 0] : [2][32]'))
        self.returns(void)


class AddContract(Contract):
    def specification(self):
        (x, x_p) = ptr_to_fresh(self, ty.array(2, ty.i32), "x")
        p = self.alloc(ty.alias('struct.s'), points_to=struct(x_p))

        self.execute_func(p)

        self.returns(cryptol(f'{x.name()}@0 + {x.name()}@1'))


class IdContract(Contract):
    def specification(self):
        (x, x_p) = ptr_to_fresh(self, ty.array(2, ty.i32), "x")
        p = self.alloc(ty.alias('struct.s'), points_to=struct(x_p))

        self.execute_func(p)

        self.returns(p)


class LLVMStructTest(unittest.TestCase):
    def test_llvm_struct(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        connect(find_saw_server() + " socket")
        if __name__ == "__main__": view(LogResults())
        bcname = os.path.join(dir_path, 'llvm_struct.bc')
        mod = llvm_load_module(bcname)

        # crucible_llvm_verify m "set_indirect" [] false set_spec abc;
        self.assertIs(llvm_verify(mod, 'set_indirect', SetContract()).is_success(), True)
        # crucible_llvm_verify m "add_indirect" [] false add_spec abc;
        self.assertIs(llvm_verify(mod, 'add_indirect', AddContract()).is_success(), True)
        # crucible_llvm_verify m "s_id" [] false id_spec abc;
        self.assertIs(llvm_verify(mod, 's_id', IdContract()).is_success(), True)
        disconnect()

if __name__ == "__main__":
    unittest.main()