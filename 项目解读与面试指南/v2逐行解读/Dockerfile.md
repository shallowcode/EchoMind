# Dockerfile

## 输入输出流

构建工具、依赖安装器或配置加载器读取本文件；输出构建上下文、容器服务、依赖版本或环境参数。具体消费入口参见 SUPPORTFLOW.md。

## 先理解设计

配置文件只声明行为，不证明服务已经运行。注意默认 sandbox、认证口令、模型地址、持久卷和排除敏感运行数据。

源码 SHA256：`24c88bef02f9ec5bc090d975bc7d656c4d93d19fb9604867c79d56e8878bd39d`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```text
# EchoMind 智能客服系统 — Docker 多阶段构建
```

作者注释，说明约束或设计意图；本行不执行。

**L2**

```text
# 目标：生产镜像尽量精简，开发镜像包含调试工具
```

作者注释，说明约束或设计意图；本行不执行。

**L4**

```text
# ── 阶段 1：基础环境 ──────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L5**

```text
FROM python:3.12-slim AS base
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```text
WORKDIR /app
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```text
ENV PYTHONUNBUFFERED=1 \
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L10**

```text
    PYTHONDONTWRITEBYTECODE=1 \
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L11**

```text
    PIP_NO_CACHE_DIR=1 \
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L12**

```text
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```text
    PYTHONPATH=/app
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```text
# curl 用于健康检查；不再需要 gcc/g++（已移除本地 ML 模型）
```

作者注释，说明约束或设计意图；本行不执行。

**L16**

```text
RUN apt-get update && apt-get install -y --no-install-recommends \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```text
    curl \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```text
    && rm -rf /var/lib/apt/lists/*
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```text
# ── 阶段 2：安装 Python 依赖 ──────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L21**

```text
FROM base AS dependencies
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```text
COPY requirements.txt .
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```text
RUN pip install --upgrade pip && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```text
    pip install -r requirements.txt
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```text
# 预下载 ChromaDB 内置的 ONNX embedding 模型（~79MB），避免运行时下载超时
```

作者注释，说明约束或设计意图；本行不执行。

**L28**

```text
RUN mkdir -p /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2 && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```text
    curl -L --retry 3 --retry-delay 5 -o /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```text
    https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```text
    cd /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2 && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```text
    tar -xzf onnx.tar.gz && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```text
    rm onnx.tar.gz
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```text
# ── 阶段 3：生产镜像 ──────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L36**

```text
FROM base AS production
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```text
# 非 root 用户运行。先创建用户，后续 COPY 直接带 owner，避免 chown -R 复制出额外大层。
```

作者注释，说明约束或设计意图；本行不执行。

**L39**

```text
RUN useradd -m -u 1000 echomind
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```text
# 从依赖阶段复制已安装的包
```

作者注释，说明约束或设计意图；本行不执行。

**L42**

```text
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```text
COPY --from=dependencies /usr/local/bin /usr/local/bin
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```text
# 复制预下载的 ONNX 模型缓存
```

作者注释，说明约束或设计意图；本行不执行。

**L45**

```text
COPY --from=dependencies --chown=echomind:echomind /root/.cache/chroma /home/echomind/.cache/chroma
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```text
# 复制应用代码
```

作者注释，说明约束或设计意图；本行不执行。

**L48**

```text
COPY --chown=echomind:echomind . .
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```text
# 创建必要目录，只调整运行期需要写入的目录权限，避免递归 chown 整个应用。
```

作者注释，说明约束或设计意图；本行不执行。

**L51**

```text
RUN mkdir -p /app/data/chroma /app/logs /app/config && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```text
    chown echomind:echomind /app/data /app/data/chroma /app/logs /app/config
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```text
USER echomind
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```text
EXPOSE 8000
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```text
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```text
    CMD curl -f http://localhost:8000/health || exit 1
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```text
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```text
# ── 阶段 4：开发镜像 ──────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L63**

```text
FROM dependencies AS development
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```text
COPY . .
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```text
RUN mkdir -p /app/data/chroma /app/logs /app/config /app/tests && \
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```text
    chmod -R 777 /app/data /app/logs
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```text
EXPOSE 8000
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```text
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```text
# The default build must be the unprivileged production image.
```

作者注释，说明约束或设计意图；本行不执行。

**L75**

```text
FROM production AS final
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

Docker/Redis 需要在目标运行环境验证；镜像摘要、供应链与备份恢复需进一步固定和演练。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
