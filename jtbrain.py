import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("file", help="brainfuck file with code")
args = parser.parse_args()


class BrainfuckInterpreter():
    BRAINFUCK_CHARSER = "><+-.,[]"
    memory = [0 for _ in range(30000)]
    code_ptr = 0
    mem_ptr = 0
    code = None

    def __init__(self, file):

        with open(file, "r") as f:
            self.code = f.read()
        self.strip_code()

    def strip_code(self):
        self.code = [c for c in self.code if c in self.BRAINFUCK_CHARSER]

    def matching_close(self):
        depth = 0
        while True:
            self.code_ptr += 1
            if self.code[self.code_ptr] == ']':
                if depth == 0:
                    return self.code_ptr
                depth -= 1
            if self.code[self.code_ptr] == '[':
                depth += 1

    def matching_open(self):
        depth = 0
        while True:
            self.code_ptr -= 1
            if self.code[self.code_ptr] == '[':
                if depth == 0:
                    return self.code_ptr
                depth -= 1
            if self.code[self.code_ptr] == ']':
                depth += 1
    
    def exec(self):
        while True:
            try:
                self.code[self.code_ptr]
            except:
                break
            if self.code[self.code_ptr] == '>':
                self.mem_ptr += 1
                self.code_ptr += 1
            elif self.code[self.code_ptr] == '<':
                self.mem_ptr -= 1
                self.code_ptr += 1
            elif self.code[self.code_ptr] == '+':
                self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] + 1) & 0xff
                self.code_ptr += 1
            elif self.code[self.code_ptr] == '-':
                self.memory[self.mem_ptr] = (self.memory[self.mem_ptr] - 1) & 0xff
                self.code_ptr += 1
            elif self.code[self.code_ptr] == '.':
                sys.stdout.write("%c" % chr(self.memory[self.mem_ptr]))
                self.code_ptr += 1
            elif self.code[self.code_ptr] == ',':
                self.memory[self.mem_ptr] = ord(sys.stdin.read(1))
                self.code_ptr += 1
            elif self.code[self.code_ptr] == '[':
                if self.memory[self.mem_ptr] == 0:
                    self.code_ptr = self.matching_close()
                else:
                    self.code_ptr += 1
            elif self.code[self.code_ptr] == ']':
                if self.memory[self.mem_ptr] != 0:
                    self.code_ptr =self.matching_open()
                else:
                    self.code_ptr += 1
            else:
                self.code_ptr += 1
            #wait = input()

bf = BrainfuckInterpreter(args.file)
bf.exec()

print("")