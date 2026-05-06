---
name: xhs-qianfan-apis
description: Use Xiaohongshu QianFan platform API for distributor data including distributor lists, categories, shops, and product information. Use when the user wants to analyze XHS distributors or e-commerce data.
allowed-tools: ["Bash(python *)"]
argument-hint: "[operation: get_distributors|get_categories|get_products]"
---

## 千帆平台 API（分销商数据）

> **项目路径**: `C:\Users\PC\Documents\Spider_XHS-xhs_new_api`
> 运行 Python 脚本前需先 `cd` 到项目目录。

### 初始化

```python
import sys, os
sys.path.insert(0, r'C:\Users\PC\Documents\Spider_XHS-xhs_new_api')
from apis.xhs_qianfan_apis import QianFanAPI

qf_api = QianFanAPI()
from xhs_utils.common_util import load_env
cookies_str = load_env()
```

### 核心 API

#### 获取分销商列表
```python
success, msg, distributors = qf_api.get_some_distributors(
    num=50,
    cookies=cookies_str,
    proxies=None
)
```

#### 获取分销商合作品类
```python
success, msg, categories = qf_api.get_categories(cookies_str)
```

#### 获取分销商店铺信息
```python
success, msg, shops = qf_api.get_shop_info(distributor_id, cookies_str)
```

#### 获取商品信息
```python
success, msg, products = qf_api.get_products(shop_id, cookies_str)
```

### 典型用法

```python
# 获取分销商数据并分析
distributors = qf_api.get_some_distributors(num=100, cookies=cookies_str)
# 可结合 AI 进行分销策略分析
```

### 注意事项
- 千帆平台为小红书电商/分销相关平台
- 需要有效的千帆账号 Cookie
