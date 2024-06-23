import tkinter as tk
from tkinter import filedialog, messagebox
from tokenizer import leer_archivo, procesar_texto, guardar_resultado, cargar_tokens, guardar_tokens

class TokenizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tokenizador de Texto")

        self.label = tk.Label(root, text="Seleccione un archivo de texto para analizar:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Seleccionar Archivo", command=self.seleccionar_archivo)
        self.select_button.pack(pady=10)

        self.process_button = tk.Button(root, text="Procesar Texto", command=self.procesar_texto, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.text_box = tk.Text(root, height=10, width=50)
        self.text_box.pack(pady=10)

        self.lexema_text = tk.Text(root, height=4, width=50, wrap=tk.WORD)
        self.lexema_text.pack(pady=10)
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
        self.current_lexema = None
        self.pending_lexemas = []

        # Load the previous tokens from the file
        cargar_tokens("tokens.json")

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def seleccionar_archivo(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            self.process_button.config(state=tk.NORMAL)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, f"Archivo seleccionado: {self.file_path}")

    def clasificar_manual(self, texto, lexema, index):
        self.current_lexema = lexema
        self.texto_completo = texto
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
        if self.file_path:
            texto = leer_archivo(self.file_path)
            resultado = procesar_texto(texto, self.clasificar_manual)
            guardar_resultado(resultado, "resultado.json")
            guardar_tokens("tokens.json")  # Save the updated tokens
            messagebox.showinfo("Proceso completado", "El análisis se ha completado y los resultados se han guardado en 'resultado.json'.")
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo primero.")

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
        guardar_tokens("tokens.json")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenizadorApp(root)
    root.mainloop()
