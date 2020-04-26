import sys

class BrainfuckCharset():
    BRAINFUCK_CHARSET = {
        ">": 0x1,
        "<": 0x2,
        "+": 0x3,
        "-": 0x4,
        ".": 0x5,
        ",": 0x6,
        "[": 0x7,
        "]": 0x8,
    }

class BrainfuckOptimizer():
    OPTIMIZATION_ZERO = 0x1 << 0
    OPTIMIZATION_ARITHMETICS = 0x1 << 1
    OPTIMIZATION_MOVES = 0x1 << 2
    OPTIMIZATION_NOPS = 0x1 << 3 #must be just before brackets for 100% effiecency
    OPTIMIZATION_BRACKETS = 0x1 << 4 #must be last
    OPTIMIZATIONS = {}

    def __init__(self, code, verbosity = None, optimization = 0):
        self.code = code
        self.verbosity = verbosity
        self.optimization = optimization
        self.brackets = None
    
        self.OPTIMIZATIONS = {
            self.OPTIMIZATION_ZERO: (self.optimize_zero, "ZERO"),
            self.OPTIMIZATION_ARITHMETICS: (self.optimize_arithmetics, "ARITHEMITCS"),
            self.OPTIMIZATION_MOVES: (self.optimize_moves, "MOVES"),
            self.OPTIMIZATION_NOPS: (self.optimize_nops, "NOPS"),
            self.OPTIMIZATION_BRACKETS: (self.optimize_brackets, "BRACKETS"),
        }
    
    def optimize(self):
        optimization_text = []
        i = 1
        while self.optimization:
            if self.optimization:
                self.OPTIMIZATIONS[i][0]()
                optimization_text.append(self.OPTIMIZATIONS[i][1])
            self.optimization = self.optimization & ~(i)
            i *= 2
        optimization_text = optimization_text if optimization_text else ["NONE"]
        if self.verbosity:
            print("Optimizations: %s" % ' '.join(optimization_text))

        return (self.code, self.brackets)
 
    def optimize_arithmetics(self):
        for i in range(len(self.code) - 1):
            ch = self.code[i]
            if ch == BrainfuckCharset.BRAINFUCK_CHARSET["-"] or ch == BrainfuckCharset.BRAINFUCK_CHARSET["+"]:
                counter = 1
                j = 1
                while counter < 16 and ch == self.code[i + j]:
                    counter += 1
                    self.code[i + j] = 0
                    j += 1
                opcode = 0x90 if ch == BrainfuckCharset.BRAINFUCK_CHARSET["-"] else 0xa0
                if (counter > 1):
                    self.code[i] = opcode + counter - 1

    def optimize_moves(self):
        for i in range(len(self.code) - 1):
            ch = self.code[i]
            if ch == BrainfuckCharset.BRAINFUCK_CHARSET[">"] or ch == BrainfuckCharset.BRAINFUCK_CHARSET["<"]:
                counter = 1
                j = 1
                while counter < 16 and ch == self.code[i + j]:
                    counter += 1
                    self.code[i + j] = 0
                    j += 1
                opcode = 0xb0 if ch == BrainfuckCharset.BRAINFUCK_CHARSET[">"] else 0xc0
                if (counter > 1):
                    self.code[i] = opcode + counter - 1

    def optimize_zero(self):
        OPTIMIZE = list("[-]")
        for i in range(len(self.code) - 3):
            if OPTIMIZE == self.code[i:i + 3]:
                self.code[i] = 0x80
                self.code[i + 1] = 0
                self.code[i + 2] = 0

    def optimize_brackets(self, start = None):
        self.brackets = {}
        save = True if start is None else False
        end = start + 1 if start is not None else len(self.code) - 1
        start = start if start is not None else 0
        for i in range(start, end):
            ch = self.code[i]
            if ch == BrainfuckCharset.BRAINFUCK_CHARSET["]"] or ch == BrainfuckCharset.BRAINFUCK_CHARSET["["]:
                delta = 1 if ch == BrainfuckCharset.BRAINFUCK_CHARSET["["] else -1
                matching_bracket = BrainfuckCharset.BRAINFUCK_CHARSET["]"] if ch == BrainfuckCharset.BRAINFUCK_CHARSET["["] else BrainfuckCharset.BRAINFUCK_CHARSET["["]
                depth = 0
                j = i
                while True:
                    j += delta
                    if self.code[j] == matching_bracket:
                        if depth == 0:
                            if save:
                                self.brackets[i] = j
                                break
                            else:
                                return j
                        depth -= 1
                    if self.code[j] == ch:
                        depth += 1

    def optimize_nops(self):
        self.code = [x for x in self.code if x]

