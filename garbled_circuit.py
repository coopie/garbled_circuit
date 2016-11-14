
from random import random


class InputGate:
    def __init__(self):
        self.value = None
        self.garbled = False
        self.garbled_output_values = None

    def set_value(self, value):
        self.value = value

    def garble(self, generate_key, encrypt):
        if self.garbled:
            assert self.garbled_output_values != None
            assert type(self.garbled_output_values) == tuple
            assert len(self.garbled_output_values) == 3
            return self.garbled_output_values
        else:
            output_keys = (generate_key(), generate_key())
            xor_flag = random_bit()
            self.garbled = True
            self.garbled_output_values = output_keys + (xor_flag,)
            return self.garbled_output_values

    def __call__(self):
        assert self.value != None
        if not self.garbled:
            return self.value
        else:
            keys = self.garbled_output_values[:2]
            xor_flag = self.garbled_output_values[-1]
            return (keys[self.value], xor_flag ^ self.value)


class Gate:
    '''
    Class for non input gates.
    '''
    def __init__(self, gate_lookup, *inputs):
        self.gate_lookup = gate_lookup

        first_key = None
        for key in gate_lookup:
            if first_key == None: first_key = key
            assert type(key) == tuple
            assert len(key) == len(first_key)

        self.inputs = inputs
        self.garbled = False
        self.garbled_output_values = None

    def __call__(self):
        input_vals = [input_gate() for input_gate in self.inputs]
        if not self.garbled:
            input_vals = tuple(input_vals)
            return self.gate_lookup[input_vals]
        else:
            xor_values = tuple([x[-1] for x in input_vals])
            keys = [x[0] for x in input_vals]

            encrypted_value = self.gate_lookup[xor_values]
            key, xor_output = int_to_tuple(
                recursive_decrypt(encrypted_value, self.decrypt, keys)
            )
            return (key, xor_output)



    def garble(self, generate_key, encrypt, decrypt):
        '''
        Garble the circuit if not already garbled, return the ka0, ka1 tuple, anlong with the xor bit value for the wire.

        encrypt(value, key)
        decrypt(value, key)
        '''
        if self.garbled:
            assert self.garbled_output_values != None
            assert type(self.garbled_output_values) == tuple
            assert len(self.garbled_output_values) == 3
            return self.garbled_output_values


        garbled_input_values = [
            input_gate.garble(generate_key, encrypt)
            for input_gate in self.inputs
        ]

        output_keys = (generate_key(), generate_key())
        # TODO:
        # this is the value of the xor flag of k1
        xor_flag = random_bit()

        boolean_permutations = permutations_of_input([
            (0,1) for i in range(len(garbled_input_values))])


        new_lookup = {}

        input_keys = [x[:2] for x in garbled_input_values]
        garbled_xor_flags = [x[-1] for x in garbled_input_values]

        for lookup_key in boolean_permutations:
            key_indeces = tuple([
                lookup_value ^ garbled_xor_flag
                for lookup_value, garbled_xor_flag in zip(lookup_key, garbled_xor_flags)
            ])

            gate_value = self.gate_lookup[key_indeces]
            output_value = output_keys[gate_value]

            xor_value = xor_flag ^ gate_value

            encryption_keys = [keys[key_index] for keys, key_index in zip(input_keys, key_indeces)]

            # aplly encryption in reverse, so decription is in order
            encrypted_value = recursive_encrypt(
                tuple_to_int((output_value, xor_value)),
                encrypt,
                list(reversed(encryption_keys))
            )
            new_lookup[lookup_key] = encrypted_value

        self.gate_lookup = new_lookup

        self.garbled_output_values = output_keys + (xor_flag,)
        self.garbled = True
        self.decrypt = decrypt
        return self.garbled_output_values


def logic_bgate(bfunction, *inputs):
    assert len(inputs) == 2
    lookup = {}
    for i in range(2):
        for j in range(2):
            t_val = bfunction(i, j)
            assert t_val in {0,1}
            lookup[(i, j)] = t_val

    return Gate(lookup ,*inputs)

def and_gate(*inputs):
    def f(a, b):
        return a and b
    return logic_bgate(f, *inputs)

def or_gate(*inputs):
    def f(a, b):
        return a or b
    return logic_bgate(f, *inputs)

def xor_gate(*inputs):
    def f(a, b):
        return int(a != b)
    return logic_bgate(f, *inputs)

def permutations_of_input(inputs):
    if inputs == []:
        return [()]
    else:
        head = inputs[0]
        permutations = permutations_of_input(inputs[1:])

        with_input_0 = [(head[0],) + x for x in permutations]
        with_input_1 = [(head[1],) + x for x in permutations]
        return with_input_0 + with_input_1

def recursive_encrypt(value, encrypt, keys):
    if len(keys) == 0:
        return value
    return recursive_encrypt(encrypt(value, keys[0]), encrypt, keys[1:])

def recursive_decrypt(value, decrypt, keys):
    if len(keys) == 0:
        return value
    return recursive_decrypt(decrypt(value, keys[0]) ,decrypt, keys[1:])


def tuple_to_int(t):
    '''
    Takes a tuple (n, {0,1})
    '''
    x, flag = t
    return x*2 + flag

def int_to_tuple(x):
    flag = x % 2
    i = x // 2
    return (i, flag)

def random_bit():
    return int(random() > 0.5)
