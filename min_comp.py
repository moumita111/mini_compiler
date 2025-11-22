# Mini Compiler Project

import ply.lex as lex
import ply.yacc as yacc
from tkinter import *
from tkinter import ttk, messagebox



class LexicalAnalyzer:
    
    keywords = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'int': 'INT',
        'float': 'FLOAT',
    }

    
    tokens = list(keywords.values()) + [
        'ID', 'NUMBER',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'EQ', 'LT', 'GT', 'ASSIGN',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON'
    ]


    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQ = r'=='
    t_LT = r'<'
    t_GT = r'>'
    t_ASSIGN = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMICOLON = r';'
    t_ignore = ' \t'

    
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.keywords.get(t.value, 'ID')
        return t


    def t_COMMENT(self, t):
        r'//.*'
        pass

    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    
    def t_error(self, t):
        self.errors.append(f"Illegal token '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def __init__(self):
        self.errors = []
        self.lexer = lex.lex(module=self)

    def analyze(self, source_code):
        self.lexer.input(source_code)
        tokens_output = []
        while True:
            token = self.lexer.token()
            if not token:
                break
            tokens_output.append(f"{token.type:<10} {token.value}")
        return "\n".join(tokens_output)



class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def declare(self, name, var_type):
        if name in self.symbols:
            return f"Error: Variable '{name}' already declared"
        self.symbols[name] = var_type
        return None

    def get_type(self, name):
        return self.symbols.get(name, None)

    def display(self):
        output = "Variable\tType\n---------------------\n"
        for name, vtype in self.symbols.items():
            output += f"{name}\t\t{vtype}\n"
        return output


# =====================================================
#  SYNTAX & SEMANTIC ANALYZER + INTERMEDIATE CODE
# =====================================================

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.symbols = SymbolTable()
        self.temp_counter = 0
        self.intermediate_code = []
        self.errors = []
        self.parser = yacc.yacc(module=self)

    # Grammar rules
    def p_program(self, p):
        """program : stmt_list"""
        pass

    def p_stmt_list(self, p):
        """stmt_list : stmt_list stmt
                     | stmt"""
        pass

    def p_stmt(self, p):
        """stmt : decl_stmt
                | assign_stmt
                | if_stmt
                | while_stmt"""
        pass

    def p_decl_stmt(self, p):
        """decl_stmt : type ID SEMICOLON"""
        err = self.symbols.declare(p[2], p[1])
        if err:
            self.errors.append(err)

    def p_type(self, p):
        """type : INT
                | FLOAT"""
        p[0] = p[1]

    def p_assign_stmt(self, p):
        """assign_stmt : ID ASSIGN expr SEMICOLON"""
        var_type = self.symbols.get_type(p[1])
        if not var_type:
            self.errors.append(f"Error: '{p[1]}' not declared before use")
        self.emit(f"{p[1]} = {p[3]}")

    def p_if_stmt(self, p):
        """if_stmt : IF LPAREN condition RPAREN LBRACE stmt_list RBRACE
                   | IF LPAREN condition RPAREN LBRACE stmt_list RBRACE ELSE LBRACE stmt_list RBRACE"""
        if len(p) == 8:
            label_end = self.new_label()
            self.emit(f"if not {p[3]} goto {label_end}")
            self.emit(f"{label_end}:")
        else:
            label_else = self.new_label()
            label_end = self.new_label()
            self.emit(f"if not {p[3]} goto {label_else}")
            self.emit(f"goto {label_end}")
            self.emit(f"{label_else}:")
            self.emit(f"{label_end}:")

    def p_while_stmt(self, p):
        """while_stmt : WHILE LPAREN condition RPAREN LBRACE stmt_list RBRACE"""
        start_lbl = self.new_label()
        end_lbl = self.new_label()
        self.emit(f"{start_lbl}:")
        self.emit(f"if not {p[3]} goto {end_lbl}")
        self.emit(f"goto {start_lbl}")
        self.emit(f"{end_lbl}:")

    def p_condition(self, p):
        """condition : expr EQ expr
                     | expr LT expr
                     | expr GT expr"""
        p[0] = f"{p[1]} {p[2]} {p[3]}"

    def p_expr(self, p):
        """expr : expr PLUS expr
                | expr MINUS expr
                | expr TIMES expr
                | expr DIVIDE expr
                | LPAREN expr RPAREN
                | NUMBER
                | ID"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4 and p[1] == '(':
            p[0] = p[2]
        else:
            temp = self.new_temp()
            self.emit(f"{temp} = {p[1]} {p[2]} {p[3]}")
            p[0] = temp

    def p_error(self, p):
        if p:
            self.errors.append(f"Syntax error near '{p.value}'")
        else:
            self.errors.append("Unexpected end of input")

    # Helper functions
    def emit(self, code_line):
        self.intermediate_code.append(code_line)

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.temp_counter += 1
        return f"L{self.temp_counter}"

    def parse(self, source_code):
        self.intermediate_code = []
        self.errors = []
        self.symbols = SymbolTable()
        self.parser.parse(source_code, lexer=self.lexer.lexer)
        return "\n".join(self.intermediate_code)


# =====================================================
#  SIMPLE CODE GENERATOR (ASSEMBLY-LIKE)
# =====================================================

class AssemblyGenerator:
    def generate(self, intermediate_code):
        lines = intermediate_code.splitlines()
        assembly = ["; Assembly-like representation\n"]
        for line in lines:
            if '=' in line:
                left, right = line.split('=', 1)
                assembly.append(f"MOV {left.strip()}, {right.strip()}")
            elif 'goto' in line:
                assembly.append(line)
            else:
                assembly.append(f"; {line}")
        return "\n".join(assembly)


# =====================================================
#  GUI APPLICATION
# =====================================================

class CompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compiler - Moumita Afreen")

        # Text area
        Label(root, text="Enter Code:", font=("Arial", 11, "bold")).pack(anchor='w')
        self.textbox = Text(root, height=10, width=90, font=("Consolas", 10))
        self.textbox.pack()

        Button(root, text="Compile Code", command=self.compile_code, bg="#4CAF50", fg="white").pack(pady=5)

        # Tabs
        self.tabs = ttk.Notebook(root)
        self.output_boxes = {}
        for name in ["Tokens", "Symbol Table", "Intermediate Code", "Assembly", "Errors"]:
            frame = Frame(self.tabs)
            txt = Text(frame, height=15, width=90, font=("Consolas", 10))
            txt.pack()
            self.output_boxes[name] = txt
            self.tabs.add(frame, text=name)
        self.tabs.pack()

        # Components
        self.lexical = LexicalAnalyzer()
        self.parser = Parser(self.lexical)
        self.codegen = AssemblyGenerator()

    def compile_code(self):
        code = self.textbox.get("1.0", END)
        tokens = self.lexical.analyze(code)
        intermediate = self.parser.parse(code)
        assembly = self.codegen.generate(intermediate)

        # Display outputs
        self.output_boxes["Tokens"].delete("1.0", END)
        self.output_boxes["Tokens"].insert("1.0", tokens)

        self.output_boxes["Symbol Table"].delete("1.0", END)
        self.output_boxes["Symbol Table"].insert("1.0", self.parser.symbols.display())

        self.output_boxes["Intermediate Code"].delete("1.0", END)
        self.output_boxes["Intermediate Code"].insert("1.0", intermediate)

        self.output_boxes["Assembly"].delete("1.0", END)
        self.output_boxes["Assembly"].insert("1.0", assembly)

        self.output_boxes["Errors"].delete("1.0", END)
        self.output_boxes["Errors"].insert("1.0", "\n".join(self.lexical.errors + self.parser.errors))

        messagebox.showinfo("Compilation Complete", "Code compiled successfully!")

# =====================================================
#  MAIN EXECUTION
# =====================================================

if __name__ == "__main__":
    root = Tk()
    app = CompilerApp(root)
    root.mainloop()
