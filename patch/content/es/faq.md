# Preguntas frecuentes del parche de ACB

### ¿Qué hace «Attach to Game»?

Permite que el lanzador aplique modificaciones al juego, como una velocidad de cámara superior a 10.

### ¿Qué hace el botón «Remove Music»?

Desactiva la música del juego que no sean los susurros, de modo que la música pasa a controlar únicamente los susurros.

### ¿Por qué es tan grande el parche?

El parche simplemente descarga todos los archivos del multijugador. Eso nos facilita el mantenimiento, pero hace que la descarga tarde más.

### ¿La versión parcheada es compatible con la original?

Sí, pero nadie debería estar jugando a la versión original.

### ¿Dónde están los mapas de los DLC?

Los mapas malos no se incluyen en el parche por defecto. Puedes abrir el parcheador y descargarlos desde ahí.

### No tengo un PC gaming, ¿puedo usar GeForce NOW u otro servicio de streaming de juegos?

Prueba primero con tu ordenador antes de descartarlo. El juego tiene ya más de una década, así que la mayoría de los portátiles básicos lo mueven sin problema. Tu móvil probablemente podría ejecutarlo si tuviera Windows. Lo que no puedes hacer es jugar por streaming, no.

### ¿Qué mandos se recomiendan para que resulte más cómodo?

Los mandos de PS5 y de Xbox 360 (NO los de Xbox One ni similares) funcionan al conectarlos en Windows, sin más. Los mandos de PS5 permiten reasignar botones manualmente dentro del juego.

# Resolución de problemas

### Aparece un error que se queja de que falta «msvcr120.dll».

Descarga e instala la versión de 32 bits (x86) de [Microsoft Visual C++ 2013](https://www.microsoft.com/en-us/download/details.aspx?id=40784).

### Windows Defender dice que el lanzador es un virus o un troyano.

Es una falsa alarma. Si te interesa, [aquí tienes una explicación de por qué ocurre](https://www.reddit.com/r/learnpython/comments/e99bhe/why_does_pyinstaller_trigger_windows_defender/).

Windows intentará bloquear el programa con todas sus fuerzas. Para decirle a Windows que todo está bien, haz lo siguiente:

1. Ve a configuración, busca «Seguridad de Windows», luego «Configuración de protección antivirus y contra amenazas» y pulsa en «Administrar la configuración».
    ![Administrar la configuración](/static/manage_settings.png "Administrar la configuración")

2. Desactiva la «protección en tiempo real» y vuelve a intentar la descarga; debería funcionar. **NO vuelvas a activar todavía la protección en tiempo real, o borrará el lanzador.**
    ![Protección en tiempo real](/static/real_time.png "Protección en tiempo real")

3. Ejecuta el lanzador para asegurarte de que funciona.
4. Cierra el lanzador y vuelve a la página de protección antivirus, baja hasta el final y pulsa en «Agregar o quitar exclusiones»
    ![Agregar o quitar exclusiones](/static/exclusions.png "Agregar o quitar exclusiones")

5. Después pulsa «Agregar una exclusión», busca el lanzador en tu ordenador y selecciónalo.
    ![Agregar una exclusión](/static/add_exclusion.png "Agregar una exclusión")
6. Ahora que el lanzador está añadido como exclusión, vuelve a la página de protección antivirus y activa de nuevo la protección en tiempo real.
7. Ejecuta el lanzador para comprobar que todo sigue funcionando.

### El juego arranca pero dice que el servidor no está disponible.

Si estás en Rusia o en otro país con un cortafuegos que bloquea las VPN, escribe directamente a un administrador por Discord (o por correo electrónico) y veremos qué podemos hacer. Si no es el caso:

Esto significa que se da una de estas situaciones:

1. El servidor de juego al que intentas conectarte está funcionando en una IP equivocada.
2. Intentas conectarte a un servidor de juego a través de [WireGuard](/patch/quick-start#wireguard), pero no estás conectado.
3. La máquina del servidor de juego está bloqueando las conexiones con un cortafuegos.
4. El servidor de juego no está en marcha.
5. Tu conexión a internet está caída.
6. La IP de tu servidor está mal configurada.

Lo primero que debes hacer es ejecutar `ping onlineconfigservice.ubi.com` en un símbolo del sistema.

Si hace ping correctamente a la dirección IP que has introducido y NO a `216.98.50.240`, puedes descartar los casos 2, 4, 5 y 6.

Si hace ping a `216.98.50.240`, tienes que [configurar la dirección IP en el lanzador](/patch/quick-start#enter-the-server-ip).

Si hace ping a una dirección con el formato `10.8.0.X` pero los pings fallan, o tú o el servidor de juego no está conectado a la VPN de WireGuard.

En cualquier otro caso, quéjate a quien hospeda el servidor.

### Mi mando de PS3 no funciona.

Sigue [este tutorial](https://www.youtube.com/watch?v=9kmmKjLxpXk&pp=ygUfcHMzIGNvbnRyb2xsZXIgdHJpZ2dlciBzd2FwIHNjcA%3D%3D). Elige la opción de mando de Xbox en ACB.

### Mi mando de PS4/5 no funciona.

Prueba a seguir [esta guía](https://ds4-windows.com/get-started/#installation-setup). Elige la opción de mando de Xbox en ACB.

### Mi mando que no es de PS3/4/5 no funciona bien (por ejemplo, los gatillos no responden).

Descarga [el hack xinput.asi](https://assassins.network/static/xinput.asi) y colócalo en la carpeta del juego ACB. Es la carpeta que aparece en el lanzador y debería contener un archivo llamado `dinput8`. Elige `Xinput Controller 1` como mando en ACB.

### Los gatillos de mi mando no funcionan en Linux.

1. Consigue [SDL2 Gamepad Mapper](https://github.com/Ryochan7/sdl2-gamepad-mapper)
2. Asigna L2 como L3 y R2 como R3, y omite la cruceta abajo, L2 y R2.
3. Copia la cadena de asignación y ponla como asignación de mando SDL2 en Lutris o como variable `SDL_GAMECONTROLLERCONFIG` en [Steam](https://help.steampowered.com/en/faqs/view/7D01-D2DD-D75E-2955).
4. Inicia ACB y asigna todos los botones manualmente.

## Problemas de conectividad

(Esto es irrelevante mientras usemos WireGuard/Tailscale.)

ACB necesita que el puerto UDP `7917` esté abierto. Si un solo usuario de la sala no es accesible en ese puerto, cualquier otro jugador con el puerto cerrado no podrá entrar.

Para abrir el puerto, busca «port forward» junto con la marca y el modelo de tu router. Cuando te pregunte qué puerto abrir, basta con redirigir el puerto UDP 7917 al PC donde tengas ACB.

El lanzador muestra el estado de la conectividad en la parte inferior. Para comprobar si has abierto el puerto correctamente, tendrás que reiniciar el lanzador.
