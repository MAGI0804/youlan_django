package controllers

import (
	"fmt"
	"log"
	"net/http"
	"strconv"
	"github.com/gin-gonic/gin"
	"django_to_go/db"
	"django_to_go/models"
)

// CommodityController 商品控制器

type CommodityController struct{}

// CommodityList 获取商品列表
func (cc *CommodityController) CommodityList(c *gin.Context) {
	// 获取查询参数
	pageNum, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
	category := c.Query("category")
	keyword := c.Query("keyword")

	// 计算偏移量
	offset := (pageNum - 1) * pageSize

	// 构建查询
	var commodities []models.Commodity
	query := db.DB.Model(&models.Commodity{})

	// 添加分类筛选
	if category != "" {
		query = query.Where("category = ?", category)
	}

	// 添加关键词搜索
	if keyword != "" {
		query = query.Where("name LIKE ? OR style_code LIKE ?", "%"+keyword+"%", "%"+keyword+"%")
	}

	// 执行分页查询
	var total int64
	if err := query.Count(&total).Error; err != nil {
		log.Printf("获取商品总数失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	if err := query.Offset(offset).Limit(pageSize).Order("commodity_id DESC").Find(&commodities).Error; err != nil {
		log.Printf("获取商品列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 准备响应数据
	responseData := gin.H{
		"code":    200,
		"message": "获取成功",
		"data": gin.H{
			"total": total,
			"items": convertCommoditiesToMap(commodities, c),
		},
	}

	c.JSON(http.StatusOK, responseData)
}

// CommodityDetail 获取商品详情
func (cc *CommodityController) CommodityDetail(c *gin.Context) {
	commodityIDStr := c.Param("id")
	commodityID, err := strconv.Atoi(commodityIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的商品ID"})
		return
	}

	// 查询商品
	var commodity models.Commodity
	if err := db.DB.Where("commodity_id = ?", commodityID).First(&commodity).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "商品不存在"})
		return
	}

	// 查询商品图片
	var commodityImages []models.CommodityImage
	if err := db.DB.Where("commodity_id = ?", commodityID).Find(&commodityImages).Error; err != nil {
		log.Printf("获取商品图片失败: %v", err)
	}

	// 查询商品状态
	var commoditySituation models.CommoditySituation
	if err := db.DB.Where("commodity_id = ?", strconv.Itoa(commodityID)).First(&commoditySituation).Error; err != nil {
		// 如果没有状态记录，创建一个默认的
		commoditySituation = models.CommoditySituation{
			CommodityID: strconv.Itoa(commodityID),
			Status:      "online",
			SalesVolume: 0,
			StyleCode:   commodity.StyleCode,
		}
		if err := db.DB.Create(&commoditySituation).Error; err != nil {
			log.Printf("创建商品状态记录失败: %v", err)
		}
	}

	// 准备响应数据
	detailMap := convertCommodityToMap(commodity, c)
	detailMap["images"] = convertImagesToMap(commodityImages, c)
	detailMap["status"] = commoditySituation.Status
	detailMap["sales_volume"] = commoditySituation.SalesVolume

	responseData := gin.H{
		"code":    200,
		"message": "获取成功",
		"data":    detailMap,
	}

	c.JSON(http.StatusOK, responseData)
}

