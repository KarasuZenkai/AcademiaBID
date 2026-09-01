# Entrega segura de configuración a infraestructura

Este documento se puede subir a GitHub porque **no contiene valores reales**. Define qué información se entrega fuera del repositorio cuando infraestructura solicite el canal seguro.

## Regla principal

Ningún secreto se guarda en GitHub, GitLab, imágenes Docker, archivos adjuntos abiertos ni conversaciones generales. Infraestructura debe proporcionar un canal seguro y registrar los valores como variables protegidas/enmascaradas.

## Secretos que se entregan por canal seguro

| Variable | Propósito | Responsable de cargarla |
|---|---|---|
| `AZURE_BACKEND_CLIENT_SECRET` | Permite al backend usar Microsoft Graph en nombre del usuario autenticado. | Infraestructura |
| `DATABASE_URL` | Cadena privada de conexión a PostgreSQL productivo. | Infraestructura |

`DATABASE_URL` debe construirse con las credenciales de la base productiva; no se reutilizan credenciales locales.

## Configuración que se comunica a infraestructura

Estos valores no son contraseñas, pero se proporcionan junto con la entrega técnica para evitar errores de configuración:

```text
AUTH_PROVIDER=entra
AZURE_TENANT_ID
AZURE_BACKEND_CLIENT_ID
AZURE_BACKEND_SCOPE
AZURE_FRONTEND_CLIENT_ID
SHAREPOINT_SITE_HOST
SHAREPOINT_SITE_PATH
```

## Configuración pública de frontend

Estos valores se integran al build del frontend. No son secretos, pero deben corresponder al ambiente de producción:

```text
NEXT_PUBLIC_AUTH_PROVIDER=entra
NEXT_PUBLIC_AZURE_TENANT_ID
NEXT_PUBLIC_AZURE_FRONTEND_CLIENT_ID
NEXT_PUBLIC_AZURE_BACKEND_SCOPE
NEXT_PUBLIC_API_URL
```

## Valores que infraestructura debe definir

```text
DATABASE_URL
CORS_ORIGINS
NEXT_PUBLIC_API_URL
DOMINIO_PRODUCTIVO
```

El dominio final se debe registrar como Redirect URI de la aplicación frontend en Microsoft Entra antes de liberar producción.

## Archivo local confidencial

El archivo `docs/ENTREGA_SEGURA_INFRAESTRUCTURA.txt` contiene los valores locales de configuración. Está ignorado por Git y **no se sube**. Sólo se comparte cuando infraestructura indique un canal seguro.

## Rotación obligatoria

Antes de producción se debe crear un secreto nuevo de Microsoft Entra. El secreto usado en desarrollo local no se reutiliza en producción. Tras confirmar que la nueva configuración funciona, el secreto anterior debe revocarse.

## Confirmación que se debe pedir a infraestructura

Antes de entregar valores reales, solicitar por escrito:

1. El canal seguro autorizado para secretos.
2. El responsable que cargará las variables.
3. El ambiente al que se aplicarán: pruebas o producción.
4. El dominio final de la aplicación.
5. La confirmación de que las variables quedarán protegidas y enmascaradas.
