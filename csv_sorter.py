import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv


class CSVSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Sortierer")
        self.root.geometry("600x400")
        self.df = None
        self.original_headers = None

        # Hauptframe
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons für Dateiauswahl
        self.load_button = ttk.Button(self.main_frame, text="CSV Datei laden", command=self.load_csv)
        self.load_button.grid(row=0, column=0, pady=5, sticky=tk.W)

        # Label für geladene Datei
        self.file_label = ttk.Label(self.main_frame, text="Keine Datei geladen")
        self.file_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Frame für Spaltenauswahl
        self.column_frame = ttk.LabelFrame(self.main_frame, text="Spaltenauswahl", padding="5")
        self.column_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Combobox für Spaltenauswahl
        self.column_label = ttk.Label(self.column_frame, text="Sortieren nach:")
        self.column_label.grid(row=0, column=0, padx=5)
        self.column_combo = ttk.Combobox(self.column_frame, state="disabled")
        self.column_combo.grid(row=0, column=1, padx=5)
        self.column_combo.bind('<<ComboboxSelected>>', self.on_column_select)

        # Sortierrichtung
        self.sort_var = tk.StringVar(value="aufsteigend")
        self.asc_radio = ttk.Radiobutton(self.column_frame, text="Aufsteigend",
                                         variable=self.sort_var, value="aufsteigend",
                                         command=self.on_sort_change)
        self.desc_radio = ttk.Radiobutton(self.column_frame, text="Absteigend",
                                          variable=self.sort_var, value="absteigend",
                                          command=self.on_sort_change)
        self.asc_radio.grid(row=1, column=0, pady=5)
        self.desc_radio.grid(row=1, column=1, pady=5)

        # Button zum Sortieren und Speichern
        self.sort_button = ttk.Button(self.main_frame, text="Sortieren und Speichern",
                                      command=self.sort_and_save, state="disabled")
        self.sort_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Vorschau der Daten
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="Datenvorschau", padding="5")
        self.preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview für Datenvorschau
        self.tree = ttk.Treeview(self.preview_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars für Treeview
        self.vsb = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.hsb = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.tree.xview)
        self.hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

    def load_csv(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")])
            if file_path:
                # CSV-Header mit Original-Formatierung lesen
                with open(file_path, 'r') as f:
                    # Direct raw reading of the first line to preserve exact formatting
                    raw_header_line = f.readline().strip()
                    # Split by comma but preserve quoted strings
                    self.original_headers = raw_header_line.split(',')

                # DataFrame laden
                self.df = pd.read_csv(file_path, quoting=0)

                self.file_label.config(text=f"Geladen: {file_path}")
                self.column_combo['values'] = self.original_headers
                self.column_combo['state'] = 'readonly'
                self.column_combo.set(self.original_headers[0])
                self.sort_button['state'] = 'normal'
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei:\n{str(e)}")

    def on_column_select(self, event=None):
        if self.df is not None:
            self.sort_and_update_preview()

    def on_sort_change(self):
        if self.df is not None:
            self.sort_and_update_preview()

    def sort_and_update_preview(self):
        if self.df is not None:
            selected_header = self.column_combo.get()

            # Finde den tatsächlichen Spaltennamen im DataFrame
            actual_column = None
            for orig, df_col in zip(self.original_headers, self.df.columns):
                if orig == selected_header:
                    actual_column = df_col
                    break

            ascending = self.sort_var.get() == "aufsteigend"
            self.df_sorted = self.df.sort_values(by=actual_column, ascending=ascending)
            self.update_preview()

    def update_preview(self):
        # Treeview leeren
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Spalten konfigurieren
        self.tree['columns'] = self.original_headers
        for col, orig_header in zip(self.df.columns, self.original_headers):
            self.tree.heading(orig_header, text=orig_header)
            max_width = max(
                [len(str(self.df[col].iloc[i])) for i in range(len(self.df))] +
                [len(str(orig_header))]
            ) * 10
            self.tree.column(orig_header, width=min(max_width, 300))

        # Daten anzeigen
        df_to_show = self.df_sorted if hasattr(self, 'df_sorted') else self.df
        for i, row in df_to_show.iterrows():
            self.tree.insert("", "end", values=list(row))

    def sort_and_save(self):
        if self.df is None:
            return

        try:
            selected_header = self.column_combo.get()

            # Finde den tatsächlichen Spaltennamen im DataFrame
            actual_column = None
            for orig, df_col in zip(self.original_headers, self.df.columns):
                if orig == selected_header:
                    actual_column = df_col
                    break

            # Sortieren mit dem tatsächlichen Spaltennamen
            ascending = self.sort_var.get() == "aufsteigend"
            sorted_df = self.df.sort_values(by=actual_column, ascending=ascending)

            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Dateien", "*.csv")]
            )

            if save_path:
                # Speichern mit Original-Headerformattierung
                header_line = ','.join(self.original_headers)

                # Speichern mit angepasstem Header
                with open(save_path, 'w', newline='') as f:
                    # Schreibe zuerst die Header-Zeile
                    f.write(header_line + '\n')

                    # Schreibe dann die Daten
                    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                    writer.writerows(sorted_df.values)
                messagebox.showinfo("Erfolg", "Datei wurde erfolgreich gespeichert!")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Sortieren/Speichern:\n{str(e)}")


def main():
    root = tk.Tk()
    app = CSVSorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
