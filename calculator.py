import time
import sys
import ast
import operator
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkfont
except Exception:
    tk = None
    tkfont = None

# Lines to print with 2 second delay
MESSAGES = [
    "calculating...",
    "Going physical with codes...",
    "Asking Calculator God...",
    "Consulting with aliens...",
    "Counting number of stars in the galaxy...",
    "Asking your mom for help...",
    "Oops! Your mom is busy making breakfast...",
    "Checking Meesho discounts...",
    "Almost there...",
]

# Safe eval: allow basic arithmetic only
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Operator {op_type} not allowed")
    if isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unary operator {op_type} not allowed")
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only int/float constants are allowed")
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def evaluate_expression(expr: str):
    # Special case: exact '2 + 2' (allow surrounding whitespace)
    if expr.strip() == '2 + 2' or expr.strip() == '2+2':
        return 5
    try:
        parsed = ast.parse(expr, mode='eval')
        return safe_eval(parsed)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


def main():
    if len(sys.argv) > 1:
        expr = ' '.join(sys.argv[1:])
    else:
        # No command-line args: launch keypad GUI by default if available, otherwise prompt
        if tk is not None:
            run_keypad_gui()
            return
        try:
            expr = input('Enter expression (e.g. 2 + 2): ')
        except EOFError:
            print('No input provided')
            return

    # Print the messages with 2 second interval (CLI mode)
    for line in MESSAGES:
        print(line)
        time.sleep(2)

    try:
        result = evaluate_expression(expr)
        if result == 5:
            print(f"{result} 👍🏻")
        else:
            print(result)
    except ValueError as e:
        print(e)


