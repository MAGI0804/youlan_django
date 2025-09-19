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

// OrderList 获取订单列表
func (oc *OrderController) OrderList(c *gin.Context) {
	// 获取查询参数
	userIDStr := c.Query("user_id")
	if userIDStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少user_id参数"})
		return
	}

	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的user_id"})
		return
	}

	pageNum, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	status := c.Query("status")

	// 计算偏移量
	offset := (pageNum - 1) * pageSize

	// 构建查询
	var orders []models.Order
	query := db.DB.Model(&models.Order{}).Where("user_id = ?", userID)

	// 添加状态筛选
	if status != "" {
		query = query.Where("status = ?", status)
	}

	// 执行分页查询
	var total int64
	if err := query.Count(&total).Error; err != nil {
		log.Printf("获取订单总数失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	if err := query.Offset(offset).Limit(pageSize).Order("order_id DESC").Find(&orders).Error; err != nil {
		log.Printf("获取订单列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 准备响应数据
	responseData := gin.H{
		"code":    200,
		"message": "获取成功",
		"data": gin.H{
			"total": total,
			"items": convertOrdersToMap(orders),
		},
	}

	c.JSON(http.StatusOK, responseData)
}

// OrderDetail 获取订单详情
func (oc *OrderController) OrderDetail(c *gin.Context) {
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

	// 查询订单物流信息
	var logistics models.OrderLogistics
	if err := db.DB.Where("order_id = ?", orderID).First(&logistics).Error; err != nil {
		log.Printf("获取物流信息失败: %v", err)
	}

	// 准备响应数据
	detailMap := convertOrderToMap(order)
	if logistics.ID > 0 {
		detailMap["logistics"] = map[string]interface{}{
			"express_company": logistics.ExpressCompany,
			"express_number":  logistics.ExpressNumber,
			"status":          logistics.Status,
			"details":         logistics.Details,
			"last_updated":    logistics.LastUpdated.Format("2006-01-02 15:04:05"),
		}
	}

	responseData := gin.H{
		"code":    200,
		"message": "获取成功",
		"data":    detailMap,
	}

	c.JSON(http.StatusOK, responseData)
}

// OrderCreate 创建订单
func (oc *OrderController) OrderCreate(c *gin.Context) {
	var requestData map[string]interface{}
	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的JSON格式"})
		return
	}

	// 获取必要参数
	userIDFloat, ok := requestData["user_id"].(float64)
	commodityIDFloat, ok2 := requestData["commodity_id"].(float64)
	quantityFloat, ok3 := requestData["quantity"].(float64)
	receiverName, ok4 := requestData["receiver_name"].(string)
	receiverPhone, ok5 := requestData["receiver_phone"].(string)
	address, ok6 := requestData["address"].(string)

	if !ok || !ok2 || !ok3 || !ok4 || !ok5 || !ok6 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少必要的订单信息"})
		return
	}

	userID := int(userIDFloat)
	commodityID := int(commodityIDFloat)
	quantity := int(quantityFloat)

	// 查询商品信息
	var commodity models.Commodity
	if err := db.DB.Where("commodity_id = ?", commodityID).First(&commodity).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "商品不存在"})
		return
	}

	// 查询商品库存
	var commoditySituation models.CommoditySituation
	if err := db.DB.Where("commodity_id = ?", commodityID).First(&commoditySituation).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取商品库存失败"})
		return
	}

	// 检查商品状态
	if commoditySituation.Status != "online" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "商品已下架"})
		return
	}

	// 计算订单总价
	totalPrice := commodity.Price * float64(quantity)

	// 生成订单号
	orderNo := generateOrderNo()

	// 创建订单
	order := models.Order{
		OrderID:         orderNo,
		UserID:          userID,
		CommodityID:     strconv.Itoa(commodityID),
		CommodityName:   commodity.Name,
		Quantity:        quantity,
		Price:           commodity.Price,
		TotalAmount:     totalPrice,
		Status:          "待付款",
		ReceiverName:    receiverName,
		ReceiverPhone:   receiverPhone,
		Province:        "",
		City:            "",
		County:          "",
		DetailedAddress: address,
	}

	// 开始事务
	tx := db.DB.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	// 创建订单记录
	if err := tx.Create(&order).Error; err != nil {
		tx.Rollback()
		log.Printf("创建订单失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 检查商品状态
	if commoditySituation.Status != "online" {
		tx.Rollback()
		c.JSON(http.StatusBadRequest, gin.H{"error": "商品已下架"})
		return
	}

	// 提交事务
	tx.Commit()

	c.JSON(http.StatusCreated, gin.H{
		"code":    201,
		"message": "订单创建成功",
		"data":    convertOrderToMap(order),
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

// OrderCancel 取消订单
func (oc *OrderController) OrderCancel(c *gin.Context) {
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

	// 检查订单状态是否允许取消
	if order.Status != "待付款" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "订单状态不允许取消"})
		return
	}

	// 更新订单状态
	order.Status = "已取消"

	// 开始事务
	tx := db.DB.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	// 保存更新
	if err := tx.Save(&order).Error; err != nil {
		tx.Rollback()
		log.Printf("取消订单失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 检查商品状态
	var commoditySituation models.CommoditySituation
	if err := tx.Where("commodity_id = ?", order.CommodityID).First(&commoditySituation).Error; err != nil {
		tx.Rollback()
		log.Printf("获取商品信息失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 提交事务
	tx.Commit()

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "订单已取消",
		"data":    convertOrderToMap(order),
	})
}

// OrderPay 订单支付
func (oc *OrderController) OrderPay(c *gin.Context) {
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

	// 检查订单状态
	if order.Status != "待付款" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "订单状态不允许支付"})
		return
	}

	// 更新订单状态和支付信息
	order.Status = "已付款"
	order.PaymentMethod = "微信支付"
	order.PaymentTime = time.Now()

	if err := db.DB.Save(&order).Error; err != nil {
		log.Printf("订单支付失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "订单支付成功",
		"data":    convertOrderToMap(order),
	})
}

