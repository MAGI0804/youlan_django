# Django项目迁移与部署指南

本指南详细介绍如何将`youlan_kids_django`项目迁移到远程服务器，并在8080端口上部署，同时配置远程开发环境。

## 一、服务器环境准备

### 1. 确认服务器已安装以下软件
```bash
# 检查Docker是否安装
docker --version

# 检查Docker Compose是否安装
docker-compose --version

# 检查Git是否安装
git --version
```

### 2. 安装必要软件（CentOS系统）

由于CentOS默认仓库中没有docker-compose包，我们需要采用替代方法安装。以下是针对国内网络环境优化的安装方案：

```bash
# 安装Docker
sudo yum install docker git -y
sudo systemctl start docker
sudo systemctl enable docker

# 配置Docker国内镜像源（提高后续镜像拉取速度）
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://registry.docker-cn.com", "https://docker.mirrors.ustc.edu.cn"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

# 方法1：使用pip安装Docker Compose（推荐）
sudo yum install python3-pip -y
# 安装必要的系统依赖和Python模块（解决bcrypt和cryptography安装失败问题）
sudo yum install gcc gcc-c++ python3-devel openssl-devel libffi-devel -y
# 安装setuptools_rust模块
sudo pip3 install setuptools_rust
# 安装Rust编译器（解决cryptography库编译失败问题 - 国内源）
# 使用中国科学技术大学的Rust镜像源
curl --proto '=https' --tlsv1.2 -sSf https://mirrors.ustc.edu.cn/rust-static/rustup/rustup-init.sh | sh
# 加载Rust环境变量
source $HOME/.cargo/env
# 配置Cargo国内镜像源
cat << 'EOF' >> ~/.cargo/config
[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"
# 如果git协议不可用，使用https
# registry = "https://mirrors.ustc.edu.cn/crates.io-index"
EOF
# 配置pip国内镜像源
sudo mkdir -p /root/.pip
sudo tee /root/.pip/pip.conf <<-'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
sudo pip3 install docker-compose

# 如果仍然遇到bcrypt安装问题，可以尝试升级pip并使用--no-binary选项
sudo pip3 install --upgrade pip
sudo pip3 install docker-compose --no-binary :all:

# 或者尝试安装特定版本的docker-compose，可能兼容性更好
sudo pip3 install docker-compose==1.29.2

# 方法2：直接下载Docker Compose二进制文件（国内源）
# 注意：请访问https://github.com/docker/compose/releases获取最新版本号
sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装是否成功
docker-compose --version

### 4. Docker Compose安装故障排除

Docker Compose安装过程中可能遇到各种依赖问题，特别是在国内网络环境下。以下是针对常见错误的详细解决方案，请根据您遇到的具体错误信息选择对应方案：

```bash
# 问题0：setuptools_rust模块缺失
# 解决方案：安装setuptools_rust模块

sudo pip3 install setuptools_rust

# 问题1：cryptography库编译失败（Rust编译器缺失）
# 解决方案1：安装Rust编译器
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 解决方案2：使用国内源安装预编译的cryptography wheel文件
pip install cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple --only-binary=cryptography

# 问题2：权限错误
# 解决方案：使用sudo或以root用户执行安装命令

sudo pip3 install docker-compose

# 问题3：内存不足错误
# 解决方案：增加交换空间

sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 使交换空间永久生效
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

# 问题4：找不到命令错误
# 解决方案：检查PATH环境变量或创建软链接
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 问题5：依赖冲突
# 解决方案：使用virtualenv隔离环境

sudo pip3 install virtualenv
virtualenv compose-env
source compose-env/bin/activate
pip install docker-compose
```
```

### 3. 创建项目目录
```bash
mkdir -p /opt/projects
sudo chown -R $USER:$USER /opt/projects
cd /opt/projects
```

## 二、代码迁移到服务器

### 方法1：使用Git克隆（推荐）
```bash
# 在服务器上克隆代码仓库
cd /opt/projects
# 注意：<仓库URL>是您的Git代码仓库地址，需要替换为实际的URL
# 您可以从代码托管平台（如GitHub、GitLab、Gitee等）获取仓库URL
# 通常获取方式：
# 1. 登录您的代码托管平台，找到对应的仓库
# 2. 点击"克隆"或"复制"按钮获取仓库URL
# 3. URL格式通常为：https://<平台地址>/<用户名>/<仓库名>.git 或 git@<平台地址>:<用户名>/<仓库名>.git
# 4. 如果没有仓库，请联系项目管理员获取
# 5. 如果是私有仓库，确保您的服务器已经配置了SSH密钥或其他认证方式
git clone https://github.com/MAGI0804/youlan_django.git
cd youlan_kids_django

# 如果有.gitignore文件，请检查是否包含了不必要的文件
```

