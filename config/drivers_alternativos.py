"""
══════════════════════════════════════════════════════════════════════════════
DRIVERS ALTERNATIVOS - v1.0
══════════════════════════════════════════════════════════════════════════════
Descripción: Drivers opcionales por proceso/caso de uso.
             Solo se usan cuando el usuario lo solicita explícitamente.
             NO reemplazan los drivers estándar de drivers_mapping.py.

Uso: Permiten recalcular el CR con un denominador diferente al estándar
     del Commerce Group, dando una perspectiva complementaria.

Version: 1.0
Last Update: Febrero 2026
Referencias:
- Drivers estándar: config/drivers_mapping.py
- Documentación: docs/DRIVERS_ALTERNATIVOS.md
- Drivers por categoría: docs/DRIVERS_BY_CATEGORY.md
══════════════════════════════════════════════════════════════════════════════
"""


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE DRIVERS ALTERNATIVOS
# ══════════════════════════════════════════════════════════════════════════════
#
# Estructura jerárquica:
#   Commerce Group → Proceso → CDU → driver_key → configuración
#
# Cada driver alternativo contiene:
#   - label: Nombre legible para reportes
#   - description: Qué mide este driver y para qué sirve
#   - tabla_fuente: Tabla principal de BigQuery
#   - fecha_field: Campo de fecha para filtrar períodos
#   - count_expression: Expresión SQL para contar el driver
#   - filter_by_site: Si se debe filtrar por site
#   - sites_disponibles: Sites donde la tabla tiene datos
#   - query_driver: Query SQL para obtener el driver total (P1 y P2)
#   - query_detalle: Query SQL completa con clasificaciones y detalle
#   - notas: Contexto de negocio y cuándo usar este driver
#
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# MAPEO SITE → PREFIJO WAREHOUSE
# ══════════════════════════════════════════════════════════════════════════════
# Algunas tablas no tienen SITE_ID directo; el site se deriva del prefijo
# del warehouse_id. Este mapeo se usa para construir el filtro correcto.

SITE_TO_WAREHOUSE_PREFIX = {
    'MLA': 'AR',
    'MLB': 'BR',
    'MLM': 'MX',
    'MCO': 'CO',
    'MLC': 'CL',
}