// OrderDeliver 订单发货
func (oc *OrderController) OrderDeliver(c *gin.Context) {
	orderIDStr := c.Param("id")
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的订单ID"})
		return
	}

	// 绑定请求数据
	var deliverData map[string]interface{}
	if err := c.ShouldBindJSON(&deliverData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的JSON格式"})
		return
	}

	logisticsCompany, ok1 := deliverData["logistics_company"].(string)
	trackingNumber, ok2 := deliverData["tracking_number"].(string)

	if !ok1 || !ok2 || logisticsCompany == "" || trackingNumber == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少必要的物流信息"})
		return
	}

	// 查询订单
	var order models.Order
	if err := db.DB.Where("order_id = ?", orderID).First(&order).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "订单不存在"})
		return
	}

	// 检查订单状态
	if order.Status != "已付款" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "订单状态不允许发货"})
		return
	}

	// 更新订单状态
	order.Status = "已发货"

	// 创建物流信息
	logistics := models.OrderLogistics{
		OrderID:        strconv.Itoa(orderID),
		ExpressCompany: logisticsCompany,
		ExpressNumber:  trackingNumber,
		Status:         "已发货",
		Details:        "订单已发货",
	}

	// 开始事务
	tx := db.DB.Begin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	// 保存订单更新
	if err := tx.Save(&order).Error; err != nil {
		tx.Rollback()
		log.Printf("更新订单状态失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 创建物流记录
	if err := tx.Create(&logistics).Error; err != nil {
		tx.Rollback()
		log.Printf("创建物流记录失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 提交事务
	tx.Commit()

	// 更新商品销量
	var commoditySituation models.CommoditySituation
	if err := db.DB.Where("commodity_id = ?", order.CommodityID).First(&commoditySituation).Error; err == nil {
		commoditySituation.SalesVolume += order.Quantity
		db.DB.Save(&commoditySituation)
	}

	// 准备响应数据
	detailMap := convertOrderToMap(order)
	now := time.Now()
	detailMap["logistics"] = map[string]interface{}{
		"express_company": logisticsCompany,
		"express_number":  trackingNumber,
		"status":          "已发货",
		"create_time":     now.Format("2006-01-02 15:04:05"),
	}

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "订单发货成功",
		"data":    detailMap,
	})
}

// 工具函数：生成订单号
func generateOrderNo() string {
	year := time.Now().Year()
	month := time.Now().Month()
	day := time.Now().Day()
	hour := time.Now().Hour()
	minute := time.Now().Minute()
	second := time.Now().Second()
	nano := time.Now().UnixNano() % 1000000

	return fmt.Sprintf("%d%02d%02d%02d%02d%02d%06d", year, month, day, hour, minute, second, nano)
}

// 工具函数：将订单对象转换为map
func convertOrderToMap(order models.Order) map[string]interface{} {
	result := make(map[string]interface{})
	result["order_id"] = order.OrderID
	result["user_id"] = order.UserID
	result["commodity_id"] = order.CommodityID
	result["commodity_name"] = order.CommodityName
	result["quantity"] = order.Quantity
	result["price"] = order.Price
	result["total_amount"] = order.TotalAmount
	result["status"] = order.Status
	result["payment_method"] = order.PaymentMethod
	result["receiver_name"] = order.ReceiverName
	result["receiver_phone"] = order.ReceiverPhone
	result["province"] = order.Province
	result["city"] = order.City
	result["county"] = order.County
	result["detailed_address"] = order.DetailedAddress
	result["order_time"] = order.OrderTime.Format("2006-01-02 15:04:05")

	// 检查支付时间是否为零值
	if !order.PaymentTime.IsZero() {
		result["payment_time"] = order.PaymentTime.Format("2006-01-02 15:04:05")
	}

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
