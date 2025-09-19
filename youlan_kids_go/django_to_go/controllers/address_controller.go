package controllers

import (
	"net/http"

	"django_to_go/db"
	"django_to_go/models"

	"github.com/gin-gonic/gin"
)

// AddressController 地址控制器
type AddressController struct{}

// AddAddress 添加地址
func (ac *AddressController) AddAddress(c *gin.Context) {
	var requestData struct {
		UserID      uint   `json:"user_id" binding:"required"`
		Consignee   string `json:"consignee" binding:"required"`
		Phone       string `json:"phone" binding:"required"`
		Province    string `json:"province" binding:"required"`
		City        string `json:"city" binding:"required"`
		District    string `json:"district" binding:"required"`
		DetailAddr  string `json:"detail_addr" binding:"required"`
		IsDefault   bool   `json:"is_default"`
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

	// 如果设置为默认地址，先将该用户的其他默认地址取消
	if requestData.IsDefault {
		// 取消该用户的所有默认地址
		db.DB.Model(&models.Address{}).
			Where("user_id = ? AND is_default = ?", requestData.UserID, true).
			Update("is_default", false)
	}

	// 创建新地址
	address := models.Address{
		UserID:      requestData.UserID,
		Consignee:   requestData.Consignee,
		Phone:       requestData.Phone,
		Province:    requestData.Province,
		City:        requestData.City,
		District:    requestData.District,
		DetailAddr:  requestData.DetailAddr,
		IsDefault:   requestData.IsDefault,
	}

	if err := db.DB.Create(&address).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "添加地址失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "地址添加成功",
		"data":    address,
	})
}

// DeleteAddress 删除地址
func (ac *AddressController) DeleteAddress(c *gin.Context) {
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

	// 查询地址
	var address models.Address
	if err := db.DB.Where("id = ?", requestData.ID).First(&address).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "地址不存在",
		})
		return
	}

	// 删除地址
	if err := db.DB.Delete(&address).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "删除地址失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "地址删除成功",
	})
}

// UpdateAddress 更新地址
func (ac *AddressController) UpdateAddress(c *gin.Context) {
	var requestData struct {
		ID          uint   `json:"id" binding:"required"`
		Consignee   string `json:"consignee" binding:"required"`
		Phone       string `json:"phone" binding:"required"`
		Province    string `json:"province" binding:"required"`
		City        string `json:"city" binding:"required"`
		District    string `json:"district" binding:"required"`
		DetailAddr  string `json:"detail_addr" binding:"required"`
		IsDefault   bool   `json:"is_default"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询地址
	var address models.Address
	if err := db.DB.Where("id = ?", requestData.ID).First(&address).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "地址不存在",
		})
		return
	}

	// 如果设置为默认地址，先将该用户的其他默认地址取消
	if requestData.IsDefault {
		db.DB.Model(&models.Address{}).
			Where("user_id = ? AND is_default = ? AND id != ?", address.UserID, true, requestData.ID).
			Update("is_default", false)
	}

	// 更新地址信息
	address.Consignee = requestData.Consignee
	address.Phone = requestData.Phone
	address.Province = requestData.Province
	address.City = requestData.City
	address.District = requestData.District
	address.DetailAddr = requestData.DetailAddr
	address.IsDefault = requestData.IsDefault

	if err := db.DB.Save(&address).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "更新地址失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "地址更新成功",
		"data":    address,
	})
}

// SetDefaultAddress 设置默认地址
func (ac *AddressController) SetDefaultAddress(c *gin.Context) {
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

	// 查询地址
	var address models.Address
	if err := db.DB.Where("id = ?", requestData.ID).First(&address).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "地址不存在",
		})
		return
	}

	// 取消该用户的所有默认地址
	db.DB.Model(&models.Address{}).
		Where("user_id = ? AND is_default = ?", address.UserID, true).
		Update("is_default", false)

	// 设置当前地址为默认
	address.IsDefault = true
	if err := db.DB.Save(&address).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "设置默认地址失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "默认地址设置成功",
	})
}

// GetAddresses 查询地址列表
func (ac *AddressController) GetAddresses(c *gin.Context) {
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

	// 查询用户的所有地址
	var addresses []models.Address
	if err := db.DB.Where("user_id = ?", requestData.UserID).Find(&addresses).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "查询地址失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "查询成功",
		"data":    addresses,
	})
}

// GetAddressByID 查询单个地址
func (ac *AddressController) GetAddressByID(c *gin.Context) {
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

	// 查询地址
	var address models.Address
	if err := db.DB.Where("id = ?", requestData.ID).First(&address).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "地址不存在",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "查询成功",
		"data":    address,
	})
}