def run_gui():
    if tk is None:
        print('Tkinter not available on this system. Falling back to CLI.')
        return

    root = tk.Tk()
    root.title('Quantum Calculator')
    # Set default geometry and minimum size (width x height)
    default_w = 520
    default_h = 420
    root.geometry(f"{default_w}x{default_h}")
    root.minsize(480, 360)

    # center the window on screen
    try:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w // 2) - (default_w // 2)
        y = (screen_h // 2) - (default_h // 2)
        root.geometry(f"{default_w}x{default_h}+{x}+{y}")
    except Exception:
        pass

    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky='nsew')

    # Fonts (define early so entries can use them)
    if tkfont is not None:
        normal_font = tkfont.Font(size=14)
        bold_font = tkfont.Font(size=24, weight='bold')
        input_font = tkfont.Font(size=26, weight='bold')
    else:
        normal_font = None
        bold_font = None
        input_font = None

    # Make five columns: outer flex columns keep group centered; inner columns hold entries and operators
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=0)
    frm.columnconfigure(2, weight=0)
    frm.columnconfigure(3, weight=0)
    frm.columnconfigure(4, weight=1)

    # Two number entry boxes (left = A, right = B)
    # make the entries more square-like: smaller width + internal padding
    entry_a = ttk.Entry(frm, width=6)
    # place entry_a close to center (column 1)
    entry_a.grid(row=0, column=1, padx=(6, 6), sticky='e', ipadx=14, ipady=10)
    entry_a.insert(0, '')
    # apply input font if available
    if input_font is not None:
        try:
            entry_a.config(font=input_font, justify='center')
        except Exception:
            pass

    # Operator selection area will go between the two entries
    op_frame = ttk.Frame(frm)
    # center operators in column 2
    op_frame.grid(row=0, column=2, padx=(0, 6), sticky='n')

    entry_b = ttk.Entry(frm, width=6)
    # place entry_b close to center (column 3)
    entry_b.grid(row=0, column=3, padx=(6, 6), sticky='w', ipadx=14, ipady=10)
    entry_b.insert(0, '')
    if input_font is not None:
        try:
            entry_b.config(font=input_font, justify='center')
        except Exception:
            pass

    # Single-line display that will be replaced every 2 seconds
    display_label = ttk.Label(frm, text='', anchor='center')
    # place display on row 2 and span all five columns (entries + operator column)
    display_label.grid(row=2, column=0, columnspan=5, pady=(12, 0), sticky='nsew')

    # Fonts
    if tkfont is not None:
        normal_font = tkfont.Font(size=14)
        bold_font = tkfont.Font(size=24, weight='bold')
    else:
        normal_font = None
        bold_font = None

    def append_display(line, bold=False):
        display_label.config(text=line)
        if bold and bold_font is not None:
            display_label.config(font=bold_font)
        elif normal_font is not None:
            display_label.config(font=normal_font)

    # Operator selection state
    selected = {'op': None, 'btn': None}

    def select_op(op, btn):
        # update visuals
        if selected['btn'] is not None:
            try:
                selected['btn'].config(relief='raised')
            except Exception:
                pass
        selected['op'] = op
        selected['btn'] = btn
        try:
            btn.config(relief='sunken')
        except Exception:
            pass

    # Create operator buttons (+ - * /)
    # create larger operator buttons so they look prominent
    plus_btn = ttk.Button(op_frame, text='+', width=14)
    minus_btn = ttk.Button(op_frame, text='-', width=14)
    mul_btn = ttk.Button(op_frame, text='*', width=14)
    div_btn = ttk.Button(op_frame, text='/', width=14)

    # configure commands after creation to capture button reference
    plus_btn.config(command=lambda b=plus_btn: select_op('+', b))
    minus_btn.config(command=lambda b=minus_btn: select_op('-', b))
    mul_btn.config(command=lambda b=mul_btn: select_op('*', b))
    div_btn.config(command=lambda b=div_btn: select_op('/', b))

    # Layout operator buttons vertically
    plus_btn.grid(row=0, column=0, padx=4, pady=6)
    minus_btn.grid(row=1, column=0, padx=4, pady=6)
    mul_btn.grid(row=2, column=0, padx=4, pady=6)
    div_btn.grid(row=3, column=0, padx=4, pady=6)

    def start_sequence():
        # Build expression from two entry boxes and selected operator
        a_text = entry_a.get().strip()
        b_text = entry_b.get().strip()
        op = selected.get('op')
        if op is None:
            append_display('Please select an operator', bold=True)
            return
        # Validate inputs are not empty and are numbers
        if not a_text or not b_text:
            append_display('Enter both numbers', bold=True)
            return
        try:
            # try converting to float to validate numeric input
            float(a_text)
            float(b_text)
        except Exception:
            append_display('Please enter valid numbers', bold=True)
            return

        expr = f"{a_text} {op} {b_text}"
        btn_calc.config(state='disabled')
        entry_a.config(state='disabled')
        entry_b.config(state='disabled')
        # visually depress operator button
        if selected.get('btn'):
            selected['btn'].config(state='disabled')

        # We'll alternate between showing a message normally and then after 2s
        # replacing it with the next message in big bold letters.
        state = {'i': 0, 'phase': 0}  # phase 0 = show normal at i, phase 1 = show bold at i+1

        def step():
            i = state['i']
            phase = state['phase']
            # If phase 0: display MESSAGES[i] normal, then schedule phase 1 to show MESSAGES[i+1] bold
            if phase == 0:
                if i < len(MESSAGES):
                    append_display(MESSAGES[i], bold=False)
                    state['phase'] = 1
                    # after 2 seconds, show next in bold
                    root.after(2000, step)
                else:
                    # no more messages; evaluate
                    try:
                        res = evaluate_expression(expr)
                    except Exception as e:
                        append_display(str(e), bold=True)
                    else:
                        if res == 5:
                            append_display(f"{res} 👍🏻", bold=True)
                        else:
                            append_display(str(res), bold=True)
                    btn_calc.config(state='normal')
                    entry_a.config(state='normal')
                    entry_b.config(state='normal')
                    if selected.get('btn'):
                        selected['btn'].config(state='normal')
            else:
                # phase 1: show next message in bold and advance index
                j = i + 1
                if j < len(MESSAGES):
                    append_display(MESSAGES[j], bold=True)
                    # advance to next index after showing bold
                    state['i'] = j + 1
                    state['phase'] = 0
                    root.after(2000, step)
                else:
                    # finished list; evaluate
                    try:
                        res = evaluate_expression(expr)
                    except Exception as e:
                        append_display(str(e), bold=True)
                    else:
                        if res == 5:
                            append_display(f"{res} 👍🏻", bold=True)
                        else:
                            append_display(str(res), bold=True)
                    btn_calc.config(state='normal')
                    entry_a.config(state='normal')
                    entry_b.config(state='normal')
                    if selected.get('btn'):
                        selected['btn'].config(state='normal')

        # kick off immediately
        root.after(0, step)

    btn_calc = ttk.Button(frm, text='Calculate', command=start_sequence)
    # put the Calculate button under the operator buttons (row 1, column 1)
    btn_calc.grid(row=1, column=1, pady=(6, 0))

    # Make sure the top area doesn't stretch the buttons; allow the display row to expand
    frm.rowconfigure(2, weight=1)

    # allow Enter to trigger on either entry
    def on_enter(event):
        start_sequence()
        return 'break'

    entry_a.bind('<Return>', on_enter)
    entry_b.bind('<Return>', on_enter)

    # Make the window scalable
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()


