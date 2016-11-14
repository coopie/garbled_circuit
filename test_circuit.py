import garbled_circuit as gc

A = gc.InputGate()
B = gc.InputGate()
C = gc.InputGate()
D = gc.InputGate()

def get_Q():
    return gc.or_gate(
        gc.xor_gate(A, C),
        gc.xor_gate(B, D)
    )

def get_P():
    return gc.or_gate(
        gc.and_gate(
            C,
            gc.not_gate(A)
        ),
        gc.and_gate(
            gc.and_gate(
                gc.not_gate(B),
                D
            ),
            gc.not_gate(
                gc.xor_gate(
                    A, C
                )
            )
        )
    )

P_truth_table = {
     (0, 0, 0, 0): 0,
     (0, 0, 0, 1): 1,
     (0, 0, 1, 0): 1,
     (0, 0, 1, 1): 1,
     (0, 1, 0, 0): 0,
     (0, 1, 0, 1): 0,
     (0, 1, 1, 0): 1,
     (0, 1, 1, 1): 1,
     (1, 0, 0, 0): 0,
     (1, 0, 0, 1): 0,
     (1, 0, 1, 0): 0,
     (1, 0, 1, 1): 1,
     (1, 1, 0, 0): 0,
     (1, 1, 0, 1): 0,
     (1, 1, 1, 0): 0,
     (1, 1, 1, 1): 0
}

def test_P():
    P = get_P()

    inputs = gc.permutations_of_input([(0,1) for i in range(4)])

    for circuit_input in inputs:
        expected = P_truth_table[circuit_input]
        A.set_value(circuit_input[0])
        B.set_value(circuit_input[1])
        C.set_value(circuit_input[2])
        D.set_value(circuit_input[3])
        result = P()
        assert result == expected, str(result) + " does not meet expected value: " + str(expected) + " with input: " + str(circuit_input)


def test_Q():
    Q = get_Q()
    inputs = gc.permutations_of_input([(0,1) for i in range(4)])

    for circuit_input in inputs:
        A.set_value(circuit_input[0])
        B.set_value(circuit_input[1])
        C.set_value(circuit_input[2])
        D.set_value(circuit_input[3])

        result = Q()
        expected = int(circuit_input[0] != circuit_input[2] or circuit_input[1] != circuit_input[3] )
        assert result == expected, str(result) + " does not meet expected value: " + str(expected) + " with input: " + str(circuit_input)


def test_Q_Garbled():
    Q = get_Q()
    inputs = gc.permutations_of_input([(0,1) for i in range(4)])

    i = 10
    def gen_key():
        nonlocal i
        i += 1
        return i

    def encrypt(key, value): return key * value
    def decrypt(key, value): return key / value

    k0, k1, xor_flag = Q.garble(gen_key, encrypt, decrypt)

    for circuit_input in inputs:
        A.set_value(circuit_input[0])
        B.set_value(circuit_input[1])
        C.set_value(circuit_input[2])
        D.set_value(circuit_input[3])

        encrypted_result, xor_value = Q()
        result = None
        if encrypted_result == k0:
            result = 0
        elif encrypted_result == k1:
            result = 1
        else:
            assert False, 'invalid end value ' + str(result) + ' for encrypted result: ' + str(encrypted_result)


        expected = int(circuit_input[0] != circuit_input[2] or circuit_input[1] != circuit_input[3] )
        assert result == expected, str(result) + " does not meet expected value: " + str(expected) + " with input: " + str(circuit_input)


def test_Q_Garbled():
    P = get_P()
    inputs = gc.permutations_of_input([(0,1) for i in range(4)])

    i = 10
    def gen_key():
        nonlocal i
        i += 1
        return i

    def encrypt(key, value): return key * value
    def decrypt(key, value): return key / value

    k0, k1, xor_flag = P.garble(gen_key, encrypt, decrypt)

    for circuit_input in inputs:
        A.set_value(circuit_input[0])
        B.set_value(circuit_input[1])
        C.set_value(circuit_input[2])
        D.set_value(circuit_input[3])

        encrypted_result, xor_value = P()
        result = None
        if encrypted_result == k0:
            result = 0
        elif encrypted_result == k1:
            result = 1
        else:
            assert False, 'invalid end value ' + str(result) + ' for encrypted result: ' + str(encrypted_result)


        expected = P_truth_table[circuit_input]
        assert result == expected, str(result) + " does not meet expected value: " + str(expected) + " with input: " + str(circuit_input)
