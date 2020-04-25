import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("file", help="brainfuck file with code")
args = parser.parse_args()

memory = [0 for _ in range(30000)]
code_ptr = 0
mem_ptr = 0

BRAINFUCK_CHARSER = "><+-.,[]"

def strip_code(code):
    return [c for c in code if c in BRAINFUCK_CHARSER]

def matching_close(code_ptr):
    depth = 0
    while True:
        code_ptr += 1
        if code[code_ptr] == ']':
            if depth == 0:
                return code_ptr
            depth -= 1
        if code[code_ptr] == '[':
            depth += 1

def matching_open(code_ptr):
    depth = 0
    while True:
        code_ptr -= 1
        if code[code_ptr] == '[':
            if depth == 0:
                return code_ptr
            depth -= 1
        if code[code_ptr] == ']':
            depth += 1

with open(args.file, "r") as f:
    code = f.read()

print(code)

code = strip_code(code)

#print(code)


while True:
    try:
        code[code_ptr]
    except:
        break
    if code[code_ptr] == '>':
        mem_ptr += 1
        code_ptr += 1
    elif code[code_ptr] == '<':
        mem_ptr -= 1
        code_ptr += 1
    elif code[code_ptr] == '+':
        memory[mem_ptr] = (memory[mem_ptr] + 1) & 0xff
        code_ptr += 1
    elif code[code_ptr] == '-':
        memory[mem_ptr] = (memory[mem_ptr] - 1) & 0xff
        code_ptr += 1
    elif code[code_ptr] == '.':
        sys.stdout.write("%c" % chr(memory[mem_ptr]))
        code_ptr += 1
    elif code[code_ptr] == ',':
        memory[mem_ptr] = ord(sys.stdin.read(1))
        code_ptr += 1
    elif code[code_ptr] == '[':
        if memory[mem_ptr] == 0:
            code_ptr = matching_close(code_ptr)
        else:
            code_ptr += 1
    elif code[code_ptr] == ']':
        if memory[mem_ptr] != 0:
            code_ptr = matching_open(code_ptr)
        else:
            code_ptr += 1
    else:
        code_ptr += 1
    #wait = input()

print("")