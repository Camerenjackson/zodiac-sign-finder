"""Professional desktop GUI for the zodiac sign finder."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from zodiac_gui import theme as T
from zodiac_gui.zodiac_logic import (
    ELEMENT_COLORS,
    MONTHS,
    SIGNS_BY_ELEMENT,
    ZodiacError,
    ZodiacResult,
    max_day_for_month,
    lookup,
)


class HoverButton(tk.Frame):
    """Flat primary button with hover and press feedback."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        *,
        bg: str = T.ACCENT,
        fg: str = "#0f172a",
        hover_bg: str = T.ACCENT_HOVER,
    ) -> None:
        super().__init__(master, bg=master.cget("bg") if hasattr(master, "cget") else T.BG)
        self._command = command
        self._bg = bg
        self._hover_bg = hover_bg

        self.label = tk.Label(
            self,
            text=text,
            font=(T.FONT_FAMILY, 11, "bold"),
            bg=bg,
            fg=fg,
            padx=20,
            pady=12,
            cursor="hand2",
        )
        self.label.pack(fill=tk.BOTH, expand=True)

        for widget in (self, self.label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, _event: object = None) -> None:
        self.label.configure(bg=self._bg)
        self._command()

    def _on_enter(self, _event: object = None) -> None:
        self.label.configure(bg=self._hover_bg)

    def _on_leave(self, _event: object = None) -> None:
        self.label.configure(bg=self._bg)


class ZodiacApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(T.WINDOW_TITLE)
        self.geometry("900x640")
        self.minsize(780, 580)
        self.configure(bg=T.BG)

        self._result: ZodiacResult | None = None
        self._anim_job: str | None = None

        self._build_menu()
        self._build_styles()
        self._build_ui()
        self._wire_live_updates()
        self._set_status("Ready — adjust your birth date or press Enter to calculate.")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self, tearoff=0, bg=T.SURFACE, fg=T.TEXT)
        file_menu = tk.Menu(menubar, tearoff=0, bg=T.SURFACE, fg=T.TEXT)
        file_menu.add_command(label="Copy result", accelerator="Ctrl+C", command=self._copy_result)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg=T.SURFACE, fg=T.TEXT)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<Control-c>", lambda _e: self._copy_result())
        self.bind("<Return>", lambda _e: self._calculate())

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Sidebar.TCombobox",
            fieldbackground=T.SURFACE,
            background=T.SURFACE,
            foreground=T.TEXT,
            arrowcolor=T.TEXT_MUTED,
            padding=8,
        )
        style.map(
            "Sidebar.TCombobox",
            fieldbackground=[("readonly", T.SURFACE)],
            foreground=[("readonly", T.TEXT)],
        )
        style.configure(
            "Sidebar.Horizontal.TScale",
            background=T.BG_ELEVATED,
            troughcolor=T.SURFACE,
        )

    def _build_ui(self) -> None:
        top = tk.Frame(self, bg=T.BG_ELEVATED, height=56)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(
            top,
            text="✦  Zodiac Sign Finder",
            font=T.FONT_TITLE,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
        ).pack(side=tk.LEFT, padx=24, pady=14)

        tk.Label(
            top,
            text=f"v{T.APP_VERSION}  ·  Western tropical zodiac",
            font=T.FONT_SMALL,
            bg=T.BG_ELEVATED,
            fg=T.TEXT_DIM,
        ).pack(side=tk.RIGHT, padx=24)

        body = tk.Frame(self, bg=T.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        sidebar = tk.Frame(body, bg=T.SURFACE, highlightbackground=T.BORDER, highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        sidebar.configure(width=280)
        sidebar.pack_propagate(False)

        pad = tk.Frame(sidebar, bg=T.SURFACE, padx=20, pady=20)
        pad.pack(fill=tk.BOTH, expand=True)

        tk.Label(pad, text="Birth date", font=T.FONT_HEADING, bg=T.SURFACE, fg=T.TEXT).pack(
            anchor=tk.W
        )
        tk.Label(
            pad,
            text="Updates live as you change month or day.",
            font=T.FONT_SMALL,
            bg=T.SURFACE,
            fg=T.TEXT_MUTED,
            wraplength=220,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(4, 16))

        tk.Label(pad, text="Month", font=T.FONT_BODY, bg=T.SURFACE, fg=T.TEXT_MUTED).pack(
            anchor=tk.W, pady=(0, 4)
        )
        self.month_var = tk.StringVar(value=MONTHS[0])
        self.month_combo = ttk.Combobox(
            pad,
            textvariable=self.month_var,
            values=MONTHS,
            state="readonly",
            style="Sidebar.TCombobox",
            width=24,
        )
        self.month_combo.pack(fill=tk.X, pady=(0, 16))

        tk.Label(pad, text="Day", font=T.FONT_BODY, bg=T.SURFACE, fg=T.TEXT_MUTED).pack(
            anchor=tk.W, pady=(0, 4)
        )

        day_row = tk.Frame(pad, bg=T.SURFACE)
        day_row.pack(fill=tk.X, pady=(0, 8))

        self.day_var = tk.IntVar(value=15)
        self.day_spin = tk.Spinbox(
            day_row,
            from_=1,
            to=31,
            textvariable=self.day_var,
            width=6,
            font=T.FONT_BODY,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            buttonbackground=T.SURFACE,
            highlightthickness=1,
            highlightbackground=T.BORDER,
            highlightcolor=T.BORDER_FOCUS,
            readonlybackground=T.BG_ELEVATED,
            insertbackground=T.TEXT,
            command=self._on_day_spin,
        )
        self.day_spin.pack(side=tk.LEFT)

        self.day_label = tk.Label(
            day_row,
            text="of 31 days",
            font=T.FONT_SMALL,
            bg=T.SURFACE,
            fg=T.TEXT_DIM,
        )
        self.day_label.pack(side=tk.LEFT, padx=(12, 0))

        self.day_scale = ttk.Scale(
            pad,
            from_=1,
            to=31,
            orient=tk.HORIZONTAL,
            variable=self.day_var,
            command=self._on_scale,
            style="Sidebar.Horizontal.TScale",
        )
        self.day_scale.pack(fill=tk.X, pady=(0, 20))

        HoverButton(pad, "Calculate sign", self._calculate).pack(fill=tk.X, pady=(0, 8))

        secondary = tk.Label(
            pad,
            text="Copy result",
            font=(T.FONT_FAMILY, 10, "underline"),
            bg=T.SURFACE,
            fg=T.TEXT_MUTED,
            cursor="hand2",
        )
        secondary.pack()
        secondary.bind("<Button-1>", lambda _e: self._copy_result())
        secondary.bind("<Enter>", lambda _e: secondary.configure(fg=T.ACCENT))
        secondary.bind("<Leave>", lambda _e: secondary.configure(fg=T.TEXT_MUTED))

        tk.Label(pad, text="Elements", font=T.FONT_HEADING, bg=T.SURFACE, fg=T.TEXT).pack(
            anchor=tk.W, pady=(24, 8)
        )
        for element, signs in SIGNS_BY_ELEMENT.items():
            row = tk.Frame(pad, bg=T.SURFACE)
            row.pack(fill=tk.X, pady=3)
            tk.Label(
                row,
                text="●",
                font=(T.FONT_FAMILY, 10),
                bg=T.SURFACE,
                fg=ELEMENT_COLORS[element],
            ).pack(side=tk.LEFT)
            tk.Label(
                row,
                text=f"{element}: {', '.join(signs)}",
                font=T.FONT_SMALL,
                bg=T.SURFACE,
                fg=T.TEXT_MUTED,
                wraplength=210,
                justify=tk.LEFT,
            ).pack(side=tk.LEFT, padx=(6, 0))

        main_panel = tk.Frame(
            body, bg=T.BG_ELEVATED, highlightbackground=T.BORDER, highlightthickness=1
        )
        main_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_inner = tk.Frame(main_panel, bg=T.BG_ELEVATED, padx=32, pady=28)
        self.result_inner.pack(fill=tk.BOTH, expand=True)

        self.placeholder = tk.Label(
            self.result_inner,
            text="Select your birth date\n\nYour zodiac sign and element\nwill appear here instantly.",
            font=T.FONT_BODY,
            bg=T.BG_ELEVATED,
            fg=T.TEXT_DIM,
            justify=tk.CENTER,
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.result_frame = tk.Frame(self.result_inner, bg=T.BG_ELEVATED)

        self.symbol_label = tk.Label(
            self.result_frame, text="", font=T.FONT_SYMBOL, bg=T.BG_ELEVATED, fg=T.ACCENT
        )
        self.symbol_label.pack(anchor=tk.W)

        self.sign_label = tk.Label(
            self.result_frame, text="", font=T.FONT_SIGN, bg=T.BG_ELEVATED, fg=T.TEXT
        )
        self.sign_label.pack(anchor=tk.W, pady=(4, 12))

        badge_row = tk.Frame(self.result_frame, bg=T.BG_ELEVATED)
        badge_row.pack(anchor=tk.W, pady=(0, 16))

        self.element_badge = tk.Label(
            badge_row,
            text="",
            font=(T.FONT_FAMILY, 10, "bold"),
            padx=12,
            pady=6,
        )
        self.element_badge.pack(side=tk.LEFT)

        self.range_badge = tk.Label(
            badge_row,
            text="",
            font=T.FONT_SMALL,
            bg=T.SURFACE,
            fg=T.TEXT_MUTED,
            padx=10,
            pady=6,
        )
        self.range_badge.pack(side=tk.LEFT, padx=(8, 0))

        tk.Frame(self.result_frame, bg=T.BORDER, height=1).pack(fill=tk.X, pady=(0, 16))

        self.birth_label = tk.Label(
            self.result_frame,
            text="",
            font=T.FONT_BODY,
            bg=T.BG_ELEVATED,
            fg=T.TEXT_MUTED,
        )
        self.birth_label.pack(anchor=tk.W)

        self.message_label = tk.Label(
            self.result_frame,
            text="",
            font=T.FONT_BODY,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            wraplength=480,
            justify=tk.LEFT,
        )
        self.message_label.pack(anchor=tk.W, pady=(16, 0))

        status_bar = tk.Frame(self, bg=T.SURFACE, height=28)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=T.FONT_SMALL,
            bg=T.SURFACE,
            fg=T.TEXT_DIM,
            anchor=tk.W,
        ).pack(fill=tk.X, padx=16, pady=6)

        self._sync_day_limits()
        self._calculate(silent=True)

    def _wire_live_updates(self) -> None:
        self.month_var.trace_add("write", lambda *_: self._on_month_change())
        self.day_var.trace_add("write", lambda *_: self._schedule_live_calc())

    def _schedule_live_calc(self) -> None:
        if self._anim_job:
            self.after_cancel(self._anim_job)
        self._anim_job = self.after(120, self._calculate_live)

    def _on_month_change(self) -> None:
        self._sync_day_limits()
        self._schedule_live_calc()

    def _on_scale(self, _value: str) -> None:
        self._schedule_live_calc()

    def _on_day_spin(self) -> None:
        self._schedule_live_calc()

    def _sync_day_limits(self) -> None:
        try:
            max_day = max_day_for_month(self.month_var.get())
        except ZodiacError:
            max_day = 31
        self.day_spin.configure(to=max_day)
        self.day_scale.configure(to=max_day)
        self.day_label.configure(text=f"of {max_day} days")
        if self.day_var.get() > max_day:
            self.day_var.set(max_day)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _calculate(self, silent: bool = False) -> None:
        try:
            day = int(self.day_var.get())
        except (tk.TclError, ValueError):
            if not silent:
                messagebox.showerror("Invalid day", "Please enter a valid day number.")
            self._set_status("Invalid day — enter a number between 1 and 31.")
            return

        try:
            result = lookup(self.month_var.get(), day)
        except ZodiacError as exc:
            if not silent:
                messagebox.showerror("Invalid input", str(exc))
            self._set_status(str(exc))
            return

        self._result = result
        self._show_result(result)
        self._set_status(
            f"Calculated: {result.sign} ({result.element}) — born {result.month_name} {result.day}."
        )

    def _calculate_live(self) -> None:
        self._anim_job = None
        self._calculate(silent=True)

    def _show_result(self, result: ZodiacResult) -> None:
        self.placeholder.place_forget()
        self.result_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.symbol_label.configure(text=result.symbol, fg=result.element_color)
        self.sign_label.configure(text=result.sign)
        self.element_badge.configure(
            text=f"  {result.element.upper()}  ",
            bg=result.element_color,
            fg="#0f172a",
        )
        self.range_badge.configure(text=f"  {result.date_range}  ")
        self.birth_label.configure(text=f"Your birthday: {result.month_name} {result.day}")
        self.message_label.configure(text=result.element_message)
        self._pulse_result()

    def _pulse_result(self) -> None:
        original = self.sign_label.cget("fg")
        self.sign_label.configure(fg=T.ACCENT)
        self.after(180, lambda: self.sign_label.configure(fg=original))

    def _copy_result(self) -> None:
        if self._result is None:
            messagebox.showinfo("Nothing to copy", "Calculate a sign first.")
            return
        self.clipboard_clear()
        self.clipboard_append(self._result.clipboard_text)
        self._set_status("Result copied to clipboard.")
        messagebox.showinfo("Copied", "Zodiac result copied to your clipboard.")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About",
            f"{T.APP_NAME} v{T.APP_VERSION}\n\n"
            "Professional birth-date lookup for Western zodiac signs and elements.\n\n"
            "Runs entirely on your computer — no accounts or cloud storage.\n\n"
            "Built with Python and tkinter.",
        )


def main() -> None:
    app = ZodiacApp()
    app.mainloop()
