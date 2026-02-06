"""
ContaFácil - Sistema de Contabilidad PGC Español
MVP - Prototipo Funcional
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
import os
from io import BytesIO

# Configuración de página
st.set_page_config(
    page_title="ContaFácil - Contabilidad PGC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# DATOS DE EJEMPLO (En producción usaríamos PostgreSQL)
# =====================================================

if 'entidades' not in st.session_state:
    st.session_state.entidades = [
        {
            'id': 1,
            'nif': 'B12345678',
            'razon_social': 'POINT TRADING S.L.',
            'tipo': 'sociedad_limitada',
            'regimen_iva': 'general',
            'plan_contable': 'pymes'
        },
        {
            'id': 2,
            'nif': '12345678A',
            'razon_social': 'GARCÍA LÓPEZ, JUAN (Autónomo)',
            'tipo': 'autonomo_directa',
            'regimen_iva': 'general',
            'plan_contable': 'pymes'
        },
        {
            'id': 3,
            'nif': 'H03123456',
            'razon_social': 'COMUNIDAD PROP. EDIFICIO LOS NARANJOS',
            'tipo': 'comunidad_propietarios',
            'regimen_iva': 'no_sujeto',
            'plan_contable': 'comunidades'
        }
    ]

if 'asientos' not in st.session_state:
    st.session_state.asientos = []

if 'terceros' not in st.session_state:
    st.session_state.terceros = [
        {'id': 1, 'nif': 'B98765432', 'nombre': 'SUMINISTROS INDUSTRIALES SL', 'tipo': 'proveedor', 'iban': 'ES7620770024003102575766'},
        {'id': 2, 'nif': 'A11111111', 'nombre': 'CLIENTE EJEMPLO SA', 'tipo': 'cliente', 'iban': 'ES9121000418450200051332'},
        {'id': 3, 'nif': '11111111A', 'nombre': 'PROPIETARIO 1A - García Martínez', 'tipo': 'propietario', 'iban': 'ES7921000813610123456789'},
        {'id': 4, 'nif': '22222222B', 'nombre': 'PROPIETARIO 1B - López Fernández', 'tipo': 'propietario', 'iban': 'ES4720385778983000760236'},
    ]

if 'recibos' not in st.session_state:
    st.session_state.recibos = []

if 'facturas' not in st.session_state:
    st.session_state.facturas = []

# =====================================================
# PLAN DE CUENTAS PGC
# =====================================================

PLAN_CUENTAS_PYMES = {
    '100': {'descripcion': 'Capital social', 'tipo': 'patrimonio'},
    '129': {'descripcion': 'Resultado del ejercicio', 'tipo': 'patrimonio'},
    '400': {'descripcion': 'Proveedores', 'tipo': 'pasivo'},
    '410': {'descripcion': 'Acreedores por prestación servicios', 'tipo': 'pasivo'},
    '430': {'descripcion': 'Clientes', 'tipo': 'activo'},
    '465': {'descripcion': 'Remuneraciones pendientes pago', 'tipo': 'pasivo'},
    '472': {'descripcion': 'H.P. IVA soportado', 'tipo': 'activo'},
    '475': {'descripcion': 'H.P. acreedora conceptos fiscales', 'tipo': 'pasivo'},
    '4750': {'descripcion': 'H.P. acreedora por IVA', 'tipo': 'pasivo'},
    '4751': {'descripcion': 'H.P. acreedora por retenciones', 'tipo': 'pasivo'},
    '476': {'descripcion': 'Organismos Seg. Social acreedores', 'tipo': 'pasivo'},
    '477': {'descripcion': 'H.P. IVA repercutido', 'tipo': 'pasivo'},
    '570': {'descripcion': 'Caja, euros', 'tipo': 'activo'},
    '572': {'descripcion': 'Bancos c/c', 'tipo': 'activo'},
    '600': {'descripcion': 'Compras de mercaderías', 'tipo': 'gasto'},
    '621': {'descripcion': 'Arrendamientos y cánones', 'tipo': 'gasto'},
    '622': {'descripcion': 'Reparaciones y conservación', 'tipo': 'gasto'},
    '623': {'descripcion': 'Servicios profesionales indep.', 'tipo': 'gasto'},
    '624': {'descripcion': 'Transportes', 'tipo': 'gasto'},
    '625': {'descripcion': 'Primas de seguros', 'tipo': 'gasto'},
    '626': {'descripcion': 'Servicios bancarios', 'tipo': 'gasto'},
    '627': {'descripcion': 'Publicidad y propaganda', 'tipo': 'gasto'},
    '628': {'descripcion': 'Suministros', 'tipo': 'gasto'},
    '629': {'descripcion': 'Otros servicios', 'tipo': 'gasto'},
    '640': {'descripcion': 'Sueldos y salarios', 'tipo': 'gasto'},
    '642': {'descripcion': 'Seguridad Social empresa', 'tipo': 'gasto'},
    '700': {'descripcion': 'Ventas de mercaderías', 'tipo': 'ingreso'},
    '705': {'descripcion': 'Prestaciones de servicios', 'tipo': 'ingreso'},
    '759': {'descripcion': 'Ingresos por servicios diversos', 'tipo': 'ingreso'},
    '769': {'descripcion': 'Otros ingresos financieros', 'tipo': 'ingreso'},
}

PLAN_CUENTAS_COMUNIDADES = {
    '100': {'descripcion': 'Fondo de reserva', 'tipo': 'patrimonio'},
    '110': {'descripcion': 'Remanente', 'tipo': 'patrimonio'},
    '129': {'descripcion': 'Resultado del ejercicio', 'tipo': 'patrimonio'},
    '410': {'descripcion': 'Acreedores prestación servicios', 'tipo': 'pasivo'},
    '430': {'descripcion': 'Propietarios cuenta corriente', 'tipo': 'activo'},
    '4300': {'descripcion': 'Propietarios - Cuotas ordinarias', 'tipo': 'activo'},
    '4301': {'descripcion': 'Propietarios - Derramas', 'tipo': 'activo'},
    '4309': {'descripcion': 'Propietarios - Dudoso cobro', 'tipo': 'activo'},
    '465': {'descripcion': 'Remuneraciones pendientes pago', 'tipo': 'pasivo'},
    '4751': {'descripcion': 'H.P. acreedora retenciones', 'tipo': 'pasivo'},
    '476': {'descripcion': 'Organismos Seg. Social acreedores', 'tipo': 'pasivo'},
    '570': {'descripcion': 'Caja', 'tipo': 'activo'},
    '572': {'descripcion': 'Bancos c/c', 'tipo': 'activo'},
    '5721': {'descripcion': 'Banco cuenta ordinaria', 'tipo': 'activo'},
    '5722': {'descripcion': 'Banco fondo reserva', 'tipo': 'activo'},
    '621': {'descripcion': 'Arrendamientos y cánones', 'tipo': 'gasto'},
    '622': {'descripcion': 'Reparaciones y conservación', 'tipo': 'gasto'},
    '623': {'descripcion': 'Servicios profesionales', 'tipo': 'gasto'},
    '6230': {'descripcion': 'Honorarios administrador', 'tipo': 'gasto'},
    '625': {'descripcion': 'Primas de seguros', 'tipo': 'gasto'},
    '626': {'descripcion': 'Servicios bancarios', 'tipo': 'gasto'},
    '628': {'descripcion': 'Suministros', 'tipo': 'gasto'},
    '6280': {'descripcion': 'Suministro eléctrico', 'tipo': 'gasto'},
    '6281': {'descripcion': 'Suministro agua', 'tipo': 'gasto'},
    '629': {'descripcion': 'Otros servicios', 'tipo': 'gasto'},
    '6290': {'descripcion': 'Limpieza', 'tipo': 'gasto'},
    '6291': {'descripcion': 'Jardinería', 'tipo': 'gasto'},
    '6293': {'descripcion': 'Mantenimiento ascensor', 'tipo': 'gasto'},
    '630': {'descripcion': 'Tributos', 'tipo': 'gasto'},
    '640': {'descripcion': 'Sueldos y salarios', 'tipo': 'gasto'},
    '642': {'descripcion': 'Seguridad Social empresa', 'tipo': 'gasto'},
    '740': {'descripcion': 'Cuotas de propietarios', 'tipo': 'ingreso'},
    '7400': {'descripcion': 'Cuotas ordinarias', 'tipo': 'ingreso'},
    '7401': {'descripcion': 'Derramas', 'tipo': 'ingreso'},
    '752': {'descripcion': 'Ingresos por arrendamientos', 'tipo': 'ingreso'},
}

# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def obtener_plan_cuentas(tipo_entidad):
    """Devuelve el plan de cuentas según tipo de entidad"""
    if tipo_entidad == 'comunidad_propietarios':
        return PLAN_CUENTAS_COMUNIDADES
    return PLAN_CUENTAS_PYMES

def generar_numero_asiento(entidad_id):
    """Genera número de asiento correlativo"""
    asientos_entidad = [a for a in st.session_state.asientos if a['entidad_id'] == entidad_id]
    return len(asientos_entidad) + 1

def calcular_iva(base, tipo_iva):
    """Calcula cuota de IVA"""
    return round(base * tipo_iva / 100, 2)

# =====================================================
# SIDEBAR - SELECCIÓN DE ENTIDAD
# =====================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/accounting.png", width=80)
    st.title("ContaFácil")
    st.caption("Contabilidad PGC Español")
    
    st.divider()
    
    st.subheader("🏢 Entidad Activa")
    
    entidad_seleccionada = st.selectbox(
        "Seleccionar:",
        st.session_state.entidades,
        format_func=lambda e: f"{e['razon_social'][:30]}..."
    )
    
    if entidad_seleccionada:
        tipo_badges = {
            'sociedad_limitada': '🏛️ S.L.',
            'sociedad_anonima': '🏛️ S.A.',
            'autonomo_directa': '👤 Autónomo',
            'autonomo_modulos': '👤 Módulos',
            'comunidad_propietarios': '🏘️ Comunidad',
        }
        
        st.info(f"""
        **NIF:** {entidad_seleccionada['nif']}  
        **Tipo:** {tipo_badges.get(entidad_seleccionada['tipo'], entidad_seleccionada['tipo'])}  
        **IVA:** {entidad_seleccionada['regimen_iva'].title()}
        """)
    
    st.divider()
    
    st.subheader("📅 Ejercicio")
    ejercicio = st.selectbox("Año:", [2026, 2025, 2024], index=0)
    
    st.divider()
    
    # Estadísticas rápidas
    asientos_entidad = [a for a in st.session_state.asientos 
                        if a['entidad_id'] == entidad_seleccionada['id']]
    
    st.metric("Asientos", len(asientos_entidad))

# =====================================================
# CONTENIDO PRINCIPAL
# =====================================================

st.title(f"📊 {entidad_seleccionada['razon_social']}")

# Pestañas principales
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📄 Subir Documentos",
    "📒 Libro Diario",
    "📊 Libro Mayor",
    "🧾 Modelos Fiscales",
    "💰 Cobros/Pagos",
    "⚙️ Configuración"
])

# =====================================================
# TAB 1: SUBIR DOCUMENTOS
# =====================================================

with tab1:
    st.header("📄 Contabilización Automática de Documentos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Subir documento")
        
        uploaded_file = st.file_uploader(
            "Arrastra o selecciona un PDF (factura, nómina, etc.)",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="El sistema extraerá los datos y propondrá el asiento contable"
        )
        
        if uploaded_file:
            st.success(f"✅ Archivo cargado: {uploaded_file.name}")
            
            # Simulación de OCR + IA (en producción usaríamos Claude API)
            st.info("🔄 Procesando documento con IA...")
            
            # Datos de ejemplo extraídos
            with st.expander("📋 Datos extraídos del documento", expanded=True):
                tipo_doc = st.selectbox(
                    "Tipo de documento detectado:",
                    ["Factura recibida", "Factura emitida", "Nómina", "Extracto bancario"]
                )
                
                if tipo_doc == "Factura recibida":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        proveedor = st.text_input("Proveedor:", "SUMINISTROS INDUSTRIALES SL")
                        nif_prov = st.text_input("NIF Proveedor:", "B98765432")
                        fecha_fra = st.date_input("Fecha factura:", date.today())
                    with col_b:
                        num_factura = st.text_input("Nº Factura:", "2024/1234")
                        base_imp = st.number_input("Base imponible:", value=1000.00, step=0.01)
                        tipo_iva = st.selectbox("Tipo IVA:", [21, 10, 4, 0])
                    
                    cuota_iva = calcular_iva(base_imp, tipo_iva)
                    total = base_imp + cuota_iva
                    
                    st.divider()
                    st.write(f"**Cuota IVA:** {cuota_iva:.2f} €")
                    st.write(f"**TOTAL FACTURA:** {total:.2f} €")
                    
                    # Propuesta de asiento
                    st.divider()
                    st.subheader("📝 Asiento propuesto")
                    
                    cuenta_gasto = st.selectbox(
                        "Cuenta de gasto:",
                        ['600 - Compras mercaderías', '621 - Arrendamientos', 
                         '622 - Reparaciones', '623 - Servicios profesionales',
                         '628 - Suministros', '629 - Otros servicios']
                    )
                    
                    # Mostrar asiento
                    df_asiento = pd.DataFrame([
                        {'Cuenta': cuenta_gasto.split(' - ')[0], 
                         'Descripción': cuenta_gasto.split(' - ')[1],
                         'Debe': f"{base_imp:.2f} €", 'Haber': ''},
                        {'Cuenta': '472', 
                         'Descripción': 'H.P. IVA soportado',
                         'Debe': f"{cuota_iva:.2f} €", 'Haber': ''},
                        {'Cuenta': '400', 
                         'Descripción': f'Proveedor: {proveedor}',
                         'Debe': '', 'Haber': f"{total:.2f} €"},
                    ])
                    
                    st.dataframe(df_asiento, use_container_width=True, hide_index=True)
                    
                    if st.button("✅ Contabilizar", type="primary"):
                        # Guardar asiento
                        nuevo_asiento = {
                            'id': len(st.session_state.asientos) + 1,
                            'entidad_id': entidad_seleccionada['id'],
                            'numero': generar_numero_asiento(entidad_seleccionada['id']),
                            'fecha': fecha_fra.isoformat(),
                            'concepto': f"Fra. {num_factura} - {proveedor}",
                            'apuntes': [
                                {'cuenta': cuenta_gasto.split(' - ')[0], 'debe': base_imp, 'haber': 0},
                                {'cuenta': '472', 'debe': cuota_iva, 'haber': 0},
                                {'cuenta': '400', 'debe': 0, 'haber': total},
                            ]
                        }
                        st.session_state.asientos.append(nuevo_asiento)
                        st.success(f"✅ Asiento nº {nuevo_asiento['numero']} contabilizado correctamente")
                        st.balloons()
                
                elif tipo_doc == "Factura emitida":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        cliente = st.text_input("Cliente:", "CLIENTE EJEMPLO SA")
                        nif_cli = st.text_input("NIF Cliente:", "A11111111")
                        fecha_fra = st.date_input("Fecha factura:", date.today())
                    with col_b:
                        num_factura = st.text_input("Nº Factura:", "2024/0001")
                        base_imp = st.number_input("Base imponible:", value=2500.00, step=0.01)
                        tipo_iva = st.selectbox("Tipo IVA:", [21, 10, 4, 0])
                    
                    cuota_iva = calcular_iva(base_imp, tipo_iva)
                    total = base_imp + cuota_iva
                    
                    st.divider()
                    st.subheader("📝 Asiento propuesto")
                    
                    df_asiento = pd.DataFrame([
                        {'Cuenta': '430', 
                         'Descripción': f'Cliente: {cliente}',
                         'Debe': f"{total:.2f} €", 'Haber': ''},
                        {'Cuenta': '700', 
                         'Descripción': 'Ventas de mercaderías',
                         'Debe': '', 'Haber': f"{base_imp:.2f} €"},
                        {'Cuenta': '477', 
                         'Descripción': 'H.P. IVA repercutido',
                         'Debe': '', 'Haber': f"{cuota_iva:.2f} €"},
                    ])
                    
                    st.dataframe(df_asiento, use_container_width=True, hide_index=True)
                    
                    if st.button("✅ Contabilizar", type="primary"):
                        nuevo_asiento = {
                            'id': len(st.session_state.asientos) + 1,
                            'entidad_id': entidad_seleccionada['id'],
                            'numero': generar_numero_asiento(entidad_seleccionada['id']),
                            'fecha': fecha_fra.isoformat(),
                            'concepto': f"Fra. emitida {num_factura} - {cliente}",
                            'apuntes': [
                                {'cuenta': '430', 'debe': total, 'haber': 0},
                                {'cuenta': '700', 'debe': 0, 'haber': base_imp},
                                {'cuenta': '477', 'debe': 0, 'haber': cuota_iva},
                            ]
                        }
                        st.session_state.asientos.append(nuevo_asiento)
                        st.success(f"✅ Asiento nº {nuevo_asiento['numero']} contabilizado correctamente")
    
    with col2:
        st.subheader("📌 Asientos rápidos")
        
        if entidad_seleccionada['tipo'] == 'comunidad_propietarios':
            st.write("**Comunidad de propietarios:**")
            if st.button("🏠 Emitir cuotas mensuales"):
                st.session_state.mostrar_cuotas = True
            if st.button("💡 Registrar factura suministro"):
                st.session_state.mostrar_suministro = True
            if st.button("👷 Registrar nómina empleado"):
                st.session_state.mostrar_nomina = True
        else:
            st.write("**Empresa/Autónomo:**")
            if st.button("🛒 Compra mercaderías"):
                pass
            if st.button("💰 Venta mercaderías"):
                pass
            if st.button("👷 Nóminas mes"):
                pass

# =====================================================
# TAB 2: LIBRO DIARIO
# =====================================================

with tab2:
    st.header("📒 Libro Diario")
    
    asientos_entidad = [a for a in st.session_state.asientos 
                        if a['entidad_id'] == entidad_seleccionada['id']]
    
    if not asientos_entidad:
        st.info("No hay asientos registrados. Sube un documento o crea un asiento manual.")
        
        if st.button("➕ Crear asiento manual"):
            st.session_state.crear_asiento_manual = True
    else:
        # Filtros
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            fecha_desde = st.date_input("Desde:", date(ejercicio, 1, 1))
        with col2:
            fecha_hasta = st.date_input("Hasta:", date(ejercicio, 12, 31))
        
        st.divider()
        
        # Mostrar asientos
        for asiento in sorted(asientos_entidad, key=lambda x: x['numero']):
            with st.expander(f"**Asiento {asiento['numero']}** | {asiento['fecha']} | {asiento['concepto']}", expanded=False):
                
                # Crear tabla de apuntes
                datos_apuntes = []
                total_debe = 0
                total_haber = 0
                
                plan = obtener_plan_cuentas(entidad_seleccionada['tipo'])
                
                for apunte in asiento['apuntes']:
                    cuenta_info = plan.get(apunte['cuenta'], {'descripcion': 'Cuenta no encontrada'})
                    datos_apuntes.append({
                        'Cuenta': apunte['cuenta'],
                        'Descripción': cuenta_info['descripcion'],
                        'Debe': f"{apunte['debe']:.2f}" if apunte['debe'] else '',
                        'Haber': f"{apunte['haber']:.2f}" if apunte['haber'] else '',
                    })
                    total_debe += apunte['debe']
                    total_haber += apunte['haber']
                
                df = pd.DataFrame(datos_apuntes)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                col_tot1, col_tot2 = st.columns(2)
                with col_tot1:
                    st.write(f"**Total Debe:** {total_debe:.2f} €")
                with col_tot2:
                    st.write(f"**Total Haber:** {total_haber:.2f} €")
                
                if abs(total_debe - total_haber) < 0.01:
                    st.success("✓ Asiento cuadrado")
                else:
                    st.error("✗ Asiento descuadrado")
        
        st.divider()
        
        # Totales del diario
        total_debe_diario = sum(
            sum(a['debe'] for a in asiento['apuntes']) 
            for asiento in asientos_entidad
        )
        total_haber_diario = sum(
            sum(a['haber'] for a in asiento['apuntes']) 
            for asiento in asientos_entidad
        )
        
        st.subheader("Totales del Diario")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Debe", f"{total_debe_diario:,.2f} €")
        with col2:
            st.metric("Total Haber", f"{total_haber_diario:,.2f} €")

# =====================================================
# TAB 3: LIBRO MAYOR
# =====================================================

with tab3:
    st.header("📊 Libro Mayor")
    
    plan = obtener_plan_cuentas(entidad_seleccionada['tipo'])
    asientos_entidad = [a for a in st.session_state.asientos 
                        if a['entidad_id'] == entidad_seleccionada['id']]
    
    if not asientos_entidad:
        st.info("No hay movimientos registrados.")
    else:
        # Agrupar por cuenta
        movimientos_por_cuenta = {}
        
        for asiento in asientos_entidad:
            for apunte in asiento['apuntes']:
                cuenta = apunte['cuenta']
                if cuenta not in movimientos_por_cuenta:
                    movimientos_por_cuenta[cuenta] = {
                        'movimientos': [],
                        'total_debe': 0,
                        'total_haber': 0
                    }
                
                movimientos_por_cuenta[cuenta]['movimientos'].append({
                    'fecha': asiento['fecha'],
                    'concepto': asiento['concepto'],
                    'debe': apunte['debe'],
                    'haber': apunte['haber']
                })
                movimientos_por_cuenta[cuenta]['total_debe'] += apunte['debe']
                movimientos_por_cuenta[cuenta]['total_haber'] += apunte['haber']
        
        # Selector de cuenta
        cuentas_con_movimientos = sorted(movimientos_por_cuenta.keys())
        
        cuenta_seleccionada = st.selectbox(
            "Seleccionar cuenta:",
            cuentas_con_movimientos,
            format_func=lambda c: f"{c} - {plan.get(c, {}).get('descripcion', 'Sin descripción')}"
        )
        
        if cuenta_seleccionada:
            datos = movimientos_por_cuenta[cuenta_seleccionada]
            
            st.subheader(f"Cuenta {cuenta_seleccionada} - {plan.get(cuenta_seleccionada, {}).get('descripcion', '')}")
            
            df_mayor = pd.DataFrame(datos['movimientos'])
            df_mayor['Debe'] = df_mayor['debe'].apply(lambda x: f"{x:.2f}" if x else '')
            df_mayor['Haber'] = df_mayor['haber'].apply(lambda x: f"{x:.2f}" if x else '')
            
            st.dataframe(
                df_mayor[['fecha', 'concepto', 'Debe', 'Haber']].rename(
                    columns={'fecha': 'Fecha', 'concepto': 'Concepto'}
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Saldo
            saldo = datos['total_debe'] - datos['total_haber']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Debe", f"{datos['total_debe']:,.2f} €")
            with col2:
                st.metric("Total Haber", f"{datos['total_haber']:,.2f} €")
            with col3:
                tipo_cuenta = plan.get(cuenta_seleccionada, {}).get('tipo', '')
                if tipo_cuenta in ['activo', 'gasto']:
                    saldo_texto = "Saldo Deudor" if saldo >= 0 else "Saldo Acreedor"
                else:
                    saldo_texto = "Saldo Acreedor" if saldo <= 0 else "Saldo Deudor"
                st.metric(saldo_texto, f"{abs(saldo):,.2f} €")

# =====================================================
# TAB 4: MODELOS FISCALES
# =====================================================

with tab4:
    st.header("🧾 Generación de Modelos Fiscales AEAT")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuración")
        
        periodo_tipo = st.radio("Periodicidad:", ["Trimestral", "Mensual", "Anual"])
        
        if periodo_tipo == "Trimestral":
            periodo = st.selectbox("Trimestre:", ["1T", "2T", "3T", "4T"])
        elif periodo_tipo == "Mensual":
            periodo = st.selectbox("Mes:", 
                [f"{i:02d}" for i in range(1, 13)],
                format_func=lambda m: ["Enero", "Febrero", "Marzo", "Abril", 
                    "Mayo", "Junio", "Julio", "Agosto", "Septiembre", 
                    "Octubre", "Noviembre", "Diciembre"][int(m)-1]
            )
        else:
            periodo = "0A"
        
        # Modelos disponibles según tipo entidad
        if entidad_seleccionada['tipo'] in ['sociedad_limitada', 'sociedad_anonima']:
            modelos_disp = {
                'Trimestral': ['303 - IVA', '111 - Retenciones IRPF', '115 - Ret. Alquileres'],
                'Anual': ['390 - Resumen IVA', '190 - Resumen Ret.', '200 - Impuesto Sociedades', '347 - Op. Terceros']
            }
        elif entidad_seleccionada['tipo'] in ['autonomo_directa', 'autonomo_modulos']:
            modelos_disp = {
                'Trimestral': ['303 - IVA', '130 - Pago frac. IRPF', '111 - Retenciones'],
                'Anual': ['390 - Resumen IVA', '100 - IRPF', '347 - Op. Terceros']
            }
        else:  # Comunidad
            modelos_disp = {
                'Trimestral': ['111 - Retenciones IRPF', '115 - Ret. Alquileres'],
                'Anual': ['190 - Resumen Ret.', '180 - Resumen Alq.', '184 - Atribución rentas', '347 - Op. Terceros']
            }
        
        modelo_lista = modelos_disp.get(periodo_tipo, modelos_disp.get('Trimestral', []))
        modelo_sel = st.selectbox("Modelo:", modelo_lista)
    
    with col2:
        st.subheader(f"Modelo {modelo_sel.split(' - ')[0]}")
        
        if '303' in modelo_sel:
            st.write("**IVA - Autoliquidación**")
            
            # Calcular desde asientos
            asientos_entidad = [a for a in st.session_state.asientos 
                                if a['entidad_id'] == entidad_seleccionada['id']]
            
            # IVA Repercutido (cuenta 477)
            iva_rep = sum(
                apunte['haber'] 
                for asiento in asientos_entidad 
                for apunte in asiento['apuntes'] 
                if apunte['cuenta'] == '477'
            )
            
            # IVA Soportado (cuenta 472)
            iva_sop = sum(
                apunte['debe'] 
                for asiento in asientos_entidad 
                for apunte in asiento['apuntes'] 
                if apunte['cuenta'] == '472'
            )
            
            # Base imponible (ventas 700)
            base_ventas = sum(
                apunte['haber'] 
                for asiento in asientos_entidad 
                for apunte in asiento['apuntes'] 
                if apunte['cuenta'] == '700'
            )
            
            # Base compras (600)
            base_compras = sum(
                apunte['debe'] 
                for asiento in asientos_entidad 
                for apunte in asiento['apuntes'] 
                if apunte['cuenta'] == '600'
            )
            
            st.write("**IVA DEVENGADO**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.text_input("[01] Base 21%:", value=f"{base_ventas:.2f}", disabled=True)
            with col_b:
                st.text_input("[02] Cuota 21%:", value=f"{iva_rep:.2f}", disabled=True)
            
            st.write("**IVA DEDUCIBLE**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.text_input("[28] Base op. interiores:", value=f"{base_compras:.2f}", disabled=True)
            with col_b:
                st.text_input("[29] Cuota soportada:", value=f"{iva_sop:.2f}", disabled=True)
            
            st.divider()
            
            total_devengado = iva_rep
            total_deducir = iva_sop
            diferencia = total_devengado - total_deducir
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("[27] Total cuota devengada", f"{total_devengado:.2f} €")
            with col_b:
                st.metric("[45] Total a deducir", f"{total_deducir:.2f} €")
            with col_c:
                color = "normal" if diferencia >= 0 else "inverse"
                st.metric("[71] Resultado", f"{diferencia:.2f} €", delta_color=color)
            
            st.divider()
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📥 Generar fichero AEAT", type="primary"):
                    # Generar fichero formato BOE
                    contenido_fichero = f"""<T3030{ejercicio}{periodo}{entidad_seleccionada['nif'].ljust(9)}{entidad_seleccionada['razon_social'][:40].ljust(40)}I {int(base_ventas*100):017d} {int(iva_rep*100):017d} {int(base_compras*100):017d} {int(iva_sop*100):017d} {int(diferencia*100):017d}</T303>"""
                    
                    st.download_button(
                        "📥 Descargar modelo303.txt",
                        contenido_fichero,
                        file_name=f"modelo303_{ejercicio}_{periodo}.txt",
                        mime="text/plain"
                    )
            
            with col_btn2:
                st.link_button("🌐 Ir a Sede AEAT", "https://sede.agenciatributaria.gob.es")
        
        elif '111' in modelo_sel:
            st.write("**Retenciones e ingresos a cuenta - Rendimientos del trabajo**")
            
            # Datos de ejemplo
            st.number_input("[01] Nº perceptores trabajo:", value=2, disabled=True)
            st.number_input("[02] Importe percepciones:", value=3500.00, disabled=True)
            st.number_input("[03] Importe retenciones:", value=525.00, disabled=True)
            
            st.metric("[30] Resultado a ingresar", "525.00 €")
        
        elif '347' in modelo_sel:
            st.write("**Declaración anual de operaciones con terceras personas**")
            st.info("Incluye operaciones > 3.005,06 € anuales con cada tercero")
            
            # Simular operaciones
            df_ops = pd.DataFrame([
                {'NIF': 'B98765432', 'Nombre': 'SUMINISTROS INDUSTRIALES SL', 'Importe': 15230.50, 'Clave': 'A'},
                {'NIF': 'A11111111', 'Nombre': 'CLIENTE EJEMPLO SA', 'Importe': 8500.00, 'Clave': 'B'},
            ])
            
            st.dataframe(df_ops, use_container_width=True, hide_index=True)
            
            if st.button("📥 Generar fichero 347"):
                st.success("Fichero generado correctamente")

# =====================================================
# TAB 5: COBROS Y PAGOS
# =====================================================

with tab5:
    st.header("💰 Gestión de Cobros y Pagos")
    
    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "📋 Recibos Pendientes",
        "📦 Generar Remesa SEPA",
        "💳 Enlace Pago Tarjeta",
        "💸 Pagos a Proveedores"
    ])
    
    with subtab1:
        st.subheader("Recibos pendientes de cobro")
        
        if entidad_seleccionada['tipo'] == 'comunidad_propietarios':
            # Generar recibos de cuotas
            if st.button("➕ Generar cuotas del mes"):
                mes_actual = date.today().replace(day=1)
                propietarios = [t for t in st.session_state.terceros if t['tipo'] == 'propietario']
                
                for prop in propietarios:
                    nuevo_recibo = {
                        'id': len(st.session_state.recibos) + 1,
                        'entidad_id': entidad_seleccionada['id'],
                        'numero': f"R-{mes_actual.strftime('%Y%m')}-{prop['id']:03d}",
                        'tercero': prop,
                        'importe': 125.50,
                        'concepto': f"Cuota ordinaria {mes_actual.strftime('%B %Y')}",
                        'fecha_emision': date.today().isoformat(),
                        'fecha_vencimiento': (mes_actual + timedelta(days=10)).isoformat(),
                        'estado': 'pendiente',
                        'metodo': 'domiciliacion'
                    }
                    st.session_state.recibos.append(nuevo_recibo)
                
                st.success(f"✅ Generados {len(propietarios)} recibos de cuotas")
        
        # Mostrar recibos pendientes
        recibos_entidad = [r for r in st.session_state.recibos 
                          if r['entidad_id'] == entidad_seleccionada['id'] 
                          and r['estado'] == 'pendiente']
        
        if recibos_entidad:
            df_recibos = pd.DataFrame([{
                'Número': r['numero'],
                'Deudor': r['tercero']['nombre'][:30],
                'Concepto': r['concepto'][:30],
                'Importe': f"{r['importe']:.2f} €",
                'Vencimiento': r['fecha_vencimiento'],
                'Estado': r['estado'].title()
            } for r in recibos_entidad])
            
            st.dataframe(df_recibos, use_container_width=True, hide_index=True)
            
            total_pendiente = sum(r['importe'] for r in recibos_entidad)
            st.metric("Total pendiente", f"{total_pendiente:,.2f} €")
        else:
            st.info("No hay recibos pendientes")
    
    with subtab2:
        st.subheader("📦 Generar Remesa SEPA (Domiciliaciones)")
        
        recibos_domiciliables = [r for r in st.session_state.recibos 
                                  if r['entidad_id'] == entidad_seleccionada['id'] 
                                  and r['estado'] == 'pendiente'
                                  and r['metodo'] == 'domiciliacion']
        
        if not recibos_domiciliables:
            st.info("No hay recibos pendientes con domiciliación")
        else:
            st.write(f"**{len(recibos_domiciliables)} recibos** disponibles para domiciliar")
            
            fecha_cobro = st.date_input(
                "Fecha de cobro solicitada:",
                value=date.today() + timedelta(days=5),
                min_value=date.today() + timedelta(days=2)
            )
            
            if st.button("🏦 Generar fichero SEPA XML", type="primary"):
                # Generar XML SEPA
                from datetime import datetime
                import uuid
                
                msg_id = f"SEPA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
                
                total = sum(r['importe'] for r in recibos_domiciliables)
                
                xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{datetime.now().isoformat()}</CreDtTm>
      <NbOfTxs>{len(recibos_domiciliables)}</NbOfTxs>
      <CtrlSum>{total:.2f}</CtrlSum>
      <InitgPty>
        <Nm>{entidad_seleccionada['razon_social'][:70]}</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>{msg_id}-001</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <NbOfTxs>{len(recibos_domiciliables)}</NbOfTxs>
      <CtrlSum>{total:.2f}</CtrlSum>
      <PmtTpInf>
        <SvcLvl><Cd>SEPA</Cd></SvcLvl>
        <LclInstrm><Cd>CORE</Cd></LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>{fecha_cobro.isoformat()}</ReqdColltnDt>
      <Cdtr>
        <Nm>{entidad_seleccionada['razon_social'][:70]}</Nm>
      </Cdtr>
      <CdtrAcct>
        <Id><IBAN>ES9121000418450200051332</IBAN></Id>
      </CdtrAcct>
      <CdtrAgt>
        <FinInstnId><BIC>CAIXESBBXXX</BIC></FinInstnId>
      </CdtrAgt>'''
                
                for recibo in recibos_domiciliables:
                    xml_content += f'''
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>E2E-{recibo['numero']}</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">{recibo['importe']:.2f}</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>MAND-{recibo['tercero']['id']:03d}</MndtId>
            <DtOfSgntr>2024-01-01</DtOfSgntr>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId><Othr><Id>NOTPROVIDED</Id></Othr></FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>{recibo['tercero']['nombre'][:70]}</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id><IBAN>{recibo['tercero']['iban']}</IBAN></Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>{recibo['concepto'][:140]}</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>'''
                
                xml_content += '''
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>'''
                
                st.success(f"""
                ✅ Remesa generada correctamente
                
                - **ID Mensaje:** {msg_id}
                - **Recibos:** {len(recibos_domiciliables)}
                - **Importe total:** {total:,.2f} €
                - **Fecha cobro:** {fecha_cobro.strftime('%d/%m/%Y')}
                """)
                
                st.download_button(
                    "📥 Descargar fichero SEPA (XML)",
                    xml_content,
                    file_name=f"remesa_{msg_id}.xml",
                    mime="application/xml"
                )
    
    with subtab3:
        st.subheader("💳 Generar enlace de pago con tarjeta")
        
        st.info("""
        **Integración con pasarelas de pago:**
        - Stripe (recomendado para empezar)
        - Redsys (TPV bancario español)
        
        Configura las claves API en el archivo de configuración.
        """)
        
        recibo_pago = st.selectbox(
            "Seleccionar recibo:",
            [r for r in st.session_state.recibos 
             if r['entidad_id'] == entidad_seleccionada['id'] 
             and r['estado'] == 'pendiente'],
            format_func=lambda r: f"{r['numero']} - {r['tercero']['nombre'][:20]} - {r['importe']:.2f}€"
        )
        
        if recibo_pago:
            if st.button("🔗 Generar enlace de pago"):
                # En producción, esto llamaría a la API de Stripe
                enlace_ficticio = f"https://checkout.stripe.com/pay/cs_test_{uuid.uuid4().hex[:24]}"
                
                st.success("✅ Enlace generado")
                st.code(enlace_ficticio)
                
                st.info("Puedes enviar este enlace al cliente por email o WhatsApp")
    
    with subtab4:
        st.subheader("💸 Remesa de pagos a proveedores (SEPA Transfer)")
        
        st.write("Programa transferencias a tus proveedores")
        
        # Simulación de facturas pendientes de pago
        facturas_pagar = [
            {'id': 1, 'proveedor': 'SUMINISTROS INDUSTRIALES SL', 'nif': 'B98765432', 
             'iban': 'ES7620770024003102575766', 'importe': 1210.00, 'concepto': 'Fra. 2024/123'},
            {'id': 2, 'proveedor': 'SEGUROS MAPFRE', 'nif': 'A28141935', 
             'iban': 'ES8901280001000123456789', 'importe': 850.00, 'concepto': 'Póliza anual'},
        ]
        
        df_pagos = pd.DataFrame(facturas_pagar)
        st.dataframe(df_pagos[['proveedor', 'importe', 'concepto']], use_container_width=True, hide_index=True)
        
        if st.button("🏦 Generar remesa de pagos SEPA"):
            st.success("✅ Fichero SEPA Credit Transfer generado")
            st.download_button(
                "📥 Descargar XML",
                "<xml>Contenido SEPA CT</xml>",
                file_name="remesa_pagos_sepa.xml",
                mime="application/xml"
            )

# =====================================================
# TAB 6: CONFIGURACIÓN
# =====================================================

with tab6:
    st.header("⚙️ Configuración")
    
    subtab_config1, subtab_config2, subtab_config3 = st.tabs([
        "🏢 Entidades",
        "👥 Terceros",
        "🏦 Cuentas Bancarias"
    ])
    
    with subtab_config1:
        st.subheader("Gestión de Entidades")
        
        if st.button("➕ Nueva Entidad"):
            st.session_state.nueva_entidad = True
        
        for entidad in st.session_state.entidades:
            with st.expander(f"{entidad['razon_social']} ({entidad['nif']})"):
                st.write(f"**Tipo:** {entidad['tipo']}")
                st.write(f"**Régimen IVA:** {entidad['regimen_iva']}")
                st.write(f"**Plan contable:** {entidad['plan_contable']}")
    
    with subtab_config2:
        st.subheader("Gestión de Terceros (Clientes/Proveedores/Propietarios)")
        
        if st.button("➕ Nuevo Tercero"):
            st.session_state.nuevo_tercero = True
        
        df_terceros = pd.DataFrame(st.session_state.terceros)
        st.dataframe(df_terceros, use_container_width=True, hide_index=True)
    
    with subtab_config3:
        st.subheader("Cuentas Bancarias")
        
        st.info("""
        **Para domiciliaciones SEPA necesitas:**
        - IBAN de la cuenta
        - BIC/SWIFT del banco
        - Identificador de acreedor SEPA (solicitar al banco)
        """)
        
        cuenta_ejemplo = {
            'nombre': 'Cuenta Principal',
            'iban': 'ES91 2100 0418 4502 0005 1332',
            'bic': 'CAIXESBBXXX',
            'banco': 'CaixaBank',
            'creditor_id': 'ES12000B12345678'
        }
        
        st.json(cuenta_ejemplo)

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("""
**ContaFácil v0.1** - Prototipo MVP  
Desarrollado para POINT · Contabilidad PGC Español  
⚠️ Este es un prototipo de demostración. Los datos no se guardan de forma persistente.
""")