DRIVERS_ALTERNATIVOS = {

    # ========================================================================
    # ME PREDESPACHO
    # ========================================================================
    'ME PreDespacho': {
        'driver_estandar_ref': 'shipping_drivers / SUM(drv.OS_WITHOUT_FBM)',
        'procesos': {

            # ────────────────────────────────────────────────────────────────
            # PROCESO: Reputación ME
            # ────────────────────────────────────────────────────────────────
            'Reputación ME': {
                'cdus': {

                    # ════════════════════════════════════════════════════════
                    # CDU: HT Colecta
                    # ════════════════════════════════════════════════════════
                    'HT Colecta': {
                        'alternativas': {

                            'paradas_colecta': {
                                'label': 'Paradas de Colecta',
                                'description': (
                                    'Total de paradas de colecta únicas realizadas '
                                    'en el período. Cada parada se define como la combinación '
                                    'única de vendedor (CUST_ID) + fecha (DATES_DT) + warehouse '
                                    '(WAREHOUSE_ID). Permite calcular el CR sobre el volumen '
                                    'real de operaciones de colecta, no sobre órdenes.'
                                ),
                                'tabla_fuente': 'meli-bi-data.WHOWNER.DM_SHP_FBM_PICKUP',
                                'fecha_field': 'DATES_DT',
                                'count_expression': "COUNT(DISTINCT CONCAT(CUST_ID, '-', CAST(DATES_DT AS STRING), '-', WAREHOUSE_ID))",
                                'filter_by_site': True,
                                'sites_disponibles': ['MLA', 'MLB', 'MLC', 'MCO', 'MLM'],
                                'notas': (
                                    'Útil para calcular el CR sobre el volumen real de '
                                    'operaciones de colecta (paradas), en lugar de órdenes. '
                                    'Permite evaluar cuántos contactos genera cada parada de '
                                    'colecta, lo cual es más representativo para el proceso '
                                    'de Reputación ME / HT Colecta.'
                                ),

                                # ────────────────────────────────────────────
                                # QUERY DRIVER: Solo conteo de paradas P1/P2
                                # ────────────────────────────────────────────
                                'query_driver': """
SELECT
    COUNT(DISTINCT CASE 
        WHEN CAST(DATES_DT AS DATE) BETWEEN '{p1_start}' AND '{p1_end}'
        THEN CONCAT(CUST_ID, '-', CAST(DATES_DT AS STRING), '-', WAREHOUSE_ID)
    END) AS DRV_P1,
    COUNT(DISTINCT CASE 
        WHEN CAST(DATES_DT AS DATE) BETWEEN '{p2_start}' AND '{p2_end}'
        THEN CONCAT(CUST_ID, '-', CAST(DATES_DT AS STRING), '-', WAREHOUSE_ID)
    END) AS DRV_P2
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_PICKUP`
WHERE CAST(DATES_DT AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
    AND SITE_ID {site_filter}
""",

                                # ────────────────────────────────────────────
                                # QUERY DRIVER SEMANAL: Para gráfico de tendencia
                                # ────────────────────────────────────────────
                                'query_driver_semanal': """
SELECT
    DATE_TRUNC(CAST(DATES_DT AS DATE), WEEK(MONDAY)) AS SEMANA,
    COUNT(DISTINCT CONCAT(CUST_ID, '-', CAST(DATES_DT AS STRING), '-', WAREHOUSE_ID)) AS DRIVER
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_PICKUP`
WHERE CAST(DATES_DT AS DATE) BETWEEN DATE_SUB('{p2_end}', INTERVAL 25 WEEK) AND '{p2_end}'
    AND SITE_ID {site_filter}
GROUP BY SEMANA
ORDER BY SEMANA
""",

                                # ────────────────────────────────────────────
                                # QUERY DETALLE: Con clasificaciones completas
                                # ────────────────────────────────────────────
                                'query_detalle': """
SELECT 
    DATES_DT AS DATES,
    EXTRACT(WEEK FROM DATES_DT) AS Semana,
    SITE_ID,
    CONCAT(CUST_ID, '-', CAST(DATES_DT AS STRING), '-', WAREHOUSE_ID) AS Parada,
    FIRST_TYPE_DESCRIPTION,
    SCHEDULED_CHECK,
    STATUS_ON_TIME,
    CUST_ID,
    INBOUND_ID,
    UNITS_RECEIVED,
    CASE 
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'No están preparados', 'Não havia pacotes para coletar', 
            'No había paquetes para colectar', 'El vendedor no los tiene preparados', 
            'Los paquetes o etiquetas están en mal estado', 'O vendedor não os tem preparados', 
            'Os pacotes ou etiquetas estão em mau estado', 'No hay paquetes para colectar', 
            'Não há pacotes para coletar'
        ) THEN 'No había paquetes'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'El local estaba cerrado', 'Negocio cerrado', 'Negócio fechado', 
            'No había nadie en el domicilio', 'Não havia ninguém no endereço', 
            'O local estava fechado'
        ) THEN 'Local Cerrado'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Llevo carga fragil y no apilable', 'Me quedé sin espacio', 
            'Não tenho mais espaço', 'El vehículo tiene sobrepeso', 
            'O veículo está acima do peso', 'Carrego carga frágil e não pode ser empilhada'
        ) THEN 'Sin espacio'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Rota Cancelada', 'Ruta Cancelada'
        ) THEN 'Ruta No Iniciada'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Faltam dados do endereço', 'Há um problema com o endereço', 
            'Tuve un problema con el domicilio', 'Domicilio incorrecto', 
            'Endereço incorreto', 'Está en una zona inaccesible', 
            'Zona inaccesible', 'Fica em uma área inacessível', 'Área inacessível', 
            'El domicilio es incorrecto', 'El domicilio está en una zona inaccesible', 
            'O endereço está incorreto', 'O endereço está em uma área inacessível'
        ) THEN 'Problemas con dirección'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Domicilio no visitado', 'Endereço não visitado', 
            'No pasé por el domicilio', 'Não passei pelo endereço'
        ) THEN 'No pasó'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Tuve un problema mecánico', 'Blocked', 'Bloqueado', 'Confiscado', 
            'Devolvido', 'Devuelto', 'Sofri um acidente', 'Tentativa de roubo', 
            'Tive um problema mecânico', 'Transferido', 'Tuve un accidente', 
            'Roubado', 'Roubaram os pacotes', 'O pacote está avariado', 
            'O pacote foi perdido', 'O pacote foi recusado', 
            'O pacote não pertence à minha região', 'Palavra-chave incorreta.', 
            'Palabra clave incorrecta.', 'Pronto a entregar', 'Robado', 
            'No puedo seguir conduciendo', 'Não posso continuar dirigindo', 
            'Me robaron los paquetes', 'Intento de robo', 'El paquete está dañado', 
            'El paquete no pertenece a mi zona', 'El paquete se perdió', 
            'El comprador cambió de dirección', 'O comprador mudou de endereço', 
            'Próximo destino'
        ) THEN 'Otros'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'El vendedor no tiene el código de autorización', 
            'O vendedor não tem o código de autorização'
        ) THEN 'El vendedor no tiene el código de autorización'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Colecta Parcial', 'Coleta Parcial'
        ) THEN 'Colecta Parcial'
        WHEN FIRST_TYPE_DESCRIPTION IS NULL AND STATUS_ON_TIME IN ('ON_TIME')
            THEN 'Sin Incidencia'
        WHEN FIRST_TYPE_DESCRIPTION IS NULL AND STATUS_ON_TIME IN ('LATE', 'EARLY')
            THEN 'Sin Incidencia - Early/Late'
        ELSE 'Revisar'
    END AS INCIDENT_TYPE,
    CASE
        WHEN (
            FIRST_TYPE_DESCRIPTION IN (
                'El vendedor no tiene el código de autorización', 
                'O vendedor não tem o código de autorização',
                'Os pacotes ou etiquetas estão em mau estado', 
                'O vendedor não os tem preparados', 
                'Los paquetes o etiquetas están en mal estado', 
                'El vendedor no los tiene preparados', 'No están preparados', 
                'Não havia pacotes para coletar', 'No había paquetes para colectar', 
                'El local estaba cerrado', 'Negocio cerrado', 'Negócio fechado', 
                'No había nadie en el domicilio', 'Não havia ninguém no endereço', 
                'O local estava fechado', 'No hay paquetes para colectar', 
                'Não há pacotes para coletar'
            ) 
            AND STATUS_ON_TIME = 'ON_TIME' 
            AND COVERAGE = 'DENTRO_COBERTURA'
        ) THEN 'Seller'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Colecta Parcial', 'Coleta Parcial'
        ) THEN 'Colecta parcial'
        WHEN FIRST_TYPE_DESCRIPTION IN (
            'Faltam dados do endereço', 'Há um problema com o endereço', 
            'Tuve un problema con el domicilio', 'Endereço incorreto', 
            'Domicilio incorrecto', 'Está en una zona inaccesible', 
            'Zona inaccesible', 'Área inacessível', 'Fica em uma área inacessível', 
            'El domicilio es incorrecto', 'El domicilio está en una zona inaccesible', 
            'O endereço está incorreto', 'O endereço está em uma área inacessível'
        ) THEN 'Problemas con dirección'
        WHEN (FIRST_TYPE_DESCRIPTION IS NULL AND STATUS_ON_TIME IN ('ON_TIME'))
            THEN 'Sin Problema'
        ELSE 'MELI'
    END AS CULPA,
    WAS_OUT_OF_RANGE,
    COVERAGE,
    CONFORMITY,
    STOP_TYPE
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_PICKUP`
WHERE SITE_ID {site_filter}
    AND CAST(DATES_DT AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
""",

                                # ────────────────────────────────────────────
                                # CLASIFICACIONES DISPONIBLES
                                # ────────────────────────────────────────────
                                'clasificaciones': {
                                    'INCIDENT_TYPE': {
                                        'label': 'Tipo de Incidencia',
                                        'valores': [
                                            'No había paquetes',
                                            'Local Cerrado',
                                            'Sin espacio',
                                            'Ruta No Iniciada',
                                            'Problemas con dirección',
                                            'No pasó',
                                            'Otros',
                                            'El vendedor no tiene el código de autorización',
                                            'Colecta Parcial',
                                            'Sin Incidencia',
                                            'Sin Incidencia - Early/Late',
                                            'Revisar'
                                        ]
                                    },
                                    'CULPA': {
                                        'label': 'Atribución de Culpa',
                                        'valores': [
                                            'Seller',
                                            'MELI',
                                            'Colecta parcial',
                                            'Problemas con dirección',
                                            'Sin Problema'
                                        ]
                                    },
                                    'STATUS_ON_TIME': {
                                        'label': 'Estado de Puntualidad',
                                        'valores': ['ON_TIME', 'LATE', 'EARLY']
                                    },
                                    'COVERAGE': {
                                        'label': 'Cobertura',
                                        'valores': ['DENTRO_COBERTURA']  # Hay otros valores posibles
                                    }
                                }
                            },

                        }  # fin alternativas de HT Colecta
                    },

                }  # fin cdus de Reputación ME
            },

        }  # fin procesos de ME PreDespacho
    },

    # ========================================================================
    # FBM SELLERS
    # ========================================================================
    'FBM Sellers': {
        'driver_estandar_ref': 'shipping_drivers / SUM(drv.OS_WITH_FBM)',
        'procesos': {

            # ────────────────────────────────────────────────────────────────
            # PROCESO: _TODOS (aplica a todos los procesos de FBM Sellers)
            # ────────────────────────────────────────────────────────────────
            '_TODOS': {
                'descripcion': 'Aplica a todos los procesos de FBM Sellers',
                'cdus': {

                    # ════════════════════════════════════════════════════════
                    # CDU: _CONTIENE_INBOUND
                    # Aplica a todos los CDUs cuyo nombre contiene "INBOUND"
                    # ════════════════════════════════════════════════════════
                    '_CONTIENE_INBOUND': {
                        'cdu_match_type': 'contains',
                        'cdu_match_value': 'INBOUND',
                        'descripcion': 'Aplica a todos los CDUs que contienen INBOUND en su nombre',
                        'alternativas': {

                            'inbounds': {
                                'label': 'Inbounds (Cantidad de INBOUND_ID)',
                                'description': (
                                    'Total de inbounds únicos recibidos en el período. '
                                    'Cada inbound se identifica por INBOUND_ID. Excluye '
                                    'transferencias, warehouses TW/TR, merchants CBT y '
                                    'removals. Permite calcular el CR sobre el volumen '
                                    'real de operaciones de inbound en FBM.'
                                ),
                                'tabla_fuente': 'meli-bi-data.WHOWNER.BT_FBM_INBOUND_OPERATION_AGG',
                                'tabla_join': 'meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN',
                                'fecha_field': 'min_arrival_datetime_tz',
                                'count_expression': 'COUNT(DISTINCT i.INBOUND_ID)',
                                'filter_by_site': True,
                                'site_filter_type': 'warehouse_prefix',
                                'sites_disponibles': ['MLA', 'MLB', 'MLC', 'MCO', 'MLM'],
                                'numerador_filtro': {
                                    'campo': 'PROCESS_ID',
                                    'condicion': 'IN (615, 1981, 2418)',
                                    'descripcion': 'El incoming (numerador) debe filtrarse solo por estos Process IDs al usar este driver alternativo'
                                },
                                'notas': (
                                    'Útil para calcular el CR sobre el volumen real de '
                                    'operaciones de inbound (recepciones), en lugar de '
                                    'órdenes con FBM. El site se deriva del prefijo del '
                                    'warehouse_id (AR=MLA, BR=MLB, MX=MLM, CO=MCO, CL=MLC). '
                                    'Excluye: transfers, warehouses TW/TR, merchants CBT, '
                                    'removals (INB_FLAG_REMOVAL=0). '
                                    'IMPORTANTE: El numerador (incoming) debe filtrarse por '
                                    'PROCESS_ID IN (615, 1981, 2418).'
                                ),

                                # ────────────────────────────────────────────
                                # FILTROS BASE (siempre aplicados)
                                # ────────────────────────────────────────────
                                'filtros_base': {
                                    'inb_shipment_type': "NOT IN ('transfer')",
                                    'warehouse_id': "NOT LIKE '%TW%' AND NOT LIKE '%TR%'",
                                    'CUS_CBT_MERCHANT_ID': 'IS NULL (via LEFT JOIN)',
                                    'INB_FLAG_REMOVAL': 'IN (0)',
                                },

                                # ────────────────────────────────────────────
                                # QUERY DRIVER: Conteo de inbounds P1/P2
                                # ────────────────────────────────────────────
                                'query_driver': """
SELECT
    COUNT(DISTINCT CASE 
        WHEN CAST(i.min_arrival_datetime_tz AS DATE) BETWEEN '{p1_start}' AND '{p1_end}'
        THEN i.INBOUND_ID
    END) AS DRV_P1,
    COUNT(DISTINCT CASE 
        WHEN CAST(i.min_arrival_datetime_tz AS DATE) BETWEEN '{p2_start}' AND '{p2_end}'
        THEN i.INBOUND_ID
    END) AS DRV_P2
FROM `meli-bi-data.WHOWNER.BT_FBM_INBOUND_OPERATION_AGG` AS i
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` AS b
    ON i.CUS_CUST_ID = b.CUS_CUST_ID
WHERE CAST(i.min_arrival_datetime_tz AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
    AND i.inb_shipment_type NOT IN ('transfer')
    AND i.warehouse_id NOT LIKE '%TW%'
    AND i.warehouse_id NOT LIKE '%TR%'
    AND b.CUS_CBT_MERCHANT_ID IS NULL
    AND i.INB_FLAG_REMOVAL IN (0)
    AND i.warehouse_id LIKE '{warehouse_prefix}%'
""",

                                # ────────────────────────────────────────────
                                # QUERY DRIVER SEMANAL: Para gráfico de tendencia
                                # ────────────────────────────────────────────
                                'query_driver_semanal': """
SELECT
    DATE_TRUNC(CAST(i.min_arrival_datetime_tz AS DATE), WEEK(MONDAY)) AS SEMANA,
    COUNT(DISTINCT i.INBOUND_ID) AS DRIVER
FROM `meli-bi-data.WHOWNER.BT_FBM_INBOUND_OPERATION_AGG` AS i
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` AS b
    ON i.CUS_CUST_ID = b.CUS_CUST_ID
WHERE CAST(i.min_arrival_datetime_tz AS DATE) BETWEEN DATE_SUB('{p2_end}', INTERVAL 25 WEEK) AND '{p2_end}'
    AND i.inb_shipment_type NOT IN ('transfer')
    AND i.warehouse_id NOT LIKE '%TW%'
    AND i.warehouse_id NOT LIKE '%TR%'
    AND b.CUS_CBT_MERCHANT_ID IS NULL
    AND i.INB_FLAG_REMOVAL IN (0)
    AND i.warehouse_id LIKE '{warehouse_prefix}%'
GROUP BY SEMANA
ORDER BY SEMANA
""",

                                # ────────────────────────────────────────────
                                # QUERY DETALLE: Con métricas completas
                                # ────────────────────────────────────────────
                                'query_detalle': """
SELECT 
    i.INBOUND_ID,
    COUNT(DISTINCT i.INBOUND_SKU) AS Q_SKUs,
    SUM(i.INB_QUANTITY) AS Q_UNITS,
    i.CUS_CUST_ID, 
    i.WAREHOUSE_ID, 
    i.INB_SHIPMENT_TYPE, 
    i.LAST_INB_STATUS, 
    FORMAT_DATE('%Y-%m-%d', CAST(i.min_arrival_datetime_tz AS DATE)) AS fecha_llegada,
    CASE 
        WHEN i.warehouse_id LIKE 'BR%' THEN 'MLB'
        WHEN i.warehouse_id LIKE 'AR%' THEN 'MLA'
        WHEN i.warehouse_id LIKE 'MX%' THEN 'MLM'
        WHEN i.warehouse_id LIKE 'CO%' THEN 'MCO'
        WHEN i.warehouse_id LIKE 'CL%' THEN 'MLC'
    END AS Site
FROM `meli-bi-data.WHOWNER.BT_FBM_INBOUND_OPERATION_AGG` AS i
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` AS b
    ON i.CUS_CUST_ID = b.CUS_CUST_ID
WHERE CAST(i.min_arrival_datetime_tz AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
    AND i.inb_shipment_type NOT IN ('transfer')
    AND i.warehouse_id NOT LIKE '%TW%'
    AND i.warehouse_id NOT LIKE '%TR%'
    AND b.CUS_CBT_MERCHANT_ID IS NULL
    AND i.INB_FLAG_REMOVAL IN (0)
    AND i.warehouse_id LIKE '{warehouse_prefix}%'
GROUP BY 1, 4, 5, 6, 7, 8, 9
""",

                                # ────────────────────────────────────────────
                                # CLASIFICACIONES DISPONIBLES
                                # ────────────────────────────────────────────
                                'clasificaciones': {
                                    'LAST_INB_STATUS': {
                                        'label': 'Estado del Inbound',
                                        'valores': []  # Se poblan dinámicamente
                                    },
                                    'INB_SHIPMENT_TYPE': {
                                        'label': 'Tipo de Envío',
                                        'valores': []  # Excluye 'transfer'
                                    }
                                }
                            },

                        }  # fin alternativas de _CONTIENE_INBOUND
                    },

                }  # fin cdus de _TODOS
            },

            # ────────────────────────────────────────────────────────────────
            # PROCESO: FBM-Retiro de Stock
            # ────────────────────────────────────────────────────────────────
            'FBM-Retiro de Stock': {
                'cdus': {

                    # ════════════════════════════════════════════════════════
                    # CDU: _TODOS (aplica a todos los CDUs de Retiro de Stock)
                    # ════════════════════════════════════════════════════════
                    '_TODOS': {
                        'descripcion': 'Aplica a todos los CDUs de FBM-Retiro de Stock',
                        'alternativas': {

                            'retiro_requests': {
                                'label': 'Requests de Retiro de Stock',
                                'description': (
                                    'Total de requests de retiro de stock únicos (FBM_WIT_REQUEST_ID) '
                                    'realizados en el período. Cada request se deduplica tomando la '
                                    'primera fecha de creación. Excluye warehouses TW/TR. Permite '
                                    'calcular el CR sobre el volumen real de operaciones de retiro '
                                    'de stock en FBM, en lugar de órdenes con FBM.'
                                ),
                                'tabla_fuente': 'meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2',
                                'tabla_join_segmento': 'meli-bi-data.EXPLOTACION.SEGMENTO',
                                'tabla_join_sugeridos': 'meli-bi-data.WHOWNER.DM_SUGGESTION_KVS_DATA',
                                'fecha_field': 'FBM_WIT_DATE_CREATED',
                                'count_expression': 'COUNT(DISTINCT FBM_WIT_REQUEST_ID)',
                                'filter_by_site': True,
                                'site_filter_type': 'direct',
                                'sites_disponibles': ['MLA', 'MLB', 'MLM', 'MCO', 'MLC'],
                                'notas': (
                                    'Útil para calcular el CR sobre el volumen real de '
                                    'operaciones de retiro de stock (withdrawal requests), '
                                    'en lugar de órdenes con FBM. El site se filtra directamente '
                                    'por SIT_SITE_ID. Excluye: warehouses TW/TR. Se deduplica '
                                    'por FBM_WIT_REQUEST_ID tomando la primera fecha de creación.'
                                ),

                                # ────────────────────────────────────────────
                                # FILTROS BASE (siempre aplicados)
                                # ────────────────────────────────────────────
                                'filtros_base': {
                                    'warehouse_id': "NOT LIKE '%TW%' AND NOT LIKE '%TR%'",
                                    'deduplicacion': 'QUALIFY ROW_NUMBER() OVER(PARTITION BY FBM_WIT_REQUEST_ID ORDER BY FBM_WIT_DATE_CREATED ASC) = 1',
                                },

                                # ────────────────────────────────────────────
                                # QUERY DRIVER: Conteo de requests P1/P2
                                # ────────────────────────────────────────────
                                'query_driver': """
WITH base AS (
    SELECT
        a.SIT_SITE_ID,
        a.FBM_WIT_REQUEST_ID,
        CAST(a.FBM_WIT_DATE_CREATED AS DATE) AS DATE_CREATED
    FROM `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2` a
    WHERE CAST(a.FBM_WIT_DATE_CREATED AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
        AND a.warehouse_id NOT LIKE '%TR%'
        AND a.warehouse_id NOT LIKE '%TW%'
    QUALIFY ROW_NUMBER() OVER(PARTITION BY a.FBM_WIT_REQUEST_ID ORDER BY a.FBM_WIT_DATE_CREATED ASC) = 1
)
SELECT
    COUNT(DISTINCT CASE
        WHEN DATE_CREATED BETWEEN '{p1_start}' AND '{p1_end}'
        THEN FBM_WIT_REQUEST_ID
    END) AS DRV_P1,
    COUNT(DISTINCT CASE
        WHEN DATE_CREATED BETWEEN '{p2_start}' AND '{p2_end}'
        THEN FBM_WIT_REQUEST_ID
    END) AS DRV_P2
FROM base
WHERE SIT_SITE_ID {site_filter}
""",

                                # ────────────────────────────────────────────
                                # QUERY DRIVER SEMANAL: Para gráfico de tendencia
                                # ────────────────────────────────────────────
                                'query_driver_semanal': """
WITH base AS (
    SELECT
        a.SIT_SITE_ID,
        a.FBM_WIT_REQUEST_ID,
        CAST(a.FBM_WIT_DATE_CREATED AS DATE) AS DATE_CREATED
    FROM `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2` a
    WHERE CAST(a.FBM_WIT_DATE_CREATED AS DATE) BETWEEN DATE_SUB('{p2_end}', INTERVAL 25 WEEK) AND '{p2_end}'
        AND a.warehouse_id NOT LIKE '%TR%'
        AND a.warehouse_id NOT LIKE '%TW%'
    QUALIFY ROW_NUMBER() OVER(PARTITION BY a.FBM_WIT_REQUEST_ID ORDER BY a.FBM_WIT_DATE_CREATED ASC) = 1
)
SELECT
    DATE_TRUNC(DATE_CREATED, WEEK(MONDAY)) AS SEMANA,
    COUNT(DISTINCT FBM_WIT_REQUEST_ID) AS DRIVER
FROM base
WHERE SIT_SITE_ID {site_filter}
GROUP BY SEMANA
ORDER BY SEMANA
""",

                                # ────────────────────────────────────────────
                                # QUERY DETALLE: Con clasificaciones completas
                                # ────────────────────────────────────────────
                                'query_detalle': """
WITH
predata2 AS (
    SELECT DISTINCT
        a.fbm_wit_request_id,
        p.segmento
    FROM `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2` a
    LEFT JOIN `meli-bi-data.EXPLOTACION.SEGMENTO` p
        ON a.cus_cust_id_sel = p.cus_cust_id_sel
),
CONFIRMED AS (
    SELECT DISTINCT
        CAST(LEFT(DATE_TAKE, 10) AS DATE) AS DATE_CREATED,
        SELLER_ID, SITE_ID, STATUS, V.TYPE, V.VALUE
    FROM `meli-bi-data.WHOWNER.DM_SUGGESTION_KVS_DATA`, UNNEST(VALUES) AS V
    WHERE V.TYPE = 'withdrawal_id'
        AND STATUS = 'CONFIRMED'
),
sugerido AS (
    SELECT DISTINCT
        fbm_wit_request_id,
        CASE
            WHEN CAST(fbm_wit_request_id AS STRING) IN (SELECT CAST(value AS STRING) FROM CONFIRMED)
            THEN 1 ELSE 0
        END AS flag_sugerido
    FROM `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2`
)
SELECT
    SIT_SITE_ID AS SITE,
    FORMAT_DATE('%Y%m', DATE_CREATED) AS MES_RETIRO,
    CONCAT(FORMAT_DATE('%y', DATE_CREATED), 'Q', EXTRACT(QUARTER FROM DATE_CREATED)) AS QUARTER_RETIRO,
    CONCAT(FORMAT_DATE('%y', DATE_CREATED), 'Q', EXTRACT(QUARTER FROM DATE_CREATED), '%%WK', EXTRACT(WEEK FROM DATE_CREATED)) AS SEMANA_RETIRO,
    FBM_SHIPMENT_TYPE AS TIPO_LOGISTICO2,
    SEGMENTO,
    CASE WHEN SUM_TRANSFER > 0 THEN 'TRANSFER' ELSE FBM_SHIPMENT_TYPE END AS TIPO_LOGISTICO,
    flag_sugerido,
    COUNT(FBM_WIT_REQUEST_ID) AS REQUEST
FROM (
    SELECT
        a.SIT_SITE_ID,
        a.FBM_SHIPMENT_TYPE,
        a.FBM_WIT_REQUEST_ID,
        r.segmento,
        s.flag_sugerido,
        CAST(a.FBM_WIT_DATE_CREATED AS DATE) AS DATE_CREATED,
        SUM(CASE WHEN FBM_SHIPMENT_TYPE = 'TRANSFER' THEN 1 ELSE 0 END) OVER(PARTITION BY a.FBM_WIT_REQUEST_ID) AS SUM_TRANSFER
    FROM `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2` a
    LEFT JOIN predata2 r ON a.fbm_wit_request_id = r.fbm_wit_request_id
    LEFT JOIN sugerido s ON a.fbm_wit_request_id = s.fbm_wit_request_id
    WHERE CAST(a.FBM_WIT_DATE_CREATED AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
        AND a.warehouse_id NOT LIKE '%TR%'
        AND a.warehouse_id NOT LIKE '%TW%'
        AND a.SIT_SITE_ID {site_filter}
    QUALIFY ROW_NUMBER() OVER(PARTITION BY a.FBM_WIT_REQUEST_ID ORDER BY a.FBM_WIT_DATE_CREATED ASC) = 1
)
GROUP BY ALL
""",

                                # ────────────────────────────────────────────
                                # CLASIFICACIONES DISPONIBLES
                                # ────────────────────────────────────────────
                                'clasificaciones': {
                                    'TIPO_LOGISTICO': {
                                        'label': 'Tipo Logístico (con transfers)',
                                        'valores': ['TRANSFER', 'CROSS_DOCKING', 'SAME_WAREHOUSE', 'DROP_OFF']
                                    },
                                    'TIPO_LOGISTICO2': {
                                        'label': 'Tipo Logístico Original',
                                        'valores': []
                                    },
                                    'SEGMENTO': {
                                        'label': 'Segmento del Seller',
                                        'valores': []
                                    },
                                    'flag_sugerido': {
                                        'label': 'Retiro Sugerido',
                                        'valores': [0, 1]
                                    }
                                }
                            },

                            'sellers_con_stock': {
                                'label': 'Sellers con Stock',
                                'description': (
                                    'Total de sellers únicos (CUS_CUST_ID) que tienen stock mayor a 0 '
                                    'en el período. Solo considera sellers 3P y CBT. Permite calcular '
                                    'el CR sobre la base real de sellers con inventario activo en FBM, '
                                    'en lugar de órdenes con FBM.'
                                ),
                                'tabla_fuente': 'meli-bi-data.WHOWNER.DM_SHP_FBM_STOCK_QUALITY',
                                'tabla_join': 'meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN',
                                'fecha_field': 'CALENDAR_DATE',
                                'count_expression': 'COUNT(DISTINCT S.CUS_CUST_ID)',
                                'filter_by_site': True,
                                'site_filter_type': 'direct',
                                'sites_disponibles': ['MLA', 'MLB', 'MLM', 'MCO', 'MLC'],
                                'notas': (
                                    'Útil para calcular el CR sobre la base de sellers con '
                                    'inventario activo (stock > 0) en FBM, en lugar de órdenes. '
                                    'Solo incluye sellers 3P y CBT (CUS_SALES_INITIATIVE). '
                                    'Permite evaluar cuántos contactos genera cada seller con stock, '
                                    'lo cual es más representativo para el proceso de Retiro de Stock.'
                                ),

                                # ────────────────────────────────────────────
                                # FILTROS BASE (siempre aplicados)
                                # ────────────────────────────────────────────
                                'filtros_base': {
                                    'CUS_SALES_INITIATIVE': "LIKE '%3P%' OR LIKE '%CBT%'",
                                    'SKU_TOTAL_STOCK': '> 0',
                                },

                                # ────────────────────────────────────────────
                                # QUERY DRIVER: Conteo de sellers P1/P2
                                # ────────────────────────────────────────────
                                'query_driver': """
SELECT
    COUNT(DISTINCT CASE
        WHEN CAST(S.CALENDAR_DATE AS DATE) BETWEEN '{p1_start}' AND '{p1_end}'
        THEN S.CUS_CUST_ID
    END) AS DRV_P1,
    COUNT(DISTINCT CASE
        WHEN CAST(S.CALENDAR_DATE AS DATE) BETWEEN '{p2_start}' AND '{p2_end}'
        THEN S.CUS_CUST_ID
    END) AS DRV_P2
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_STOCK_QUALITY` S
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` I
    ON S.CUS_CUST_ID = I.CUS_CUST_ID
WHERE CAST(S.CALENDAR_DATE AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
    AND (S.CUS_SALES_INITIATIVE LIKE '%3P%' OR S.CUS_SALES_INITIATIVE LIKE '%CBT%')
    AND S.SKU_TOTAL_STOCK > 0
    AND S.SIT_SITE_ID {site_filter}
""",

                                # ────────────────────────────────────────────
                                # QUERY DRIVER SEMANAL: Para gráfico de tendencia
                                # ────────────────────────────────────────────
                                'query_driver_semanal': """
SELECT
    DATE_TRUNC(CAST(S.CALENDAR_DATE AS DATE), WEEK(MONDAY)) AS SEMANA,
    COUNT(DISTINCT S.CUS_CUST_ID) AS DRIVER
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_STOCK_QUALITY` S
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` I
    ON S.CUS_CUST_ID = I.CUS_CUST_ID
WHERE CAST(S.CALENDAR_DATE AS DATE) BETWEEN DATE_SUB('{p2_end}', INTERVAL 25 WEEK) AND '{p2_end}'
    AND (S.CUS_SALES_INITIATIVE LIKE '%3P%' OR S.CUS_SALES_INITIATIVE LIKE '%CBT%')
    AND S.SKU_TOTAL_STOCK > 0
    AND S.SIT_SITE_ID {site_filter}
GROUP BY SEMANA
ORDER BY SEMANA
""",

                                # ────────────────────────────────────────────
                                # QUERY DETALLE: Con clasificaciones completas
                                # ────────────────────────────────────────────
                                'query_detalle': """
SELECT
    CAST(S.CALENDAR_DATE AS DATE) AS FECHA,
    FORMAT_DATE('%%Y', S.CALENDAR_DATE) AS YEAR,
    EXTRACT(MONTH FROM S.CALENDAR_DATE) AS MONTH,
    EXTRACT(WEEK FROM S.CALENDAR_DATE) AS SEMANA,
    S.SIT_SITE_ID AS SITE,
    CASE WHEN I.ITE_CBT_ORIGIN IS NULL THEN 'local' ELSE I.ITE_CBT_ORIGIN END AS ORIGEN,
    CASE
        WHEN S.CUS_SALES_INITIATIVE LIKE '%3P%' THEN '3P'
        WHEN S.CUS_SALES_INITIATIVE LIKE '%CBT%' THEN 'CBT'
    END AS TYPE_SELLER,
    COUNT(DISTINCT S.CUS_CUST_ID) AS SELLERS_CON_STOCK
FROM `meli-bi-data.WHOWNER.DM_SHP_FBM_STOCK_QUALITY` S
LEFT JOIN `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` I
    ON S.CUS_CUST_ID = I.CUS_CUST_ID
WHERE CAST(S.CALENDAR_DATE AS DATE) BETWEEN '{p1_start}' AND '{p2_end}'
    AND (S.CUS_SALES_INITIATIVE LIKE '%3P%' OR S.CUS_SALES_INITIATIVE LIKE '%CBT%')
    AND S.SKU_TOTAL_STOCK > 0
    AND S.SIT_SITE_ID {site_filter}
GROUP BY ALL
""",

                                # ────────────────────────────────────────────
                                # CLASIFICACIONES DISPONIBLES
                                # ────────────────────────────────────────────
                                'clasificaciones': {
                                    'ORIGEN': {
                                        'label': 'Origen del Seller',
                                        'valores': ['local'],
                                        'detalle': 'Si ITE_CBT_ORIGIN es NULL se clasifica como local'
                                    },
                                    'TYPE_SELLER': {
                                        'label': 'Tipo de Seller',
                                        'valores': ['3P', 'CBT']
                                    }
                                }
                            },

                        }  # fin alternativas de _TODOS
                    },

                }  # fin cdus de FBM-Retiro de Stock
            },

        }  # fin procesos de FBM Sellers
    },

    # ========================================================================
    # MODERACIONES
    # ========================================================================
    'Moderaciones': {
        'driver_estandar_ref': 'orders_by_site / COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'procesos': {

            # ────────────────────────────────────────────────────────────────
            # PROCESO: _TODOS (aplica a todos los procesos de Moderaciones)
            # ────────────────────────────────────────────────────────────────
            '_TODOS': {
                'descripcion': 'Aplica a todos los procesos de Moderaciones',
                'cdus': {

                    # ════════════════════════════════════════════════════════
                    # CDU: _TODOS (aplica a todos los CDUs de Moderaciones)
                    # ════════════════════════════════════════════════════════
                    '_TODOS': {
                        'descripcion': 'Aplica a todos los CDUs de Moderaciones',
                        'alternativas': {

                            'items_moderados': {
                                'label': 'Items Moderados (Cantidad de mod_event_id)',
                                'description': (
                                    'Total de eventos de moderación únicos (mod_event_id) en el período. '
                                    'Solo considera primera moderación (FLG_FIRST_MOD = true). '
                                    'A más items moderados, más contactos potenciales en Moderaciones. '
                                    'Un aumento en órdenes NO explica la variación de Moderaciones; '
                                    'este driver refleja el volumen real de acciones de moderación.'
                                ),
                                'tabla_fuente': 'meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_MODERATIONS',
                                'fecha_field': 'MONTH_ID',
                                'count_expression': 'COUNT(DISTINCT mod_event_id)',
                                'filter_by_site': True,
                                'site_filter_type': 'direct',
                                'sites_disponibles': ['MLA', 'MLB', 'MLM', 'MCO', 'MLC', 'MLU', 'MEC', 'MPE'],
                                'notas': (
                                    'Útil para calcular el CR de Moderaciones sobre el volumen real '
                                    'de items moderados, en lugar de órdenes del site. Un aumento en '
                                    'órdenes NO explica variaciones en Moderaciones; lo que las explica '
                                    'es el volumen de items moderados. Solo se cuentan primeras '
                                    'moderaciones (FLG_FIRST_MOD = true). Excluye MLV. '
                                    'NOTA: MONTH_ID es campo de partición mensual, el gráfico de '
                                    'tendencia es MENSUAL (no semanal).'
                                ),

                                # ────────────────────────────────────────────
                                # FILTROS BASE (siempre aplicados)
                                # ────────────────────────────────────────────
                                'filtros_base': {
                                    'FLG_FIRST_MOD': '= true (solo primera moderación)',
                                    'SIT_SITE_ID': "<> 'MLV' (excluido siempre)",
                                },

                                # ────────────────────────────────────────────
                                # QUERY DRIVER: Conteo de moderaciones P1/P2
                                # ────────────────────────────────────────────
                                'query_driver': """
SELECT
    COUNT(DISTINCT CASE
        WHEN MONTH_ID BETWEEN '{p1_start}' AND '{p1_end}'
        THEN mod_event_id
    END) AS DRV_P1,
    COUNT(DISTINCT CASE
        WHEN MONTH_ID BETWEEN '{p2_start}' AND '{p2_end}'
        THEN mod_event_id
    END) AS DRV_P2
FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_MODERATIONS`
WHERE MONTH_ID BETWEEN '{p1_start}' AND '{p2_end}'
    AND FLG_FIRST_MOD = true
    AND SIT_SITE_ID {site_filter}
""",

                                # ────────────────────────────────────────────
                                # QUERY DRIVER SEMANAL: Tendencia MENSUAL
                                # (MONTH_ID es partición mensual)
                                # ────────────────────────────────────────────
                                'query_driver_semanal': """
SELECT
    MONTH_ID AS SEMANA,
    COUNT(DISTINCT mod_event_id) AS DRIVER
FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_MODERATIONS`
WHERE MONTH_ID BETWEEN DATE_SUB('{p2_end}', INTERVAL 12 MONTH) AND '{p2_end}'
    AND FLG_FIRST_MOD = true
    AND SIT_SITE_ID {site_filter}
GROUP BY SEMANA
ORDER BY SEMANA
""",

                                # ────────────────────────────────────────────
                                # QUERY DETALLE: Con clasificaciones completas
                                # ────────────────────────────────────────────
                                'query_detalle': """
SELECT
    MONTH_ID,
    SIT_SITE_ID,
    FILTER_GROUP,
    FLG_CBT,
    CASE
        WHEN FILTER_GROUP = 'PI' THEN 'PI'
        WHEN FILTER_GROUP = 'DP' THEN 'DP'
        WHEN FILTER_GROUP = 'AP' THEN 'AP'
        WHEN FILTER_GROUP = 'TP' AND filter_name NOT IN ('NOT_CERTIFIED_QUALITY_THUMBNAIL','NOT_CERTIFIED_QUALITY_THUMBNAIL_ACTIVE','PG_POOR_QUALITY_PICTURE_AUTO','POOR_QUALITY_PICTURE','POOR_QUALITY_THUMBNAIL','POOR_QUALITY_THUMBNAIL_ACTIVE','WTF_POOR_QUALITY_THUMBNAIL','PICTURE_SIZE_ERROR','PICTURE_WATERMARK_ERROR','PICTURE_TEXT_OR_LOGO_ERROR','PICTURE_WATERMARK_VARIANT','PICTURE_SIZE_VARIANT','GOOD_QUALITY_THUMBNAIL','PICTURE_ILLUMINATION_VARIANT','PRESENTATION_VARIANT','SINGLE_UNIT_VARIANT','GENERAL_QUALITY_VARIANT','ILLUMINATION_VARIANT','COMBINED_QUALITY_VARIANT','CENTERED_PHOTO_VARIANT','TEST_GENERAL_QUALITY','TEST_SINGLE_UNIT','TEST_ILLUMINATION','TEST_POOR_TWO','TEST_POOR_THREE','TEST_POOR_ONE','FASHION_WRONG_GENDER_WFP_VARIATIONS','FASHION_WRONG_GENDER_WFP','CENTERED_PHOTO','TMP_FASHION_ADHOC_FONDOS','MINIMUM_SIZE','SINGLE_UNIT','PRESENTATION','TEXT_LOGO','WATERMARK','WHITE_BACKGROUND','PROFESSIONAL_PICTURE') THEN 'TP'
        WHEN FILTER_GROUP = 'TP' AND filter_name IN ('NOT_CERTIFIED_QUALITY_THUMBNAIL','NOT_CERTIFIED_QUALITY_THUMBNAIL_ACTIVE','PG_POOR_QUALITY_PICTURE_AUTO','POOR_QUALITY_PICTURE','POOR_QUALITY_THUMBNAIL','POOR_QUALITY_THUMBNAIL_ACTIVE','WTF_POOR_QUALITY_THUMBNAIL','PICTURE_SIZE_ERROR','PICTURE_WATERMARK_ERROR','PICTURE_TEXT_OR_LOGO_ERROR','PICTURE_WATERMARK_VARIANT','PICTURE_SIZE_VARIANT','GOOD_QUALITY_THUMBNAIL','PICTURE_ILLUMINATION_VARIANT','PRESENTATION_VARIANT','SINGLE_UNIT_VARIANT','GENERAL_QUALITY_VARIANT','ILLUMINATION_VARIANT','COMBINED_QUALITY_VARIANT','CENTERED_PHOTO_VARIANT','TEST_GENERAL_QUALITY','TEST_SINGLE_UNIT','TEST_ILLUMINATION','TEST_POOR_TWO','TEST_POOR_THREE','TEST_POOR_ONE','FASHION_WRONG_GENDER_WFP_VARIATIONS','FASHION_WRONG_GENDER_WFP','CENTERED_PHOTO','TMP_FASHION_ADHOC_FONDOS','MINIMUM_SIZE','SINGLE_UNIT','PRESENTATION','TEXT_LOGO','WATERMARK','WHITE_BACKGROUND','PROFESSIONAL_PICTURE') THEN 'PQ'
    END AS FILTER_GROUP_CX,
    CASE
        WHEN filter_name IN ('NOT_CERTIFIED_QUALITY_THUMBNAIL','NOT_CERTIFIED_QUALITY_THUMBNAIL_ACTIVE','PG_POOR_QUALITY_PICTURE_AUTO','POOR_QUALITY_PICTURE','POOR_QUALITY_THUMBNAIL','POOR_QUALITY_THUMBNAIL_ACTIVE','WTF_POOR_QUALITY_THUMBNAIL','PICTURE_SIZE_ERROR','PICTURE_WATERMARK_ERROR','PICTURE_TEXT_OR_LOGO_ERROR','PICTURE_WATERMARK_VARIANT','PICTURE_SIZE_VARIANT','GOOD_QUALITY_THUMBNAIL','PICTURE_ILLUMINATION_VARIANT','PRESENTATION_VARIANT','SINGLE_UNIT_VARIANT','GENERAL_QUALITY_VARIANT','ILLUMINATION_VARIANT','COMBINED_QUALITY_VARIANT','CENTERED_PHOTO_VARIANT','TEST_GENERAL_QUALITY','TEST_SINGLE_UNIT','TEST_ILLUMINATION','TEST_POOR_TWO','TEST_POOR_THREE','TEST_POOR_ONE','FASHION_WRONG_GENDER_WFP_VARIATIONS','FASHION_WRONG_GENDER_WFP','CENTERED_PHOTO','TMP_FASHION_ADHOC_FONDOS','MINIMUM_SIZE','SINGLE_UNIT','PRESENTATION','TEXT_LOGO','WATERMARK','WHITE_BACKGROUND','PROFESSIONAL_PICTURE') THEN 'Calidad de Foto'
        WHEN FILTER_NAME IN ('DOMAIN_WRONG_CATEG_V2','DOMAIN_WRONG_CATEG_CBT_V2','DOMAIN_WRONG_CATEG','DOMAIN_WRONG_CATEG_CATALOGO','DOMAIN_WRONG_CATEG_CBT_PICTURE_V2','DOMAIN_WRONG_CATEG_VENTAS_V2','DOMAIN_WRONG_TITLE','MAL_CATEGORIZADO_CATEG','MAL_CATEGORIZADO_CLASIFICADOS_A_CORE','MAL_CATEGORIZADO_CORE_A_AUTOS','MAL_CATEGORIZADO_CORE_A_CORE','MAL_CATEGORIZADO_CORE_A_INMUEBLES','MAL_CATEGORIZADO_CORE_A_SERVICIOS','MAL_CATEGORIZADO_ESPECIALES_A_ESPECIALES','MAL_CATEGORIZADO_PRICE','ML_MAL_CATEGORIZADO_ALCOHOL_GEL','WTF_WRONG_CATEG','WTF_WRONG_CATEG_V2','WTF_WRONG_PRICE','WTF_WRONG_PRICE_CLASSI_BI_V2','MAL_CATEGORIZADO_CORE_A_CLASI_AUTO','FR_PORNOGRAFIA_MAL_CATEGORIZADA_AUTO_V2','PORNOGRAFIA_MAL_CATEGORIZADA_ADULTOS') THEN 'Mal Categorizado'
        WHEN FILTER_NAME IN ('EXACT_DUPLICATE_CATALOG','EXACT_DUPLICATE_CORE_PRODUCTIZED','EXACT_DUPLICATE_CORE_PRODUCTIZED_WFP','EXACT_DUPLICATE_MOTORS_PLATES','EXACT_DUPLICATE_NO_TITLE','EXACT_DUPLICATE','EXACT_DUPLICATE_CBT','EXACT_DUPLICATE_CBT_WFP','EXACT_DUPLICATE_WFP','EXACT_DUPLICATE_RE','EXACT_DUPLICATE_MOTORS','EXACT_DUPLICATE_PRICE','EXACT_DUPLICATE_PRICE_WFP','EXACT_DUPLICATE_LEV','EXACT_DUPLICATE_CBT_PRICE','EXACT_DUPLICATE_CBT_PRICE_WFP','INVALID_PLATES','BS_EXACT_DUPLICATE','BS_EXACT_DUPLICATE_CBT','BS_EXACT_DUPLICATE_RE','BS_EXACT_DUPLICATE_WFP','TEST_CF_FORBIDDEN_OUT_OF_MKT','TEST_CF_PAUSED_OUT_OF_MKT','TEST_CF_FORBIDDEN_ELEMENT') THEN 'Duplicados'
        WHEN FILTER_NAME IN ('MELI_LABEL','MELI_LABEL_OCR','OCR_GOO_MELI_LABEL_OCR','PG_BRAND_PICTURE_AUTO') THEN 'Labels'
        WHEN FILTER_NAME IN ('BS_CLOSE_CLAIM_BY_SELLER_AUTO','BS_EVAS_CLAIM_BY_SELLER_AUTO','EVASION_CHOICE','EVASION_COMISIONES','EVASION_FISCAL_RECARGO','EVASION_OFERTAS_IRREGULARES','EVASION_OPERACIONES_IRREGULARES','EVASION_PRECIO','EVASION_RELATIVA_AL_PRECIO','EVASION_TEST_RESTRICCIONES','FF_SHIPPING_FISCAL_INFORMATION','FF_SHIPPING_FISCAL_RULE','FF_SHIPPING_TAX_PAYER_TYPE','FI_EVASION_AUTO','FI_EVASION_CONTROL','FR_EVAS_CANT_LLANTAS_AUTO','FR_EVAS_CANT_NEUMATICOS_AUTO','FR_EVASION_LINKS_AUTO','FR_EVASION_MIN_PRICE_AUTO','FR_EVASION_PRICE_AUTO','FR_EVASION_SHIPPING_AUTO','MERCADOENVIOS_RECARGO','ML_EVAF_GRAL_AUTO_T','ML_EVASION_AUTO','ML_EVASION_BULK_AUTO','ML_EVASION_RESERVA','ML_IPHONE_USADO_FSO_MLA','OPERACIONES_IRREGULARES_QR') THEN 'Evasion'
        WHEN FILTER_NAME IN ('PG_PICTURE_OUT_TOPIC_AUTO','PG_PICTURE_OUT_TOPIC_LL_AUTO') THEN 'Out of Topic'
        WHEN FILTER_NAME IN ('CONTENIDO_SENSIBLE_FOTOS','PG_CONTENIDO_SENSIBLE_FOTOS_AUTO','PG_CONTENIDO_SEXUAL_EXPLICITO_AUTO','CONTENIDO_SEXUAL_EXPLICITO','CONTENIDO_SENSIBLE_NICKNAMES','CONT_SENSIBLE_SEXUAL','PORNOGRAFIA_MAL_CATEGORIZADA_ADULTOS','CONTENIDO_SENSIBLE_EXTREMO') THEN 'Contenido Sensible'
        ELSE 'Otros TP'
    END AS FILTER_GROUP_CX3,
    FILTER_NAME,
    COUNT(DISTINCT mod_event_id) AS MODERACIONES
FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_MODERATIONS`
WHERE MONTH_ID BETWEEN '{p1_start}' AND '{p2_end}'
    AND FLG_FIRST_MOD = true
    AND SIT_SITE_ID {site_filter}
GROUP BY ALL
""",

                                # ────────────────────────────────────────────
                                # CLASIFICACIONES DISPONIBLES
                                # ────────────────────────────────────────────
                                'clasificaciones': {
                                    'FILTER_GROUP': {
                                        'label': 'Grupo de Filtro (original)',
                                        'valores': ['PI', 'DP', 'AP', 'TP']
                                    },
                                    'FILTER_GROUP_CX': {
                                        'label': 'Grupo de Filtro CX (separa PQ de TP)',
                                        'valores': ['PI', 'DP', 'AP', 'TP', 'PQ'],
                                        'detalle': {
                                            'PI': 'Propiedad Intelectual',
                                            'DP': 'Datos Personales',
                                            'AP': 'Artículos Prohibidos',
                                            'TP': 'Técnica Prohibida (sin calidad de foto)',
                                            'PQ': 'Calidad de Foto (subconjunto de TP)'
                                        }
                                    },
                                    'FILTER_GROUP_CX3': {
                                        'label': 'Sub-agrupación de filtros (granular)',
                                        'valores': [
                                            'Calidad de Foto',
                                            'Mal Categorizado',
                                            'Duplicados',
                                            'Labels',
                                            'Evasion',
                                            'Out of Topic',
                                            'Contenido Sensible',
                                            'Otros TP'
                                        ]
                                    },
                                    'FLG_CBT': {
                                        'label': 'Flag Cross-Border Trade',
                                        'valores': []
                                    },
                                    'FILTER_NAME': {
                                        'label': 'Nombre de Filtro (detalle individual)',
                                        'valores': []
                                    }
                                },

                                # ────────────────────────────────────────────
                                # INCOMING ALTERNATIVO: Contactos asociados
                                # a cada filtro de moderación. Permite
                                # correlacionar incoming con variaciones del
                                # driver. NO reemplaza el incoming estándar.
                                # ────────────────────────────────────────────
                                'incoming_alternativo': {
                                    'label': 'Incoming por Filtro de Moderación',
                                    'description': (
                                        'Contactos (CAS_CASE_ID) asociados a cada filtro/proceso '
                                        'de moderación. Permite correlacionar el incoming con las '
                                        'variaciones del driver de items moderados. '
                                        'NO reemplaza el incoming estándar del CR.'
                                    ),
                                    'tabla_fuente': 'meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_CX_CONTACTS_MODS',
                                    'tabla_join': 'meli-bi-data.WHOWNER.BT_CX_CONTACTS',
                                    'query': """
SELECT
    mod.MONTH_ID,
    mod.SIT_SITE_ID,
    mod.PROCESS_NAME,
    mod.CDU_RBK,
    mod.SOLUTION_NAME,
    mod.FILTER_NAME,
    mod.filter_group,
    mod.FILTER_GROUP_AJUSTADO,
    mod.FLG_CBT,
    CASE
        WHEN mod.FILTER_GROUP_AJUSTADO = 'PI' OR (mod.FILTER_NAME IS NULL AND mod.PROCESS_NAME = 'PR - Propiedad intelectual') THEN 'PI'
        WHEN mod.FILTER_GROUP_AJUSTADO = 'DP' OR (mod.FILTER_NAME IS NULL AND mod.PROCESS_NAME = 'PR - PR - Datos Personales') THEN 'DP'
        WHEN mod.FILTER_GROUP_AJUSTADO = 'AP' OR (mod.FILTER_NAME IS NULL AND mod.PROCESS_NAME = 'PR - ArtÍculos prohibidos') THEN 'AP'
        WHEN mod.filter_name IN ('ILLUMINATION','PRESENTATION','SINGLE_UNIT','GENERAL_QUALITY','CENTERED_PHOTO','CORRECT_POSE','PROTAGONIST_PRODUCT','COMPLETE_PRODUCT','CORRECT_BACKGROUND','PROFESSIONAL_PICTURE','WHITE_ BACKGROUND','MINIMUM_SIZE','TEXT_LOGO','WATERMARK','NOT_CERTIFIED_QUALITY_THUMBNAIL','NOT_CERTIFIED_QUALITY_THUMBNAIL_ACTIVE','PG_POOR_QUALITY_PICTURE_AUTO','POOR_QUALITY_PICTURE','POOR_QUALITY_THUMBNAIL','POOR_QUALITY_THUMBNAIL_ACTIVE','WTF_POOR_QUALITY_THUMBNAIL','PICTURE_SIZE_ERROR','PICTURE_WATERMARK_ERROR','PICTURE_TEXT_OR_LOGO_ERROR','PICTURE_WATERMARK_VARIANT','PICTURE_SIZE_VARIANT','GOOD_QUALITY_THUMBNAIL','PICTURE_ILLUMINATION_VARIANT','PRESENTATION_VARIANT','SINGLE_UNIT_VARIANT','GENERAL_QUALITY_VARIANT','ILLUMINATION_VARIANT','COMBINED_QUALITY_VARIANT','CENTERED_PHOTO_VARIANT','TEST_GENERAL_QUALITY','TEST_SINGLE_UNIT','TEST_ILLUMINATION','TEST_POOR_TWO','TEST_POOR_THREE','TEST_POOR_ONE','FASHION_WRONG_GENDER_WFP_VARIATIONS','FASHION_WRONG_GENDER_WFP','CENTERED_PHOTO','TMP_FASHION_ADHOC_FONDOS','MINIMUM_SIZE','SINGLE_UNIT','PRESENTATION','TEXT_LOGO','WATERMARK','WHITE_BACKGROUND','PROFESSIONAL_PICTURE')
            OR (mod.FILTER_NAME IS NULL AND mod.PROCESS_NAME = 'Calidad de foto') THEN 'PQ'
        WHEN mod.FILTER_GROUP_AJUSTADO = 'TP' AND mod.filter_name NOT IN ('ILLUMINATION','PRESENTATION','SINGLE_UNIT','GENERAL_QUALITY','CENTERED_PHOTO','CORRECT_POSE','PROTAGONIST_PRODUCT','COMPLETE_PRODUCT','CORRECT_BACKGROUND','PROFESSIONAL_PICTURE','WHITE_ BACKGROUND','MINIMUM_SIZE','TEXT_LOGO','WATERMARK','NOT_CERTIFIED_QUALITY_THUMBNAIL','NOT_CERTIFIED_QUALITY_THUMBNAIL_ACTIVE','PG_POOR_QUALITY_PICTURE_AUTO','POOR_QUALITY_PICTURE','POOR_QUALITY_THUMBNAIL','POOR_QUALITY_THUMBNAIL_ACTIVE','WTF_POOR_QUALITY_THUMBNAIL','PICTURE_SIZE_ERROR','PICTURE_WATERMARK_ERROR','PICTURE_TEXT_OR_LOGO_ERROR','PICTURE_WATERMARK_VARIANT','PICTURE_SIZE_VARIANT','GOOD_QUALITY_THUMBNAIL','PICTURE_ILLUMINATION_VARIANT','PRESENTATION_VARIANT','SINGLE_UNIT_VARIANT','GENERAL_QUALITY_VARIANT','ILLUMINATION_VARIANT','COMBINED_QUALITY_VARIANT','CENTERED_PHOTO_VARIANT','TEST_GENERAL_QUALITY','TEST_SINGLE_UNIT','TEST_ILLUMINATION','TEST_POOR_TWO','TEST_POOR_THREE','TEST_POOR_ONE','FASHION_WRONG_GENDER_WFP_VARIATIONS','FASHION_WRONG_GENDER_WFP','CENTERED_PHOTO','TMP_FASHION_ADHOC_FONDOS','MINIMUM_SIZE','SINGLE_UNIT','PRESENTATION','TEXT_LOGO','WATERMARK','WHITE_BACKGROUND','PROFESSIONAL_PICTURE')
            OR (mod.FILTER_NAME IS NULL AND mod.PROCESS_NAME = 'PR - Técnica prohibida') THEN 'TP'
    END AS FILTER_GROUP_CX,
    inc.user_team_name AS NOMBRE_DEL_EQUIPO,
    CASE WHEN inc.user_ldap LIKE 'ext%' THEN 'Externo' ELSE 'Interno' END AS Centro_rep,
    COUNT(mod.CAS_CASE_ID) AS INCOMING,
    COUNT(inc.ITE_ITEM_ID) AS ITE_ITEM_ID
FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_CX_CONTACTS_MODS` mod
LEFT JOIN `meli-bi-data.WHOWNER.BT_CX_CONTACTS` inc
    ON inc.cas_case_id = mod.cas_case_id
WHERE mod.MONTH_ID BETWEEN '{p1_start}' AND '{p2_end}'
    AND mod.SIT_SITE_ID {site_filter}
GROUP BY ALL
"""
                                },
                            },

                        }  # fin alternativas de _TODOS CDU
                    },

                }  # fin cdus de _TODOS proceso
            },

        }  # fin procesos de Moderaciones
    },

}


