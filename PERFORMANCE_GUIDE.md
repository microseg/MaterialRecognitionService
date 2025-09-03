# MaskTerial Performance Guide

## Instance Type Recommendations

### 🟢 **Recommended for Production (CPU)**

| Instance Type | vCPU | Memory | Storage | Cost/Hour | Use Case |
|---------------|------|--------|---------|-----------|----------|
| **t3.large** | 2 | 8 GB | 200 GB | ~$0.083 | ✅ **Recommended** |
| t3.xlarge | 4 | 16 GB | 200 GB | ~$0.166 | High performance |
| c5.large | 2 | 4 GB | 200 GB | ~$0.085 | Compute optimized |

### 🟡 **Minimum Requirements**

| Instance Type | vCPU | Memory | Storage | Cost/Hour | Status |
|---------------|------|--------|---------|-----------|--------|
| t3.medium | 2 | 4 GB | 200 GB | ~$0.0416 | ⚠️ Minimum |
| t3.micro | 2 | 1 GB | 200 GB | ~$0.0208 | ❌ Not recommended |

### 🔴 **GPU Instances (For High Performance)**

| Instance Type | vCPU | Memory | GPU | Cost/Hour | Use Case |
|---------------|------|--------|-----|-----------|----------|
| g4dn.xlarge | 4 | 16 GB | 1x T4 | ~$0.526 | ✅ GPU processing |
| g4dn.2xlarge | 8 | 32 GB | 1x T4 | ~$0.736 | High throughput |

## Current Configuration

**Updated to: t3.large**
- ✅ **vCPU**: 2 cores
- ✅ **Memory**: 8 GB (sufficient for model loading)
- ✅ **Storage**: 200 GB (enough for all models)
- ✅ **Cost**: ~$0.083/hour (~$60/month)

## Performance Optimizations

### 1. **Memory Management**
```python
# In maskterial_app.py
import gc

def cleanup_memory():
    """Clean up memory after processing"""
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
```

### 2. **Model Loading Strategy**
```python
# Load models on demand
class LazyModelLoader:
    def __init__(self, model_path):
        self.model_path = model_path
        self._models = {}
    
    def get_model(self, material_type):
        if material_type not in self._models:
            self._models[material_type] = self.load_model(material_type)
        return self._models[material_type]
```

### 3. **Docker Optimizations**
```dockerfile
# Multi-stage build to reduce image size
FROM python:3.11-slim as builder
# ... build dependencies

FROM python:3.11-slim
# ... copy only necessary files
```

## Monitoring and Scaling

### CloudWatch Metrics to Monitor
- **CPU Utilization**: Target < 80%
- **Memory Usage**: Target < 85%
- **Disk Usage**: Target < 80%
- **Network I/O**: Monitor for bottlenecks

### Auto Scaling Triggers
```yaml
# Example CloudWatch alarms
- CPU > 80% for 5 minutes → Scale up
- Memory > 85% for 5 minutes → Scale up
- CPU < 30% for 10 minutes → Scale down
```

## Cost Optimization

### 1. **Reserved Instances**
- 1-year RI: ~40% savings
- 3-year RI: ~60% savings

### 2. **Spot Instances** (For non-critical workloads)
- Up to 90% savings
- Risk of interruption

### 3. **Right-sizing**
- Monitor actual usage
- Adjust instance size based on metrics

## Troubleshooting

### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check Docker memory
docker stats
```

### Slow Processing
```bash
# Check CPU usage
top
htop

# Check disk I/O
iotop
```

### Model Loading Issues
```bash
# Check model directory
ls -la /opt/maskterial/models/

# Verify model files
python verify_models.py
```

## Migration Guide

### From t3.micro to t3.large
1. **Backup data**: Ensure all data is backed up
2. **Update CDK**: Deploy with new instance type
3. **Test performance**: Run verification tests
4. **Monitor costs**: Track new pricing

### Performance Testing
```bash
# Test with sample images
curl -X POST "http://your-instance:5000/detect" \
  -F "image=@test_image.jpg" \
  -F "customer_id=test"

# Monitor response time
time curl -X POST "http://your-instance:5000/detect" \
  -F "image=@test_image.jpg" \
  -F "customer_id=test"
```

## Recommendations

### For Development/Testing
- **t3.medium**: Sufficient for testing
- **t3.large**: Better for development

### For Production
- **t3.large**: Good balance of performance/cost
- **t3.xlarge**: For high throughput
- **g4dn.xlarge**: For GPU acceleration

### For Cost Optimization
- Use Reserved Instances
- Monitor and right-size
- Consider Spot instances for batch processing
