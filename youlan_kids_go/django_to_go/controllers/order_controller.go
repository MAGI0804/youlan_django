package controllers

import (
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"django_to_go/db"
	"django_to_go/models"
)

// OrderController 订单控制器

type OrderController struct{}

// OrderList 获取订单列表 - 与Django版本的orders_query函数对应
func (oc *OrderController) OrderList(c *gin.Context) {
	// 绑定请求参数
	var queryData struct {
		Shopname  string `json:"shopname" binding:"required"`
		UserID    int    `json:"user_id"`
		Status    string `json:"status"`
		Page      int    `json:"page" binding:"required,min=1"`
		PageSize  int    `json:"page_size" binding:"required,min=1,max=50"`
		BeginTime string `json:"begin_time"`
		EndTime   string `json:"end_time"`
	}

	if err := c.ShouldBindJSON(&queryData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "请求参数错误"})
		return
	}

	// 验证shopname
	if queryData.Shopname != "youlan_kids" {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "无效的店铺名称"})
		return
	}

	// 限制PageSize最大值为50
	if queryData.PageSize > 50 {
		queryData.PageSize = 50
	}

	// 构建查询
	var orders []models.Order
	query := db.DB.Model(&models.Order{}) // 注意这里使用了正确的表名

	// 应用user_id过滤
	if queryData.UserID > 0 {
		query = query.Where("user_id = ?", queryData.UserID)
	}

	// 应用状态过滤
	validStatuses := []string{"pending", "shipped", "delivered", "canceled", "processing"}
	if queryData.Status != "" {
		statusValid := false
		for _, validStatus := range validStatuses {
			if validStatus == queryData.Status {
				statusValid = true
				break
			}
		}
		if !statusValid {
			c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "订单状态无效"})
			return
		}
		query = query.Where("status = ?", queryData.Status)
	}

	// 应用日期过滤
	if queryData.BeginTime != "" {
		beginTime, err := time.Parse("2006-01-02", queryData.BeginTime)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "日期格式必须为YYYY-MM-DD"})
			return
		}
		// 转换为UTC时间（Django默认存储UTC时间）
		beginTime = beginTime.Add(-8 * time.Hour)
		query = query.Where("order_time >= ?", beginTime)
	}

	if queryData.EndTime != "" {
		endTime, err := time.Parse("2006-01-02", queryData.EndTime)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "日期格式必须为YYYY-MM-DD"})
			return
		}
		// 转换为UTC时间并加一天（包含当天）
		endTime = endTime.Add(-8*time.Hour + 24*time.Hour)
		query = query.Where("order_time < ?", endTime)
	}

	// 计算偏移量
	offset := (queryData.Page - 1) * queryData.PageSize

	// 执行分页查询
	var total int64
	if err := query.Count(&total).Error; err != nil {
		log.Printf("获取订单总数失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "服务器内部错误"})
		return
	}

	if err := query.Offset(offset).Limit(queryData.PageSize).Order("order_time DESC").Find(&orders).Error; err != nil {
		log.Printf("获取订单列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "服务器内部错误"})
		return
	}

	// 转换订单数据格式
	result := make([]map[string]interface{}, 0, len(orders))
	for _, order := range orders {
		orderMap := convertOrderToMap(order)
		// 添加物流过程空列表（批量查询时不返回实际物流信息）
		orderMap["logistics_process"] = []interface{}{}
		result = append(result, orderMap)
	}

	// 准备响应数据
	c.JSON(http.StatusOK, gin.H{
		"status":   "success",
		"data":     result,
		"page":     queryData.Page,
		"page_size": queryData.PageSize,
		"total":    total,
	})
}

// OrderDetail 获取订单详情 - 与Django版本的query_order_data函数对应
func (oc *OrderController) OrderDetail(c *gin.Context) {
	// 绑定请求参数
	var queryData struct {
		OrderID string `json:"order_id" binding:"required"`
		UserID  int    `json:"user_id"`
	}

	if err := c.ShouldBindJSON(&queryData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "请求体格式错误"})
		return
	}

	// 构建查询条件
	query := db.DB.Model(&models.Order{}).Where("order_id = ?", queryData.OrderID)

	// 如果提供了user_id，则添加到查询条件中
	if queryData.UserID > 0 {
		query = query.Where("user_id = ?", queryData.UserID)
	}

	// 查询订单
	var order models.Order
	if err := query.First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"status": "error", "message": "订单不存在"})
		return
	}

	// 准备响应数据
	detailMap := convertOrderToMap(order)

	// 返回订单信息（不含物流更新和物流信息返回）
	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "查询订单信息成功",
		"data":    detailMap
	})
}

