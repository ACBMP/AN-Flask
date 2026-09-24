# Información sobre el servidor privado

### Preguntas frecuentes

#### ¿Cómo funciona el sistema de servidor privado?

Existe un único software de servidor privado que se ejecuta en un ordenador, ya sea un servidor o el PC de alguien. Los usuarios solo tienen que redirigir la página `onlineconfigservice.ubi.com` a la dirección IP del servidor y listo. Esto se hace desde el lanzador.

#### ¿A qué servidor me conecto?

Si vas a jugar con otras personas, se recomienda que alguien que esté jugando [hospede el servidor](/patch/server#server-hosting).
Para hacer pruebas puedes usar el servidor público de Vinny: `10.8.0.21`.

#### ¿De dónde puedo descargar el software del servidor privado?

Puedes descargarlo desde [el repositorio del servidor](https://github.com/michal-kapala/acb-rdv/releases).

#### Tengo una cuenta en AN, pero no en mi servidor. ¿Cómo lo soluciono?

Puedes añadir una cuenta nueva desde la interfaz del servidor o [descargar la base de datos más reciente desde aquí](/static/database.sqlite) y colocarla en la carpeta del servidor.

#### ¿Dónde informo de problemas con el servidor?

[En este servidor de Discord](https://discord.gg/Fxyrt55h).

### Hospedar el servidor {: #server-hosting }

Hospedar el servidor en un PC doméstico es bastante complicado. La forma segura más sencilla de hospedarlo para jugar con otras personas requiere estos pasos:

1. Abre [WireGuard](/patch/wireguard) y activa la conexión.
2. Busca tu IP de WireGuard mirando el número que aparece bajo `Addresses` en la primera interfaz. El formato es `10.8.0.X`. Por ejemplo, la dirección de Dell es `10.8.0.2`.
3. Edita `ACBRDV.exe.config` y cambia el valor que sigue a `key="SecureServerAddress"` por tu IP de WireGuard del paso anterior. Por ejemplo: `<add key="SecureServerAddress" value="10.8.0.2"/>`.
4. [Desactiva el cortafuegos](https://www.guidingtech.com/how-to-disable-firewall-on-windows/).
5. Inicia el servidor. Puede que tengas que pulsar el botón «Start» de la parte superior.
