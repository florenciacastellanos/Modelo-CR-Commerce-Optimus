"""
Diccionario de Sinónimos de Causas Raíz - Con Auto-Aprendizaje
==============================================================

Este módulo gestiona la consolidación de causas raíz similares entre períodos.
Incluye un sistema de auto-aprendizaje que:
1. Detecta nuevas similitudes durante los análisis
2. Las registra en un archivo JSON de biblioteca
3. Permite revisión humana antes de confirmar sinónimos permanentes

Autor: CR Commerce Analytics Team
Fecha: 6 Febrero 2026
Version: 1.0
"""

import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

# ========================================
# CONFIGURACIÓN
# ========================================

UMBRAL_SIMILARIDAD = 0.65  # >= 65% se considera candidato a sinónimo
UMBRAL_CONFIRMADO = 0.80   # >= 80% se auto-confirma como sinónimo
MIN_PALABRAS_COMUNES = 2   # Mínimo de palabras clave en común

# Ruta al archivo de biblioteca aprendida
BIBLIOTECA_PATH = Path(__file__).parent / "causas_biblioteca_aprendida.json"

# ========================================
# SINÓNIMOS CONOCIDOS (SEMILLA INICIAL)
# ========================================

SINONIMOS_SEMILLA = {
    "arrepentimiento": {
        "nombre_canonico": "Cancelación por arrepentimiento del comprador",
        "variantes": [
            "cancelación por arrepentimiento",
            "arrepentimiento o compra errónea",
            "arrepentimiento o producto no necesario",
            "compra por error",
            "ya no lo necesita",
            "no necesita el producto",
            "compró por error",
            "se arrepintió"
        ]
    },
    "tracking_seguimiento": {
        "nombre_canonico": "Falta de información de seguimiento del envío",
        "variantes": [
            "falta de información de seguimiento",
            "sin información de seguimiento",
            "no hay tracking",
            "sin actualizaciones de envío",
            "envío sin actualizaciones",
            "falta seguimiento",
            "sin seguimiento del paquete"
        ]
    },
    "extravio": {
        "nombre_canonico": "Extravío de paquete o envío perdido",
        "variantes": [
            "extravío de paquete",
            "paquete extraviado",
            "envío extraviado",
            "paquete perdido",
            "envío perdido",
            "se perdió el paquete"
        ]
    },
    "demora_entrega": {
        "nombre_canonico": "Demora o incumplimiento en fecha de entrega",
        "variantes": [
            "demora en fecha de entrega",
            "incumplimiento fecha de entrega",
            "demora o incumplimiento",
            "no llegó a tiempo",
            "entrega tardía",
            "retraso en entrega",
            "demora en la entrega"
        ]
    },
    "coordinacion_vendedor": {
        "nombre_canonico": "Problemas de coordinación del envío con vendedor",
        "variantes": [
            "coordinación del envío",
            "problemas con vendedor",
            "vendedor no responde",
            "falta comunicación vendedor",
            "vendedor no envía"
        ]
    },
    "entregado_no_recibido": {
        "nombre_canonico": "Paquete marcado como entregado pero no recibido",
        "variantes": [
            "marcado entregado no recibido",
            "figura entregado pero no llegó",
            "sistema dice entregado",
            "entregado pero no recibido"
        ]
    },
    "problema_stock": {
        "nombre_canonico": "Inconsistencia o falta de stock",
        "variantes": [
            "falta de stock",
            "sin stock",
            "producto no disponible",
            "inconsistencia de stock",
            "agotado"
        ]
    },
    "saturacion_bodega": {
        "nombre_canonico": "Demora en despacho por saturación de bodega",
        "variantes": [
            "saturación de bodega",
            "demora por alta demanda",
            "problema de bodega",
            "demora en despacho"
        ]
    }
}

# ========================================
# PALABRAS CLAVE PARA MATCHING
# ========================================

PALABRAS_CLAVE = {
    "arrepentimiento": ["arrepent", "error", "errone", "no necesit", "cancelar", "cancel"],
    "tracking": ["seguimiento", "tracking", "actualiz", "rastreo", "rastrear"],
    "extravio": ["extrav", "perd", "desaparec"],
    "demora": ["demor", "retras", "tard", "incumpl", "tiempo"],
    "vendedor": ["vendedor", "coordinación", "comunic", "responde"],
    "entrega": ["entreg", "recib", "lleg"],
    "stock": ["stock", "inventario", "disponib", "agotad"]
}