// ChangeStatus 修改订单状态 - 与Django版本的change_status函数对应
func (oc *OrderController) ChangeStatus(c *gin.Context) {
	// 绑定请求数据
	var requestData struct {
		OrderID      string `json:"order_id" binding:"required"`
		Status       string `json:"status" binding:"required"`
		ExpressCompany string `json:"express_company"`
		ExpressNumber  string `json:"express_number"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 验证状态值
	validStatus := map[string]bool{
		"pending":   true,
		"paid":      true,
		"shipped":   true,
		"delivered": true,
		"cancelled": true,
	}

	if !validStatus[requestData.Status] {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "无效的订单状态",
		})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", requestData.OrderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "订单不存在",
		})
		return
	}

	// 如果状态是shipped，验证物流信息
	if requestData.Status == "shipped" {
		if requestData.ExpressCompany == "" || requestData.ExpressNumber == "" {
			c.JSON(http.StatusBadRequest, gin.H{
				"status":  "error",
				"message": "发货状态需要提供物流信息",
			})
			return
		}
		order.ExpressCompany = requestData.ExpressCompany
		order.ExpressNumber = requestData.ExpressNumber
	}

	// 更新订单状态
	order.Status = requestData.Status
	if requestData.Status == "paid" {
		order.PaymentTime = time.Now()
	}

	if err := db.DB.Save(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "修改订单状态失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "订单状态修改成功",
		"data": gin.H{"order_id": requestData.OrderID, "status": requestData.Status}
	})
}

	responseData := gin.H{
		"code":    200,
		"message": "获取成功",
		"data":    detailMap,
	}

	c.JSON(http.StatusOK, responseData)
}

// OrderCreate 创建订单 - 与Django版本的add_order函数对应
func (oc *OrderController) OrderCreate(c *gin.Context) {
	// 绑定请求参数
	var orderData struct {
		ReceiverName    string        `json:"receiver_name" binding:"required"`
		Province        string        `json:"province" binding:"required"`
		City            string        `json:"city" binding:"required"`
		County          string        `json:"county" binding:"required"`
		DetailedAddress string        `json:"detailed_address" binding:"required"`
		OrderAmount     float64       `json:"order_amount" binding:"required"`
		ProductList     []interface{} `json:"product_list" binding:"required,dive"`
		UserID          int           `json:"user_id" binding:"required"`
		ReceiverPhone   string        `json:"receiver_phone"`
		ExpressCompany  string        `json:"express_company"`
		ExpressNumber   string        `json:"express_number"`
	}

	if err := c.ShouldBindJSON(&orderData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "请求参数错误"})
		return
	}

	// 验证product_list是否为列表
	if len(orderData.ProductList) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "product_list不能为空列表"})
		return
	}

	// 生成订单号
	orderID := generateOrderNo()

	// 创建订单
	order := models.Order{
		OrderID:        orderID,
		UserID:         orderData.UserID,
		ReceiverName:   orderData.ReceiverName,
		ReceiverPhone:  orderData.ReceiverPhone,
		Province:       orderData.Province,
		City:           orderData.City,
		County:         orderData.County,
		DetailedAddress: orderData.DetailedAddress,
		OrderAmount:    orderData.OrderAmount,
		ProductList:    orderData.ProductList,
		ExpressCompany: orderData.ExpressCompany,
		ExpressNumber:  orderData.ExpressNumber,
		Status:         "pending",
		OrderTime:      time.Now(),
	}

	// 保存订单
	if err := db.DB.Create(&order).Error; err != nil {
		log.Printf("创建订单失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "服务器内部错误"})
		return
	}

	// 准备响应数据
	responseData := map[string]interface{}{
		"order_id": orderID,
		"user_id":  orderData.UserID,
		"receiver_name": orderData.ReceiverName,
		"receiver_phone": orderData.ReceiverPhone,
		"express_company": orderData.ExpressCompany,
		"express_number": orderData.ExpressNumber,
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "订单创建成功",
		"order_id": orderID,
		"data":     responseData,
	})
}

// OrderUpdate 更新订单
func (oc *OrderController) OrderUpdate(c *gin.Context) {
	orderIDStr := c.Param("id")
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的订单ID"})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", orderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "订单不存在"})
		return
	}

	// 绑定请求数据
	var updateData map[string]interface{}
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的JSON格式"})
		return
	}

	// 更新字段
	if status, ok := updateData["status"].(string); ok && status != "" {
		order.Status = status
	}

	if paymentMethod, ok := updateData["payment_method"].(string); ok && paymentMethod != "" {
		order.PaymentMethod = paymentMethod
	}

	if paymentTime, ok := updateData["payment_time"].(string); ok && paymentTime != "" {
		parsedTime, timeErr := time.Parse("2006-01-02 15:04:05", paymentTime)
		if timeErr == nil {
			order.PaymentTime = parsedTime
		}
	}

	// 根据Order结构体，以下字段不存在：DeliveryMethod, ExpressCompany, ExpressNumber
	if deliveryMethod, ok := updateData["delivery_method"].(string); ok && deliveryMethod != "" {
		order.DeliveryMethod = deliveryMethod
	}

	if expressCompany, ok := updateData["express_company"].(string); ok && expressCompany != "" {
		order.ExpressCompany = expressCompany
	}

	if expressNumber, ok := updateData["express_number"].(string); ok && expressNumber != "" {
		order.ExpressNumber = expressNumber
	}

	// 保存更新
	if err := db.DB.Save(&order).Error; err != nil {
		log.Printf("更新订单失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "订单更新成功",
		"data":    convertOrderToMap(order),
	})
}

// OrderCancel 取消订单 - 与Django版本的功能保持一致
func (oc *OrderController) OrderCancel(c *gin.Context) {
	// 获取订单ID
	orderID := c.Query("order_id")
	if orderID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "订单ID不能为空",
		})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", orderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "订单不存在",
		})
		return
	}

	// 检查订单状态
	if order.Status != "pending" && order.Status != "paid" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "只有待支付和已支付状态的订单才能取消",
		})
		return
	}

	// 更新订单状态
	order.Status = "cancelled"
	if err := db.DB.Save(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "取消订单失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "订单取消成功",
		"data": gin.H{"order_id": orderID}
	})
}

// OrderPay 支付订单 - 与Django版本的功能保持一致
func (oc *OrderController) OrderPay(c *gin.Context) {
	// 获取订单ID
	orderID := c.Query("order_id")
	if orderID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "订单ID不能为空",
		})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", orderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "订单不存在",
		})
		return
	}

	// 检查订单状态是否允许支付
	if order.Status != "pending" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "订单状态不允许支付",
		})
		return
	}

	// 更新订单状态
	order.Status = "paid"
	order.PaymentTime = time.Now()

	// 保存更新
	if err := db.DB.Save(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "支付订单失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "订单支付成功",
		"data": gin.H{"order_id": orderID}
	})
}

// OrderDeliver 发货 - 与Django版本update_express_info函数对应
func (oc *OrderController) OrderDeliver(c *gin.Context) {
	// 绑定请求数据
	var deliverData struct {
		OrderID        string `json:"order_id" binding:"required"`
		ExpressCompany string `json:"express_company" binding:"required"`
		ExpressNumber  string `json:"express_number" binding:"required"`
	}

	if err := c.ShouldBindJSON(&deliverData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效"
		})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", deliverData.OrderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "订单不存在"
		})
		return
	}

	// 检查订单状态是否允许发货
	if order.Status != "paid" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "订单状态不允许发货"
		})
		return
	}

	// 更新订单状态和物流信息
	order.Status = "shipped"
	order.ExpressCompany = deliverData.ExpressCompany
	order.ExpressNumber = deliverData.ExpressNumber
	if err := db.DB.Save(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "更新订单物流信息失败"
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "订单发货成功",
		"data": gin.H{"order_id": deliverData.OrderID}
	})
}

// 工具函数：生成订单号 - 格式为Y+YYYYMMDD+8位随机数字
func generateOrderNo() string {
	currentDate := time.Now().Format("20060102")
	maxRetries := 5
	var orderID string
	
	for retry := 0; retry < maxRetries; retry++ {
		// 生成8位随机数字
		var randomNum string
		for i := 0; i < 8; i++ {
			randomNum += fmt.Sprintf("%d", time.Now().UnixNano()%10)
			// 添加小延迟以确保随机性
			time.Sleep(time.Nanosecond)
		}
		
		orderID = fmt.Sprintf("Y%s%s", currentDate, randomNum)
			
		// 检查订单号是否已存在
		var count int64
		err := db.DB.Model(&models.Order{}).Where("order_id = ?", orderID).Count(&count).Error
		if err == nil && count == 0 {
			return orderID
		}
	}
	
	// 如果重试多次仍失败，使用时间戳作为后备方案
	return fmt.Sprintf("Y%s%d", currentDate, time.Now().UnixNano()%100000000)
}

// 工具函数：将订单对象转换为map - 与Django版本返回格式一致
func convertOrderToMap(order models.Order) map[string]interface{} {
	result := make(map[string]interface{})
	result["order_id"] = order.OrderID
	result["user_id"] = order.UserID
	result["receiver_name"] = order.ReceiverName
	result["receiver_phone"] = order.ReceiverPhone
	result["province"] = order.Province
	result["city"] = order.City
	result["county"] = order.County
	result["detailed_address"] = order.DetailedAddress
	result["order_amount"] = order.OrderAmount
	result["product_list"] = order.ProductList
	result["status"] = order.Status
	
	// 转换下单时间为UTC+8并格式化（与Django版本保持一致）
	orderTimeCN := order.OrderTime.Add(8 * time.Hour)
	result["order_time"] = orderTimeCN.Format("2006-01-02 15:04:05")
	
	// 添加物流相关字段
	if order.ExpressCompany != "" {
		result["express_company"] = order.ExpressCompany
	} else {
		result["express_company"] = ""
	}
	
	if order.ExpressNumber != "" {
		result["express_number"] = order.ExpressNumber
	} else {
		result["express_number"] = ""
	}
	
	// 初始化空物流过程列表
	result["logistics_process"] = []interface{}{}

	return result
}

// 工具函数：将订单列表转换为map数组
func convertOrdersToMap(orders []models.Order) []map[string]interface{} {
	result := make([]map[string]interface{}, 0, len(orders))
	for _, order := range orders {
		result = append(result, convertOrderToMap(order))
	}
	return result
}

// ChangeReceivingData 修改收货信息 - 与Django版本的change_receiving_data函数对应
func (oc *OrderController) ChangeReceivingData(c *gin.Context) {
	// 绑定请求数据
	var requestData struct {
		OrderID        string `json:"order_id" binding:"required"`
		ReceiverName   string `json:"receiver_name" binding:"required"`
		ReceiverPhone  string `json:"receiver_phone" binding:"required"`
		Province       string `json:"province" binding:"required"`
		City           string `json:"city" binding:"required"`
		County         string `json:"county" binding:"required"`
		DetailedAddress string `json:"detailed_address" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", requestData.OrderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "订单不存在",
		})
		return
	}

	// 检查订单状态是否允许修改收货信息
	if order.Status == "shipped" || order.Status == "delivered" || order.Status == "cancelled" {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "订单状态不允许修改收货信息",
		})
		return
	}

	// 更新收货信息
	order.ReceiverName = requestData.ReceiverName
	order.ReceiverPhone = requestData.ReceiverPhone
	order.Province = requestData.Province
	order.City = requestData.City
	order.County = requestData.County
	order.DetailedAddress = requestData.DetailedAddress

	if err := db.DB.Save(&order).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "修改收货信息失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "收货信息修改成功",
		"data": gin.H{"order_id": requestData.OrderID}
	})
}
