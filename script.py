import pandas as pd


# --------------------------------------------------------------------
# 2) Unión de listas de pasajeros y vuelos por año
# Se leen los CSVs de pasajeros de 2016 y 2017 y se concatenan en una sola lista.
# NOTA: Se detectan posibles duplicados (por ejemplo, en 2017 el pasajero "Scot Wooten" aparece repetido).
# Se eliminan duplicados basándonos en el ID_Pasajero.
# --------------------------------------------------------------------
pasajeros2016 = pd.read_csv('pasajeros2016.csv')
pasajeros2017 = pd.read_csv('pasajeros2017.csv')
pasajeros = pd.concat([pasajeros2016, pasajeros2017], ignore_index=True)
# Eliminar duplicados en función de ID_Pasajero
pasajeros = pasajeros.drop_duplicates(subset='ID_Pasajero', keep='first')

print("\n Pasajeros:")
print(pasajeros)

# Leer vuelos de 2016 y 2017 y unirlos en una sola lista.
vuelos2016 = pd.read_csv('vuelos2016.csv')
vuelos2017 = pd.read_csv('vuelos2017.csv')
vuelos = pd.concat([vuelos2016, vuelos2017], ignore_index=True)
print("\n Vuelos:")
print(vuelos)

# --------------------------------------------------------------------
# 3) Relacionar pasajeros y vuelos
# Se realiza un merge entre la tabla de vuelos y la lista consolidada de pasajeros.
# Relación: INNER JOIN.
# Utilizamos la columna "Cve_Cliente" de vuelos y "ID_Pasajero" de pasajeros.
# Esto se realiza porque cada vuelo está asociado a un pasajero, y queremos solo los registros con 
# información en ambas tablas.
# --------------------------------------------------------------------
vuelos_pasajeros = pd.merge(vuelos, pasajeros, left_on='Cve_Cliente', right_on='ID_Pasajero', how='inner')
print("\n Vuelos y Pasajeros:")
print(vuelos_pasajeros)

# --------------------------------------------------------------------
# 4) Unir con datos de líneas aéreas
# Se relacionan los vuelos/pasajeros con las líneas aéreas usando la columna "Cve_LA".
# Si no se encuentra coincidencia, asignamos "Otra" a la línea aérea.
# Luego se filtran las columnas resultantes para dejar únicamente:
#  - Viaje (Fecha del viaje)
#  - Clase
#  - Precio
#  - Ruta
#  - Edad
#  - Línea Aérea
# --------------------------------------------------------------------
lineas = pd.read_csv('LineasAereas.csv')
df_consolidado = pd.merge(vuelos_pasajeros, lineas, left_on='Cve_LA', right_on='Code', how='left')
df_consolidado['Linea_Aerea'] = df_consolidado['Linea_Aerea'].fillna('Otra')
df_consolidado = df_consolidado[['Viaje', 'Clase', 'Precio', 'Ruta', 'Edad', 'Linea_Aerea']]

print("Consolidado de Vuelos, Pasajeros y Líneas Aéreas:")
print(df_consolidado)
# --------------------------------------------------------------------
# 5) Calcular el promedio semestral del precio
# Se transforma la columna "Viaje" en datetime para extraer el año y el mes.
# El semestre se define como:
#    1: Ene-Jun (Mes 1-6)
#    2: Jul-Dic (Mes 7-12)
# Se agrupa por Año, Clase, Ruta, Línea Aérea y Semestre para obtener el promedio.
# --------------------------------------------------------------------

df_consolidado['Viaje'] = pd.to_datetime(df_consolidado['Viaje'])
df_consolidado['Año'] = df_consolidado['Viaje'].dt.year
df_consolidado['Mes'] = df_consolidado['Viaje'].dt.month
# Semestre 1 si 'Mes' es menor o igual a 6, 2 si es mayor a 6.
df_consolidado['Semestre'] = df_consolidado['Mes'].apply(lambda m: 1 if m <= 6 else 2)



# Agrupar por Año, Clase, Ruta, Semestre y Linea_Aerea y calcula el promedio del precio.
avg_df = df_consolidado.groupby(['Año','Clase','Ruta','Semestre','Linea_Aerea'])['Precio'].mean().reset_index()

# Pivotamos para que las columnas sean las Linea Aereas
pivot_df = avg_df.pivot_table(index=['Año', 'Clase', 'Ruta', 'Semestre'], 
                              columns='Linea_Aerea', 
                              values='Precio').reset_index()

print("Promedio semestral del precio:")
print(pivot_df)