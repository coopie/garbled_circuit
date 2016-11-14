import garbled_circuit as gc

def test_running_circuit():
    def ret_1(): return 1
    def ret_0(): return 0

    gate = gc.and_gate(ret_1, ret_1)
    assert gate() == 1
    gate = gc.and_gate(ret_0, ret_0)
    assert gate() == 0
    gate = gc.and_gate(ret_0, ret_1)
    assert gate() == 0
    gate = gc.and_gate(ret_1, ret_0)
    assert gate() == 0

    gate = gc.xor_gate(ret_1, ret_0)
    assert gate() == 1
    gate = gc.xor_gate(ret_0, ret_0)
    assert gate() == 0

    gate = gc.or_gate(ret_0, ret_0)
    assert gate() == 0
    gate = gc.or_gate(ret_0, ret_1)
    assert gate() == 1


def test_permutations_of_input():
    thing = [(0,1), (2,3)]
    perm = gc.permutations_of_input(thing)
    print(perm)
    assert set(perm) == {(0,2), (0,3), (1,2), (1,3)}

def test_int_to_tuple():
    assert gc.int_to_tuple(3) == (1,1)
    assert gc.int_to_tuple(8) == (4,0)

def test_tuple_to_int():
    assert gc.tuple_to_int((1,1)) == 3
    assert gc.tuple_to_int((4,0)) == 8



def test_garble_input_gate():
    gate = gc.InputGate()
    gate.set_value(0)
    assert gate() == 0

    i = 10
    def gen_key():
        nonlocal i
        i += 1
        return i

    def encrypt(key, value): pass

    k0, k1, xor_flag = gate.garble(gen_key, encrypt)
    assert k0 == 11
    assert k1 == 12
    assert gate() == (k0, 0)

def test_garbled_and_gate():
    input0 = gc.InputGate()
    input0.set_value(0)
    assert input0() == 0

    input1 = gc.InputGate()
    input1.set_value(1)
    assert input1() == 1

    and_gate = gc.and_gate(input0, input1)


    i = 10
    def gen_key():
        nonlocal i
        i += 1
        return i

    def encrypt(key, value): return key * value
    def decrypt(key, value): return key / value

    k0, k1, xor_flag = and_gate.garble(gen_key, encrypt, decrypt)
    assert k0 == 15
    assert k1 == 16

    assert and_gate() == (k0, xor_flag ^ 0)

    input0.set_value(1)
    assert and_gate() == (k1, xor_flag ^ 1)
