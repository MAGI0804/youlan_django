package controllers

import (
	"net/http"

	"django_to_go/db"
	"django_to_go/models"

	"github.com/gin-gonic/gin"
)

// CartController 购物车控制器
type CartController struct{}

// AddToCart 添加商品到购物车
func (cc *CartController) AddToCart(c *gin.Context) {
	var requestData struct {
		UserID    uint `json:"user_id" binding:"required"`
		ProductID uint `json:"product_id" binding:"required"`
		Quantity  int  `json:"quantity" binding:"required,min=1"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 检查用户是否存在
	var user models.User
	if err := db.DB.Where("id = ?", requestData.UserID).First(&user).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "用户不存在",
		})
		return
	}

	// 检查商品是否存在
	var product models.Product
	if err := db.DB.Where("id = ?", requestData.ProductID).First(&product).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "商品不存在",
		})
		return
	}

	// 检查购物车中是否已存在该商品
	var cartItem models.CartItem
	if err := db.DB.Where("user_id = ? AND product_id = ?", requestData.UserID, requestData.ProductID).First(&cartItem).Error; err == nil {
		// 商品已存在，更新数量
		cartItem.Quantity += requestData.Quantity
		if err := db.DB.Save(&cartItem).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"status":  "error",
				"message": "更新购物车失败",
			})
			return
		}
	} else {
		// 商品不存在，创建新的购物车项
		cartItem = models.CartItem{
			UserID:    requestData.UserID,
			ProductID: requestData.ProductID,
			Quantity:  requestData.Quantity,
		}
		if err := db.DB.Create(&cartItem).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"status":  "error",
				"message": "添加到购物车失败",
			})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "添加到购物车成功",
	})
}

// BatchDeleteFromCart 批量删除购物车商品
func (cc *CartController) BatchDeleteFromCart(c *gin.Context) {
	var requestData struct {
		UserID      uint   `json:"user_id" binding:"required"`
		CartItemIDs []uint `json:"cart_item_ids" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 检查用户是否存在
	var user models.User
	if err := db.DB.Where("id = ?", requestData.UserID).First(&user).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "用户不存在",
		})
		return
	}

	// 删除购物车项
	if err := db.DB.Where("user_id = ? AND id IN (?)", requestData.UserID, requestData.CartItemIDs).Delete(&models.CartItem{}).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "删除购物车商品失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "购物车商品删除成功",
	})
}

// QueryCartItems 查询购物车所有商品
func (cc *CartController) QueryCartItems(c *gin.Context) {
	var requestData struct {
		UserID uint `json:"user_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询用户的购物车商品
	var cartItems []models.CartItem
	if err := db.DB.Where("user_id = ?", requestData.UserID).Preload("Product").Find(&cartItems).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "查询购物车失败",
		})
		return
	}

	// 转换为响应格式
	result := make([]map[string]interface{}, 0, len(cartItems))
	for _, item := range cartItems {
		result = append(result, map[string]interface{}{
			"id":          item.ID,
			"user_id":     item.UserID,
			"product_id":  item.ProductID,
			"quantity":    item.Quantity,
			"product_name": item.Product.Name,
			"price":       item.Product.Price,
			"image_url":   item.Product.ImageURL,
			"create_time": item.CreateTime.Format("2006-01-02 15:04:05"),
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "查询成功",
		"data":    result,
	})
}

// UpdateCartItemQuantity 更新购物车商品数量
func (cc *CartController) UpdateCartItemQuantity(c *gin.Context) {
	var requestData struct {
		ID       uint `json:"id" binding:"required"`
		Quantity int  `json:"quantity" binding:"required,min=1"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询购物车项
	var cartItem models.CartItem
	if err := db.DB.Where("id = ?", requestData.ID).First(&cartItem).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "购物车商品不存在",
		})
		return
	}

	// 更新数量
	cartItem.Quantity = requestData.Quantity
	if err := db.DB.Save(&cartItem).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "更新购物车商品数量失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "购物车商品数量更新成功",
	})
}

// IncreaseCartItemQuantity 购物车商品数量加1
func (cc *CartController) IncreaseCartItemQuantity(c *gin.Context) {
	var requestData struct {
		ID uint `json:"id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询购物车项
	var cartItem models.CartItem
	if err := db.DB.Where("id = ?", requestData.ID).First(&cartItem).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "购物车商品不存在",
		})
		return
	}

	// 数量加1
	cartItem.Quantity++
	if err := db.DB.Save(&cartItem).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "增加购物车商品数量失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "购物车商品数量增加成功",
	})
}

// DecreaseCartItemQuantity 购物车商品数量减1
func (cc *CartController) DecreaseCartItemQuantity(c *gin.Context) {
	var requestData struct {
		ID uint `json:"id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询购物车项
	var cartItem models.CartItem
	if err := db.DB.Where("id = ?", requestData.ID).First(&cartItem).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "购物车商品不存在",
		})
		return
	}

	// 检查数量是否大于1
	if cartItem.Quantity <= 1 {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "商品数量不能小于1",
		})
		return
	}

	// 数量减1
	cartItem.Quantity--
	if err := db.DB.Save(&cartItem).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "减少购物车商品数量失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "购物车商品数量减少成功",
	})
}

// ClearCart 清空购物车
func (cc *CartController) ClearCart(c *gin.Context) {
	var requestData struct {
		UserID uint `json:"user_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 清空用户的购物车
	if err := db.DB.Where("user_id = ?", requestData.UserID).Delete(&models.CartItem{}).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "清空购物车失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "购物车已清空",
	})
}