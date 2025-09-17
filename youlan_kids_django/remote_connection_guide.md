# 远程服务器连接指南

本指南将详细介绍如何连接到远程CentOS服务器（iZuf635nesowrxp7kll8pgZ），进行项目开发、部署和维护工作。

### 服务器基本信息
- **操作系统**：CentOS Linux 8
- **用户名**：ecs-assist-user
- **服务器名称**：iZuf635nesowrxp7kll8pgZ
- **Docker状态**：未安装（需要先安装Docker）
- **磁盘空间**：系统盘40G（已用7.1G，可用33G），数据盘49G（已用4.3G，可用43G）
- **内存**：约3.7G

### 快速连接方式
项目根目录下提供了`connect_server.bat`批处理脚本，Windows用户可以直接双击运行该脚本快速连接到服务器。

## 一、基本 SSH 连接

### Windows 系统

#### 使用 Windows 终端/PowerShell

1. 打开 Windows 终端或 PowerShell

2. 执行以下命令连接到服务器：
   ```powershell
   ssh 用户名@服务器IP地址
   ```
   例如：
   ```powershell
   ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

3. 首次连接时，系统会提示确认服务器指纹，输入 `yes` 并按回车

4. 输入您的服务器密码，完成连接

#### 使用 PuTTY 工具

1. 下载并安装 [PuTTY](https://www.putty.org/)

2. 打开 PuTTY 应用程序

3. 在 "Host Name (or IP address)" 字段中输入服务器的 IP 地址

4. 确保端口设置为 22（SSH 默认端口）

5. 点击 "Open" 按钮

6. 首次连接时，会弹出安全警告，点击 "Yes" 确认

7. 在弹出的终端窗口中，输入用户名和密码完成连接

### macOS/Linux 系统

1. 打开终端应用程序

2. 执行以下命令连接到服务器：
   ```bash
   ssh 用户名@服务器IP地址
   ```
   例如：
   ```bash
   ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

3. 首次连接时，输入 `yes` 确认服务器指纹

4. 输入服务器密码，完成连接

## 二、使用 SSH 密钥认证

SSH 密钥认证可以让您无需每次连接都输入密码，更加安全和便捷。

### 在本地生成 SSH 密钥

#### Windows (PowerShell)

```powershell
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 默认会保存在 C:\Users\您的用户名\.ssh\id_rsa
# 可以设置密码保护密钥（可选）

# 查看公钥内容
cat ~/.ssh/id_rsa.pub
```

#### macOS/Linux

```bash
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 默认会保存在 ~/.ssh/id_rsa
# 可以设置密码保护密钥（可选）

# 查看公钥内容
cat ~/.ssh/id_rsa.pub
```

### 将公钥上传到服务器

#### 方法 1：使用 ssh-copy-id

```bash
# Windows 用户需要先安装 Git Bash 或 WSL
ssh-copy-id 用户名@服务器IP地址
```

#### 方法 2：手动上传

1. 将本地生成的公钥内容复制到剪贴板

2. 通过 SSH 连接到服务器

3. 在服务器上执行：
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   nano ~/.ssh/authorized_keys
   ```

4. 将剪贴板中的公钥粘贴到文件中，保存并退出

5. 设置正确的权限：
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   ```

### 配置 SSH 客户端（可选）

在本地创建或编辑 `~/.ssh/config` 文件，添加以下内容：

```ssh-config
   Host youlan-server
     HostName iZuf635nesowrxp7kll8pgZ
     User ecs-assist-user
     IdentityFile ~/.ssh/id_rsa
     Port 22
     # 保持连接活跃
     ServerAliveInterval 60
   ```

这样，您以后就可以使用 `ssh youlan-server` 快速连接到服务器了。

## 三、使用 VS Code 远程开发

VS Code 提供了强大的远程开发功能，可以直接在本地编辑和调试远程服务器上的代码。

### 步骤 1：安装 VS Code 扩展

1. 打开 VS Code
2. 安装以下扩展：
   - Remote - SSH
   - Remote - Containers (如果需要在容器中开发)
   - Python
   - Django

### 步骤 2：连接到远程服务器

1. 点击 VS Code 左下角的绿色图标（远程连接按钮）
2. 选择 "Remote-SSH: Connect to Host..."
3. 选择 "Add New SSH Host..."
4. 输入 SSH 连接命令，例如：`ssh ubuntu@192.168.1.100`
5. 选择要保存配置的文件（通常是默认值）
6. 再次点击左下角的绿色图标，选择您刚才添加的主机
7. VS Code 会打开一个新窗口并连接到远程服务器

### 步骤 3：在远程服务器上打开项目

1. 连接成功后，点击 "Open Folder"
2. 导航到您的项目目录（例如 `/home/ubuntu/youlan_kids_customization/youlan_kids_django`）
3. 点击 "OK" 打开项目

### 步骤 4：配置调试环境