class BrainfuckInterpreter():
    BRAINFUCK_DEF_MEMORY = 8
    running = True
    memory = None
    loops = []
    code_ptr = 0
    mem_ptr = 0
    code = None
    input_data = None
    optimization = 0

    def __init__(self, file, verbosity = None, input_data = None, ram = None, optimization = 0):
        with open(file, "r") as f:
            self.code = f.read()
        if input_data:
            self.input_data = open(input_data, "r")
        else:
            self.input_data = sys.stdin
        self.strip_code()
        self.translate_code()
        self.brackets = None
        self.memory = [0 for _ in range(ram if ram else self.BRAINFUCK_DEF_MEMORY)]
        self.optimization = optimization
        self.optimizer = BrainfuckOptimizer(code=self.code, optimization=self.optimization, verbosity=verbosity)
        self.code, self.brackets = self.optimizer.optimize()

    def strip_code(self):
        self.code = [c for c in self.code if c in [*BrainfuckCharset.BRAINFUCK_CHARSET]]

    def translate_code(self):
        self.code = [BrainfuckCharset.BRAINFUCK_CHARSET[c] for c in self.code]

    def code_ptr_set(self, value):
        self.code_ptr = value
    
    def code_ptr_inc(self):
        self.code_ptr += 1
        try:
            self.code[self.code_ptr]
        except IndexError:
            self.running = False

    def memory_inc(self, value = 1):
        try:
            self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] + value) & 0xff
        except IndexError:
            self.memory.append(0)
            self.memory_inc()

    def memory_dec(self, value = 1):
        try:
            self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] - value) & 0xff
        except IndexError:
            self.memory.append(0)
            self.memory_dec()

    def memory_set(self, value):
        try:
            self.memory[self.mem_ptr] = value & 0xff
        except IndexError:
            self.memory.append(value & 0xff)
    
    def memory_is_zero(self):
        try:
            return self.memory[self.mem_ptr] == 0
        except IndexError:
            self.memory.append(0)
            self.memory_is_zero()

    def matching_close(self):
        if self.brackets:
            return self.brackets[self.code_ptr]
        return self.optimizer.optimize_brackets(self.code_ptr)

    def matching_open(self):
        if self.brackets:
            return self.brackets[self.code_ptr]
        return self.optimizer.optimize_brackets(self.code_ptr)
    
    def exec(self):
        while self.running:
            if self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET[">"]:
                self.mem_ptr += 1
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["<"]:
                self.mem_ptr -= 1
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["+"]:
                self.memory_inc()
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["-"]:
                self.memory_dec()
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["."]:
                sys.stdout.write("%c" % chr(self.memory[self.mem_ptr]))
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET[","]:
                self.memory[self.mem_ptr] = ord(self.input_data.read(1))
                self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["["]:
                self.code_ptr_set(self.matching_close()) if self.memory_is_zero() else self.code_ptr_inc()
            elif self.code[self.code_ptr] == BrainfuckCharset.BRAINFUCK_CHARSET["]"]:
                self.code_ptr_set(self.matching_open()) if not self.memory_is_zero() else self.code_ptr_inc()
            #Extensions/OPTIMIZATIONs
            elif self.code[self.code_ptr] == 0x80:
                self.memory_set(0)
                self.code_ptr_inc()
            elif (self.code[self.code_ptr] & 0xf0) == 0x90:
                self.memory_dec((self.code[self.code_ptr] & 0x0f) + 1)
                self.code_ptr_inc()
            elif (self.code[self.code_ptr] & 0xf0) == 0xa0:
                self.memory_inc((self.code[self.code_ptr] & 0x0f) + 1)
                self.code_ptr_inc()
            elif (self.code[self.code_ptr] & 0xf0) == 0xb0:
                self.mem_ptr += (self.code[self.code_ptr] & 0x0f) + 1
                self.code_ptr_inc()
            elif (self.code[self.code_ptr] & 0xf0) == 0xc0:
                self.mem_ptr -= (self.code[self.code_ptr] & 0x0f) + 1
                self.code_ptr_inc()
            else:
                self.code_ptr_inc()
            #wait = input()

if __name__ == "__main__":
    import argparse
    import timeit
    
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="brainfuck file with code")
    parser.add_argument("-i", "--input", help="brainfuck file with code")
    parser.add_argument("-v", "--verbosity", action="store_true", help="verbose")
    args = parser.parse_args()
    """
    for i in range(1 << 4):
        bf = BrainfuckInterpreter(file=args.file, verbosity=args.verbosity, input_data=args.input, OPTIMIZATION=i)
        print("OPTIMIZATION %d, elapsed: %fs" % (i, timeit.Timer(bf.exec).timeit()))
    """
    for i in [0, 2**4 - 1, 2**5 - 1]:
        bf = BrainfuckInterpreter(file=args.file, verbosity=args.verbosity, input_data=args.input, optimization=i)
        print("elapsed: %fs" % (timeit.Timer(bf.exec).timeit()))
