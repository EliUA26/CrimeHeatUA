CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS delitos (
    id SERIAL PRIMARY KEY,
    
    -- Información del hecho
    tipo_delito VARCHAR(50) NOT NULL, -- ASALTO, MOTOCHORRO, HOMICIDIO, etc.
    fecha_evento DATE DEFAULT CURRENT_DATE,
    gravedad INTEGER CHECK (gravedad BETWEEN 1 AND 10), -- 1: Leve, 10: Crítico
    resumen_breve TEXT,
    
    -- Ubicación
    ubicacion_texto TEXT,             -- Ejemplo: "Avda. Mariscal López y Perú"
    ciudad VARCHAR(100) DEFAULT 'Asunción',
    barrio VARCHAR(100),
    
    -- Geometría (Punto geográfico)
    -- 4326 es el estándar WGS84 usado por GPS y Leaflet.js
    geom GEOMETRY(Point, 4326), 
    
    -- Metadatos para auditoría
    url_fuente TEXT UNIQUE,           -- Link a la noticia original para evitar duplicados
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear un índice espacial para optimizar el mapa de calor
-- Esto es vital para que cuando haya miles de puntos, el mapa no se trabe
CREATE INDEX IF NOT EXISTS idx_delitos_geom ON delitos USING GIST (geom);

-- 4. INSERT DE PRUEBA (MOCK DATA) - Zonas reales de Asunción
-- Nota: En ST_MakePoint se pone primero LONGITUD y luego LATITUD
-- Asunción está aproximadamente en Long: -57.6, Lat: -25.2

DELETE FROM delitos; -- Limpiar datos previos si existen

INSERT INTO delitos (tipo_delito, fecha_evento, gravedad, ubicacion_texto, barrio, geom, resumen_breve)
VALUES 
(
    'ASALTO', 
    '2026-04-20', 
    8, 
    'Cerca del Panteón de los Héroes', 
    'La Encarnación', 
    ST_SetSRID(ST_MakePoint(-57.63591, -25.28219), 4326),
    'Asalto a mano armada a peatón en pleno microcentro.'
),
(
    'MOTOCHORRO', 
    '2026-04-22', 
    6, 
    'Inmediaciones del Estadio General Pablo Rojas', 
    'Barrio Obrero', 
    ST_SetSRID(ST_MakePoint(-57.63600, -25.30150), 4326),
    'Arrebato de celular por parte de dos personas en motocicleta.'
),
(
    'ROBO_DOMICILIARIO', 
    '2026-04-24', 
    5, 
    'Cerca de la Avda. Santa Teresa', 
    'Santa Maria', 
    ST_SetSRID(ST_MakePoint(-57.55500, -25.29500), 4326),
    'Ingreso a vivienda particular durante la madrugada.'
),
(
    'HOMICIDIO', 
    '2026-04-25', 
    10, 
    'Zona Costanera Norte', 
    'Ricardo Brugada (Chacarita)', 
    ST_SetSRID(ST_MakePoint(-57.62500, -25.27500), 4326),
    'Hallazgo de cuerpo con impactos de bala en zona marginal.'
);

-- Mensaje de verificación para la consola
SELECT 'Base de datos de Delitos configurada con éxito' AS estado;