// CommodityCreate 创建商品
func (cc *CommodityController) CommodityCreate(c *gin.Context) {
	var requestData models.Commodity
	if err := c.ShouldBindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的JSON格式"})
		return
	}

	// 验证必要字段
	if requestData.Name == "" || requestData.Price <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少必要的商品信息"})
		return
	}

	// 创建商品
	commodity := models.Commodity{
		Name:       requestData.Name,
		StyleCode:  requestData.StyleCode,
		Category:   requestData.Category,
		Price:      requestData.Price,
		Size:       requestData.Size,
		Color:      requestData.Color,
		Image:      "default.png", // 默认图片路径
	}

	if err := db.DB.Create(&commodity).Error; err != nil {
		log.Printf("创建商品失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	// 创建商品状态
	commoditySituation := models.CommoditySituation{
		CommodityID: commodity.CommodityID,
		Status:      "online", // 设置为在线状态
	}

	if err := db.DB.Create(&commoditySituation).Error; err != nil {
		log.Printf("创建商品状态失败: %v", err)
	}

	// 如果有款式代码，处理款式相关数据
	if requestData.StyleCode != "" {
		// 查找或创建款式数据
		var styleCodeData models.StyleCodeData
		if err := db.DB.Where("style_code = ?", requestData.StyleCode).First(&styleCodeData).Error; err != nil {
			styleCodeData = models.StyleCodeData{
				StyleCode: requestData.StyleCode,
			}
			if err := db.DB.Create(&styleCodeData).Error; err != nil {
				log.Printf("创建款式数据失败: %v", err)
			}
		}

		// 查找或创建款式状态
	var styleCodeSituation models.StyleCodeSituation
	if err := db.DB.Where("style_code = ?", requestData.StyleCode).First(&styleCodeSituation).Error; err != nil {
		styleCodeSituation = models.StyleCodeSituation{
			StyleCode: requestData.StyleCode,
			Status:    "online",
		}
		if err := db.DB.Create(&styleCodeSituation).Error; err != nil {
			log.Printf("创建款式状态失败: %v", err)
		}
	}
	}

	c.JSON(http.StatusCreated, gin.H{
		"code":    201,
		"message": "商品创建成功",
		"data":    gin.H{"commodity_id": commodity.CommodityID},
	})
}

// CommodityUpdate 更新商品
func (cc *CommodityController) CommodityUpdate(c *gin.Context) {
	commodityIDStr := c.Param("id")
	commodityID, err := strconv.Atoi(commodityIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的商品ID"})
		return
	}

	// 查询商品
	var commodity models.Commodity
	if err := db.DB.Where("commodity_id = ?", commodityID).First(&commodity).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "商品不存在"})
		return
	}

	// 绑定请求数据
	var updateData models.Commodity
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的JSON格式"})
		return
	}

	// 更新字段
	if updateData.Name != "" {
		commodity.Name = updateData.Name
	}
	if updateData.StyleCode != "" {
		commodity.StyleCode = updateData.StyleCode
	}
	if updateData.Category != "" {
		commodity.Category = updateData.Category
	}
	if updateData.Price > 0 {
		commodity.Price = updateData.Price
	}
	if updateData.Size != "" {
		commodity.Size = updateData.Size
	}
	if updateData.Color != "" {
		commodity.Color = updateData.Color
	}
	if updateData.CategoryDetail != "" {
		commodity.CategoryDetail = updateData.CategoryDetail
	}
	if updateData.Height != "" {
		commodity.Height = updateData.Height
	}
	if updateData.SpecCode != "" {
		commodity.SpecCode = updateData.SpecCode
	}
	if updateData.Notes != "" {
		commodity.Notes = updateData.Notes
	}

	// 保存更新
	if err := db.DB.Save(&commodity).Error; err != nil {
		log.Printf("更新商品失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "商品更新成功",
	})
}

// CommodityDelete 删除商品
func (cc *CommodityController) CommodityDelete(c *gin.Context) {
	commodityIDStr := c.Param("id")
	commodityID, err := strconv.Atoi(commodityIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的商品ID"})
		return
	}

	// 查询商品
	var commodity models.Commodity
	if err := db.DB.Where("commodity_id = ?", strconv.Itoa(commodityID)).First(&commodity).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "商品不存在"})
		return
	}

	// 删除商品（软删除）
	if err := db.DB.Delete(&commodity).Error; err != nil {
		log.Printf("删除商品失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "服务器内部错误"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "商品删除成功",
	})
}

// 工具函数：将商品对象转换为map
func convertCommodityToMap(commodity models.Commodity, c *gin.Context) map[string]interface{} {
	result := make(map[string]interface{})
	result["commodity_id"] = commodity.CommodityID
	result["name"] = commodity.Name
	result["style_code"] = commodity.StyleCode
	result["category"] = commodity.Category
	result["category_detail"] = commodity.CategoryDetail
	result["price"] = commodity.Price
	result["size"] = commodity.Size
	result["color"] = commodity.Color
	result["height"] = commodity.Height
	result["spec_code"] = commodity.SpecCode
	result["notes"] = commodity.Notes
	result["created_at"] = commodity.CreatedAt.Format("2006-01-02 15:04:05")

	// 处理图片URL
	if commodity.Image != "" {
		baseURL := fmt.Sprintf("%s://%s", c.Request.URL.Scheme, c.Request.Host)
		result["image"] = baseURL + "/" + commodity.Image
	}

	return result
}

// 工具函数：将商品列表转换为map数组
func convertCommoditiesToMap(commodities []models.Commodity, c *gin.Context) []map[string]interface{} {
	result := make([]map[string]interface{}, 0, len(commodities))
	for _, commodity := range commodities {
		result = append(result, convertCommodityToMap(commodity, c))
	}
	return result
}

// 工具函数：将图片列表转换为map数组
func convertImagesToMap(images []models.CommodityImage, c *gin.Context) []map[string]interface{} {
	result := make([]map[string]interface{}, 0, len(images))
	baseURL := fmt.Sprintf("%s://%s", c.Request.URL.Scheme, c.Request.Host)

	for _, image := range images {
		imgMap := make(map[string]interface{})
		imgMap["id"] = image.ID
		imgMap["url"] = baseURL + "/" + image.Image
		imgMap["is_main"] = image.IsMain
		result = append(result, imgMap)
	}

	return result
}
