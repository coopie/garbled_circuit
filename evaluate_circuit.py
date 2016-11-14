"""
Prints the truth table of the garbled circuit.
"""

import garbled_circuit as gc
from random import randint

A = gc.InputGate()
B = gc.InputGate()
C = gc.InputGate()
D = gc.InputGate()

Q = gc.or_gate(
    gc.xor_gate(A, C),
    gc.xor_gate(B, D)
)

P = gc.or_gate(
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

inputs = gc.permutations_of_input([(0,1) for i in range(4)])

def gen_key():
    return randint(0, 1000)


def encrypt(value, key):
    return value ^ key

decrypt = encrypt


kp0, kp1, pxor_flag = P.garble(gen_key, encrypt, decrypt)
p_lookup = {
    kp1: 1,
    kp0: 0
}

kq0, kq1, qxor_flag = Q.garble(gen_key, encrypt, decrypt)
q_lookup = {
    kq1: 1,
    kq0: 0
}


print('A, B, C, D, cmp(A, B, C, D)')

for circuit_input in inputs:
    A.set_value(circuit_input[0])
    B.set_value(circuit_input[1])
    C.set_value(circuit_input[2])
    D.set_value(circuit_input[3])

    presult_encrypted, pxor_value = P()
    p_result = p_lookup[presult_encrypted]

    qresult_encrypted, qxor_value = Q()
    q_result = q_lookup[qresult_encrypted]

    result_2bit = str(p_result) + str(q_result)

    inputs_strs = list(map(str, circuit_input))


    print(', '.join(inputs_strs + [result_2bit]))
