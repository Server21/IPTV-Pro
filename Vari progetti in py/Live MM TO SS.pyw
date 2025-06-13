import tkinter as tk
from tkinter import ttk

# ======= CONFIGURAZIONE STILE =======
FG_COLOR = '#2D3436'
BG_COLOR = '#D3D3D3'
FONT_FAMILY = 'Segoe UI'

class TimeConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MMTOSS')
        self.geometry('200x90')
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)
        self._setup_styles()
        self._build_ui()
        self._updating = False  # Flag per evitare loop di aggiornamento

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, font=(FONT_FAMILY, 12), foreground=FG_COLOR)
        style.configure('TEntry', font=(FONT_FAMILY, 14), justify='center')

    def _build_ui(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill='both', expand=True)

        # Tempo (MM:SS)
        ttk.Label(frame, text='Tempo (MM:SS):').grid(row=0, column=0, sticky='w')
        self.time_var = tk.StringVar(value='')
        time_entry = ttk.Entry(frame, textvariable=self.time_var, width=7)
        time_entry.grid(row=0, column=1, padx=(10,0))

        # Secondi totali
        ttk.Label(frame, text='Secondi totali:').grid(row=1, column=0, sticky='w', pady=(10,0))
        self.sec_var = tk.StringVar(value='0')
        sec_entry = ttk.Entry(frame, textvariable=self.sec_var, width=7)
        sec_entry.grid(row=1, column=1, padx=(10,0), pady=(10,0))

        # Bind live without loop
        self.time_var.trace_add('write', self._on_time_change)
        self.sec_var.trace_add('write', self._on_sec_change)

    @staticmethod
    def _parse_mmss(value: str):
        '''Parse MM:SS into seconds or return None.'''
        try:
            parts = value.split(':')
            if len(parts) != 2:
                return None
            m, s = parts
            if not (m.isdigit() and s.isdigit()):
                return None
            mm, ss = int(m), int(s)
            if ss < 0 or ss >= 60 or mm < 0:
                return None
            return mm * 60 + ss
        except:
            return None

    @staticmethod
    def _format_mmss(total: int):
        '''Format seconds into M:SS.'''
        mm = total // 60
        ss = total % 60
        return f"{mm}:{ss:02}"

    def _on_time_change(self, *args):
        if self._updating:
            return
        total = self._parse_mmss(self.time_var.get())
        if total is not None:
            self._updating = True
            self.sec_var.set(str(total))
            self._updating = False
        else:
            # invalid input, do nothing or clear
            pass

    def _on_sec_change(self, *args):
        if self._updating:
            return
        val = self.sec_var.get()
        if val.isdigit():
            total = int(val)
            mmss = self._format_mmss(total)
            self._updating = True
            self.time_var.set(mmss)
            self._updating = False
        else:
            # invalid, do nothing
            pass

if __name__ == '__main__':
    app = TimeConverterApp()
    app.mainloop()