# ══════════════════════════════════════════════════════════════════════════════
# ALIASES PARA BÚSQUEDA FLEXIBLE
# ══════════════════════════════════════════════════════════════════════════════

DRIVER_ALT_ALIASES = {
    # Commerce Groups
    'me_predespacho': 'ME PreDespacho',
    'ME_PREDESPACHO': 'ME PreDespacho',
    'ME PreDespacho': 'ME PreDespacho',
    'me predespacho': 'ME PreDespacho',

    'fbm_sellers': 'FBM Sellers',
    'FBM_SELLERS': 'FBM Sellers',
    'FBM Sellers': 'FBM Sellers',
    'fbm sellers': 'FBM Sellers',
    'fbm': 'FBM Sellers',
    'FBM': 'FBM Sellers',

    'moderaciones': 'Moderaciones',
    'MODERACIONES': 'Moderaciones',
    'Moderaciones': 'Moderaciones',

    # Procesos
    'reputacion_me': 'Reputación ME',
    'REPUTACION_ME': 'Reputación ME',
    'Reputacion ME': 'Reputación ME',
    'Reputación ME': 'Reputación ME',
    'reputacion me': 'Reputación ME',

    '_todos': '_TODOS',
    '_TODOS': '_TODOS',

    'fbm_retiro_de_stock': 'FBM-Retiro de Stock',
    'FBM_RETIRO_DE_STOCK': 'FBM-Retiro de Stock',
    'FBM-Retiro de Stock': 'FBM-Retiro de Stock',
    'fbm-retiro de stock': 'FBM-Retiro de Stock',
    'retiro de stock': 'FBM-Retiro de Stock',
    'retiro_de_stock': 'FBM-Retiro de Stock',
    'retiro stock': 'FBM-Retiro de Stock',

    # CDUs
    'ht_colecta': 'HT Colecta',
    'HT_COLECTA': 'HT Colecta',
    'HT Colecta': 'HT Colecta',
    'ht colecta': 'HT Colecta',

    '_contiene_inbound': '_CONTIENE_INBOUND',
    '_CONTIENE_INBOUND': '_CONTIENE_INBOUND',
    'inbound': '_CONTIENE_INBOUND',
    'INBOUND': '_CONTIENE_INBOUND',

    # Drivers alternativos
    'paradas_colecta': 'paradas_colecta',
    'paradas de colecta': 'paradas_colecta',
    'paradas colecta': 'paradas_colecta',
    'pickup stops': 'paradas_colecta',

    'inbounds': 'inbounds',
    'inbound_id': 'inbounds',
    'cantidad de inbounds': 'inbounds',
    'qty inbounds': 'inbounds',

    'retiro_requests': 'retiro_requests',
    'retiro requests': 'retiro_requests',
    'requests de retiro': 'retiro_requests',
    'withdrawal requests': 'retiro_requests',
    'cantidad de requests': 'retiro_requests',
    'qty requests': 'retiro_requests',

    'items_moderados': 'items_moderados',
    'items moderados': 'items_moderados',
    'moderaciones driver': 'items_moderados',
    'moderated items': 'items_moderados',
    'cantidad de moderaciones': 'items_moderados',
    'mod_event_id': 'items_moderados',

    'sellers_con_stock': 'sellers_con_stock',
    'sellers con stock': 'sellers_con_stock',
    'sellers stock': 'sellers_con_stock',
    'sellers with stock': 'sellers_con_stock',
    'cantidad de sellers': 'sellers_con_stock',
    'qty sellers': 'sellers_con_stock',
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _normalize(value: str) -> str:
    """Normaliza un valor usando los aliases disponibles."""
    return DRIVER_ALT_ALIASES.get(value, value)


def get_drivers_alternativos(commerce_group: str, proceso: str = None, cdu: str = None) -> dict:
    """
    Retorna los drivers alternativos disponibles para un commerce group,
    opcionalmente filtrados por proceso y/o CDU.

    Args:
        commerce_group: Nombre del Commerce Group
        proceso: (Opcional) Nombre del proceso
        cdu: (Opcional) Nombre del CDU

    Returns:
        Diccionario con los drivers alternativos encontrados.
        Vacío si no hay drivers alternativos para la combinación dada.

    Example:
        >>> get_drivers_alternativos('ME PreDespacho', 'Reputación ME', 'HT Colecta')
        {'paradas_colecta': {...}}
    """
    cg = _normalize(commerce_group)

    if cg not in DRIVERS_ALTERNATIVOS:
        return {}

    cg_config = DRIVERS_ALTERNATIVOS[cg]

    # Si no se especifica proceso, retornar todos los procesos con sus alternativas
    if proceso is None:
        return cg_config.get('procesos', {})

    proc = _normalize(proceso)
    procesos = cg_config.get('procesos', {})

    if proc not in procesos:
        return {}

    proc_config = procesos[proc]

    # Si no se especifica CDU, retornar todos los CDUs del proceso
    if cdu is None:
        return proc_config.get('cdus', {})

    cdu_norm = _normalize(cdu)
    cdus = proc_config.get('cdus', {})

    if cdu_norm not in cdus:
        return {}

    return cdus[cdu_norm].get('alternativas', {})


def get_driver_alternativo(commerce_group: str, proceso: str, cdu: str, driver_key: str) -> dict:
    """
    Retorna la configuración de un driver alternativo específico.

    Args:
        commerce_group: Nombre del Commerce Group
        proceso: Nombre del proceso
        cdu: Nombre del CDU
        driver_key: Key del driver alternativo (ej: 'paradas_colecta')

    Returns:
        Diccionario con la configuración completa del driver.

    Raises:
        KeyError: Si la combinación no existe.

    Example:
        >>> config = get_driver_alternativo('ME PreDespacho', 'Reputación ME', 'HT Colecta', 'paradas_colecta')
        >>> config['label']
        'Paradas de Colecta'
    """
    alternativas = get_drivers_alternativos(commerce_group, proceso, cdu)

    dk = _normalize(driver_key)

    if dk not in alternativas:
        available = list(alternativas.keys()) if alternativas else []
        raise KeyError(
            f"Driver alternativo '{driver_key}' no encontrado para "
            f"{commerce_group} > {proceso} > {cdu}. "
            f"Disponibles: {available}"
        )

    return alternativas[dk]


def _resolve_site_params(config: dict, site: str) -> dict:
    """
    Resuelve los parámetros de filtro de site según el tipo de driver.
    
    Algunos drivers usan SITE_ID directo (site_filter_type='direct' o ausente),
    otros derivan el site del prefijo del warehouse_id (site_filter_type='warehouse_prefix').
    
    Args:
        config: Configuración del driver alternativo
        site: Código del site (ej: 'MLA', 'MLB')
    
    Returns:
        Diccionario con los parámetros de site resueltos para usar en .format()
    """
    site_filter_type = config.get('site_filter_type', 'direct')
    
    params = {'site': site}
    
    if site_filter_type == 'warehouse_prefix':
        # Site se deriva del prefijo del warehouse_id
        prefix = SITE_TO_WAREHOUSE_PREFIX.get(site)
        if not prefix:
            raise ValueError(
                f"Site '{site}' no tiene mapeo de warehouse_prefix. "
                f"Sites con mapeo: {list(SITE_TO_WAREHOUSE_PREFIX.keys())}"
            )
        params['warehouse_prefix'] = prefix
        params['site_filter'] = f"LIKE '{prefix}%'"  # Fallback si alguna query usa site_filter
    elif config.get('filter_by_site', False):
        params['site_filter'] = f"= '{site}'"
        params['warehouse_prefix'] = SITE_TO_WAREHOUSE_PREFIX.get(site, '')
    else:
        params['site_filter'] = "NOT IN ('MLV')"
        params['warehouse_prefix'] = ''
    
    return params


def build_driver_query(commerce_group: str, proceso: str, cdu: str, driver_key: str,
                       p1_start: str, p1_end: str, p2_start: str, p2_end: str,
                       site: str) -> str:
    """
    Construye la query SQL del driver alternativo con los parámetros reemplazados.

    Args:
        commerce_group: Nombre del Commerce Group
        proceso: Nombre del proceso
        cdu: Nombre del CDU
        driver_key: Key del driver alternativo
        p1_start: Fecha inicio P1 (YYYY-MM-DD)
        p1_end: Fecha fin P1 (YYYY-MM-DD)
        p2_start: Fecha inicio P2 (YYYY-MM-DD)
        p2_end: Fecha fin P2 (YYYY-MM-DD)
        site: Código del site (ej: 'MLA', 'MLB')

    Returns:
        Query SQL lista para ejecutar.

    Raises:
        KeyError: Si el driver no existe.
        ValueError: Si el site no está disponible para este driver.
    """
    config = get_driver_alternativo(commerce_group, proceso, cdu, driver_key)

    # Validar que el site esté disponible
    sites_ok = config.get('sites_disponibles', [])
    if sites_ok and site not in sites_ok:
        raise ValueError(
            f"Site '{site}' no disponible para driver '{driver_key}'. "
            f"Sites disponibles: {sites_ok}"
        )

    # Resolver parámetros de site
    site_params = _resolve_site_params(config, site)

    # Reemplazar placeholders
    query = config['query_driver'].format(
        p1_start=p1_start,
        p1_end=p1_end,
        p2_start=p2_start,
        p2_end=p2_end,
        **site_params
    )

    return query.strip()


def build_detail_query(commerce_group: str, proceso: str, cdu: str, driver_key: str,
                       p1_start: str, p1_end: str, p2_start: str, p2_end: str,
                       site: str) -> str:
    """
    Construye la query SQL de detalle con clasificaciones completas.

    Args:
        Mismos que build_driver_query.

    Returns:
        Query SQL de detalle lista para ejecutar.
    """
    config = get_driver_alternativo(commerce_group, proceso, cdu, driver_key)

    sites_ok = config.get('sites_disponibles', [])
    if sites_ok and site not in sites_ok:
        raise ValueError(
            f"Site '{site}' no disponible para driver '{driver_key}'. "
            f"Sites disponibles: {sites_ok}"
        )

    site_params = _resolve_site_params(config, site)

    query = config['query_detalle'].format(
        p1_start=p1_start,
        p1_end=p1_end,
        p2_start=p2_start,
        p2_end=p2_end,
        **site_params
    )

    return query.strip()


def build_weekly_query(commerce_group: str, proceso: str, cdu: str, driver_key: str,
                       p2_end: str, site: str) -> str:
    """
    Construye la query SQL semanal para gráficos de tendencia.

    Args:
        commerce_group: Nombre del Commerce Group
        proceso: Nombre del proceso
        cdu: Nombre del CDU
        driver_key: Key del driver alternativo
        p2_end: Fecha fin P2 (YYYY-MM-DD) - se calculan 25 semanas hacia atrás
        site: Código del site

    Returns:
        Query SQL semanal lista para ejecutar.
    """
    config = get_driver_alternativo(commerce_group, proceso, cdu, driver_key)

    sites_ok = config.get('sites_disponibles', [])
    if sites_ok and site not in sites_ok:
        raise ValueError(
            f"Site '{site}' no disponible para driver '{driver_key}'. "
            f"Sites disponibles: {sites_ok}"
        )

    site_params = _resolve_site_params(config, site)

    query = config['query_driver_semanal'].format(
        p2_end=p2_end,
        **site_params
    )

    return query.strip()


def listar_drivers_disponibles(commerce_group: str = None) -> list:
    """
    Lista todos los drivers alternativos disponibles, opcionalmente
    filtrados por commerce group.

    Args:
        commerce_group: (Opcional) Filtrar por commerce group

    Returns:
        Lista de diccionarios con:
        - commerce_group, proceso, cdu, driver_key, label, description

    Example:
        >>> listar_drivers_disponibles()
        [
            {
                'commerce_group': 'ME PreDespacho',
                'proceso': 'Reputación ME',
                'cdu': 'HT Colecta',
                'driver_key': 'paradas_colecta',
                'label': 'Paradas de Colecta',
                'description': '...'
            }
        ]
    """
    resultado = []

    for cg_name, cg_data in DRIVERS_ALTERNATIVOS.items():
        if commerce_group and _normalize(commerce_group) != cg_name:
            continue

        for proc_name, proc_data in cg_data.get('procesos', {}).items():
            for cdu_name, cdu_data in proc_data.get('cdus', {}).items():
                # Detectar si es un CDU con pattern matching
                cdu_display = cdu_name
                cdu_match_info = None
                if cdu_data.get('cdu_match_type') == 'contains':
                    cdu_display = f"*{cdu_data['cdu_match_value']}* (patrón)"
                    cdu_match_info = {
                        'type': 'contains',
                        'value': cdu_data['cdu_match_value']
                    }

                # Detectar si es un proceso comodín
                proc_display = proc_name
                if proc_name == '_TODOS':
                    proc_display = '(Todos los procesos)'

                for dk, dk_data in cdu_data.get('alternativas', {}).items():
                    entry = {
                        'commerce_group': cg_name,
                        'proceso': proc_display,
                        'proceso_key': proc_name,
                        'cdu': cdu_display,
                        'cdu_key': cdu_name,
                        'driver_key': dk,
                        'label': dk_data.get('label', dk),
                        'description': dk_data.get('description', ''),
                        'tabla_fuente': dk_data.get('tabla_fuente', ''),
                        'sites_disponibles': dk_data.get('sites_disponibles', []),
                        'site_filter_type': dk_data.get('site_filter_type', 'direct'),
                    }
                    if cdu_match_info:
                        entry['cdu_match'] = cdu_match_info
                    resultado.append(entry)

    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ══════════════════════════════════════════════════════════════════════════════

"""
from config.drivers_alternativos import (
    get_drivers_alternativos,
    get_driver_alternativo,
    build_driver_query,
    build_detail_query,
    build_weekly_query,
    listar_drivers_disponibles
)

# ── EJEMPLO 1: Listar todos los drivers alternativos ──
todos = listar_drivers_disponibles()
for d in todos:
    print(f"{d['commerce_group']} > {d['proceso']} > {d['cdu']} > {d['label']}")
# ME PreDespacho > Reputación ME > HT Colecta > Paradas de Colecta
# FBM Sellers > (Todos los procesos) > *INBOUND* (patrón) > Inbounds (Cantidad de INBOUND_ID)
# FBM Sellers > FBM-Retiro de Stock > (Todos los CDUs) > Requests de Retiro
# FBM Sellers > FBM-Retiro de Stock > (Todos los CDUs) > Sellers con Stock

# ── EJEMPLO 2: Driver con site_filter directo (paradas_colecta) ──
query = build_driver_query(
    commerce_group='ME PreDespacho',
    proceso='Reputación ME',
    cdu='HT Colecta',
    driver_key='paradas_colecta',
    p1_start='2025-12-01', p1_end='2025-12-31',
    p2_start='2026-01-01', p2_end='2026-01-31',
    site='MLA'
)
# Genera: ... AND SITE_ID = 'MLA'

# ── EJEMPLO 3: Driver con warehouse_prefix (inbounds FBM) ──
query = build_driver_query(
    commerce_group='FBM Sellers',
    proceso='_TODOS',
    cdu='_CONTIENE_INBOUND',
    driver_key='inbounds',
    p1_start='2025-12-01', p1_end='2025-12-31',
    p2_start='2026-01-01', p2_end='2026-01-31',
    site='MLA'
)
# Genera: ... AND i.warehouse_id LIKE 'AR%'

# ── EJEMPLO 4: Query de detalle con clasificaciones ──
detail = build_detail_query(
    commerce_group='FBM Sellers',
    proceso='_TODOS',
    cdu='_CONTIENE_INBOUND',
    driver_key='inbounds',
    p1_start='2025-12-01', p1_end='2025-12-31',
    p2_start='2026-01-01', p2_end='2026-01-31',
    site='MLB'
)
# Genera: ... AND i.warehouse_id LIKE 'BR%'
# Ejecutar con: Get-Content query.sql -Raw | bq query --use_legacy_sql=false --format=csv

# ── EJEMPLO 5: Query semanal para gráfico ──
weekly = build_weekly_query(
    commerce_group='FBM Sellers',
    proceso='_TODOS',
    cdu='_CONTIENE_INBOUND',
    driver_key='inbounds',
    p2_end='2026-01-31',
    site='MLM'
)
# Genera: ... AND i.warehouse_id LIKE 'MX%'
"""
