# 🧮 Simple Calculator API

一个基于Flask的简单计算器API，用于演示CI/CD pipeline工作流程。

## 🚀 API端点

### 基础端点

- `GET /` - API信息和端点列表
- `GET /health` - 健康检查
- `GET /test` - 部署测试

### 计算器端点

#### GET请求（简单计算）

- `GET /add/{a}/{b}` - 加法运算
- `GET /subtract/{a}/{b}` - 减法运算  
- `GET /multiply/{a}/{b}` - 乘法运算
- `GET /divide/{a}/{b}` - 除法运算

#### POST请求（灵活计算）

- `POST /calculate` - 通用计算端点

## 📝 使用示例

### 1. 获取API信息

```bash
curl http://34.234.208.1:8000/
```

响应：
```json
{
  "message": "Welcome to Simple Calculator API!",
  "version": "1.0.2",
  "environment": "production",
  "endpoints": {
    "/": "API information",
    "/health": "Health check",
    "/calculate": "Perform calculations (POST)",
    "/add/<a>/<b>": "Add two numbers (GET)",
    "/subtract/<a>/<b>": "Subtract two numbers (GET)",
    "/multiply/<a>/<b>": "Multiply two numbers (GET)",
    "/divide/<a>/<b>": "Divide two numbers (GET)"
  }
}
```

### 2. 使用GET请求进行计算

```bash
# 加法
curl http://34.234.208.1:8000/add/10/5

# 减法
curl http://34.234.208.1:8000/subtract/10/3

# 乘法
curl http://34.234.208.1:8000/multiply/4/7

# 除法
curl http://34.234.208.1:8000/divide/15/3
```

### 3. 使用POST请求进行计算

```bash
# 加法
curl -X POST http://34.234.208.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 25, "b": 15}'

# 乘法
curl -X POST http://34.234.208.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "multiply", "a": 6, "b": 8}'
```

### 4. 健康检查

```bash
curl http://34.234.208.1:8000/health
```

## 🧪 测试API

运行测试脚本：

```bash
python3 test_calculator.py
```

## 📊 响应格式

### 成功响应

```json
{
  "operation": "add",
  "a": 10.0,
  "b": 5.0,
  "result": 15.0,
  "timestamp": "2025-08-29T22:15:30.123456"
}
```

### 错误响应

```json
{
  "error": "Division by zero"
}
```

## 🔧 部署

这个API通过以下流程自动部署：

1. 代码推送到GitHub
2. GitHub触发AWS CodePipeline
3. CodeBuild部署到EC2实例
4. 服务自动启动

## 🌐 访问地址

- **API地址**: http://34.234.208.1:8000
- **健康检查**: http://34.234.208.1:8000/health

## 🛠️ 技术栈

- **后端框架**: Flask
- **部署平台**: AWS EC2
- **CI/CD**: AWS CodePipeline + CodeBuild
- **版本控制**: GitHub

## 📈 监控

- 通过 `/health` 端点监控服务状态
- 查看EC2实例日志：`sudo journalctl -u matsight-backend -f`
- 监控pipeline状态：AWS CodePipeline控制台
