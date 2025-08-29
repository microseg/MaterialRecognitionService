# Material Recognition Service

这是一个测试应用，用于验证完整的CI/CD部署工作流程。

## 项目结构

```
MaterialRecognitionService/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
└── README.md          # 项目说明
```

## 功能

- **Hello World**: 简单的问候接口
- **健康检查**: 服务状态监控
- **测试接口**: 部署验证
- **信息接口**: 服务信息展示

## 部署工作流程

1. **本地开发** → 在用户EC2上开发代码
2. **代码推送** → 推送到GitHub main分支
3. **自动触发** → GitHub Actions触发AWS CodePipeline
4. **自动部署** → CodeBuild部署到生产EC2
5. **服务上线** → 生产环境服务可用

## 测试命令

```bash
# 启动服务
python app.py

# 测试接口
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/test
curl http://localhost:8000/info
```

## 部署后验证

部署完成后，可以通过以下方式验证：

```bash
# 从生产EC2测试
curl http://localhost:8000/

# 从外部访问（如果有公网IP）
curl http://[PRODUCTION_EC2_IP]:8000/
```
