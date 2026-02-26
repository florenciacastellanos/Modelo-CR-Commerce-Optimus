$json = @'
{
  "Arrepentimiento - XD": {
    "proceso": "Arrepentimiento - XD",
    "commerce_group": "PDD",
    "site": "MLA",
    "periodo": "Dec 2025",
    "total_conversaciones": 6,
    "causas": [
      {
        "causa": "Producto danado durante envio por embalaje inadecuado",
        "porcentaje": 33,
        "casos_estimados": 2,
        "descripcion": "Productos llegan con danos fisicos por falta de proteccion en el empaque durante el transporte, incluyendo cajas abiertas, abolladuras y roturas.",
        "sentimiento": {"frustracion": 70, "satisfaccion": 30},
        "citas": [
          {"case_id": "420832390", "fecha": "2025-12-05", "texto": "Lucia enfrenta un problema con un joystick de Nintendo Switch que recibio en condiciones danadas. La caja llego abierta y abollada, impidiendo venderlo como nuevo."},
          {"case_id": "423512947", "fecha": "2025-12-16", "texto": "El usuario reporto que el Plato Giratorio llego danado y necesitaba un reembolso. Se reembolso $20.000 a la cuenta de Mercado Pago."}
        ]
      },
      {
        "causa": "Producto no cumple expectativas de calidad esperada",
        "porcentaje": 33,
        "casos_estimados": 2,
        "descripcion": "Compradores reciben productos que no cumplen con la calidad esperada o talle adecuado, generando arrepentimiento y solicitudes de devolucion.",
        "sentimiento": {"frustracion": 55, "satisfaccion": 45},
        "citas": [
          {"case_id": "421656526", "fecha": "2025-12-09", "texto": "El comprador encontro el conjunto deportivo de mujer demasiado grande y decidio realizar una devolucion completa con reembolso."},
          {"case_id": "423425007", "fecha": "2025-12-16", "texto": "El comprador se quejo de la mala calidad de las varillas de rattan economico, indicando que no cumplen con su funcion."}
        ]
      },
      {
        "causa": "Error del comprador al seleccionar producto equivocado",
        "porcentaje": 17,
        "casos_estimados": 1,
        "descripcion": "El comprador se equivoca al realizar la compra y recibe un producto que no necesitaba, generando proceso de devolucion y cambio.",
        "sentimiento": {"frustracion": 40, "satisfaccion": 60},
        "citas": [
          {"case_id": "423347196", "fecha": "2025-12-16", "texto": "El comprador recibio un pedido incorrecto por error en su compra. Queria cambiar los productos por otros para el cumpleanos de su hijo."}
        ]
      },
      {
        "causa": "Problemas logisticos en retiro y entrega de paquetes",
        "porcentaje": 17,
        "casos_estimados": 1,
        "descripcion": "Dificultades para retirar paquetes de sucursales de correo cuando el titular no puede presentarse por vacaciones u otras circunstancias.",
        "sentimiento": {"frustracion": 50, "satisfaccion": 50},
        "citas": [
          {"case_id": "426260016", "fecha": "2025-12-29", "texto": "El vendedor tuvo problemas para retirar un paquete de Correo Argentino debido a vacaciones y no ser el titular del pedido."}
        ]
      }
    ],
    "cobertura": {"target_pct": 80, "covered_pct": 100, "remainder_pct": 0},
    "hallazgo_principal": "Los contactos de Arrepentimiento en XD se dividen entre productos danados durante el envio por embalaje inadecuado y productos que no cumplen las expectativas de calidad o talle. Tambien se identifican errores de seleccion del comprador y dificultades logisticas para retiro de paquetes."
  }
}
'@

$json | Out-File -FilePath "output\analisis_conversaciones_claude_mla_pdd_proceso_p1_2025-12.json" -Encoding UTF8
Write-Output "Part 1 written"
