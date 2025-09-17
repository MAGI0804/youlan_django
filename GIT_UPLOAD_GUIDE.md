# Git项目上传指南

根据您的操作（已执行`git init`），本指南将帮助您完成将清理后的项目上传到GitHub的完整流程，包括解决字符编码和远程仓库配置问题。

## 步骤0：配置Git字符编码（解决中文乱码问题）

在Windows环境下，Git可能会出现中文乱码问题。执行以下命令配置Git的字符编码：

```bash
# 配置提交消息编码
$ git config --global i18n.commitEncoding utf-8
# 配置日志输出编码
$ git config --global i18n.logOutputEncoding utf-8
# 设置控制台输出编码
$ export LESSCHARSET=utf-8  # Linux/Mac
$ set LESSCHARSET=utf-8     # Windows PowerShell/Cmd
```

## 当前状态

从终端输出可以看到：
```
Reinitialized existing Git repository in D:/youlan_kids_customization/.git/
```

这表明Git仓库已成功初始化（或重新初始化）。

## 步骤1：添加所有文件到暂存区

执行以下命令将项目文件添加到Git暂存区：

```bash
git add .
```

这个命令会将当前目录下的所有文件（除了.gitignore中指定的忽略文件）添加到暂存区。

## 步骤2：检查暂存状态

添加文件后，可以使用以下命令检查暂存状态：

```bash
git status
```

这将显示哪些文件已被添加到暂存区，哪些文件尚未添加。

## 步骤3：提交更改

使用以下命令提交暂存的更改：

```bash
git commit -m "清理项目结构 - 标准化Docker配置和部署流程"
```

请根据实际情况修改提交消息，使其清晰描述您的更改内容。

## 步骤4：添加/更新GitHub远程仓库

如果您还没有在GitHub上创建仓库，请先创建一个新的仓库（不要初始化README、.gitignore或license文件）。

### 情况1：首次添加远程仓库

执行以下命令添加GitHub远程仓库：

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

请将`YOUR_USERNAME`替换为您的GitHub用户名，`YOUR_REPOSITORY`替换为您创建的仓库名称。

### 情况2：远程仓库已存在（解决`remote origin already exists.`错误）

如果执行上述命令时出现`remote origin already exists.`错误，说明远程仓库已存在。您可以：

1. **查看现有远程仓库配置**：
   ```bash
   git remote -v
   ```

2. **更新现有远程仓库URL**（如果需要修改URL）：
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   ```

3. **或者删除现有远程仓库后重新添加**（谨慎使用）：
   ```bash
   git remote remove origin
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   ```

## 步骤5：验证远程仓库连接

执行以下命令验证远程仓库是否已正确添加：

```bash
git remote -v
```

这将显示远程仓库的URL。

## 步骤6：推送代码到GitHub

执行以下命令将本地代码推送到GitHub仓库：

```bash
git push -u origin main
```

如果您的默认分支名称不是`main`，请使用正确的分支名称（例如`master`）。

第一次推送时，`-u`选项会将本地分支与远程分支关联起来，后续推送只需使用`git push`即可。

## 步骤7：处理常见问题

### 7.1 字符编码问题（解决提交消息乱码）

如果您的提交消息出现中文乱码（例如`娓呯悊椤圭洰缁撴瀯 - 鏍囧噯鍖朌ocker閰嶇疆鍜岄儴缃叉祦绋`），请执行以下命令配置Git的字符编码：

```bash
# 配置提交消息编码
$ git config --global i18n.commitEncoding utf-8
# 配置日志输出编码
$ git config --global i18n.logOutputEncoding utf-8
# 设置终端输出编码
$ set LESSCHARSET=utf-8  # Windows PowerShell/Cmd
# 或者在Linux/Mac上
$ export LESSCHARSET=utf-8
```

### 7.2 权限问题

如果在推送时遇到权限错误，可能是因为没有正确配置GitHub凭据。您可以：

- 使用GitHub CLI进行登录：
  ```bash
gh auth login
  ```

- 或者配置SSH密钥（推荐）：
  [GitHub官方文档：生成SSH密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

### 7.2 分支不存在问题

如果收到类似"branch 'main' does not exist"的错误，请确保您的本地分支名称正确：

```bash
git branch
```

如果需要创建main分支：

```bash
git checkout -b main
```

### 7.3 推送冲突

如果远程仓库已有内容导致推送冲突，请先拉取远程内容：

```bash
git pull origin main --rebase
```

然后解决可能的冲突，最后再次推送。

## 步骤8：服务器从GitHub拉取代码

完成GitHub上传后，在服务器上执行以下命令拉取最新代码（或使用之前创建的server_deploy.sh脚本）：

```bash
# 克隆GitHub仓库
cd /opt/projects
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git youlan_kids_customization

# 进入项目目录
cd youlan_kids_customization/youlan_kids_django

# 使用Docker运行项目
docker-compose up -d --build
```

## 完整命令清单

为了方便复制，以下是完整的命令清单（包括字符编码配置）：

```bash
# 本地操作 - 配置字符编码（重要！解决中文乱码问题）
git config --global i18n.commitEncoding utf-8
git config --global i18n.logOutputEncoding utf-8
set LESSCHARSET=utf-8  # Windows PowerShell/Cmd
# 或者在Linux/Mac上
# export LESSCHARSET=utf-8

# 添加文件并提交
git add .
git commit -m "清理项目结构 - 标准化Docker配置和部署流程"

# 配置远程仓库（根据情况选择）
# 情况1：首次添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
# 情况2：更新现有远程仓库URL
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

# 推送代码
git push -u origin main

# 服务器操作（假设使用/opt/projects目录）
cd /opt/projects
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git youlan_kids_customization
sudo chown -R $USER:$USER youlan_kids_customization
sudo chmod -R 755 youlan_kids_customization
cd youlan_kids_customization/youlan_kids_django
# 确保.env文件存在并配置正确
docker-compose up -d --build
```

## 后续维护

项目上传到GitHub后，您可以使用以下命令维护项目：

- 拉取最新代码：`git pull origin main`
- 添加新文件：`git add 文件名`
- 提交更改：`git commit -m "描述信息"`
- 推送更改：`git push`
- 查看提交历史：`git log`