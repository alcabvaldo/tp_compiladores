import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tokenizer import leer_archivo, procesar_texto, guardar_resultado, cargar_diccionario_tokens, guardar_diccionario_tokens

class TokenizadorApp:
    def __init__(self, root):
        # Variables
        self.nro_archivos_leidos = self.obtener_nro_archivos_leidos() + 1 #Se le suma 1 para facilitar logica del siguiente archivo
        self.diccionario_file = "diccionario.json"

        # Mostrar el número de archivos leídos
        self.archivos_leidos_label = tk.Label(root, text=f"Número de archivos leídos: {self.nro_archivos_leidos - 1}")
        self.archivos_leidos_label.pack(pady=10)

        self.root = root
        self.root.title("Tokenizador de Texto")

        self.label = tk.Label(root, text="Seleccione un archivo de texto para analizar:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Seleccionar Archivo", command=self.seleccionar_archivo)
        self.select_button.pack(padx=10, pady=10)

        self.leer_salida_button = tk.Button(root, text="Leer salida anterior?", command=lambda: [self.seleccionar_archivo_json(), self.show_json_as_table(self.file_path)])
        self.leer_salida_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.load_tokens_var = tk.BooleanVar(value=True)
        self.load_tokens_checkbox = tk.Checkbutton(root, text="Cargar diccionario de tokens previos", variable=self.load_tokens_var)
        self.load_tokens_checkbox.pack(pady=10)

        self.process_button = tk.Button(root, text="Procesar Texto", command=self.procesar_texto, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.text_box_frame = tk.Frame(root)
        self.text_box_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.text_box_scrollbar = tk.Scrollbar(self.text_box_frame)
        self.text_box_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box = tk.Text(self.text_box_frame, height=10, width=50, yscrollcommand=self.text_box_scrollbar.set)
        self.text_box.pack(fill=tk.BOTH, expand=True)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        self.lexema_text_frame = tk.Frame(root)
        self.lexema_text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.lexema_text_scrollbar = tk.Scrollbar(self.lexema_text_frame)
        self.lexema_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lexema_text = tk.Text(self.lexema_text_frame, height=4, width=50, wrap=tk.WORD, yscrollcommand=self.lexema_text_scrollbar.set)
        self.lexema_text.pack(fill=tk.BOTH, expand=True)
        self.lexema_text_scrollbar.config(command=self.lexema_text.yview)
        self.lexema_text.tag_configure("highlight", background="gray90")
        self.lexema_text.tag_configure("lexema", font=("Arial", 12, "bold"))

        self.token_label = tk.Label(root, text="Clasificar lexema desconocido como:")
        self.token_label.pack(pady=10)

        self.token_variable = tk.StringVar(root)
        self.token_variable.set("ARTICULO")  # Valor por defecto

        self.token_menu = tk.OptionMenu(root, self.token_variable, "SUSTANTIVO", "ARTICULO", "VERBO", "ADJETIVO", "ADVERBIO", "OTROS", "ERROR_LX")
        self.token_menu.pack(pady=10)

        self.confirm_button = tk.Button(root, text="Confirmar", command=self.confirmar_token, state=tk.DISABLED)
        self.confirm_button.pack(pady=10)

        self.file_path = None
        self.out_file_path = None
        self.current_lexema = None
        self.pending_lexemas = []

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, text):
        self.text_box.insert(tk.END, f"\n{text}")

    def seleccionar_archivo(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            self.process_button.config(state=tk.NORMAL)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, f"Archivo seleccionado: {self.file_path}")

    def seleccionar_archivo_json(self):
        self.out_file_path = filedialog.askopenfilename(filetypes=[("Json files", "*.json")])
        if self.out_file_path:
            self.process_button.config(state=tk.NORMAL)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, f"Archivo seleccionado: {self.out_file_path}")

    def clasificar_manual(self, texto, lexema, index):
        self.current_lexema = lexema
        self.texto_completo = texto

        self.text_box.insert(tk.END, f"\nClasificando manualmente lexema: {lexema}")

        self.highlight_lexema(texto, lexema, index)
        self.confirm_button.config(state=tk.NORMAL)
        self.process_button.config(state=tk.DISABLED)
        self.root.wait_variable(self.token_variable)
        return self.token_variable.get()

    def confirmar_token(self):
        self.process_button.config(state=tk.NORMAL)
        self.confirm_button.config(state=tk.DISABLED)
        self.current_lexema = None

    def procesar_texto(self):
        # Load the previous tokens from the file
        cargar_diccionario_tokens(self.diccionario_file, self.load_tokens_var.get())

        if self.file_path:
            self.log(f"Leyendo archivo nro: {self.nro_archivos_leidos}")
            texto = leer_archivo(self.file_path)
            resultado = procesar_texto(texto, self.nro_archivos_leidos, self.clasificar_manual, self.log)
            resultado_path = f"resultados/salida_{self.nro_archivos_leidos}.json"
            guardar_resultado(resultado, resultado_path)
            guardar_diccionario_tokens(self.diccionario_file)  # Save the updated tokens
            messagebox.showinfo("Proceso completado", f"El análisis se ha completado y los resultados se han guardado en salida_{self.nro_archivos_leidos}.json.")

            self.show_json_as_table(resultado_path)
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo primero.")

    def show_json_as_table(self, resultado_path):
        # Show the JSON file as a table
        with open(resultado_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        table_window = tk.Toplevel(self.root)
        table_window.title("Tabla de salida en lenguaje de Tokens")

        canvas = tk.Canvas(table_window)
        scrollbar = tk.Scrollbar(table_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mouse_wheel(event, canvas=canvas):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # Add column titles
        for j, key in enumerate(data[0].keys()):
            tk.Label(scrollable_frame, text=key, font='Helvetica 10 bold').grid(row=0, column=j)

        # Add rows of values
        for i, entry in enumerate(data):
            for j, (key, value) in enumerate(entry.items()):
                tk.Label(scrollable_frame, text=value).grid(row=i+1, column=j)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def obtener_nro_archivos_leidos(self):
        archivos = os.listdir('resultados/')
        print("Archivos de salida previos encontrados: " + ", ".join(archivos))
        max_num = 0
        for archivo in archivos:
            match = re.match(r'salida_(\d+)', archivo)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return max_num

    def highlight_lexema(self, texto, lexema, index):
        palabras = texto.split()
        start = max(0, index - 20)
        end = min(len(palabras), index + 21)
        surrounding_text = " ".join(palabras[start:index]) + " " + palabras[index] + " " + " ".join(palabras[index+1:end])

        self.lexema_text.config(state=tk.NORMAL)
        self.lexema_text.delete(1.0, tk.END)
        self.lexema_text.insert(tk.END, surrounding_text)
        self.lexema_text.tag_add("highlight", "1.0", tk.END)

        lexema_index = surrounding_text.find(palabras[index])
        lexema_length = len(palabras[index])
        self.lexema_text.tag_add("lexema", f"1.{lexema_index}", f"1.{lexema_index + lexema_length}")
        self.lexema_text.config(state=tk.DISABLED)

    def on_closing(self):
        # Save the tokens before closing
        guardar_diccionario_tokens(self.diccionario_file)
        self.root.destroy()
        os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenizadorApp(root)
    root.mainloop()

