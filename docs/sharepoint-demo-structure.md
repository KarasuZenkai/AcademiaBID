# Estructura demo de SharePoint

Esta es la topología ficticia que reproduce el seed local. No crea ni modifica
carpetas en el sitio corporativo y sus identificadores `demo-*` nunca deben
usarse al activar Microsoft Graph.

```text
Centrodeaprendizaje / Biblioteca Academia BID /
├── Energy / Videos / Bienvenida.mp4
├── Deportes / Videos / Bienvenida.mp4
├── Tecnologia / Videos / Bienvenida.mp4
├── Agua / Videos / Bienvenida.mp4
├── Juridico / Videos / Bienvenida.mp4
├── Contabilidad / Videos / Bienvenida.mp4
├── Finanzas / Videos / Bienvenida.mp4
├── Construccion / Videos / Bienvenida.mp4
├── Talento-Humano / Videos / Bienvenida.mp4
├── TI / Videos / Bienvenida.mp4
└── Prosper / Videos / Bienvenida.mp4
```

Cada unidad tiene un grupo demo `ACADEMIA-<UNIDAD>`. La asignación local sirve
para validar la segmentación:

| Usuario local | Unidades visibles |
| --- | --- |
| Usuario General | Deportes, Agua, Talento Humano |
| Usuario Tecnología | Tecnología, TI |
| Usuario Comercial | Energy, Finanzas, Prosper |
| Usuario Gerentes | Jurídico, Contabilidad, Construcción |
| Administrador | Todas |

Al integrar SharePoint real, estos grupos y los IDs `demo-*` se reemplazan por
los grupos y permisos existentes en las carpetas reales. La autorización será
evaluada por SharePoint mediante Microsoft Graph en nombre del usuario.
