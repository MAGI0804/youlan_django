package controllers

import (
	"net/http"

	"django_to_go/db"
	"django_to_go/models"

	"github.com/gin-gonic/gin"
)

// OperationUserController 操作用户控制器
type OperationUserController struct{}

// AddServiceUser 添加服务用户
func (ouc *OperationUserController) AddServiceUser(c *gin.Context) {
	var requestData struct {
		Username string `json:"username" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 检查用户是否已存在
	var existingUser models.OperationUser
	if err := db.DB.Where("username = ?", requestData.Username).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "用户已存在",
		})
		return
	}

	// 创建新服务用户
	serviceUser := models.OperationUser{
		Username: requestData.Username,
		Password: requestData.Password,
		UserType: "service",
		Status:   "active",
	}

	if err := db.DB.Create(&serviceUser).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "添加服务用户失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "服务用户添加成功",
		"data": gin.H{"id": serviceUser.ID},
	})
}

// AddOperationUser 添加操作用户
func (ouc *OperationUserController) AddOperationUser(c *gin.Context) {
	var requestData struct {
		Username string `json:"username" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 检查用户是否已存在
	var existingUser models.OperationUser
	if err := db.DB.Where("username = ?", requestData.Username).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "用户已存在",
		})
		return
	}

	// 创建新操作用户
	operationUser := models.OperationUser{
		Username: requestData.Username,
		Password: requestData.Password,
		UserType: "operation",
		Status:   "active",
	}

	if err := db.DB.Create(&operationUser).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "添加操作用户失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "操作用户添加成功",
		"data": gin.H{"id": operationUser.ID},
	})
}

// VerificationStatus 验证用户状态
func (ouc *OperationUserController) VerificationStatus(c *gin.Context) {
	var requestData struct {
		Username string `json:"username" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询用户
	var user models.OperationUser
	if err := db.DB.Where("username = ? AND password = ?", requestData.Username, requestData.Password).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{
			"status":  "error",
			"message": "用户名或密码错误",
		})
		return
	}

	// 检查用户状态
	if user.Status != "active" {
		c.JSON(http.StatusForbidden, gin.H{
			"status":  "error",
			"message": "用户状态异常",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "验证成功",
		"data": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"user_type": user.UserType,
		},
	})
}

// ChangePassword 修改密码
func (ouc *OperationUserController) ChangePassword(c *gin.Context) {
	var requestData struct {
		Username    string `json:"username" binding:"required"`
		OldPassword string `json:"old_password" binding:"required"`
		NewPassword string `json:"new_password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询用户
	var user models.OperationUser
	if err := db.DB.Where("username = ? AND password = ?", requestData.Username, requestData.OldPassword).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{
			"status":  "error",
			"message": "用户名或旧密码错误",
		})
		return
	}

	// 更新密码
	user.Password = requestData.NewPassword
	if err := db.DB.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "修改密码失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "密码修改成功",
	})
}