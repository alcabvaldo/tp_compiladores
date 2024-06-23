import re
import json

# Definición inicial de patrones para cada token
tokens = {
    "ARTICULO": ["el", "la", "los", "las", "un", "una", "unos", "unas"],
    "SUSTANTIVO": [],
    "VERBO": [],
    "ADJETIVO": [],
    "ADVERBIO": [],
    "OTROS": [],
    "ERROR_LX": []
}

def clasificar_lexema(lexema):
    for token, patrones in tokens.items():
        if lexema in patrones:
            return token
    return None

def actualizar_patrones(token, lexema):
    tokens[token].append(lexema)

def leer_archivo(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extraer_lexemas(texto):
    lexemas = []
    palabra = ""
    patron_letras = re.compile(r'[a-záéíóúüñ]', re.IGNORECASE)  # Incluye todas las letras del español

    for char in texto:
        if patron_letras.match(char):  # Si el carácter es una letra en español
            palabra += char
        else:
            if palabra:
                lexemas.append(palabra)
                palabra = ""
            if re.match(r'\s', char):  # Si el carácter es un espacio
                continue
            else:
                lexemas.append(char)

    if palabra:  # Añadir la última palabra si existe
        lexemas.append(palabra)

    return lexemas

def procesar_texto(texto, clasificar_manual):
    lexemas = extraer_lexemas(texto.lower())
    resultado = []

    for i, lexema in enumerate(lexemas):
        token = clasificar_lexema(lexema)
        if not token:
            token = clasificar_manual(texto, lexema, i)
            actualizar_patrones(token, lexema)

        resultado.append({
            "TOKEN": token,
            "LEXEMA": lexema,
            "POSICION": f"TXT1-{i+1}"
        })

    return resultado

def guardar_resultado(resultado, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(resultado, file, ensure_ascii=False, indent=4)

def cargar_tokens(file_path):
    global tokens
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            saved_tokens = json.load(file)
            for token, lexemas in saved_tokens.items():
                tokens[token] = lexemas
    except FileNotFoundError:
        pass

def guardar_tokens(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(tokens, file, ensure_ascii=False, indent=4)
