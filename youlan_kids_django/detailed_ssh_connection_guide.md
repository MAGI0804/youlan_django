# SSH 连接详细指南

本指南将详细解释如何获取服务器信息并在Windows系统上建立SSH连接。

## 一、获取服务器连接信息

要连接到远程服务器，您需要以下基本信息：

### 1. 服务器 IP 地址和主机名

在您的项目中，服务器信息已在 `remote_connection_guide.md` 文件中提供：

- **服务器名称**：iZuf635nesowrxp7kll8pgZ

这个服务器名称 `iZuf635nesowrxp7kll8pgZ` 实际上就是一个域名，可以直接用于SSH连接，不需要额外的IP地址。

### 2. 用户名

项目文档中已提供用户名：
- **用户名**：ecs-assist-user

### 3. 密码或密钥

通常，服务器管理员会为您提供访问密码或SSH密钥文件。如果您没有收到密码，请联系服务器管理员获取。

## 二、Windows系统SSH连接方法

### 方法一：使用项目提供的快速连接脚本

项目根目录下提供了 `connect_server.bat` 批处理脚本，您可以直接双击运行该脚本快速连接到服务器：

1. 打开文件资源管理器，导航到 `d:\youlan_kids_customization\youlan_kids_django` 目录
2. 找到 `connect_server.bat` 文件
3. 双击该文件运行
4. 在弹出的命令行窗口中，输入您的服务器密码（输入时密码不会显示在屏幕上）
5. 按 Enter 键完成连接

### 方法二：使用 Windows 终端或 PowerShell

Windows 10 及以上版本已内置 OpenSSH 客户端，您可以直接使用 Windows 终端或 PowerShell 进行连接：

1. 按下 `Win + X` 键，选择 "Windows 终端" 或 "Windows PowerShell"

2. 在打开的终端中，输入以下命令：
   ```powershell
   ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

3. 首次连接时，系统会提示确认服务器指纹，输入 `yes` 并按回车

4. 输入您的服务器密码，完成连接

### 方法三：使用 PuTTY 工具

如果您更喜欢使用图形界面工具，可以下载并使用 PuTTY：

1. 下载并安装 [PuTTY](https://www.putty.org/)

2. 打开 PuTTY 应用程序

3. 在 "Host Name (or IP address)" 字段中输入 `iZuf635nesowrxp7kll8pgZ`

4. 确保端口设置为 22（SSH 默认端口）

5. 点击 "Open" 按钮

6. 首次连接时，会弹出安全警告，点击 "Yes" 确认

7. 在弹出的终端窗口中，输入用户名 `ecs-assist-user` 和密码完成连接

## 三、验证连接是否成功

连接成功后，您将看到类似以下的命令提示符：
```
ecs-assist-user@iZuf635nesowrxp7kll8pgZ:~\$ 
```

现在您可以在命令行中执行各种 Linux 命令，例如：
```bash
# 查看当前目录
ls

# 查看磁盘空间
df -h

# 查看内存使用情况
free -h

# 查看系统信息
uname -a
cat /etc/os-release
```

## 四、常见问题解决

### 1. 连接超时

- 检查您的网络连接是否正常
- 确认服务器名称 `iZuf635nesowrxp7kll8pgZ` 拼写正确
- 可能是防火墙限制，联系服务器管理员确认端口 22 是否开放

### 2. 权限被拒绝错误

- 确认用户名 `ecs-assist-user` 拼写正确
- 确认密码输入正确（密码不会显示在屏幕上）
- 联系服务器管理员确认您的账户是否有访问权限

### 3. Windows 10 以下版本没有内置 SSH 客户端

对于 Windows 10 以下版本，您需要安装 OpenSSH 客户端或使用 PuTTY 工具。

## 五、SSH 密钥认证设置（推荐）

为了更安全、便捷地连接服务器，建议设置 SSH 密钥认证，这样就不需要每次连接都输入密码。

### 步骤 1：在本地生成 SSH 密钥对

1. 打开 Windows 终端或 PowerShell

2. 执行以下命令生成密钥对：
   ```powershell
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```
   （将 `your_email@example.com` 替换为您的邮箱）

3. 按 Enter 接受默认保存位置（通常是 `C:\Users\您的用户名\.ssh\id_rsa`）

4. 可以设置密码保护密钥（可选，建议设置）

### 步骤 2：将公钥上传到服务器

1. 使用密码登录到服务器：
   ```powershell
   ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

2. 在服务器上创建 .ssh 目录（如果不存在）：
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   ```

3. 在本地打开一个新的终端，查看并复制公钥内容：
   ```powershell
   cat ~/.ssh/id_rsa.pub
   ```

4. 返回服务器终端，将公钥添加到 authorized_keys 文件：
   ```bash
   nano ~/.ssh/authorized_keys
   ```
   （将复制的公钥粘贴到文件中，保存并退出）

5. 设置正确的权限：
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   ```

6. 退出服务器连接：
   ```bash
   exit
   ```

### 步骤 3：测试密钥认证

现在尝试重新连接服务器，系统应该不会再要求您输入密码：
```powershell
ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ
```

## 六、联系支持

如果您在连接过程中遇到任何问题，请联系服务器管理员或项目负责人获取帮助。