# cargamos librerías
library(datos)
library(tidyverse)# cargamos datos
paises07 <- as.data.frame(paises %>% filter(anio==2007))  
# paises en 2007

p07 <- ggplot(paises07
    , aes(x=pib_per_capita
    , y=esperanza_de_vida
    , color=continente
    , size=poblacion))+  geom_point() +  scale_x_log10() +  labs(title="Paises en 2007")

p07
