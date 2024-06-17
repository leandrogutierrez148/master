# definimos la cantidad de tramos
num_tramos = 7
# agregamos una columna que agrupe determine a que clase/tramo pertenece cada medición
df_aux['total_pagado_tramos'] = pd.cut(df_aux['total_pagado'], num_tramos)

# determinamos frecuencias absolutas y relativas de cada tramo
frecuencia_precio_abs = df_aux['total_pagado_tramos'].value_counts().sort_index()
frecuencia_precio_rel = df_aux['total_pagado_tramos'].value_counts(normalize=True).sort_index()

# determinamos las frecuencias acumuladas para cada tramo
frecuencia_precio_abs_acum = frecuencia_precio_abs.cumsum()
frecuencia_precio_rel_acum = frecuencia_precio_rel.cumsum()

# creamos un nuevo dataframe de frecuencias para la variable precio
frecuencias_precio = pd.DataFrame({
    'ni': frecuencia_precio_abs,
    'Ni': frecuencia_precio_abs_acum,
    'fi': frecuencia_precio_rel,
    'Fi': frecuencia_precio_rel_acum
})

frecuencias_precio

valores_medios = df_aux['total_pagado_tramos'].apply(lambda x: x.mid)

# Crear un nuevo DataFrame con los valores medios como índice
df_nuevo = pd.DataFrame(df_aux['total_pagado'].values, index=valores_medios, columns=['total_pagado'])

print(df_nuevo)