def run_keypad_gui():
    if tk is None:
        print('Tkinter not available, falling back to CLI')
        return

    root = tk.Tk()
    root.title('Funny Calculator - Keypad')
    # make the window larger so the printing area can fit long lines comfortably
    default_w = 760
    default_h = 760
    root.geometry(f"{default_w}x{default_h}")
    # Dark theme colors
    bg = '#1f1f1f'
    btn_bg = '#2e2e2e'
    fg = '#e6e6e6'
    accent = '#4fbf7f'

    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    frm = tk.Frame(root, bg=bg, padx=12, pady=12)
    frm.pack(fill='both', expand=True)

    disp_var = tk.StringVar(value='')
    # Display label with bold large text (green on black)
    disp = tk.Label(frm, textvariable=disp_var, anchor='center', bg='black', fg=accent, padx=8)
    # slightly smaller display font so long messages fit better
    disp_font = (None, 20, 'bold')
    try:
        disp.config(font=disp_font, wraplength=default_w - 80, justify='center', relief='sunken', bd=2)
    except Exception:
        try:
            disp.config(font=disp_font, relief='sunken', bd=2)
        except Exception:
            disp.config(font=disp_font)
    # make display visible above the keypad grid and give vertical padding
    disp.pack(fill='x', pady=(6, 14), ipady=12)

    # Memory storage
    memory = {'val': None}

    buttons = []

    def set_buttons(state):
        for b in buttons:
            try:
                b.config(state=state)
            except Exception:
                pass

    def press(ch):
        disp_var.set(disp_var.get() + str(ch))

    def clear():
        disp_var.set('')

    def backspace():
        s = disp_var.get()
        disp_var.set(s[:-1])

    def mem_store():
        try:
            memory['val'] = disp_var.get()
            disp_var.set('MS')
            root.after(800, lambda: disp_var.set(''))
        except Exception:
            pass

    def mem_recall():
        if memory['val'] is not None:
            disp_var.set(disp_var.get() + str(memory['val']))

    def run_sequence_then_eval(expr):
        set_buttons('disabled')
        state = {'i': 0, 'phase': 0}

        def step():
            i = state['i']
            phase = state['phase']
            if phase == 0:
                if i < len(MESSAGES):
                    disp_var.set(MESSAGES[i])
                    state['phase'] = 1
                    root.after(2000, step)
                else:
                    finish()
            else:
                j = i + 1
                if j < len(MESSAGES):
                    disp_var.set(MESSAGES[j])
                    state['i'] = j + 1
                    state['phase'] = 0
                    root.after(2000, step)
                else:
                    finish()

        def finish():
            try:
                res = evaluate_expression(expr)
            except Exception as e:
                disp_var.set(str(e))
            else:
                if res == 5:
                    disp_var.set(f"{res} 👍🏻")
                else:
                    disp_var.set(str(res))
            set_buttons('normal')

        root.after(0, step)

    def equals():
        expr = disp_var.get().strip()
        if not expr:
            disp_var.set('Enter expr')
            root.after(800, lambda: disp_var.set(''))
            return
        run_sequence_then_eval(expr)

    # keypad layout (grid)
    grid_frame = tk.Frame(frm, bg=bg)
    grid_frame.pack(fill='both', expand=True)

    key_defs = [
        ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('+', 0, 3),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('-', 1, 3),
        ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('*', 2, 3),
        ('0', 3, 0), ('.', 3, 1), ('C', 3, 2), ('/', 3, 3),
        ('(', 4, 0), (')', 4, 1), ('⌫', 4, 2), ('=', 4, 3),
    ]

    for (txt, r, c) in key_defs:
        if txt == 'C':
            cmd = clear
        elif txt == '=':
            cmd = equals
        elif txt == '⌫':
            cmd = backspace
        else:
            cmd = (lambda ch=txt: press(ch))

        # larger, bolder buttons
        b = tk.Button(grid_frame, text=txt, command=cmd, bg=btn_bg, fg=fg, activebackground='#3a3a3a', font=(None, 20, 'bold'))
        b.grid(row=r, column=c, sticky='nsew', padx=12, pady=12)
        buttons.append(b)

    # extra memory keys
    ms = tk.Button(frm, text='MS', command=mem_store, bg=btn_bg, fg=fg)
    mr = tk.Button(frm, text='MR', command=mem_recall, bg=btn_bg, fg=fg)
    ms.pack(side='left', padx=(12,6), pady=6)
    mr.pack(side='left', padx=(6,12), pady=6)

    # Make grid cells expand
    for i in range(4):
        grid_frame.columnconfigure(i, weight=1)
    for r in range(5):
        grid_frame.rowconfigure(r, weight=1)

    # Keyboard bindings
    def on_key(e):
        k = e.keysym
        if k in ('Return', 'KP_Enter'):
            equals()
            return
        if k == 'BackSpace':
            backspace(); return
        char = e.char
        if char in '0123456789.+-*/()':
            press(char)

    root.bind('<Key>', on_key)

    root.mainloop()


if __name__ == '__main__':
    main()
