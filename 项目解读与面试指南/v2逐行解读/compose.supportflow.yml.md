# compose.supportflow.yml

## 输入输出流

构建工具、依赖安装器或配置加载器读取本文件；输出构建上下文、容器服务、依赖版本或环境参数。具体消费入口参见 SUPPORTFLOW.md。

## 先理解设计

配置文件只声明行为，不证明服务已经运行。注意默认 sandbox、认证口令、模型地址、持久卷和排除敏感运行数据。

源码 SHA256：`42e7e7ff2ca38d5e8baa7ece8ebe8dfb524cdb62841c106b6938309e46362d0e`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```text
services:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L2**

```text
  redis:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```text
    image: redis:7.4-alpine
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```text
    command: ["redis-server", "--appendonly", "yes", "--requirepass", "${SF_REDIS_PASSWORD:?Set SF_REDIS_PASSWORD}"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```text
    volumes: ["sf-redis:/data"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```text
    healthcheck:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```text
      test: ["CMD-SHELL", "redis-cli -a \"$$REDIS_PASSWORD\" ping | grep PONG"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```text
      interval: 10s
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```text
      timeout: 3s
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L10**

```text
      retries: 5
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```text
    environment:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```text
      REDIS_PASSWORD: ${SF_REDIS_PASSWORD:?Set SF_REDIS_PASSWORD}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```text
  app:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```text
    build:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```text
      context: .
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```text
      target: production
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```text
    ports: ["127.0.0.1:8000:8000"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```text
    extra_hosts: ["host.docker.internal:host-gateway"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```text
    environment:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```text
      SF_DB_PATH: /app/data/supportflow.sqlite3
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```text
      SF_STORAGE: chroma
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```text
      SF_CHROMA_PATH: /app/data/supportflow-chroma
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```text
      SF_REDIS_URL: redis://:${SF_REDIS_PASSWORD}@redis:6379/0
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```text
      SF_MODEL_BACKEND: ${SF_MODEL_BACKEND:-compatible}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```text
      SF_MODEL_URL: ${SF_MODEL_URL:-http://host.docker.internal:8081/v1}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```text
      SF_MODEL_NAME: ${SF_MODEL_NAME:-Qwen3-1.7B-Q8_0}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```text
      SF_MODEL_KEY: ${SF_MODEL_KEY:-}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```text
      SF_LOCAL_CHAT_TEMPLATE: ${SF_LOCAL_CHAT_TEMPLATE:-true}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```text
      SF_PUBLIC_URL: ${SF_PUBLIC_URL:-http://localhost:8000}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```text
      SF_BUSINESS_MODE: sandbox
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```text
    volumes: ["sf-data:/app/data", "./skills:/app/skills:ro"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```text
    depends_on:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```text
      redis: {condition: service_healthy}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```text
volumes:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```text
  sf-data:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```text
  sf-redis:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

Docker/Redis 需要在目标运行环境验证；镜像摘要、供应链与备份恢复需进一步固定和演练。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
