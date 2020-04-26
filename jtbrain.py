import argparse
import sys
import timeit

parser = argparse.ArgumentParser()
parser.add_argument("file", help="brainfuck file with code")
parser.add_argument("-i", "--input", help="brainfuck file with code")
args = parser.parse_args()

class BrainfuckInterpreter():
    BRAINFUCK_CHARSER = "><+-.,[]"
    BRAINFUCK_DEF_MEMORY = 8
    running = True
    memory = None
    loops = []
    code_ptr = 0
    mem_ptr = 0
    code = None
    input_data = None

    def __init__(self, file, input_data = None, ram = None):
        with open(file, "r") as f:
            self.code = f.read()
        if input_data:
            self.input_data = open(input_data, "r")
        else:
            self.input_data = sys.stdin
        self.strip_code()
        self.loops = [-1 for _ in self.code]
        self.memory = [0 for _ in range(ram if ram else self.BRAINFUCK_DEF_MEMORY)]

    def strip_code(self):
        self.code = [c for c in self.code if c in self.BRAINFUCK_CHARSER]

    def code_ptr_set(self, value):
        self.code_ptr = value
    
    def code_ptr_inc(self):
        self.code_ptr += 1
        try:
            self.code[self.code_ptr]
        except IndexError:
            self.running = False

    def memory_inc(self):
        try:
            self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] + 1) & 0xff
        except IndexError:
            self.memory.append(0)
            self.memory_inc()

    def memory_dec(self):
        try:
            self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] - 1) & 0xff
        except IndexError:
            self.memory.append(0)
            self.memory_dec()
    
    def memory_is_zero(self):
        try:
            return self.memory[self.mem_ptr] == 0
        except IndexError:
            self.memory.append(0)
            self.memory_is_zero()

    def matching_close(self):
        if self.loops[self.code_ptr] > 0:
            return self.loops[self.code_ptr]
        depth = 0
        start_code_ptr = self.code_ptr
        while True:
            self.code_ptr += 1
            if self.code[self.code_ptr] == ']':
                if depth == 0:
                    self.loops[start_code_ptr] = self.code_ptr
                    return self.code_ptr
                depth -= 1
            if self.code[self.code_ptr] == '[':
                depth += 1

    def matching_open(self):
        if self.loops[self.code_ptr] > 0:
            return self.loops[self.code_ptr]
        depth = 0
        start_code_ptr = self.code_ptr
        while True:
            self.code_ptr -= 1
            if self.code[self.code_ptr] == '[':
                if depth == 0:
                    self.loops[start_code_ptr] = self.code_ptr
                    return self.code_ptr
                depth -= 1
            if self.code[self.code_ptr] == ']':
                depth += 1
    
    def exec(self):
        while self.running:
            if self.code[self.code_ptr] == '>':
                self.mem_ptr += 1
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == '<':
                self.mem_ptr -= 1
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == '+':
                self.memory_inc()
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == '-':
                self.memory_dec()
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == '.':
                sys.stdout.write("%c" % chr(self.memory[self.mem_ptr]))
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == ',':
                self.memory[self.mem_ptr] = ord(self.input_data.read(1))
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == '[':
                self.code_ptr_set(self.matching_close()) if self.memory_is_zero() else self.code_ptr_inc()
            elif self.code[self.code_ptr] == ']':
                self.code_ptr_set(self.matching_open()) if not self.memory_is_zero() else self.code_ptr_inc()
            else:
                self.code_ptr_inc()
            #wait = input()

bf = BrainfuckInterpreter(file=args.file, input_data=args.input)
print("Elapsed: %fs" % timeit.Timer(bf.exec).timeit())

bf = BrainfuckInterpreter(file=args.file, input_data=args.input, ram=1024)
print("Elapsed: %fs" % timeit.Timer(bf.exec).timeit())

print("")