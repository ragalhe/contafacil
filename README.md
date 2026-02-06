# 📊 ContaFácil - Sistema de Contabilidad PGC Español

Sistema de contabilidad automatizada con OCR e IA para empresas, autónomos y comunidades de propietarios en España.

## 🚀 Características

- ✅ **Contabilización automática** de documentos (facturas, nóminas) con OCR + IA
- ✅ **Plan General Contable** español (PGC Pymes y Comunidades)
- ✅ **Generación de modelos fiscales AEAT** (303, 111, 115, 347, etc.)
- ✅ **Ficheros SEPA** para domiciliaciones (ex-N19) y transferencias (ex-N34)
- ✅ **Pasarela de pago** con tarjeta (Stripe/Redsys)
- ✅ **Multi-entidad**: empresas, autónomos y comunidades de propietarios

## 📦 Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/contafacil.git
cd contafacil

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app_main.py
```

## ☁️ Despliegue en Streamlit Cloud (GRATIS)

### Paso 1: Subir a GitHub

1. Crea una cuenta en [GitHub](https://github.com) si no tienes
2. Crea un nuevo repositorio llamado `contafacil`
3. Sube todos los archivos del proyecto

### Paso 2: Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona tu repositorio `contafacil`
5. Archivo principal: `app_main.py`
6. Click en "Deploy"

¡Listo! Tu aplicación estará disponible en `https://tu-usuario-contafacil.streamlit.app`

## 🔧 Configuración de Secretos (para producción)

En Streamlit Cloud, ve a Settings > Secrets y añade:

```toml
# API Keys
ANTHROPIC_API_KEY = "sk-ant-xxxxx"
STRIPE_API_KEY = "sk_live_xxxxx"
STRIPE_WEBHOOK_SECRET = "whsec_xxxxx"

# Base de datos (opcional, para persistencia)
DATABASE_URL = "postgresql://user:pass@host:5432/contafacil"

# Email
SENDGRID_API_KEY = "SG.xxxxx"

# URL base de la aplicación
BASE_URL = "https://tu-app.streamlit.app"
```

## 🏗️ Estructura del Proyecto

```
contafacil/
├── app_main.py              # Aplicación principal Streamlit
├── requirements.txt         # Dependencias Python
├── .streamlit/
│   └── config.toml         # Configuración Streamlit
├── core/
│   ├── contabilizador.py   # Motor de contabilización
│   └── ocr/
│       └── extractor.py    # Extracción OCR + IA
├── modelos_aeat/
│   ├── base.py             # Clase base modelos fiscales
│   ├── modelo_303.py       # IVA
│   ├── modelo_111.py       # Retenciones IRPF
│   └── modelo_347.py       # Operaciones terceros
├── pagos/
│   ├── sepa_direct_debit.py    # Domiciliaciones
│   ├── sepa_credit_transfer.py # Transferencias
│   └── pasarelas/
│       ├── stripe_integration.py
│       └── redsys_integration.py
└── database/
    └── models.py           # Modelos SQLAlchemy
```

## 📋 Roadmap

### Fase 1 - MVP ✅
- [x] Interfaz básica Streamlit
- [x] Plan de cuentas PGC
- [x] Libro diario y mayor
- [x] Generación modelo 303

### Fase 2 - En desarrollo
- [ ] OCR con Claude Vision
- [ ] Base de datos PostgreSQL
- [ ] Todos los modelos AEAT
- [ ] Ficheros SEPA completos

### Fase 3 - Futuro
- [ ] API REST
- [ ] App móvil
- [ ] Integración banca online
- [ ] Facturación electrónica (Verifactu)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios.

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 📞 Soporte

Para dudas o soporte, contacta con: [tu-email@ejemplo.com]

---

Desarrollado con ❤️ para POINT Trading
