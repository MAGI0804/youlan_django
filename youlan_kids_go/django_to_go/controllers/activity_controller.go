package controllers

import (
	"net/http"
	"time"

	"django_to_go/db"
	"django_to_go/models"

	"github.com/gin-gonic/gin"
)

// ActivityController 活动控制器
type ActivityController struct{}

// AddActivityImg 添加活动图片
func (ac *ActivityController) AddActivityImg(c *gin.Context) {
	var requestData struct {
		ImgURL    string `json:"img_url" binding:"required"`
		Title     string `json:"title" binding:"required"`
		Link      string `json:"link" binding:"required"`
		StartDate string `json:"start_date" binding:"required"`
		EndDate   string `json:"end_date" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 解析日期
	startDate, err := time.Parse("2006-01-02", requestData.StartDate)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "开始日期格式错误",
		})
		return
	}

	endDate, err := time.Parse("2006-01-02", requestData.EndDate)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "结束日期格式错误",
		})
		return
	}

	// 创建活动图片
	activityImg := models.ActivityImage{
		ImgURL:    requestData.ImgURL,
		Title:     requestData.Title,
		Link:      requestData.Link,
		StartDate: startDate,
		EndDate:   endDate,
		Status:    "offline", // 默认下线状态
	}

	if err := db.DB.Create(&activityImg).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "添加活动图片失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "活动图片添加成功",
		"data": gin.H{"id": activityImg.ID},
	})
}

// UpdateActivityImageRelations 更新活动图片关系
func (ac *ActivityController) UpdateActivityImageRelations(c *gin.Context) {
	var requestData struct {
		ActivityImgID uint   `json:"activity_img_id" binding:"required"`
		ProductIDs    []uint `json:"product_ids"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 查询活动图片
	var activityImg models.ActivityImage
	if err := db.DB.Where("id = ?", requestData.ActivityImgID).First(&activityImg).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "活动图片不存在",
		})
		return
	}

	// 首先删除旧的关系
	db.DB.Where("activity_image_id = ?", requestData.ActivityImgID).Delete(&models.ActivityImageProduct{})

	// 添加新的关系
	for _, productID := range requestData.ProductIDs {
		relation := models.ActivityImageProduct{
			ActivityImageID: requestData.ActivityImgID,
			ProductID:       productID,
		}
		if err := db.DB.Create(&relation).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"status":  "error",
				"message": "更新活动图片关系失败",
			})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "活动图片关系更新成功",
	})
}

// ActivityImageOnline 活动图片上线
func (ac *ActivityController) ActivityImageOnline(c *gin.Context) {
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

	// 查询活动图片
	var activityImg models.ActivityImage
	if err := db.DB.Where("id = ?", requestData.ID).First(&activityImg).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "活动图片不存在",
		})
		return
	}

	// 更新状态为上线
	activityImg.Status = "online"
	if err := db.DB.Save(&activityImg).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "活动图片上线失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "活动图片上线成功",
	})
}

// ActivityImageOffline 活动图片下线
func (ac *ActivityController) ActivityImageOffline(c *gin.Context) {
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

	// 查询活动图片
	var activityImg models.ActivityImage
	if err := db.DB.Where("id = ?", requestData.ID).First(&activityImg).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"status":  "error",
			"message": "活动图片不存在",
		})
		return
	}

	// 更新状态为下线
	activityImg.Status = "offline"
	if err := db.DB.Save(&activityImg).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"message": "活动图片下线失败",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "活动图片下线成功",
	})
}

// BatchQueryActivityImages 批量查询活动图片
func (ac *ActivityController) BatchQueryActivityImages(c *gin.Context) {
	// 绑定请求参数
	var requestData struct {
		Status string `json:"status"`
		Page   int    `json:"page"`
		Size   int    `json:"size"`
	}

	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"message": "请求数据无效",
		})
		return
	}

	// 设置默认分页参数
	if requestData.Page <= 0 {
		requestData.Page = 1
	}
	if requestData.Size <= 0 {
		requestData.Size = 10
	}

	// 构建查询
	query := db.DB.Model(&models.ActivityImage{})

	// 添加状态过滤
	if requestData.Status != "" {
		query = query.Where("status = ?", requestData.Status)
	}

	// 查询总数
	var total int64
	query.Count(&total)

	// 查询数据
	var activityImages []models.ActivityImage
	query.Offset((requestData.Page - 1) * requestData.Size).Limit(requestData.Size).Find(&activityImages)

	// 转换为响应格式
	result := make([]map[string]interface{}, 0, len(activityImages))
	for _, img := range activityImages {
		result = append(result, map[string]interface{}{
			"id":         img.ID,
			"img_url":    img.ImgURL,
			"title":      img.Title,
			"link":       img.Link,
			"start_date": img.StartDate.Format("2006-01-02"),
			"end_date":   img.EndDate.Format("2006-01-02"),
			"status":     img.Status,
			"create_time": img.CreateTime.Format("2006-01-02 15:04:05"),
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "success",
		"message": "查询成功",
		"data":    result,
		"page":    requestData.Page,
		"page_size": requestData.Size,
		"total":   total,
	})
}