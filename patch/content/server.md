# Private Server Information

### FAQ

#### How does the private server system work?

There's one private server software that runs on one computer, either on a server or someone's PC. Users only need to redirect the `onlineconfigservice.ubi.com` page to the server's IP address and they're good to go. This is done via the launcher.

#### Which server do I connect to?

If you're playing with other people, it's recommended someone playing [hosts the server themselves](/patch/server#server-hosting).
For testing, you can use Vinny's public server: `10.8.0.21`.

#### Where can I download the private server software from?

You can donwload it from [the server repository](https://github.com/michal-kapala/acb-rdv/releases).

#### I have an account on AN, but not on my server. How do I fix this?

You can add a new account via the server GUI or [download the latest database from here](/static/database.sqlite) and place it in the server folder.

#### Where do I report server issues?

[This Discord server](https://discord.gg/Fxyrt55h).

### Server Hosting

Server hosting on a home PC is a fairly complicated ordeal. The easiest safe way to host the server to play with others requires the following steps:

1. Open [WireGuard](/patch/wireguard) and activate the connection.
2. Find your WireGuard IP by looking for the number under `Addresses` in the first interface. The format is `10.8.0.X`. For example, Dell's address is `10.8.0.2`.
3. Edit `ACBRDV.exe.config` and change the value after `key="SecureServerAddress"` to your WireGuard IP from the previous step. For example: `<add key="SecureServerAddress" value="10.8.0.2"/>`.
4. [Disable your firewall](https://www.guidingtech.com/how-to-disable-firewall-on-windows/).
5. Launch the server. You may have to click the "Start" button at the top.