1. 创建 `.vscode/launch.json` 文件（如果不存在）
2. 添加以下配置：
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Django",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/manage.py",
               "args": [
                   "runserver",
                   "0.0.0.0:8000"
               ],
               "django": true
           }
       ]
   }
   ```

3. 现在您可以直接在 VS Code 中运行和调试远程服务器上的 Django 项目了

## 四、使用 PyCharm 远程开发

PyCharm Professional 版本也支持远程开发功能。

### 步骤 1：配置远程解释器

1. 打开 PyCharm
2. 进入 Settings > Project > Python Interpreter
3. 点击齿轮图标 > Add
4. 选择 "SSH Interpreter"
5. 选择 "New server configuration"
6. 输入服务器的主机名/IP、用户名和密码或密钥文件
7. 点击 "Next" 并完成配置

### 步骤 2：配置项目路径映射

1. 在解释器配置的最后一步，设置本地路径和远程路径的映射
   - 本地路径：选择您的本地项目目录
   - 远程路径：输入服务器上的项目目录路径

### 步骤 3：配置运行/调试设置

1. 点击工具栏中的 "Edit Configurations"
2. 点击 + 号，选择 "Django Server"
3. 设置名称（例如 "Remote Django Server"）
4. 设置主机为 0.0.0.0，端口为 8000
5. 确保解释器选择的是您配置的远程解释器
6. 点击 "OK" 保存配置

### 步骤 4：部署代码到远程服务器

1. 进入 Settings > Build, Execution, Deployment > Deployment
2. 点击 + 号，选择 "SFTP"
3. 输入服务器信息并配置连接
4. 设置本地路径和远程路径的映射
5. 点击 "OK" 保存配置
6. 现在可以使用 "Tools > Deployment > Upload to ..." 上传代码到服务器

## 五、使用 Docker 远程开发

如果远程服务器上使用 Docker 运行项目，可以通过以下方式连接：

### 在 VS Code 中连接到远程容器

1. 使用 Remote - SSH 扩展连接到远程服务器
2. 在远程服务器上，右键点击 `docker-compose.yml` 文件
3. 选择 "Remote-Containers: Open Folder in Container..."
4. VS Code 会在容器中打开项目，您可以直接在容器中开发

### 直接进入远程容器

```bash
# 先通过 SSH 连接到远程服务器
ssh 用户名@服务器IP地址

# 查看正在运行的容器
docker-compose ps

# 进入 web 容器的终端
docker-compose exec web bash
```

## 六、文件传输

### 使用 SCP 命令

```bash
   # 从本地传输文件到服务器
   scp 本地文件路径 ecs-assist-user@iZuf635nesowrxp7kll8pgZ:远程路径

   # 从服务器传输文件到本地
   scp ecs-assist-user@iZuf635nesowrxp7kll8pgZ:远程文件路径 本地路径

   # 传输整个目录
   scp -r 本地目录路径 ecs-assist-user@iZuf635nesowrxp7kll8pgZ:远程路径
   ```

### 使用 WinSCP（Windows）

1. 下载并安装 [WinSCP](https://winscp.net/eng/download.php)
2. 打开 WinSCP，输入服务器 IP、用户名和密码
3. 点击 "Login" 连接
4. 现在可以通过图形界面在本地和服务器之间传输文件

## 七、常见问题及解决方案

### 1. SSH 连接超时

- 检查服务器的防火墙设置，确保 22 端口已开放
- 确认服务器的 IP 地址是否正确
- 检查网络连接是否正常

### 2. 权限被拒绝错误

- 确认用户名和密码是否正确
- 检查 SSH 密钥权限是否正确（本地私钥应为 600，服务器上的 authorized_keys 应为 600）
- 确认服务器是否允许密码认证（查看 `/etc/ssh/sshd_config` 中的 `PasswordAuthentication` 设置）

### 3. VS Code 远程连接问题

- 更新 VS Code 和 Remote - SSH 扩展到最新版本
- 检查 SSH 配置文件是否正确
- 尝试删除 `~/.ssh/known_hosts` 文件中对应的服务器条目，然后重新连接

### 4. Docker 远程容器访问问题

- 确保远程服务器的 Docker 服务正在运行
- 确认用户有足够的权限访问 Docker（可能需要将用户添加到 docker 用户组）
- 检查容器是否正在运行（使用 `docker-compose ps` 命令）

## 八、安全建议

1. **使用 SSH 密钥认证**，避免使用密码认证
2. **定期更换 SSH 密钥**，尤其是在团队成员变动时
3. **考虑修改默认的 SSH 端口（22）** 为其他端口，增加安全性
4. **在生产环境中禁用 root 用户直接登录**
5. **使用防火墙限制可以连接到服务器的 IP 地址**
6. **定期更新服务器上的软件和系统**，确保安全性

## 九、高级配置：SSH 隧道

SSH 隧道可以帮助您安全地访问远程服务器上的内部服务。

### 本地端口转发

例如，访问远程服务器上的数据库：

```bash
   # 将远程服务器的 3306 端口映射到本地的 3307 端口
   ssh -L 3307:localhost:3306 ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

这样，您可以通过连接到本地的 3307 端口来访问远程的数据库服务。

### 远程端口转发

如果需要让外部用户访问您本地的服务：

```bash
   # 将本地的 8000 端口映射到远程服务器的 8001 端口
   ssh -R 8001:localhost:8000 ecs-assist-user@iZuf635nesowrxp7kll8pgZ
   ```

外部用户现在可以通过访问远程服务器的 8001 端口来访问您本地的服务。