### 方法2：使用SCP传输文件（适用于无Git仓库的情况）
```bash
# 在本地Windows命令提示符下执行
d: && cd youlan_kids_customization
# 注意：username@server_ip需要替换为您的服务器实际用户名和IP地址
# username是您在服务器上的用户名
# server_ip是您的服务器的IP地址或域名
# 例如：admin@192.168.1.100或root@example.com
scp -r youlan_kids_django username@server_ip:/opt/projects/

# 或者使用WinSCP图形工具进行传输
```

## 三、使用Docker部署到8080端口

### 1. 修改Docker Compose配置

首先，我们需要修改`docker-compose.yml`文件，将端口映射改为8080：

```bash
# 在服务器上编辑docker-compose.yml
cd /opt/projects/youlan_kids_django
vi docker-compose.yml
```

修改`ports`部分如下：
```yaml
ports:
  - "8080:8000"
```

### 2. 使用国内镜像源（如果需要）

如果服务器在国内，可以使用我们之前创建的国内镜像源配置文件：

```bash
# 检查是否存在国内镜像配置文件
exists docker-compose.cn.yml && echo "国内镜像配置文件已存在"
```

### 3. 构建并运行Docker容器

#### 标准方式（使用默认Docker Hub）
```bash
# 构建并启动容器
docker-compose up -d --build

# 查看容器运行状态
docker-compose ps

# 查看容器日志
docker-compose logs -f web
```

#### 国内镜像源方式
```bash
# 使用国内镜像源构建并启动容器
docker-compose -f docker-compose.cn.yml up -d --build

# 查看容器运行状态
docker-compose -f docker-compose.cn.yml ps

# 查看容器日志
docker-compose -f docker-compose.cn.yml logs -f web
```

### 4. 验证部署是否成功

在浏览器中访问：`http://服务器IP:8080/admin`，如果能看到Django管理界面，则表示部署成功。

## 四、配置远程开发环境

### 1. 使用VS Code进行远程开发

#### 步骤1：安装VS Code远程开发插件
- 在本地VS Code中安装`Remote - SSH`扩展
- 安装`Remote - Containers`扩展（用于Docker容器内开发）

#### 步骤2：连接到远程服务器
- 点击VS Code左下角的绿色远程连接图标
- 选择`Remote-SSH: Connect to Host...`
- 输入`ssh username@server_ip`并连接

#### 步骤3：在远程服务器上打开项目
- 连接成功后，点击`文件 > 打开文件夹`
- 选择`/opt/projects/youlan_kids_django`

#### 步骤4：配置Python解释器
- 点击VS Code右下角的Python版本号
- 选择`Python: Select Interpreter`
- 选择`Enter interpreter path...`
- 输入`/usr/local/bin/python`（Docker容器内的Python路径）

### 2. 使用PyCharm进行远程开发

#### 步骤1：配置远程解释器
- 在PyCharm中打开项目
- 进入`File > Settings > Project > Python Interpreter`
- 点击齿轮图标，选择`Add...`
- 选择`SSH Interpreter`
- 输入服务器IP、用户名和密码
- 选择远程Python解释器路径：`/usr/local/bin/python`
- 设置同步文件夹：本地项目路径映射到服务器`/opt/projects/youlan_kids_django`

#### 步骤2：配置运行配置
- 进入`Run > Edit Configurations...`
- 点击`+`号，选择`Django server`
- 设置名称和主机为`0.0.0.0`，端口为`8080`
- 选择远程解释器
- 点击`OK`保存配置

## 五、开发与维护命令

### 1. 进入Docker容器内部
```bash
# 标准方式
docker-compose exec web /bin/bash

# 国内镜像源方式
docker-compose -f docker-compose.cn.yml exec web /bin/bash
```

### 2. 执行Django管理命令
```bash
# 在容器内执行
python manage.py migrate  # 数据库迁移
python manage.py createsuperuser  # 创建超级用户
python manage.py collectstatic  # 收集静态文件

# 或者在宿主机上执行
docker-compose exec web python manage.py migrate
```

### 3. 监控与更新
```bash
# 实时查看日志
docker-compose logs -f web

# 停止容器
docker-compose down

# 更新代码并重启容器
git pull
docker-compose up -d --build
```

## 六、常见问题与解决方案

### 1. 端口占用问题
如果8080端口已被占用，可以修改`docker-compose.yml`中的端口映射：
```yaml
ports:
  - "8081:8000"  # 将宿主机8081端口映射到容器8000端口
```

### 2. 权限问题
如果遇到文件权限问题，可以修改目录权限：
```bash
sudo chown -R $USER:$USER /opt/projects/youlan_kids_django
sudo chmod -R 755 /opt/projects/youlan_kids_django
```

### 3. 数据库连接问题
如果项目使用外部数据库，需要在`docker-compose.yml`中添加数据库服务配置，并在Django设置文件中配置数据库连接信息。

### 4. 环境变量配置
项目使用`.env`文件管理环境变量，确保该文件包含所有必要的配置项。

## 七、生产环境部署建议

1. 使用Gunicorn或uWSGI代替Django开发服务器
2. 配置Nginx作为反向代理
3. 启用HTTPS加密
4. 配置定期备份数据库和重要文件
5. 设置日志轮转和监控