# ========================================
# CLASE PRINCIPAL
# ========================================

class GestorSinonimos:
    """
    Gestor de sinónimos con capacidad de auto-aprendizaje.
    
    Funcionalidades:
    - Detecta causas similares usando múltiples métodos
    - Registra nuevas similitudes encontradas
    - Mantiene biblioteca persistente en JSON
    - Permite retroalimentación y confirmación
    """
    
    def __init__(self):
        self.sinonimos = self._cargar_sinonimos()
        self.biblioteca_aprendida = self._cargar_biblioteca()
        self.nuevas_similitudes = []  # Similitudes detectadas en esta sesión
    
    def _cargar_sinonimos(self) -> Dict:
        """Carga sinónimos semilla + biblioteca aprendida confirmada"""
        sinonimos = SINONIMOS_SEMILLA.copy()
        
        # Cargar confirmados de biblioteca
        if BIBLIOTECA_PATH.exists():
            try:
                with open(BIBLIOTECA_PATH, 'r', encoding='utf-8') as f:
                    biblioteca = json.load(f)
                
                # Agregar solo los confirmados
                for grupo_id, data in biblioteca.get('confirmados', {}).items():
                    if grupo_id not in sinonimos:
                        sinonimos[grupo_id] = data
                    else:
                        # Extender variantes existentes
                        sinonimos[grupo_id]['variantes'].extend(data.get('variantes', []))
                        sinonimos[grupo_id]['variantes'] = list(set(sinonimos[grupo_id]['variantes']))
            except Exception as e:
                print(f"[WARNING] Error cargando biblioteca: {e}")
        
        return sinonimos
    
    def _cargar_biblioteca(self) -> Dict:
        """Carga biblioteca completa (confirmados + pendientes)"""
        if BIBLIOTECA_PATH.exists():
            try:
                with open(BIBLIOTECA_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "version": "1.0",
            "ultima_actualizacion": None,
            "confirmados": {},
            "pendientes": [],
            "rechazados": []
        }
    
    def _guardar_biblioteca(self):
        """Guarda biblioteca actualizada"""
        self.biblioteca_aprendida['ultima_actualizacion'] = datetime.now().isoformat()
        
        with open(BIBLIOTECA_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.biblioteca_aprendida, f, indent=2, ensure_ascii=False)
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto para comparación"""
        texto = texto.lower().strip()
        # Eliminar puntuación
        texto = re.sub(r'[^\w\s]', ' ', texto)
        # Eliminar múltiples espacios
        texto = re.sub(r'\s+', ' ', texto)
        return texto
    
    def _calcular_similaridad_texto(self, texto1: str, texto2: str) -> float:
        """Calcula similaridad usando SequenceMatcher"""
        t1 = self._normalizar_texto(texto1)
        t2 = self._normalizar_texto(texto2)
        return SequenceMatcher(None, t1, t2).ratio()
    
    def _calcular_palabras_comunes(self, texto1: str, texto2: str) -> int:
        """Cuenta palabras significativas en común"""
        t1_palabras = set(self._normalizar_texto(texto1).split())
        t2_palabras = set(self._normalizar_texto(texto2).split())
        
        # Eliminar palabras muy comunes
        stopwords = {'de', 'la', 'el', 'en', 'con', 'por', 'para', 'del', 'al', 'o', 'y', 'a', 'un', 'una'}
        t1_palabras -= stopwords
        t2_palabras -= stopwords
        
        return len(t1_palabras & t2_palabras)
    
    def _detectar_grupo_por_palabras_clave(self, texto: str) -> Optional[str]:
        """Detecta grupo de sinónimos por palabras clave"""
        texto_norm = self._normalizar_texto(texto)
        
        for grupo_id, palabras in PALABRAS_CLAVE.items():
            matches = sum(1 for p in palabras if p in texto_norm)
            if matches >= 2:
                return grupo_id
        
        return None
    
    def buscar_sinonimo(self, causa: str) -> Optional[str]:
        """
        Busca si una causa tiene un sinónimo conocido.
        
        Returns:
            Nombre canónico si existe, None si no
        """
        causa_norm = self._normalizar_texto(causa)
        
        for grupo_id, data in self.sinonimos.items():
            # Verificar contra variantes conocidas
            for variante in data['variantes']:
                variante_norm = self._normalizar_texto(variante)
                
                # Match exacto o casi exacto
                if variante_norm in causa_norm or causa_norm in variante_norm:
                    return data['nombre_canonico']
                
                # Match por similaridad alta
                if self._calcular_similaridad_texto(causa, variante) >= UMBRAL_CONFIRMADO:
                    return data['nombre_canonico']
        
        return None
    
    def son_similares(self, causa1: str, causa2: str) -> Tuple[bool, float, str]:
        """
        Determina si dos causas son similares.
        
        Returns:
            Tuple: (son_similares, score, metodo_deteccion)
        """
        # 1. Verificar si ambas pertenecen al mismo grupo conocido
        sinonimo1 = self.buscar_sinonimo(causa1)
        sinonimo2 = self.buscar_sinonimo(causa2)
        
        if sinonimo1 and sinonimo2 and sinonimo1 == sinonimo2:
            return (True, 1.0, "grupo_conocido")
        
        # 2. Calcular similaridad de texto
        similaridad = self._calcular_similaridad_texto(causa1, causa2)
        
        if similaridad >= UMBRAL_CONFIRMADO:
            return (True, similaridad, "similaridad_alta")
        
        # 3. Verificar palabras en común
        palabras_comunes = self._calcular_palabras_comunes(causa1, causa2)
        
        if palabras_comunes >= MIN_PALABRAS_COMUNES and similaridad >= UMBRAL_SIMILARIDAD:
            return (True, similaridad, "palabras_comunes")
        
        # 4. Verificar grupos por palabras clave
        grupo1 = self._detectar_grupo_por_palabras_clave(causa1)
        grupo2 = self._detectar_grupo_por_palabras_clave(causa2)
        
        if grupo1 and grupo2 and grupo1 == grupo2 and similaridad >= 0.5:
            return (True, similaridad, "palabras_clave")
        
        # No son similares
        return (False, similaridad, "ninguno")
    
    def registrar_similitud_detectada(self, causa1: str, causa2: str, score: float, metodo: str):
        """
        Registra una nueva similitud detectada para revisión.
        
        Esta función alimenta la biblioteca de aprendizaje.
        """
        # Verificar si ya existe en pendientes o confirmados
        for pendiente in self.biblioteca_aprendida.get('pendientes', []):
            if causa1 in pendiente.get('causas', []) or causa2 in pendiente.get('causas', []):
                return  # Ya registrado
        
        nueva_similitud = {
            "causas": [causa1, causa2],
            "score": round(score, 3),
            "metodo": metodo,
            "fecha_deteccion": datetime.now().isoformat(),
            "confirmado": score >= UMBRAL_CONFIRMADO  # Auto-confirmar si score alto
        }
        
        self.nuevas_similitudes.append(nueva_similitud)
        
        # Si es auto-confirmada, agregar a confirmados
        if score >= UMBRAL_CONFIRMADO:
            grupo_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.biblioteca_aprendida.setdefault('confirmados', {})[grupo_id] = {
                "nombre_canonico": causa2,  # Usar la más reciente como canónica
                "variantes": [causa1, causa2],
                "auto_detectado": True,
                "score_original": round(score, 3)
            }
            print(f"[AUTO-LEARN] Nueva similitud confirmada: '{causa1[:40]}...' ~ '{causa2[:40]}...' (score: {score:.2f})")
        else:
            # Agregar a pendientes para revisión
            self.biblioteca_aprendida.setdefault('pendientes', []).append(nueva_similitud)
            print(f"[PENDIENTE] Similitud detectada para revision: '{causa1[:40]}...' ~ '{causa2[:40]}...' (score: {score:.2f})")
    
    def consolidar_causas(self, causas_p1: List[Dict], causas_p2: List[Dict]) -> List[Dict]:
        """
        Consolida causas similares de dos períodos.
        
        Args:
            causas_p1: Lista de causas del período 1
            causas_p2: Lista de causas del período 2
        
        Returns:
            Lista de causas consolidadas con estructura:
            {
                'causa': nombre_canonico,
                'pct_p1': porcentaje_p1,
                'pct_p2': porcentaje_p2,
                'casos_p1': casos_estimados_p1,
                'casos_p2': casos_estimados_p2,
                'var_casos': variacion,
                'var_pct': variacion_porcentual,
                'citas_p1': citas_periodo_1,
                'citas_p2': citas_periodo_2,
                'sentimiento_p1': sentimiento_p1,
                'sentimiento_p2': sentimiento_p2,
                'descripcion': descripcion
            }
        """
        causas_consolidadas = []
        causas_p1_usadas = set()
        causas_p2_usadas = set()
        
        # 1. Buscar matches entre P1 y P2
        for i, c1 in enumerate(causas_p1):
            causa1_texto = c1.get('causa', '')
            
            for j, c2 in enumerate(causas_p2):
                if j in causas_p2_usadas:
                    continue
                
                causa2_texto = c2.get('causa', '')
                
                son_similares, score, metodo = self.son_similares(causa1_texto, causa2_texto)
                
                if son_similares:
                    # Registrar para aprendizaje
                    if metodo not in ["grupo_conocido"]:
                        self.registrar_similitud_detectada(causa1_texto, causa2_texto, score, metodo)
                    
                    # Determinar nombre canónico
                    nombre_canonico = self.buscar_sinonimo(causa2_texto) or causa2_texto
                    
                    # Calcular variación
                    casos_p1 = c1.get('casos_estimados', 0)
                    casos_p2 = c2.get('casos_estimados', 0)
                    var_casos = casos_p2 - casos_p1
                    var_pct = ((casos_p2 - casos_p1) / casos_p1 * 100) if casos_p1 > 0 else (100 if casos_p2 > 0 else 0)
                    
                    causa_consolidada = {
                        'causa': nombre_canonico,
                        'pct_p1': c1.get('porcentaje', 0),
                        'pct_p2': c2.get('porcentaje', 0),
                        'casos_p1': casos_p1,
                        'casos_p2': casos_p2,
                        'var_casos': var_casos,
                        'var_pct': round(var_pct, 1),
                        'citas_p1': c1.get('citas', []),
                        'citas_p2': c2.get('citas', []),
                        'sentimiento_p1': c1.get('sentimiento', {}),
                        'sentimiento_p2': c2.get('sentimiento', {}),
                        'descripcion': c2.get('descripcion', c1.get('descripcion', ''))
                    }
                    causas_consolidadas.append(causa_consolidada)
                    
                    causas_p1_usadas.add(i)
                    causas_p2_usadas.add(j)
                    break
        
        # 2. Agregar causas de P1 sin match (DESAPARECEN en P2)
        for i, c1 in enumerate(causas_p1):
            if i not in causas_p1_usadas:
                causa_consolidada = {
                    'causa': c1.get('causa', ''),
                    'pct_p1': c1.get('porcentaje', 0),
                    'pct_p2': 0,
                    'casos_p1': c1.get('casos_estimados', 0),
                    'casos_p2': 0,
                    'var_casos': -c1.get('casos_estimados', 0),
                    'var_pct': -100.0,
                    'citas_p1': c1.get('citas', []),
                    'citas_p2': [],
                    'sentimiento_p1': c1.get('sentimiento', {}),
                    'sentimiento_p2': {},
                    'descripcion': c1.get('descripcion', '')
                }
                causas_consolidadas.append(causa_consolidada)
        
        # 3. Agregar causas de P2 sin match (NUEVAS en P2)
        for j, c2 in enumerate(causas_p2):
            if j not in causas_p2_usadas:
                causa_consolidada = {
                    'causa': c2.get('causa', ''),
                    'pct_p1': 0,
                    'pct_p2': c2.get('porcentaje', 0),
                    'casos_p1': 0,
                    'casos_p2': c2.get('casos_estimados', 0),
                    'var_casos': c2.get('casos_estimados', 0),
                    'var_pct': 100.0,
                    'citas_p1': [],
                    'citas_p2': c2.get('citas', []),
                    'sentimiento_p1': {},
                    'sentimiento_p2': c2.get('sentimiento', {}),
                    'descripcion': c2.get('descripcion', '')
                }
                causas_consolidadas.append(causa_consolidada)
        
        # v6.4.5: Ordenar por % de aparición en P2 (período más reciente) - mayor participación primero
        causas_consolidadas.sort(key=lambda x: x['pct_p2'], reverse=True)
        
        return causas_consolidadas
    
    def finalizar_sesion(self):
        """
        Guarda los aprendizajes de esta sesión.
        Llamar al final del análisis.
        """
        if self.nuevas_similitudes:
            print(f"\n[BIBLIOTECA] Guardando {len(self.nuevas_similitudes)} nuevas similitudes detectadas...")
            self._guardar_biblioteca()
            print(f"[BIBLIOTECA] Guardado en: {BIBLIOTECA_PATH.name}")
        
        return len(self.nuevas_similitudes)


# ========================================
# FUNCIONES DE UTILIDAD
# ========================================

# Instancia global del gestor
_gestor = None

def obtener_gestor() -> GestorSinonimos:
    """Obtiene instancia singleton del gestor"""
    global _gestor
    if _gestor is None:
        _gestor = GestorSinonimos()
    return _gestor

def consolidar_causas_similares(causas_p1: List[Dict], causas_p2: List[Dict]) -> List[Dict]:
    """
    Función de conveniencia para consolidar causas.
    
    Args:
        causas_p1: Lista de causas del período 1
        causas_p2: Lista de causas del período 2
    
    Returns:
        Lista de causas consolidadas
    """
    gestor = obtener_gestor()
    return gestor.consolidar_causas(causas_p1, causas_p2)

def finalizar_aprendizaje() -> int:
    """
    Finaliza la sesión y guarda aprendizajes.
    
    Returns:
        Número de nuevas similitudes detectadas
    """
    gestor = obtener_gestor()
    return gestor.finalizar_sesion()


# ========================================
# TEST
# ========================================

if __name__ == '__main__':
    print("="*80)
    print("TEST: Gestor de Sinónimos con Auto-Aprendizaje")
    print("="*80)
    
    gestor = GestorSinonimos()
    
    # Test: Causas similares
    test_cases = [
        ("Cancelación por arrepentimiento o compra errónea", "Cancelación por arrepentimiento o producto no necesario"),
        ("Falta de información de seguimiento del envío", "Extravío de paquete o envío sin actualizaciones"),
        ("Demora o incumplimiento en fecha de entrega prometida", "Demora o incumplimiento en fecha de entrega"),
        ("Problema totalmente diferente", "Otro problema sin relación")
    ]
    
    print("\nPruebas de similaridad:")
    print("-"*80)
    
    for causa1, causa2 in test_cases:
        son_sim, score, metodo = gestor.son_similares(causa1, causa2)
        status = "[OK] SIMILARES" if son_sim else "[--] DIFERENTES"
        print(f"\n{status} (score: {score:.2f}, metodo: {metodo})")
        print(f"  1: {causa1[:60]}...")
        print(f"  2: {causa2[:60]}...")
    
    # Test: Consolidación
    print("\n" + "="*80)
    print("TEST: Consolidación de causas")
    print("="*80)
    
    causas_p1 = [
        {"causa": "Cancelación por arrepentimiento o compra errónea", "porcentaje": 20, "casos_estimados": 100, "citas": []},
        {"causa": "Demora o incumplimiento en fecha de entrega prometida", "porcentaje": 40, "casos_estimados": 200, "citas": []},
        {"causa": "Falta de información de seguimiento del envío", "porcentaje": 15, "casos_estimados": 75, "citas": []}
    ]
    
    causas_p2 = [
        {"causa": "Cancelación por arrepentimiento o producto no necesario", "porcentaje": 20, "casos_estimados": 150, "citas": []},
        {"causa": "Demora o incumplimiento en fecha de entrega", "porcentaje": 45, "casos_estimados": 300, "citas": []},
        {"causa": "Extravío de paquete o envío sin actualizaciones", "porcentaje": 15, "casos_estimados": 100, "citas": []}
    ]
    
    consolidadas = gestor.consolidar_causas(causas_p1, causas_p2)
    
    print(f"\nResultado: {len(consolidadas)} causas consolidadas (de {len(causas_p1)} + {len(causas_p2)} originales)")
    for c in consolidadas:
        print(f"\n  • {c['causa'][:50]}...")
        print(f"    P1: {c['pct_p1']}% ({c['casos_p1']} casos)")
        print(f"    P2: {c['pct_p2']}% ({c['casos_p2']} casos)")
        print(f"    Var: {c['var_casos']:+d} casos ({c['var_pct']:+.1f}%)")
    
    # Guardar aprendizajes
    nuevas = gestor.finalizar_sesion()
    print(f"\n[OK] {nuevas} nuevas similitudes registradas")
