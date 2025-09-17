# Address 应用说明

## 功能介绍

Address应用用于管理用户的收货地址信息，支持新增、删除、更新和设置默认地址等操作。

## 数据模型

`Address`模型包含以下字段：
- `address_id`: 地址ID（主键，自增）
- `user`: 所属用户（外键关联User模型）
- `province`: 省份
- `city`: 市
- `county`: 县/区
- `detailed_address`: 详细地址
- `is_default`: 是否为默认地址（布尔值，默认为False）
- `remark`: 备注
- `created_at`: 创建时间
- `updated_at`: 更新时间

**注意**：当设置某个地址为默认地址时，该用户的其他地址会自动取消默认状态。

## API接口

### 1. 新增地址

**URL**: `/address/add/`
**方法**: POST
**请求参数**: 
```json
{
    "user_id": "用户ID",
    "province": "省",
    "city": "市",
    "county": "县/区",
    "detailed_address": "详细地址",
    "is_default": false,  // 可选，默认为false
    "remark": "备注"  // 可选
}
```
**响应**: 
```json
{
    "success": true,
    "message": "新增地址成功",
    "address_id": "新创建的地址ID"
}
```

### 2. 删除地址

**URL**: `/address/delete/`
**方法**: POST
**请求参数**: 
```json
{
    "address_id": "地址ID",
    "user_id": "用户ID"
}
```
**响应**: 
```json
{
    "success": true,
    "message": "删除地址成功"
}
```

### 3. 更新地址

**URL**: `/address/update/`
**方法**: POST
**请求参数**: 
```json
{
    "address_id": "地址ID",
    "user_id": "用户ID",
    "province": "省",  // 可选
    "city": "市",  // 可选
    "county": "县/区",  // 可选
    "detailed_address": "详细地址",  // 可选
    "is_default": true,  // 可选
    "remark": "备注"  // 可选
}
```
**响应**: 
```json
{
    "success": true,
    "message": "更新地址成功"
}
```

### 4. 设置默认地址

**URL**: `/address/set_default/`
**方法**: POST
**请求参数**: 
```json
{
    "address_id": "地址ID",
    "user_id": "用户ID"
}
```
**响应**: 
```json
{
    "success": true,
    "message": "设置默认地址成功"
}
```

## 错误处理

所有接口都包含错误处理机制，在请求参数错误或服务器内部错误时会返回相应的错误信息和状态码。

## 日志记录

所有关键操作都会记录日志，包括成功和失败的情况，便于调试和监控。