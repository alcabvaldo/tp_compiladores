import re
import json


lexemas_clasificados = 0
lexemas_no_clasificados = 0

# Variable to store the amount of lexemes in each token
cantidad_lexemas_por_token_en_diccionario = {}
cantidad_inicial_lexemas_por_token_en_diccionario = {}
cantidad_lexemas_por_token = {}

# Definición inicial de patrones para cada token
diccionario_tokens = {
    "ARTICULO": ["el", "la", "los", "las", "un", "una", "unos", "unas"],
    "SUSTANTIVO": ["casa", "perro", "gato", "niño", "mujer", "hombre", "libro", "coche", "ciudad", "país"],
    "VERBO": ["ser", "estar", "tener", "hacer", "poder", "decir", "ir", "ver", "dar", "saber"],
    "ADJETIVO": ["bueno", "malo", "grande", "pequeño", "nuevo", "viejo", "alto", "bajo", "largo", "corto"],
    "ADVERBIO": ["bien", "mal", "muy", "más", "menos", "nunca", "siempre", "ahora", "después", "antes"],
    "OTROS": ["y", "o", "pero", "porque", "si", "aunque", "como", "cuando", "donde", "que"],
    "ERROR_LX": ["@#$%<>`~","csa", "gto", "aunqe", "poer", "esatr", "tenr", "libor", "pquiño", "mnus", "dondee"]
}

# Initialize cantidad_lexemas_por_token
for token, lexemas in diccionario_tokens.items():
    cantidad_lexemas_por_token_en_diccionario[token] = len(lexemas)

def clasificar_lexema(lexema):
    for token, patrones in diccionario_tokens.items():
        if lexema in patrones:
            return token
    return None

def actualizar_patrones(token, lexema):
    diccionario_tokens[token].append(lexema)
    cantidad_lexemas_por_token_en_diccionario[token] += 1

def leer_archivo(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extraer_lexemas(texto, log):
    lexemas = []
    palabra = ""
    patron_letras = re.compile(r'[a-záéíóúüñ]', re.IGNORECASE)  # Incluye todas las letras del español

    for char in texto:
        if patron_letras.match(char):  # Si el carácter es una letra en español
            palabra += char
        else:
            if patron_letras.match(palabra):
                lexemas.append(palabra)
                palabra = ""
            if re.match(r'[,.¡!¿?;:"\'\s]', char):  # Si el carácter es un espacio
                continue
            else:
                log(f"ERROR: Carácter no reconocido: '{char}'")
                raise ValueError(f"Carácter no reconocido: '{char}'")

    if palabra:  # Añadir la última palabra si existe
        lexemas.append(palabra)

    return lexemas

def procesar_texto(texto, nro_archivos_leidos, clasificar_manual, log):
    global lexemas_no_clasificados,lexemas_clasificados
    lexemas = extraer_lexemas(texto.lower(), log)
    resultado = []

    for i, lexema in enumerate(lexemas):
        print("clasificando lexema: ", lexema)
        if i >= len(lexemas):
            break
        token = clasificar_lexema(lexema)
        if not token:
            print(f"lexema: {lexema} no esta clasificado, clasificando manual")
            token = clasificar_manual(texto, lexema, i)
            actualizar_patrones(token, lexema)
            lexemas_no_clasificados += 1
        else:
            lexemas_clasificados += 1

        resultado.append({
            "TOKEN": token,
            "LEXEMA": lexema,
            "POSICION": f"TXT{nro_archivos_leidos}-{i+1}"
        })
        cantidad_lexemas_por_token[token] += 1

    # Informacion para la salida del programa
    log(f"Lexemas totales: {len(lexemas)}")
    log(f"Lexemas procesados en base al diccionario: {lexemas_clasificados}, {round((lexemas_clasificados/len(lexemas))*100, 2)}% del total")
    log(f"Lexemas no en el diccionario que fueron asignados por el usuario: {lexemas_no_clasificados}, {round((lexemas_no_clasificados/len(lexemas))*100, 2)}% del total")
    log("De los lexemas leidos, corresponden a cada token: ")
    log(json.dumps(cantidad_lexemas_por_token, indent=4, ensure_ascii=False))

    log("\nCantidad de lexemas por token en el diccionario antes de la lectura:")
    log(json.dumps(cantidad_inicial_lexemas_por_token_en_diccionario, indent=4, ensure_ascii=False))
    log("Cantidad de lexemas por token en el diccionario despues de la lectura:")
    log(json.dumps(cantidad_lexemas_por_token_en_diccionario, indent=4, ensure_ascii=False))

    cantidad_nuevos_lexemas_por_token = {token: cantidad_lexemas_por_token_en_diccionario[token] - cantidad_inicial_lexemas_por_token_en_diccionario.get(token, 0) for token in cantidad_lexemas_por_token_en_diccionario}
    log("Cantidad de lexemas nuevos por categoria:")
    log(json.dumps(cantidad_nuevos_lexemas_por_token, indent=4, ensure_ascii=False))

    return resultado

def guardar_resultado(resultado, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(resultado, file, ensure_ascii=False, indent=4)

def cargar_diccionario_tokens(diccionario_file, cargar_tokens_previos):
    global diccionario_tokens, cantidad_lexemas_por_token_en_diccionario, cantidad_inicial_lexemas_por_token_en_diccionario, cantidad_lexemas_por_token
    if cargar_tokens_previos:
        try:
            with open(diccionario_file, 'r', encoding='utf-8') as file:
                saved_tokens = json.load(file)
                print("Tokens cargados desde el diccionario:")
                print(json.dumps(saved_tokens, indent=4, ensure_ascii=False))
                for token, lexemas in saved_tokens.items():
                    diccionario_tokens[token].extend(lexemas) #agrego los lexemas no precargados al diccionario
                    cantidad_lexemas_por_token[token] = 0
                    cantidad_lexemas_por_token_en_diccionario[token] = len(lexemas)
                    cantidad_inicial_lexemas_por_token_en_diccionario[token] = len(lexemas)
        except FileNotFoundError:
            pass
    else:
        print("Se utilizara el diccionario por defecto:")
        print(json.dumps(diccionario_tokens, indent=4, ensure_ascii=False))
        for token, lexemas in diccionario_tokens.items():
            cantidad_lexemas_por_token_en_diccionario[token] = len(lexemas)
            cantidad_inicial_lexemas_por_token_en_diccionario[token] = len(lexemas)
            cantidad_lexemas_por_token = 0

def guardar_diccionario_tokens(diccionario_file):
    with open(diccionario_file, 'w', encoding='utf-8') as file:
        json.dump(diccionario_tokens, file, ensure_ascii=False, indent=4)
